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


text="""
I'll analyze this email for potential phishing indicators:

## Analysis

First, let me evaluate the key components:

1. **Email Headers**:
   - SPF, DKIM, and DMARC all pass, which is a strong indicator of legitimacy
   - Sender domain (github.com) matches the expected sender for GitHub notifications

2. **Subject and Content**:
   - Subject relates to account security (sign-in notification)
   - Body is concise and typical of legitimate login notifications
   - No urgency or fear tactics employed

3. **URLs and Domains**:
   - URL is to github.com's legitimate settings page
   - No shortened links or redirects

4. **Attachments/QR Codes**:
   - None present

5. **Language Analysis**:
   - Professional, non-urgent tone
   - No personal information requested
   - Specifically notes "no action is needed" rather than prompting action

6. **IOC Enrichment**:
   - Domain: github.com is a legitimate software development platform
   - URL: https://github.com/settings/sessions is the legitimate path for viewing session information

## Evaluation

### Output
- **Verdict**: Benign
- **Confidence**: 95%
- **Reasoning**:
  - Email passes all authentication checks (SPF, DKIM, DMARC)
  - Sender domain matches expected source for GitHub notifications
  - Content matches legitimate GitHub login notification patterns
  - No suspicious URLs, attachments, or social engineering tactics
- **IOC Enrichment**:
  - github.com: Legitimate software development platform with proper security implementation
  - https://github.com/settings/sessions: Valid GitHub URL for account session management
"""


def smart_regex_extract(pattern, text, group=1, default=None, data_type=str):
    """
    Smart regex extraction that handles groups safely and applies type conversion.
    
    Args:
        pattern (str): Regex pattern to search for
        text (str): Text to search in
        group (int): Group number to extract (0 for full match, 1+ for capture groups)
        default: Default value if no match is found
        data_type: Type to convert the result to (str, int, float, etc.)
    
    Returns:
        Extracted and converted value or default
    """
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            value = match.group(group).strip()
            return data_type(value) if value else default
        except (IndexError, ValueError, AttributeError):
            return default
    return default

# def extract_message_output():
#     logger.info(f"--== Running {extract_message_output.__name__} from parser ==--")
    
#     search_verdict = re.search(r"- \*\*Verdict\*\*:\s*(.+)", text)
#     verdict = regex_parse(search_verdict)

#     search_confidence = re.search(r"### Confidence:\s*(\d+)%", text)
#     confidence = regex_parse(search_confidence)
#     # reasoning = re.findall(r"- (.*?)\n", re.search(r"### Reasoning:(.*?)(###|$)", text, re.DOTALL).group(1))
#     reasoning = re.findall(r"- (.*?)\n", re.search(r"### Reasoning:(.*?)(###|$)", text, re.DOTALL))
#     domain = re.search(r"- Domain:\s*(.*?)\s*-", text)
#     auth = re.search(r"- Email authentication:\s*(.*?)\s*-", text)
#     attachment = re.search(r"- Attachment:\s*(.*?)\s*-", text)
#     sha256 = re.search(r"- SHA256 hash:\s*(.*?)\s*-", text)
#     # domain = re.search(r"- Domain:\s*(.*?)\s*-", text).group(1).strip()
#     # auth = re.search(r"- Email authentication:\s*(.*?)\s*-", text).group(1).strip()
#     # attachment = re.search(r"- Attachment:\s*(.*?)\s*-", text).group(1).strip()
#     # sha256 = re.search(r"- SHA256 hash:\s*(.*?)\s*-", text).group(1).strip()

#     data = {
#         "Verdict": verdict,
#         "Confidence": int(confidence),
#         "Reasoning": reasoning,
#         "IOC Enrichment": {
#             "Domain": domain,
#             "Email Authentication": auth,
#             "Attachment": attachment,
#             "SHA256 Hash": sha256
#         }
#     }

#     print(data)

def extract_reasoning(text):
    """Extract reasoning list from text."""
    reasoning_match = re.search(r"### Reasoning:(.*?)(###|$)", text, re.DOTALL)
    if reasoning_match:
        reasoning_text = reasoning_match.group(1)
        return [item.strip() for item in re.findall(r"- (.*?)(?=\n|$)", reasoning_text) if item.strip()]
    return []

