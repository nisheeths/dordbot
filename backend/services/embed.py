from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Optional
import numpy as np


class TfidfEmbedder:
    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None

    def fit(self, corpus: List[str]):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_df=0.9,
            min_df=1,
            strip_accents="unicode",
        )
        self.vectorizer.fit(corpus)

    def encode(self, texts: List[str]) -> np.ndarray:
        if self.vectorizer is None:
            raise RuntimeError("TF-IDF vectorizer is not fitted")
        m = self.vectorizer.transform(texts)
        return m.astype(np.float32).toarray()
