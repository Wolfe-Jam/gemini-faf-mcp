"""
gemini-faf-mcp: Google Cloud Function for FAF Context Bridge

Media Type: application/vnd.faf+yaml
Endpoint: https://faf-source-of-truth-*.run.app

Minimal tool for Gemini to read and parse .faf files.
Returns structured JSON for AI grounding.
"""

import functions_framework
import yaml
import json


@functions_framework.http
def parse_faf(request):
    """
    Parse a .faf file and return structured JSON for Gemini.

    Gemini will pass the 'path' as an argument based on your Tool definition.
    Returns the parsed YAML as JSON for AI context grounding.
    """
    request_json = request.get_json(silent=True)

    # Get file path from request, default to project.faf
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
