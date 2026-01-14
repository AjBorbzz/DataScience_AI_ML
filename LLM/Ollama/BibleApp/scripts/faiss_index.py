import json
import pickle
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


JSONL = Path("data/bible_asv_chunked.json")
INDEX_DIR = Path("index")
INDEX_DIR.mkdir(exist_ok=True)


FAISS_PATH = INDEX_DIR / "bible_asv.faiss"
META_PATH = INDEX_DIR / "bible_asv_meta.pkl"


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_records():
    recs = []
    with JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            recs.append(json.loads(line))
    return recs


def main():
    recs = load_records()
    texts = [r["text"] for r in recs]

    model = SentenceTransformer(MODEL_NAME)
    emb = model.encode(texts, normalize_embeddings=True, batch_size=64, show_progress_bar=True)
    emb = np.array(emb, dtype="float32")

    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)

    faiss.write_index(index, str(FAISS_PATH))
    with META_PATH.open("wb") as f:
        pickle.dump(recs, f)


    # print(f"Index saved: {FAISS_PATH}")
    # print(f"Meta saved: {META_PATH}")
    # print(f"Records: {len(recs)}  Dim: {dim}")

if __name__ == "__main__":
    main()