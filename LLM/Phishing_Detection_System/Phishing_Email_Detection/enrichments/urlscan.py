import requests
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
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
        result_id = response.json().get("result")
        logger.info(f"-- urlscan_submit : request_id - {result_id} --")
        logger.info(f"-- urlscan_submit : waiting 15 seconds for the result  --")
        response = get_result(result_id, max_retries=5, wait_seconds=15)
        logger.info(f"-- urlscan_submit : result - {response} --")

    return response


def get_result(result_id, max_retries=5, wait_seconds=15):
    logger.info(f"-- get_result --")
    url = f"https://urlscan.io/api/v1/result/{result_id}/"

    for attempt in range(1, max_retries + 1):
        response = requests.get(url)

        if response.status_code == 200:
            logger.info(f"-- get_result: result ready on attempt {attempt} --")
            return response.json()

        logger.info(f"-- get_result: attempt {attempt} failed (status {response.status_code}). Retrying in {wait_seconds}s --")
        time.sleep(wait_seconds)

    logger.error(f"-- get_result: failed after {max_retries} attempts --")
    raise TimeoutError(f"Result not ready after {max_retries} attempts for ID {result_id}")


if __name__ == '__main__':
    url = "https://www.netflix.com/ph-en/"
    response = urlscan_submit(url)
    print("\n\n")
    print(response)