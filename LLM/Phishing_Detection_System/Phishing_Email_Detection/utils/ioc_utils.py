from dotenv import load_dotenv
import os
load_dotenv()
import asyncio
import aiohttp
from typing import Callable
import logging
from utils.logging_config import log_duration

def get_api_key(env_name):
    API_KEY = os.getenv(env_name)
    return API_KEY

@log_duration
async def async_poll_for_result(
        url_generator: Callable[[str], str],
        extract_result: Callable[[dict], dict],
        is_result_ready: Callable[[dict], bool],
        task_id: str,
        headers: dict = None,
        retry_intervals = [30, 20, 10]
):
    """
    Asynchronously poll for a result using a custom retry strategy.

    Parameters:
        url_generator: function to create the status URL from task_id.
        extract_result: function to extract final result from the response JSON.
        is_result_ready: function to check if result is ready.
        task_id: scan ID or job ID.
        headers: optional HTTP headers.
        retry_intervals: list of seconds to wait between retries (e.g., [30, 20, 10]).

    Returns:
        Extracted result if ready, otherwise raises TimeoutError.
    """

    url = url_generator(task_id)

    async with aiohttp.ClientSession(headers=headers) as session:
        for attempt, delay in enumerate(retry_intervals, start=1):
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP Error: {response.status}")
                
                json_data = await response.json()

                if is_result_ready(json_data):
                    return extract_result(json_data)
                
            print(f"[{task_id}] Attempt {attempt} - result not ready. Retrying in {delay}s...")
            await asyncio.sleep(delay)
    raise TimeoutError(f"[{task_id}] Result not ready after {len(retry_intervals)} attempts.")


"""
def vt_url_generator(analysis_id):
    analysis_id = analysis_id.split("-")[1]
    return f"{VT_URL}/{analysis_id}"

def vt_is_result_ready(json_data):
    return 'attributes' in json_data.get('data', {})

def vt_extract_result(json_data):
    return json_data['data']['attributes']['total_votes']

# List of analysis IDs to process concurrently
vt_tasks = [
    "analysis-abc123",
    "analysis-def456",
    "analysis-ghi789"
]

async def main():
    tasks = [
        async_poll_for_result(
            url_generator=vt_url_generator,
            extract_result=vt_extract_result,
            is_result_ready=vt_is_result_ready,
            task_id=task_id,
            headers=HEADERS,
            retry_intervals=[30, 20, 10]
        )
        for task_id in vt_tasks
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for task_id, result in zip(vt_tasks, results):
        if isinstance(result, Exception):
            print(f"[{task_id}] Failed: {result}")
        else:
            print(f"[{task_id}] Success: {result}")

# Run the async main loop
asyncio.run(main())

"""