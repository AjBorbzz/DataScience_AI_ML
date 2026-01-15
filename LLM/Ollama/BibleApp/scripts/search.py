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