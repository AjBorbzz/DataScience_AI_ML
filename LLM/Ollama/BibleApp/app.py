import json 
from pathlib import Path

INPUT_JSON = Path("data/bible_asv.json")
OUTPUT_JSONL = Path("data/bible_asv_chunked.json")

CHUNK_VERSES = 5

def main():
    bible = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    output = OUTPUT_JSONL.open("w", encoding="utf-8")
    
    for bible_item in bible:
        print(bible_item['book_name'])

if __name__ == "__main__":
    main()