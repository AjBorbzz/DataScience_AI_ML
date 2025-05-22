import re
import pandas as pd

def extract_message_output(text):
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