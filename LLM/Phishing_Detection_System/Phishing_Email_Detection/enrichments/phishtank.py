import requests
import json

PHISHTANK_API_URL = "https://checkurl.phishtank.com/checkurl/"

def check_url_with_phishtank(url: str, app_key: str = "") -> dict:
    """
    Submits a URL to PhishTank and returns the result.

    :param url: The URL to check.
    :param app_key: (Optional) Your PhishTank app key.
    :return: Dictionary with the response details.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (XSOAR/PhishingDetection)",
    }

    data = {
        'url': url,
        'format': 'json',
        'app_key': app_key # Set in ENV
    }

    try:
        response = requests.post(PHISHTANK_API_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error contacting PhishTank: {e}")
        return {"error": str(e)}
