import re
import pandas as pd
import json
from pathlib import Path
import os
import inspect
import logging
logger = logging.getLogger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / 'data'
data_path = Path(DATA_DIR / 'data.json')


def extract_message_output(text):
    logger.info(f"--== Running {extract_message_output.__name__} from parser ==--")
    verdict = re.search(r"### Verdict:\s*(.+)", text).group(1)
    confidence = re.search(r"### Confidence:\s*(\d+)%", text).group(1)
    reasoning = re.findall(r"- (.*?)\n", re.search(r"### Reasoning:(.*?)(###|$)", text, re.DOTALL).group(1))

    domain = re.search(r"- Domain:\s*(.*?)\s*-", text).group(1).strip()
    auth = re.search(r"- Email authentication:\s*(.*?)\s*-", text).group(1).strip()
    attachment = re.search(r"- Attachment:\s*(.*?)\s*-", text).group(1).strip()
    sha256 = re.search(r"- SHA256 hash:\s*(.*?)\s*-", text).group(1).strip()

    return {
        "Verdict": verdict,
        "Confidence": int(confidence),
        "Reasoning": reasoning,
        "IOC Enrichment": {
            "Domain": domain,
            "Email Authentication": auth,
            "Attachment": attachment,
            "SHA256 Hash": sha256
        }
    }

def get_data_from_csv(filepath):
    """
    Reads data from a CSV file and returns it as a list of dictionaries.

    Each dictionary in the list represents a row, with column headers as keys.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a row of data.
                    Returns an empty list if the CSV file is empty or not found.

    """
    df = pd.read_csv(filepath)
    data = df.to_dict(orient='records')
    return data

def list_of_dicts_to_csv(list_of_dicts, filename):
    """
    Converts a list of dictionaries to a CSV file.

    Args:
        list_of_dicts: A list of dictionaries.
        filename: The name of the CSV file to create.
    """
    df = pd.DataFrame(list_of_dicts)
    df.to_csv(filename, index=False)


def append_data_to_json(data_object):
    # get file path
    # check if file exists if not create one, if it exists append the data 
    """
    Checks if a JSON file exists and contains data. If it exists and
    contains an array, the function appends the provided data object to the array.

    Args:
        data_object (dict): The data object to append.
    """
    logger.info(f"--== Running {append_data_to_json.__name__} from parser ==--")
    if data_path.exists():
        try:
            with open(data_path, 'r+') as f:
                f_content = f.read()
                if f_content:
                    data = json.loads(f_content)
                    if isinstance(data, list):
                        data.append(data_object)
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                    else:
                        logger.info("---Data added to json---")
                else:
                    json.dump([data_object], open(data_path, 'w'), indent=4)
        except json.JSONDecodeError:
            logger.error("The JSON file is corrupted or does not contain valid JSON.")

    else:
        json.dump([data_object], open(data_path, 'w'), indent=4)
    logger.info(f"--== {append_data_to_json.__name__}: Successfully added data ==--")