def extract_message_output(text):
    """Extract structured data from message output text."""
    logger.info(f"--== Running {extract_message_output.__name__} from parser ==--")
    
    # Define extraction patterns with their configurations
    extractions = {
        "verdict": {
            "patterns": [
                r"- \*\*Verdict\*\*:\s*(.+)",
                r"\*\*Verdict\*\*:\s*(.+)",
                r"Verdict:\s*(.+)"
            ]
        },
        "confidence": {
            "patterns": [
                r"### Confidence:\s*(\d+)%",
                r"\*\*Confidence\*\*:\s*(\d+)%",
                r"Confidence:\s*(\d+)%"
            ],
            "data_type": int
        },
        "domain": {
            "patterns": [
                r"- Domain:\s*(.*?)\s*-",
                r"Domain:\s*(.*?)(?:\n|$)"
            ]
        },
        "auth": {
            "patterns": [
                r"- Email authentication:\s*(.*?)\s*-",
                r"Email authentication:\s*(.*?)(?:\n|$)"
            ]
        },
        "attachment": {
            "patterns": [
                r"- Attachment:\s*(.*?)\s*-",
                r"Attachment:\s*(.*?)(?:\n|$)"
            ]
        },
        "sha256": {
            "patterns": [
                r"- SHA256 hash:\s*(.*?)\s*-",
                r"SHA256 hash:\s*(.*?)(?:\n|$)"
            ]
        }
    }
    
    # Extract values using multiple pattern attempts
    results = {}
    for key, config in extractions.items():
        patterns = config["patterns"]
        data_type = config.get("data_type", str)
        default = config.get("default", None)
        
        value = None
        for pattern in patterns:
            value = smart_regex_extract(pattern, text, group=1, default=None, data_type=data_type)
            if value is not None:
                break
        
        results[key] = value if value is not None else default
    
    # Extract reasoning separately due to its complex structure
    reasoning = extract_reasoning(text)
    
    # Build final data structure
    data = {
        "Verdict": results["verdict"],
        "Confidence": results["confidence"],
        "Reasoning": reasoning,
        "IOC Enrichment": {
            "Domain": results["domain"],
            "Email Authentication": results["auth"],
            "Attachment": results["attachment"],
            "SHA256 Hash": results["sha256"]
        }
    }
    
    logger.info("Successfully extracted message output data")
    return data

# Alternative: Even more concise version using a single function
def extract_message_output_compact(text):
    """Compact version with inline pattern matching."""
    logger.info(f"--== Running {extract_message_output_compact.__name__} from parser ==--")
    
    # Helper function for multiple pattern attempts
    def multi_extract(patterns, data_type=str, default=None):
        for pattern in patterns:
            result = smart_regex_extract(pattern, text, group=1, default=None, data_type=data_type)
            if result is not None:
                return result
        return default
    
    data = {
        "Verdict": multi_extract([
            r"- \*\*Verdict\*\*:\s*(.+)",
            r"\*\*Verdict\*\*:\s*(.+)",
            r"Verdict:\s*(.+)"
        ]),
        "Confidence": multi_extract([
            r"### Confidence:\s*(\d+)%",
            r"\*\*Confidence\*\*:\s*(\d+)%",
            r"Confidence:\s*(\d+)%"
        ], data_type=int),
        "Reasoning": extract_reasoning(text),
        "IOC Enrichment": {
            "Domain": multi_extract([
                r"- Domain:\s*(.*?)\s*-",
                r"Domain:\s*(.*?)(?:\n|$)"
            ]),
            "Email Authentication": multi_extract([
                r"- Email authentication:\s*(.*?)\s*-",
                r"Email authentication:\s*(.*?)(?:\n|$)"
            ]),
            "Attachment": multi_extract([
                r"- Attachment:\s*(.*?)\s*-",
                r"Attachment:\s*(.*?)(?:\n|$)"
            ]),
            "SHA256 Hash": multi_extract([
                r"- SHA256 hash:\s*(.*?)\s*-",
                r"SHA256 hash:\s*(.*?)(?:\n|$)"
            ])
        }
    }
    
    return data

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
