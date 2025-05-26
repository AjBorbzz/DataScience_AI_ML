import requests
import os
from dotenv import load_dotenv

load_dotenv()

VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
VT_URL = "https://www.virustotal.com/api/v3/urls"

def vt_scan_url(url):
    payload = {"url": url}
    headers = {
        "accept": "application/json",
        "x-apikey": VT_API_KEY,
        "content-type": "application/x-www-form-urlencoded"
    }

    response = requests.post(VT_URL, data=payload, headers=headers)
    return response.text

def vt_get_url_report(analysis_id):
    analysis_id = analysis_id.split("-")[1]
    headers = {"accept": "application/json", "x-apikey": VT_API_KEY,}
    response = requests.get(f"{VT_URL}/{analysis_id}", headers=headers)
    # print(response.text)
    return response.text



def main():
    res = vt_scan_url("www.netflix.com")
    analysis_id = res.get("data").get("id")
    url_resport = vt_get_url_report(analysis_id)
    print(url_resport)

if __name__ == "__main__":
    main()