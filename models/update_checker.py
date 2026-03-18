import json
import urllib.request
from urllib.error import URLError

CURRENT_VERSION = "v1.0.1-stable"
REPO_API_URL = "https://api.github.com/repos/iambl0ck/4n4lyz3r/releases/latest"

class OTAUpdateChecker:
    """
    Zero-Dependency Over-The-Air Update Checker.
    Pings the GitHub Releases API securely with strict timeouts.
    """
    @staticmethod
    def check_for_updates():
        """
        Fetches the latest release tag from GitHub.
        Returns (has_update: bool, latest_version: str, url: str)
        Fails silently and returns (False, "", "") on errors or timeouts.
        """
        try:
            # Prepare a secure request with a generic user-agent to avoid API blocks
            req = urllib.request.Request(
                REPO_API_URL,
                headers={'User-Agent': f'4n4lyz3r-App/{CURRENT_VERSION}'}
            )

            # Strict 3-second timeout so we don't hang if offline
            with urllib.request.urlopen(req, timeout=3.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    latest_tag = data.get("tag_name", "")
                    html_url = data.get("html_url", "https://github.com/iambl0ck/4n4lyz3r/releases")

                    if latest_tag and latest_tag != CURRENT_VERSION:
                        # Simple string comparison is sufficient if semantic versioning is strictly followed (v1.0.1 > v1.0.0)
                        # For true semantic parsing, packaging.version or regex is better,
                        # but simple inequality works for an exact tag match check.
                        return True, latest_tag, html_url

        except (URLError, json.JSONDecodeError, Exception):
            # Fail silently on network drop, API rate limits, or parse errors
            pass

        return False, "", ""
