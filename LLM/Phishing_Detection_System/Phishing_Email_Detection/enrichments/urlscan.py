import requests
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.ioc_utils import get_api_key
from utils.logging_config import log_duration
import logging
logger = logging.getLogger(__name__)

URLSCAN_URL = "https://urlscan.io/api/v1/scan/"

@log_duration
def urlscan_submit(url):
    logger.info("-- urlscan_submit started --")
    headers = {
        'API-Key': get_api_key("URLSCAN_API_KEY"),
        'Content-Type':'application/json'
    }

    data = {
        "url": url,
        "visibility": "public"
    }

    response = requests.post(URLSCAN_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200 and response.json().get("result"):
        result_id = response.json().get("result").json().get("result")
        logger.info(f"-- urlscan_submit : request_id - {result_id} --")
        
        
        

