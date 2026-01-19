import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path


INDEX_DIR = Path("index")
FAISS_PATH = INDEX_DIR / "bible_asv.faiss"
META_PATH = INDEX_DIR / "bible_asv_meta.pkl"


MODEL_NAME = "all-MiniLM-L6-v2"

class BibleRetriever:
    def __init__(self, top_k=8):
        self.top_k = top_k
        self.index = faiss.read_index(str(FAISS_PATH))
        self.recs = pickle.loads(META_PATH.read_bytes())
        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, queries):
        seen = set()
        results = []

        for q in queries:
            qv = self.model.encode([q], normalize_embeddings=True).astype("float32")
            D, I = self.index.search(np.array(qv), k=self.top_k)

            for score, idx in zip(D[0], I[0]):
                if idx < 0:
                    continue
                rec = self.recs[idx]
                key = (rec["book"], rec["chapter"], rec["verse_start"], rec["verse_end"])
                if key not in seen:
                    seen.add(key)
                    results.append({**rec, "score": float(score)})

        results.sort(key=lambda r: r["score"], reverse=True)
        return results