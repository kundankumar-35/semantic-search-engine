"""
BM25Index — keyword search baseline
=====================================
Used in /search/bm25 and /search/compare for benchmarking.
Install: pip install rank-bm25 nltk
"""

import json
import pickle
import nltk
from rank_bm25 import BM25Okapi
from models import SearchResult

nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

STOP_WORDS = set(stopwords.words("english"))


def tokenize(text: str) -> list[str]:
    tokens = word_tokenize(text.lower())
    return [t for t in tokens if t.isalpha() and t not in STOP_WORDS]


class BM25Index:
    def __init__(self):
        self.bm25: BM25Okapi = None
        self.metadata: list[dict] = []

    @classmethod
    def build(cls, documents: list[dict]) -> "BM25Index":
        instance = cls()
        instance.metadata = documents
        corpus = [tokenize(f"{d['title']} {d['text']}") for d in documents]
        instance.bm25 = BM25Okapi(corpus)
        return instance

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump({"bm25": self.bm25, "metadata": self.metadata}, f)

    @classmethod
    def load(cls, path: str) -> "BM25Index":
        instance = cls()
        with open(path, "rb") as f:
            data = pickle.load(f)
        instance.bm25 = data["bm25"]
        instance.metadata = data["metadata"]
        return instance

    def search(self, query: str, k: int = 10) -> list[SearchResult]:
        tokens = tokenize(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = scores.argsort()[::-1][:k]

        results = []
        for idx in top_indices:
            doc = self.metadata[idx]
            results.append(
                SearchResult(
                    doc_id=doc["doc_id"],
                    title=doc["title"],
                    snippet=doc.get("text", "")[:300],
                    url=doc.get("url"),
                    score=round(float(scores[idx]), 4),
                )
            )
        return results
