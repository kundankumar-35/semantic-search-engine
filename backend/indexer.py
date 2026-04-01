"""
SemanticIndex — offline indexer + query-time search
====================================================

Offline (run once):
    index = SemanticIndex.build(documents, model_name="all-MiniLM-L6-v2")
    index.save("faiss.index", "metadata.json")

Query time (loaded by FastAPI on startup):
    index = SemanticIndex.load("faiss.index", "metadata.json")
    results = index.search("cardiac arrest", k=10)
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from models import SearchResult


class SemanticIndex:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index: faiss.Index = None
        self.metadata: list[dict] = []

    # ------------------------------------------------------------------
    # Offline: build the index from scratch
    # ------------------------------------------------------------------

    @classmethod
    def build(
        cls,
        documents: list[dict],           # [{"doc_id", "title", "text", "url"}, ...]
        model_name: str = "all-MiniLM-L6-v2",
        batch_size: int = 64,
        use_gpu: bool = False,
    ) -> "SemanticIndex":
        """
        Encode all documents and build a FAISS index.
        Typical speed: ~2,000 docs/sec on CPU with MiniLM.

        For >100k docs, switch to IndexIVFFlat:
            quantizer = faiss.IndexFlatIP(dim)
            index = faiss.IndexIVFFlat(quantizer, dim, nlist=256)
            index.train(embeddings)
        """
        instance = cls(model_name)

        texts = [f"{d['title']} {d['text']}" for d in documents]
        print(f"Encoding {len(texts):,} documents with {model_name}…")

        embeddings = instance.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,   # required for cosine sim via inner product
            convert_to_numpy=True,
        )

        dim = embeddings.shape[1]   # 384 for MiniLM, 768 for mpnet

        if use_gpu:
            res = faiss.StandardGpuResources()
            index = faiss.GpuIndexFlatIP(res, dim)
        else:
            index = faiss.IndexFlatIP(dim)

        index.add(embeddings.astype(np.float32))
        instance.index = index
        instance.metadata = documents
        print(f"Index built — {index.ntotal:,} vectors, dim={dim}")
        return instance

    # ------------------------------------------------------------------
    # Persist / load
    # ------------------------------------------------------------------

    def save(self, index_path: str, metadata_path: str):
        faiss.write_index(self.index, index_path)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False)
        print(f"Saved index → {index_path}, metadata → {metadata_path}")

    @classmethod
    def load(cls, index_path: str, metadata_path: str) -> "SemanticIndex":
        instance = cls.__new__(cls)
        instance.model = SentenceTransformer("all-MiniLM-L6-v2")
        instance.index = faiss.read_index(index_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            instance.metadata = json.load(f)
        print(f"Loaded {instance.index.ntotal:,} vectors from {index_path}")
        return instance

    # ------------------------------------------------------------------
    # Query-time search
    # ------------------------------------------------------------------

    def search(self, query: str, k: int = 10) -> list[SearchResult]:
        """
        1. Encode query to 384-dim vector
        2. FAISS inner-product search (= cosine sim because vecs are normalized)
        3. Return top-k with metadata
        """
        query_vec = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)

        scores, indices = self.index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:   # FAISS returns -1 for empty slots
                continue
            doc = self.metadata[idx]
            results.append(
                SearchResult(
                    doc_id=doc["doc_id"],
                    title=doc["title"],
                    snippet=doc.get("text", "")[:300],
                    url=doc.get("url"),
                    score=round(float(score), 4),
                )
            )
        return results

    @property
    def num_docs(self) -> int:
        return self.index.ntotal if self.index else 0
