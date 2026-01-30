"""
gemini-faf-mcp: Google Cloud Function for FAF Context Bridge

Media Type: application/vnd.faf+yaml
Endpoint: https://faf-source-of-truth-*.run.app

Features:
- POST: Parse .faf file, return JSON for AI grounding
- GET: Return live SVG badge showing FAF score
- Multi-Agent Handshake: Optimize payload per AI dialect
"""

import functions_framework
import yaml
import json
import re


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

    GET: Returns live SVG badge showing FAF score and distinction
    POST: Parse .faf file and return payload optimized for calling agent

    Multi-Agent Handshake:
    - Detects caller via User-Agent or X-FAF-Agent header
    - Claude: XML with thinking blocks (full depth)
    - Gemini: Structured JSON (prioritized sections)
    - Grok: Direct JSON (action-oriented)
    - Jules: Minimal JSON (token-efficient)
    - Codex/Copilot/Cursor: Code-focused JSON
    - Unknown: Full JSON payload

    Headers returned:
    - X-FAF-Agent-Detected: Which agent was identified
    """

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
