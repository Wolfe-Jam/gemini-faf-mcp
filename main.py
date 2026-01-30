"""
gemini-faf-mcp: Google Cloud Function for FAF Context Bridge

Media Type: application/vnd.faf+yaml
Endpoint: https://faf-source-of-truth-*.run.app
Version: 2.5.1

Features:
- GET: Return live SVG badge showing FAF score
- POST: Parse .faf file, return payload optimized for calling agent
- PUT: Voice-to-FAF - update DNA via Gemini Live voice commands
- Multi-Agent Handshake: Optimize payload per AI dialect

Security (v2.5.1):
- SW-01: Temporal Integrity - reject stale timestamps
- SW-02: Scoring Guard - Big Orange requires 100%
"""

import functions_framework
import yaml
import json
import re
import os
import base64
import requests
from datetime import datetime


# =============================================================================
# SECURITY LAYER (v2.5.1)
# =============================================================================

def validate_sw01_temporal_integrity(existing_dna, new_timestamp):
    """
    SW-01: Temporal Integrity
    Reject any payload where the generated timestamp is not greater than
    the current timestamp in the database.
    """
    existing_timestamp = existing_dna.get('generated', '')
    if existing_timestamp and new_timestamp:
        try:
            existing_dt = datetime.fromisoformat(existing_timestamp.replace('Z', '+00:00'))
            new_dt = datetime.fromisoformat(new_timestamp.replace('Z', '+00:00'))
            if new_dt <= existing_dt:
                return False, "SW-01: Temporal integrity violation - timestamp not newer"
        except (ValueError, TypeError):
            pass
    return True, None


def validate_sw02_scoring_guard(updated_dna, updates, calculate_score_func):
    """
    SW-02: Scoring Guard
    Reject any attempt to set distinction: "Big Orange" if score < 100.
    """
    setting_orange = False
    if updates.get('faf_distinction') == 'Big Orange':
        setting_orange = True
    if updates.get('x_faf_orange') == True:
        setting_orange = True
    for key, value in updates.items():
        if 'orange' in key.lower() and value in [True, 'Big Orange', 'orange']:
            setting_orange = True
            break

    if setting_orange:
        score = calculate_score_func(updated_dna)
        if score < 100:
            return False, f"SW-02: Scoring guard - Big Orange requires 100%, current: {score}%"
    return True, None


def log_mutation_telemetry(success, updates, agent='voice', score=None, has_orange=False, error=None, blocked_by=None):
    """Log mutation attempts to BigQuery (non-blocking)."""
    try:
        import uuid
        from google.cloud import bigquery
        client = bigquery.Client()
        table_id = "bucket-460122.faf_telemetry.voice_mutations"

        # Build security status
        if blocked_by:
            security_status = f"BLOCKED:{blocked_by}"
        elif success:
            security_status = "SW-01:passed,SW-02:passed"
        else:
            security_status = f"ERROR:{error}" if error else "UNKNOWN"

        row = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "mutation_summary": json.dumps(updates) if updates else "{}",
            "new_score": score if score is not None else 0,
            "has_orange": has_orange,
            "security_status": security_status,
            "raw_input": json.dumps({"updates": updates, "error": error})
        }
        client.insert_rows_json(table_id, [row])
    except Exception as e:
        print(f"Telemetry logging failed: {e}")


# =============================================================================
# VOICE-TO-FAF: GITHUB COMMIT LAYER
# =============================================================================

def get_github_token():
    """
    Get GitHub token from environment or Secret Manager.
    Token must have 'contents: write' permission on the repo.
    """
    # Try environment first (for local testing)
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return token

    # Try Google Secret Manager
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/bucket-460122/secrets/GITHUB_TOKEN/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception:
        return None


