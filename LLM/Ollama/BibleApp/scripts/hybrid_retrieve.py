import json
import pickle
from pathlib import Path

import numpy as np
import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

INDEX_DIR = Path("index")
FAISS_PATH = INDEX_DIR / "bible_asv.faiss"
META_PATH = INDEX_DIR / "bible_asv_meta.pkl"

MODEL_NAME = "all-MiniLM-L6-v2"

class HybridBibleRetriever:
    def __init__(self, top_k_vec=12, top_k_bm25=12):
        self.top_k_vec = top_k_vec
        self.top_k_bm25 = top_k_bm25

        self.index = faiss.read_index(str(FAISS_PATH))
        self.recs = pickle.loads(META_PATH.read_bytes())
        self.model = SentenceTransformer(MODEL_NAME)

        self.tokens = [r["text"].lower().split() for r in self.recs]
        self.bm25 = BM25Okapi(self.tokens)

    def _vec_search(self, q):
        qv = self.model.encode([q], normalize_embeddings=True).astype("float32")
        D, I = self.index.search(np.array(qv), k=self.top_k_vec)
        out = []
        for score, idx in zip(D[0], I[0]):
            if idx >= 0:
                out.append((idx, float(score)))
        return out

    def _bm25_search(self, q):
        scores = self.bm25.get_scores(q.lower().split())
        idxs = np.argsort(scores)[::-1][: self.top_k_bm25]
        return [(int(i), float(scores[i])) for i in idxs if scores[i] > 0]

    def search(self, queries):
        seen = set()
        results = []

        for q in queries:
            for idx, score in self._vec_search(q):
                key = (self.recs[idx]["book"], self.recs[idx]["chapter"],
                       self.recs[idx]["verse_start"], self.recs[idx]["verse_end"])
                if key not in seen:
                    seen.add(key)
                    results.append({**self.recs[idx], "score": score, "source": "vec"})

            for idx, score in self._bm25_search(q):
                key = (self.recs[idx]["book"], self.recs[idx]["chapter"],
                       self.recs[idx]["verse_start"], self.recs[idx]["verse_end"])
                if key not in seen:
                    seen.add(key)
                    results.append({**self.recs[idx], "score": score, "source": "bm25"})

        # sort: vector scores and bm25 scores are different scales; crude but works:
        results.sort(key=lambda r: r["score"], reverse=True)
        return results
