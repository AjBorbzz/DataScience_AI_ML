import sys
import os
import re
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.anthropic_client import process_phishing_detection
from utils.parser import get_data_from_csv, extract_message_output

DATA_PATH = Path().resolve().parents[0] / "data"


def main():
        # Get data from CSV
        #     data = parser.get_data_from_csv(DATA_PATH / "test.csv")
        #     print(data)
        #     data = parser.list_of_dicts_to_csv(data, "sample_data.csv")

    data = get_data_from_csv(DATA_PATH / "sample_data.csv")
    response = process_phishing_detection(data[3])
    extracted_data = extract_message_output(response)



if __name__ == '__main__':
    main()
