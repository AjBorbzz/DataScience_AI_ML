import sys
import os
# # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path

from utils import logging_config
logging_config.setup_logging()
import logging
logger = logging.getLogger(__name__)

from services.anthropic_client import process_phishing_detection
from utils.parser import get_data_from_csv, extract_message_output, append_data_to_json
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = Path().resolve() / "data"
SAMPLE_DATA_FILE = "sample_data.csv"

def main():
        # Get data from CSV
        #     data = parser.get_data_from_csv(DATA_PATH / "test.csv")
        #     print(data)
        #     data = parser.list_of_dicts_to_csv(data, "sample_data.csv")

    logger.info("-- Starting the phishing detection process. --")
    try:
        csv_data = get_data_from_csv(DATA_PATH / SAMPLE_DATA_FILE)
        # print(csv_data)
        if not csv_data:
            logger.warning(f"No Data Found in {DATA_PATH / SAMPLE_DATA_FILE}. Exiting...")
            return
        
        response = process_phishing_detection(csv_data[3])
        extracted_data = extract_message_output(response)
        append_data_to_json(extracted_data)
    except FileNotFoundError:
        logger.error(f"Error: CSV file not found at {DATA_PATH / SAMPLE_DATA_FILE}")

    except Exception as e:
        logger.error(f"An unexpected error has occured : {e}", exc_info=True)

    logger.info("---===*** Phishing Detection Process Completed. ***===---")


if __name__ == '__main__':
    main()
