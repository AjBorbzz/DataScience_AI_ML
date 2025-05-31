import requests
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.ioc_utils import get_api_key

def check_urlscan(url):
    response = requests.get(f"https://urlscan.io/api/v1/search/?q=domain:{url}")
    if response.status_code == 200 and response.json().get("results"):
        verdict = response.json()["results"][0].get("verdicts", {})
        malicious = verdict.get("overall", {}).get("malicious", False)
        return {"source": "URLScan", "malicious": malicious, "score": 100 if malicious else 0}
    return {"source": "URLScan", "malicious": False, "score": 0}


print(get_api_key("VIRUSTOTAL_API_KEY"))