import sys
import pickle
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

INDEX_DIR = Path("index")
FAISS_PATH = INDEX_DIR / "bible_kjv.faiss"
META_PATH = INDEX_DIR / "bible_kjv_meta.pkl"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5

TEST_CASES = [
    {
        "name": "money_stewardship",
        "query": "I am having trouble with money. What does the Bible say about handling money?",
        "anchors": ["money", "rich", "treasure", "silver", "gold", "mammon", "steward", "poverty", "lend", "debt"],
    },
    {
        "name": "anxiety",
        "query": "I am anxious and worried. What does the Bible say about anxiety?",
        "anchors": ["fear", "afraid", "anxious", "care", "peace", "worry"],
    },
    {
        "name": "forgiveness",
        "query": "I struggle to forgive someone who hurt me. What does the Bible say about forgiveness?",
        "anchors": ["forgive", "forgiven", "mercy", "trespass", "debt"],
    },
]