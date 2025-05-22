import requests
import os

def check_virustotal(url):
    headers = {"x-apikey": os.getenv("VT_API_KEY")}
    response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url}", headers=headers)
    data = response.json()
    positives = data['data']['attributes']['last_analysis_stats']['malicious']
    return {"source": "VirusTotal", "positives": positives, "score": min(positives * 20, 100)}