import requests
import os

def check_virustotal(url):
    headers = {"x-apikey": os.getenv("VT_API_KEY")}
    response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url}", headers=headers)
    data = response.json()
    positives = data['data']['attributes']['last_analysis_stats']['malicious']
    return {"source": "VirusTotal", "positives": positives, "score": min(positives * 20, 100)}

def check_urlscan(url):
    response = requests.get(f"https://urlscan.io/api/v1/search/?q=domain:{url}")
    if response.status_code == 200 and response.json().get("results"):
        verdict = response.json()["results"][0].get("verdicts", {})
        malicious = verdict.get("overall", {}).get("malicious", False)
        return {"source": "URLScan", "malicious": malicious, "score": 100 if malicious else 0}
    return {"source": "URLScan", "malicious": False, "score": 0}

def check_phishtank(url):
    # This requires you to register and use their API
    # Mock response
    is_phishing = False  # Replace with actual call
    return {"source": "PhishTank", "match": is_phishing, "score": 100 if is_phishing else 0}

def enrich_url(url):
    results = []
    total_score = 0
    sources = [check_virustotal, check_urlscan, check_phishtank]

    for source_func in sources:
        result = source_func(url)
        total_score += result["score"]
        results.append(result)

    average_score = total_score // len(sources)
    return {
        "url": url,
        "average_score": average_score,
        "detailed_results": results
    }