def commit_to_github(new_dna_content, commit_message=None):
    """
    Commit updated FAF DNA to GitHub.

    This enables Voice-to-FAF: speak your updates via Gemini Live,
    and they're committed directly to the repo.
    """
    token = get_github_token()
    if not token:
        return {"error": "GitHub token not configured", "code": 500}

    REPO = "Wolfe-Jam/gemini-faf-mcp"
    PATH = "project.faf"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 1. Get current file SHA (required for updates)
    url = f"https://api.github.com/repos/{REPO}/contents/{PATH}"
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return {"error": f"Failed to get file: {r.text}", "code": r.status_code}
        sha = r.json()['sha']
    except Exception as e:
        return {"error": f"GitHub API error: {str(e)}", "code": 500}

    # 2. Prepare commit
    timestamp = datetime.utcnow().isoformat() + "Z"
    if not commit_message:
        commit_message = f"voice-sync: DNA update via Gemini Live [{timestamp}]"

    # Update generated timestamp in DNA
    new_dna_content['generated'] = timestamp

    # 3. Encode and push
    yaml_content = yaml.dump(new_dna_content, default_flow_style=False, sort_keys=False)
    encoded_content = base64.b64encode(yaml_content.encode()).decode()

    payload = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha
    }

    try:
        r = requests.put(url, headers=headers, json=payload)
        if r.status_code in (200, 201):
            return {
                "success": True,
                "message": commit_message,
                "sha": r.json().get('commit', {}).get('sha', 'unknown'),
                "url": f"https://github.com/{REPO}/blob/main/{PATH}"
            }
        else:
            return {"error": f"Commit failed: {r.text}", "code": r.status_code}
    except Exception as e:
        return {"error": f"Commit error: {str(e)}", "code": 500}


def merge_dna_updates(existing, updates):
    """
    Deep merge updates into existing DNA.
    Supports dot notation: {"project.goal": "new goal"}
    """
    def set_nested(d, keys, value):
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    for key, value in updates.items():
        if '.' in key:
            # Dot notation: project.goal -> project: {goal: ...}
            keys = key.split('.')
            set_nested(existing, keys, value)
        else:
            # Direct key
            if isinstance(value, dict) and key in existing and isinstance(existing[key], dict):
                existing[key].update(value)
            else:
                existing[key] = value

    return existing


# =============================================================================
# MULTI-AGENT TRANSLATION LAYER
# =============================================================================

def detect_agent(request):
    """
    Detect calling AI agent from headers.

    Priority:
    1. X-FAF-Agent header (explicit)
    2. User-Agent pattern matching
    3. Default to 'unknown'
    """
    # Check explicit header first
    explicit_agent = request.headers.get('X-FAF-Agent', '').lower()
    if explicit_agent:
        return explicit_agent

    # Pattern match User-Agent
    user_agent = request.headers.get('User-Agent', '').lower()

    agent_patterns = {
        'claude': r'claude|anthropic',
        'gemini': r'gemini|google-ai|vertex',
        'grok': r'grok|xai',
        'jules': r'jules|google-labs',
        'codex': r'codex|openai',
        'cursor': r'cursor',
        'copilot': r'copilot|github',
    }

    for agent, pattern in agent_patterns.items():
        if re.search(pattern, user_agent):
            return agent

    return 'unknown'


def translate_for_agent(faf_data, agent):
    """
    Reshape FAF DNA based on calling agent's needs.

    Philosophy:
    - Small models (Jules): Minimal, focused payload
    - Large models (Claude): Full technical depth
    - Balanced models (Gemini): Structured, prioritized
    - Action models (Grok): Direct, concise
    """

    if agent == 'jules':
        # MINIMAL: Just the essentials for small context windows
        return {
            '_agent': 'jules',
            '_format': 'minimal',
            'project': faf_data.get('project', {}).get('name', 'Unknown'),
            'goal': faf_data.get('project', {}).get('goal', ''),
            'language': faf_data.get('project', {}).get('main_language', ''),
            'constraints': faf_data.get('ai_instructions', {}).get('constraints', []),
            'score': calculate_score(faf_data)
        }

    elif agent == 'claude':
        # FULL: Claude craves technical depth
        return {
            '_agent': 'claude',
            '_format': 'full',
            '_meta': {
                'faf_version': faf_data.get('faf_version', '2.5.0'),
                'score': calculate_score(faf_data),
                'distinction': 'Big Orange' if check_orange(faf_data) else None
            },
            **faf_data  # Everything
        }

    elif agent == 'gemini':
        # STRUCTURED: Prioritized sections for Gemini's reasoning
        return {
            '_agent': 'gemini',
            '_format': 'structured',
            'priority_1_identity': {
                'name': faf_data.get('project', {}).get('name'),
                'goal': faf_data.get('project', {}).get('goal'),
                'type': faf_data.get('project', {}).get('type')
            },
            'priority_2_technical': faf_data.get('stack', {}),
            'priority_3_behavioral': faf_data.get('ai_instructions', {}),
            'priority_4_context': faf_data.get('human_context', {}),
            'score': calculate_score(faf_data)
        }

    elif agent == 'grok':
        # DIRECT: Action-oriented for Grok's style
        return {
            '_agent': 'grok',
            '_format': 'direct',
            'what': faf_data.get('project', {}).get('name'),
            'why': faf_data.get('project', {}).get('goal'),
            'how': faf_data.get('stack', {}),
            'rules': faf_data.get('ai_instructions', {}).get('constraints', []),
            'status': f"{calculate_score(faf_data)}%"
        }

    elif agent in ('codex', 'copilot', 'cursor'):
        # CODE-FOCUSED: Emphasize stack and patterns
        return {
            '_agent': agent,
            '_format': 'code_focused',
            'project': faf_data.get('project', {}),
            'stack': faf_data.get('stack', {}),
            'patterns': faf_data.get('ai_instructions', {}).get('patterns', []),
            'avoid': faf_data.get('ai_instructions', {}).get('avoid', []),
            'score': calculate_score(faf_data)
        }

    else:
        # DEFAULT: Full payload for unknown agents
        return {
            '_agent': agent or 'unknown',
            '_format': 'full',
            **faf_data
        }


