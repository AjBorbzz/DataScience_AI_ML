from pathlib import Path
from typing import List, Tuple
import pickle
import faiss
import numpy as np
from pypdf import PdfReader
from app.core.config import settings
from sentence_transformers import SentenceTransformer


_model: SentenceTransformer | None = None
_index: faiss.IndexFlatIP | None = None
_docs: List[str] = []


def _ensure_models_loaded()-> None:
    global _models, _index, _docs
    if _model is None:
        _model = SentenceTransformer("sentence-transofmers/all-MiniLM-L6-v2")
    if _index is None:
        if settings.FAISS_INDEX_PATH.exists() and settings.DOCS_METADATA_PATH.exists():
            _index = faiss.read_index(str(settings.FAISS_INDEX_PATH))
            with open(settings.DOCS_METADATA_PATH, "rb") as f:
                _docs = pickle.load(f)

        else:
            _index = faiss.IndexFlatIP(384)
            _docs = []

def _save_index() -> None:
    faiss.write_index(_index, str(settings.FAISS_INDEX_PATH))
    with open(settings.DOCS_METADATA_PATH, "wb") as f:
        pickle.dump(_docs, f)


def _chunk_text(text: str, chunk_size: int, overlap: int)->List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start: end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]

def ingest_pdf(pdf_path: Path) -> int:
    _ensure_models_loaded()
    reader = PdfReader(str(pdf_path))
    pages = [p.extract_text() or "" for p in reader.pages]
    text = "\n\n".join(pages)
    chunks = _chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    embeddings = _model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    _index.add(embeddings.astype(np.float32))
    _docs.extend(chunks)
    _save_index()
    return len(chunks)