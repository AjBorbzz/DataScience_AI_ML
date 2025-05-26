import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
VT_URL = "https://www.virustotal.com/api/v3/urls"

HEADERS = {
    "accept": "application/json",
    "x-apikey": VT_API_KEY,
    "content-type": "application/x-www-form-urlencoded"
}

def vt_scan_url(url):
    payload = {"url": url}
    response = requests.post(VT_URL, data=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["data"]["id"]

def vt_get_url_report(analysis_id):
    # Extract the actual ID from full `id` if needed
    analysis_id = analysis_id.split("-")[-1]
    url = f"{VT_URL}/{analysis_id}"
    while True:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        json_data = response.json()
        
        status = json_data.get("data", {}).get("attributes", {}).get("status", "")
        print(f"Scan status: {status}")
        
        if status == "completed":
            return json_data
        time.sleep(5)  # Wait before retrying

def main():
    try:
        url = "https://www.netflix.com"
        print(f"Scanning URL: {url}")
        analysis_id = vt_scan_url(url)
        print(f"Analysis ID: {analysis_id}")

        report = vt_get_url_report(analysis_id)
        print("Scan completed. Report summary:")
        print(report)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