def transform_to_xml(data, root='dna'):
    """
    Transform dict to XML for Claude.
    Claude's performance spikes with XML-style "Thinking Blocks".
    """
    def dict_to_xml(d, parent_tag='item'):
        xml_parts = []
        for key, value in d.items():
            if isinstance(value, dict):
                xml_parts.append(f'<{key}>{dict_to_xml(value)}</{key}>')
            elif isinstance(value, list):
                items = ''.join(f'<item>{v}</item>' for v in value)
                xml_parts.append(f'<{key}>{items}</{key}>')
            elif value is not None:
                xml_parts.append(f'<{key}>{value}</{key}>')
        return ''.join(xml_parts)

    return f'<?xml version="1.0"?><{root}>{dict_to_xml(data)}</{root}>'


def generate_badge(score, has_orange):
    """Generate SVG badge showing FAF score and distinction."""
    if score == 100:
        status = "🏆"
        color = "#4c1"  # Green
    elif score >= 85:
        status = "🥉"
        color = "#cd7f32"  # Bronze
    elif score >= 70:
        status = "🟢"
        color = "#2ecc71"
    elif score >= 55:
        status = "🟡"
        color = "#f1c40f"
    else:
        status = "🔴"
        color = "#e74c3c"

    orange = "🍊" if has_orange else ""
    display = f"{score}% {status}{orange}"

    # Calculate width based on content
    width = 140 if has_orange else 120
    text_x = 75

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a">
    <rect width="{width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#a)">
    <rect width="60" height="20" fill="#555"/>
    <rect x="60" width="{width - 60}" height="20" fill="{color}"/>
    <rect width="{width}" height="20" fill="url(#b)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="30" y="15" fill="#010101" fill-opacity=".3">FAF</text>
    <text x="30" y="14" fill="#fff">FAF</text>
    <text x="{60 + (width - 60) // 2}" y="15" fill="#010101" fill-opacity=".3">{display}</text>
    <text x="{60 + (width - 60) // 2}" y="14" fill="#fff">{display}</text>
  </g>
