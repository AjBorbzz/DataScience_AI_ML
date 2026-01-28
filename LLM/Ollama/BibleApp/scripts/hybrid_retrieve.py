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

    def _vec_search(self, q: str):
        qv = self.model.encode([q], normalize_embeddings=True).astype("float32")
        D, I = self.index.search(np.array(qv), k=self.top_k_vec)
        out = []
        for score, idx in zip(D[0], I[0]):
            if idx >= 0:
                out.append((int(idx), float(score)))
        return out

    @staticmethod
    def _minmax_norm(vals: list[float]) -> list[float]:
        if not vals:
            return []
        lo, hi = min(vals), max(vals)
        if hi - lo < 1e-9:
            return [0.0 for _ in vals]
        return [(v - lo) / (hi - lo) for v in vals]

    def _bm25_search(self, q: str):
        scores = self.bm25.get_scores(q.lower().split())
        idxs = np.argsort(scores)[::-1][: self.top_k_bm25]
        return [(int(i), float(scores[i])) for i in idxs if scores[i] > 0]

    def search(self, queries: list[str]):
        seen = set()
        vec_hits = []   # (idx, score)
        bm_hits = []    # (idx, score)

        for q in queries:
            vec_hits.extend(self._vec_search(q))
            bm_hits.extend(self._bm25_search(q))

        # Normalize within each channel (separate scales)
        vec_scores = [s for _, s in vec_hits]
        bm_scores = [s for _, s in bm_hits]
        vec_norm = self._minmax_norm(vec_scores)
        bm_norm = self._minmax_norm(bm_scores)

        # Map best normalized score per idx per channel
        vec_best: dict[int, float] = {}
        for (idx, _raw), ns in zip(vec_hits, vec_norm):
            if idx not in vec_best or ns > vec_best[idx]:
                vec_best[idx] = ns

        bm_best: dict[int, float] = {}
        for (idx, _raw), ns in zip(bm_hits, bm_norm):
            if idx not in bm_best or ns > bm_best[idx]:
                bm_best[idx] = ns

        # Merge into unique passages; hybrid_score = max(channel scores)
        results = []
        for idx, ns in vec_best.items():
            r = self.recs[idx]
            key = (r["book"], r["chapter"], r["verse_start"], r["verse_end"])
            if key in seen:
                continue
            seen.add(key)
            results.append({**r, "source": "vec", "score": ns, "hybrid_score": ns})

        for idx, ns in bm_best.items():
            r = self.recs[idx]
            key = (r["book"], r["chapter"], r["verse_start"], r["verse_end"])
            if key in seen:
                continue
            seen.add(key)
            results.append({**r, "source": "bm25", "score": ns, "hybrid_score": ns})

        results.sort(key=lambda r: r["hybrid_score"], reverse=True)
        return results
