import urllib.request
import json
from urllib.error import URLError

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

class AIAuditor:
    """
    Zero-bloat AI Threat Intelligence auditor using raw REST APIs.
    Sends a system snapshot JSON to an LLM for advanced heuristic parsing.
    """
    @staticmethod
    def audit_snapshot(api_key, snapshot_data):
        """
        Sends the diagnostic payload securely over HTTPS to the OpenAI API.
        Requires a valid 'api_key'. Returns (success: bool, response: str).
        """
        if not api_key:
            return False, "Error: AI API Key is missing. Please configure it in Settings."

        system_prompt = (
            "You are a Senior Cybersecurity and IT Diagnostic AI. "
            "Analyze this system report JSON. Identify any suspicious processes, "
            "hardware wear-level warnings, or network anomalies. Keep your response "
            "under 3 sentences. Be highly technical."
        )

        # Clean up the payload slightly to save tokens (remove massive history arrays)
        clean_snapshot = snapshot_data.copy()
        if "fleet_data" in clean_snapshot:
            del clean_snapshot["fleet_data"] # Only audit local node

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(clean_snapshot)}
            ],
            "temperature": 0.2,
            "max_tokens": 150
        }

        data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(
            OPENAI_API_URL,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )

        try:
            # 10-second timeout for the LLM response
            with urllib.request.urlopen(req, timeout=10.0) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    ai_message = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    return True, ai_message.strip()
                else:
                    return False, f"API Error: HTTP {response.status}"

        except URLError as e:
            if hasattr(e, 'code') and e.code == 401:
                return False, "Error: Invalid AI API Key (401 Unauthorized)."
            return False, f"Connection Failed: {str(e)}"
        except Exception as e:
            return False, f"AI Audit Failed: {str(e)}"