</svg>'''
    return svg


def calculate_score(data):
    """Calculate FAF score from data."""
    # Check if scores section exists
    if 'scores' in data and 'faf_score' in data['scores']:
        return data['scores']['faf_score']

    # Fallback: count filled fields
    total_slots = 21
    filled = sum(1 for k, v in data.items() if v and v != "TBD")
    return min(int((filled / total_slots) * 100), 100)


def check_orange(data):
    """Check if project has Big Orange distinction."""
    # Check explicit flag
    if data.get('faf_distinction') == 'Big Orange':
        return True
    if data.get('x_faf_orange'):
        return True
    # Check metadata
    meta = data.get('meta', {})
    if meta.get('distinction') == 'orange':
        return True
    return False


@functions_framework.http
def parse_faf(request):
    """
    FAF Source of Truth - Multi-Agent Context Broker.

    GET:  Returns live SVG badge showing FAF score and distinction
    POST: Parse .faf file and return payload optimized for calling agent
    PUT:  Voice-to-FAF - update DNA and commit to GitHub

    Multi-Agent Handshake:
    - Detects caller via User-Agent or X-FAF-Agent header
    - Claude: XML with thinking blocks (full depth)
    - Gemini: Structured JSON (prioritized sections)
    - Grok: Direct JSON (action-oriented)
    - Jules: Minimal JSON (token-efficient)
    - Codex/Copilot/Cursor: Code-focused JSON
    - Unknown: Full JSON payload

    Voice-to-FAF (PUT):
    - Accepts JSON with updates: {"project.goal": "new goal", "state.phase": "beta"}
    - Merges into existing DNA
    - Commits to GitHub
    - Triggers Cloud Build redeploy

    Headers returned:
    - X-FAF-Agent-Detected: Which agent was identified
    """

    # Handle PUT request - Voice-to-FAF DNA updates (v2.5.1 Security Hardened)
    if request.method == 'PUT':
        try:
            request_json = request.get_json(silent=True)
            if not request_json:
                log_mutation_telemetry(False, {}, error="No request body")
                return json.dumps({"error": "Request body required"}), 400, {'Content-Type': 'application/json'}

            updates = request_json.get('updates', {})
            commit_msg = request_json.get('message')

            if not updates:
                log_mutation_telemetry(False, {}, error="No updates provided")
                return json.dumps({"error": "No updates provided"}), 400, {'Content-Type': 'application/json'}

            # Load current DNA
            with open('project.faf', 'r') as f:
                current_dna = yaml.safe_load(f)

            # Merge updates
            updated_dna = merge_dna_updates(current_dna.copy(), updates)

            # =========================================================
            # SECURITY CHECKS (v2.5.1)
            # =========================================================

            # Detect agent for telemetry
            agent = detect_agent(request)

            # SW-01: Temporal Integrity
            new_timestamp = datetime.utcnow().isoformat() + "Z"
            valid, error = validate_sw01_temporal_integrity(current_dna, new_timestamp)
            if not valid:
                log_mutation_telemetry(False, updates, agent=agent, score=calculate_score(current_dna), error=error, blocked_by="SW-01")
                return json.dumps({"error": error, "blocked_by": "SW-01"}), 403, {'Content-Type': 'application/json'}

            # SW-02: Scoring Guard
            valid, error = validate_sw02_scoring_guard(updated_dna, updates, calculate_score)
            if not valid:
                log_mutation_telemetry(False, updates, agent=agent, score=calculate_score(updated_dna), error=error, blocked_by="SW-02")
                return json.dumps({"error": error, "blocked_by": "SW-02"}), 403, {'Content-Type': 'application/json'}

            # =========================================================
            # COMMIT TO GITHUB
            # =========================================================

            result = commit_to_github(updated_dna, commit_msg)

            if result.get('success'):
                final_score = calculate_score(updated_dna)
                final_orange = check_orange(updated_dna)
                log_mutation_telemetry(True, updates, agent=agent, score=final_score, has_orange=final_orange)
                return json.dumps({
                    "success": True,
                    "message": result['message'],
                    "sha": result['sha'],
                    "url": result['url'],
                    "updates_applied": list(updates.keys()),
                    "security": {"sw01": "passed", "sw02": "passed"}
                }), 200, {'Content-Type': 'application/json'}
            else:
                log_mutation_telemetry(False, updates, error=result.get('error'))
                return json.dumps(result), result.get('code', 500), {'Content-Type': 'application/json'}

        except Exception as e:
            log_mutation_telemetry(False, {}, error=str(e))
            return json.dumps({"error": f"Voice-to-FAF error: {str(e)}"}), 500, {'Content-Type': 'application/json'}

    # Handle GET request - return badge
    if request.method == 'GET':
        try:
            with open('project.faf', 'r') as f:
                faf_data = yaml.safe_load(f)

            score = calculate_score(faf_data)
            has_orange = check_orange(faf_data)

            svg = generate_badge(score, has_orange)
            return svg, 200, {'Content-Type': 'image/svg+xml', 'Cache-Control': 'no-cache'}
        except Exception as e:
            # Return error badge
            svg = generate_badge(0, False)
            return svg, 200, {'Content-Type': 'image/svg+xml'}

    # Handle POST request - Multi-Agent Context Broker
    request_json = request.get_json(silent=True)
    file_path = request_json.get('path', 'project.faf') if request_json else 'project.faf'

    try:
        with open(file_path, 'r') as f:
            faf_data = yaml.safe_load(f)

        # Detect calling agent
        agent = detect_agent(request)

        # Translate payload for agent's dialect
        translated = translate_for_agent(faf_data, agent)

        # Claude gets XML (performance boost with thinking blocks)
        if agent == 'claude':
            xml_response = transform_to_xml(translated)
            return xml_response, 200, {
                'Content-Type': 'application/xml',
                'X-FAF-Agent-Detected': agent
            }

        # All others get JSON (optimized per agent)
        return json.dumps(translated, indent=2), 200, {
            'Content-Type': 'application/json',
            'X-FAF-Agent-Detected': agent
        }

    except FileNotFoundError:
        return json.dumps({"error": f"File {file_path} not found."}), 404
    except yaml.YAMLError as e:
        return json.dumps({"error": f"YAML parse error: {str(e)}"}), 400
    except Exception as e:
        return json.dumps({"error": str(e)}), 500
