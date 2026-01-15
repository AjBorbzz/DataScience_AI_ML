import pickle
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


INDEX_DIR = Path("index")
FAISS_PATH = INDEX_DIR / "bible_kjv.faiss"
META_PATH = INDEX_DIR / "bible_kjv_meta.pkl"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2

# Need to change paths

def fmt_ref(r):
    if r["verse_start"] == r["verse_end"]:
        return f'{r["book"]} {r["chapter"]}:{r["verse_start"]}'
    return f'{r["book"]} {r["chapter"]}:{r["verse_start"]}-{r["verse_end"]}'

def main():
    q = input("Query: ").strip()

    index = faiss.read_index(str(FAISS_PATH))
    recs = pickle.loads(META_PATH.read_bytes())
    model = SentenceTransformer(MODEL_NAME)

    qv = model.encode([q], normalize_embeddings=True).astype("float32")
    D, I = index.search(np.array(qv), k=5)