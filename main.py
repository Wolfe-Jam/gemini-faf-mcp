"""
gemini-faf-mcp: Google Cloud Function for FAF Context Bridge

Media Type: application/vnd.faf+yaml
Endpoint: https://faf-source-of-truth-*.run.app

Features:
- POST: Parse .faf file, return JSON for AI grounding
- GET: Return live SVG badge showing FAF score
"""

import functions_framework
import yaml
import json


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
    FAF Source of Truth endpoint.

    GET: Returns SVG badge showing current FAF score
    POST: Parse .faf file and return JSON for AI grounding
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

    # Handle POST request - return JSON
    request_json = request.get_json(silent=True)
    file_path = request_json.get('path', 'project.faf') if request_json else 'project.faf'

    try:
        with open(file_path, 'r') as f:
            faf_data = yaml.safe_load(f)
            return json.dumps(faf_data), 200, {'Content-Type': 'application/json'}
    except FileNotFoundError:
        return json.dumps({"error": f"File {file_path} not found."}), 404
    except yaml.YAMLError as e:
        return json.dumps({"error": f"YAML parse error: {str(e)}"}), 400
    except Exception as e:
        return json.dumps({"error": str(e)}), 500
