import faiss
import numpy as np
import json
from pathlib import Path
from typing import Tuple, List, Dict, Any


class FaissStore:
    def __init__(self):
        self.index = None
        self.metadata: List[Dict[str, Any]] = []

    def _ensure_index(self, dim: int):
        if self.index is None:
            self.index = faiss.IndexFlatIP(dim)

    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
        return vectors / norms

    def add(self, embeddings: np.ndarray, metas: List[Dict[str, Any]]):
        if embeddings.ndim != 2:
            raise ValueError("embeddings must be 2D")
        embeddings = self._normalize(embeddings.astype(np.float32))
        self._ensure_index(embeddings.shape[1])
        self.index.add(embeddings)
        self.metadata.extend(metas)

    def search(self, queries: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
        if self.index is None or self.index.ntotal == 0:
            return (
                np.zeros((queries.shape[0], top_k), dtype=np.float32),
                -np.ones((queries.shape[0], top_k), dtype=np.int64),
            )
        queries = self._normalize(queries.astype(np.float32))
        sims, idxs = self.index.search(queries, top_k)
        return sims, idxs

    def persist(self, dir_path: str):
        p = Path(dir_path)
        p.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, str(p / "index.faiss"))
        with open(p / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def load(self, dir_path: str):
        p = Path(dir_path)
        index_path = p / "index.faiss"
        meta_path = p / "metadata.json"
        if index_path.exists():
            self.index = faiss.read_index(str(index_path))
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
