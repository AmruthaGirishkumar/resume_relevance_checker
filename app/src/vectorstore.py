import faiss
import numpy as np
import os
import pickle
from typing import List, Dict

INDEX_PATH = "data/faiss_index.bin"
META_PATH = "data/faiss_meta.pkl"

class SimpleVectorStore:
    def __init__(self, dim=384):
        self.dim = dim
        self.index = None
        self.meta = []
        self._load()

    def _load(self):
        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, "rb") as f:
                self.meta = pickle.load(f)
        else:
            self.index = faiss.IndexFlatIP(self.dim)
            self.meta = []

    def add(self, vectors: np.ndarray, metadatas: List[Dict]):
        # vectors shape: (N, dim)
        self.index.add(vectors.astype("float32"))
        self.meta.extend(metadatas)
        self._save()

    def _save(self):
        os.makedirs("data", exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.meta, f)

    def search(self, vector: np.ndarray, topk=5):
        D, I = self.index.search(vector.reshape(1, -1).astype("float32"), topk)
        results = []
        for idx in I[0]:
            if idx < len(self.meta):
                results.append(self.meta[idx])
        return results

_vs = None
def get_vectorstore(dim=384):
    global _vs
    if _vs is None:
        _vs = SimpleVectorStore(dim=dim)
    return _vs
