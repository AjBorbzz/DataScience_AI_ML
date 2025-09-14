from pathlib import Path
from typing import List, Tuple
import uuid
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# ChromaDB
import chromadb
from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection

from app.core.config import settings

# Globals
_model: SentenceTransformer | None = None
_chroma: PersistentClient | None = None
_collection: Collection | None = None

# --- Settings fallbacks (in case not defined in your settings) ---
CHROMA_DB_PATH: str = str(getattr(settings, "CHROMA_DB_PATH", Path("./.chroma").resolve()))
CHROMA_COLLECTION: str = getattr(settings, "CHROMA_COLLECTION", "rag_docs")
CHUNK_SIZE: int = int(getattr(settings, "CHUNK_SIZE", 800))
CHUNK_OVERLAP: int = int(getattr(settings, "CHUNK_OVERLAP", 120))
TOP_K_DEFAULT: int = int(getattr(settings, "TOP_K", 5))
EMB_MODEL_ID: str = getattr(
    settings, "EMB_MODEL_ID", "sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------------------- Utils ---------------------------- #

def _ensure_models_loaded() -> None:
    """Lazy-load embedding model and Chroma collection."""
    global _model, _chroma, _collection

    if _model is None:
        _model = SentenceTransformer(EMB_MODEL_ID)

    if _chroma is None:
        _chroma = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    if _collection is None:
        # Create or get collection; we supply our own embeddings
        _collection = _chroma.get_or_create_collection(name=CHROMA_COLLECTION)

def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    chunks: List[str] = []
    start = 0
    n = len(text)
    step = max(1, chunk_size - overlap)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks

# ---------------------------- Public API ---------------------------- #

def ingest_pdf(pdf_path: Path) -> int:
    """
    Read a PDF, chunk it, embed the chunks, and add to ChromaDB.
    Returns the number of chunks ingested.
    """
    _ensure_models_loaded()

    reader = PdfReader(str(pdf_path))
    pages = [(p.extract_text() or "") for p in reader.pages]
    text = "\n\n".join(pages)

    chunks = _chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    if not chunks:
        return 0

    # Compute normalized embeddings (cosine-friendly)
    embeddings = _model.encode(
        chunks, convert_to_numpy=True, normalize_embeddings=True
    ).astype(np.float32)

    # Prepare ids & metadatas
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": str(pdf_path), "chunk_index": i} for i in range(len(chunks))]

    # Store in Chroma
    _collection.add(
        ids=ids,
        embeddings=[e.tolist() for e in embeddings],
        documents=chunks,
        metadatas=metadatas,
    )
    return len(chunks)

def retrieve(query: str, top_k: int | None = None) -> List[Tuple[str, float]]:
    """
    Retrieve top-k chunks for a query.
    Returns list of (document_text, score) where score ~ similarity (higher is better).
    """
    _ensure_models_loaded()
    k = top_k or TOP_K_DEFAULT

    q = _model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(
        np.float32
    )

    # Query Chroma using our embedding
    res = _collection.query(
        query_embeddings=q.tolist(),
        n_results=k,
        include=["documents", "distances"],
    )

    docs = res.get("documents", [[]])[0]
    dists = res.get("distances", [[]])[0]

    # Chroma distances are cosine distances by default (0 = identical).
    # Convert to a similarity-ish score in [0, 1] as (1 - distance).
    results: List[Tuple[str, float]] = []
    for doc, dist in zip(docs, dists):
        if doc is None:
            continue
        sim = float(1.0 - dist) if dist is not None else 0.0
        results.append((doc, sim))
    return results

def build_prompt(user_query: str, contexts: List[str]) -> list[dict[str, str]]:
    system = (
        "You are a helpful assistant that answers only using the provided context. "
        "If the answer is not in the context, say you don't know."
    )
    context_block = "\n\n".join([f"[Context {i+1}]\n{c}" for i, c in enumerate(contexts)])
    user_msg = (
        "Answer the question using ONLY the context below.\n\n"
        f"{context_block}\n\nQuestion: {user_query}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]
