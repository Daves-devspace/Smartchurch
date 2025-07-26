import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load FAISS index and metadata
BASE_DIR = os.getcwd()
IDX_PATH = os.path.join(BASE_DIR, "verse_index.faiss")
META_PATH = os.path.join(BASE_DIR, "verses_meta.json")

# Constants
SIM_THRESHOLD = 0.5
TOP_K = 3

# Load model + index once
T2 = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(IDX_PATH)
metadata = json.load(open(META_PATH))

def semantic_search(query: str):
    """
    Given a natural-language query, return top-k semantically similar verses.
    """
    emb = T2.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(emb)
    distances, indices = index.search(emb, TOP_K)

    results = []
    for score, idx in zip(distances[0], indices[0]):
        if score >= SIM_THRESHOLD and idx < len(metadata):
            entry = metadata[idx]
            results.append({**entry, "source": "semantic", "score": float(score)})

    return results
