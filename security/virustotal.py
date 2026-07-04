"""
Optional VirusTotal reputation check for a URL.

Requires a free API key from https://www.virustotal.com/gui/join-us
set as the VIRUSTOTAL_API_KEY environment variable (e.g. via a .env file).
If no key is configured, check_virustotal() returns a dict indicating the
check was skipped, so the rest of the app keeps working without it.
"""
import os
import base64
import time

import requests
from dotenv import load_dotenv

from utils.helper import get_logger

load_dotenv()
logger = get_logger(__name__)

API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
BASE_URL = "https://www.virustotal.com/api/v3"


def _url_id(url: str) -> str:
    """VirusTotal identifies URLs by the base64 (no padding) of the URL string."""
    return base64.urlsafe_b64encode(url.encode()).decode().strip("=")


def check_virustotal(url: str, timeout: float = 10.0) -> dict:
    result = {
        "checked": False,
        "malicious": 0,
        "suspicious": 0,
        "harmless": 0,
        "undetected": 0,
        "verdict": None,
        "error": None,
    }

    if not API_KEY:
        result["error"] = "VirusTotal API key not configured (set VIRUSTOTAL_API_KEY in .env)."
        return result

    headers = {"x-apikey": API_KEY}

    try:
        # Submit the URL for analysis (VT dedupes if already scanned recently)
        submit_resp = requests.post(
            f"{BASE_URL}/urls", headers=headers, data={"url": url}, timeout=timeout
        )
        submit_resp.raise_for_status()

        url_id = _url_id(url)
        # Give the analysis a brief moment, then fetch the report
        time.sleep(1.5)
        report_resp = requests.get(f"{BASE_URL}/urls/{url_id}", headers=headers, timeout=timeout)
        report_resp.raise_for_status()

        stats = report_resp.json()["data"]["attributes"]["last_analysis_stats"]
        result.update({
            "checked": True,
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
        })
        result["verdict"] = "Malicious" if (result["malicious"] + result["suspicious"]) > 0 else "Clean"

    except requests.exceptions.RequestException as e:
        logger.warning("VirusTotal check failed for %s: %s", url, e)
        result["error"] = f"VirusTotal request failed: {e}"

    return result
