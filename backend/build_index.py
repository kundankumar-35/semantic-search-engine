"""
build_index.py — run this ONCE offline to create the FAISS + BM25 indexes.

Usage:
    python build_index.py --dataset wikipedia --limit 50000

The script loads documents, encodes them with SBERT, builds the FAISS index,
builds the BM25 index, then saves both to disk. FastAPI loads from disk on startup.
"""

import argparse
import json
import os
from datasets import load_dataset
from indexer import SemanticIndex
from bm25_index import BM25Index
from config import settings

os.makedirs("data", exist_ok=True)


def load_wikipedia(limit: int) -> list[dict]:
    """Load Simple English Wikipedia via HuggingFace datasets."""
    print(f"Loading Wikipedia (limit={limit:,})…")
    ds = load_dataset("wikipedia", "20220301.simple", split="train", trust_remote_code=True)
    docs = []
    for i, row in enumerate(ds):
        if i >= limit:
            break
        docs.append({
            "doc_id": str(row["id"]),
            "title": row["title"],
            "text": row["text"][:512],   # keep snippets manageable
            "url": row["url"],
        })
    return docs


def load_from_json(path: str) -> list[dict]:
    """
    Load your own dataset from a JSON file.
    Expected format:
    [
      {"doc_id": "1", "title": "...", "text": "...", "url": "..."},
      ...
    ]
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["wikipedia", "json"], default="wikipedia")
    parser.add_argument("--json-path", default="documents.json")
    parser.add_argument("--limit", type=int, default=50_000)
    parser.add_argument("--model", default=settings.MODEL_NAME)
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    # 1. Load documents
    if args.dataset == "wikipedia":
        documents = load_wikipedia(args.limit)
    else:
        documents = load_from_json(args.json_path)

    print(f"Loaded {len(documents):,} documents.")

    # 2. Build and save semantic index
    semantic_index = SemanticIndex.build(
        documents,
        model_name=args.model,
        batch_size=args.batch_size,
    )
    semantic_index.save(settings.FAISS_INDEX_PATH, settings.METADATA_PATH)

    # 3. Build and save BM25 index
    print("Building BM25 index…")
    bm25_index = BM25Index.build(documents)
    bm25_index.save(settings.BM25_INDEX_PATH)

    print("\nDone. Start the API with:")
    print("  uvicorn main:app --reload --port 8000")


if __name__ == "__main__":
    main()
