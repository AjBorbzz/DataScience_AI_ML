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