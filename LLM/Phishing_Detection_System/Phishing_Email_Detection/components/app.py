import sys
import os
import re
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services import anthropic_client
from utils import ioc_utils, parser

DATA_PATH = Path().resolve().parents[0] / "data"




def main():
    # Get data from CSV
    data = parser.get_data_from_csv(DATA_PATH / "test.csv")
    print(data)
#     anthropic_client.process_phishing_detection(data)
    


if __name__ == '__main__':
    main()
