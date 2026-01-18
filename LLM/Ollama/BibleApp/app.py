import json, uuid
from pathlib import Path

INPUT_JSON = Path("data/bible_asv.json")
OUTPUT_JSONL = Path("data/bible_asv_chunked.json")

CHUNK_VERSES = 5

def main():
    bible = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    output = OUTPUT_JSONL.open("w", encoding="utf-8")
    
    for book, chapters in bible.items():
        for ch_str, verses in chapters.items():
            ch = int(ch_str)
            verse_nums = sorted(int(v) for v in verses.keys())
            i = 0
            while i < len(verse_nums):
                chunk = verse_nums[i:i+CHUNK_VERSES]
                vs, ve = chunk[0], chunk[-1]
                text = " ".join(verses[str(v)] for v in chunk)

                rec = {
                    "id": str(uuid.uuid4()),
                    "book": book,
                    "chapter": ch,
                    "verse_start": vs,
                    "verse_end": ve,
                    "translation": "KJV",
                    "text": text,
                }
                output.write(json.dumps(rec, ensure_ascii=False) + "\n")
                i += CHUNK_VERSES

    output.close()
    print(f"Wrote {OUTPUT_JSONL}")

if __name__ == "__main__":
    main()