"""
Semantic Search Engine — FastAPI Backend
=========================================
Endpoints:
  GET /search?q=...&k=10          → semantic (SBERT + FAISS)
  GET /search/bm25?q=...&k=10     → keyword baseline
  GET /search/compare?q=...&k=5   → side-by-side comparison
  GET /metrics                    → latency stats
  GET /health                     → health check
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from functools import lru_cache
import time
import numpy as np

from models import SearchResponse, SearchResult, CompareResponse, MetricsResponse
from indexer import SemanticIndex
from bm25_index import BM25Index
from config import settings

# ---------------------------------------------------------------------------
# App lifespan — load indexes once at startup
# ---------------------------------------------------------------------------

semantic_index: SemanticIndex = None
bm25_index: BM25Index = None
latency_log: list[float] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    global semantic_index, bm25_index
    print("Loading indexes…")
    semantic_index = SemanticIndex.load(settings.FAISS_INDEX_PATH, settings.METADATA_PATH)
    bm25_index = BM25Index.load(settings.BM25_INDEX_PATH)
    print(f"Ready — {semantic_index.num_docs:,} documents indexed.")
    yield
    print("Shutting down.")


app = FastAPI(
    title="Semantic Search API",
    description="Dense retrieval with Sentence-BERT + FAISS",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def record_latency(ms: float):
    latency_log.append(ms)
    if len(latency_log) > 10_000:   # rolling window
        latency_log.pop(0)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "docs_indexed": semantic_index.num_docs if semantic_index else 0,
    }


@app.get("/search", response_model=SearchResponse)
def semantic_search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    k: int = Query(10, ge=1, le=50, description="Number of results"),
):
    """
    Dense semantic search: embed query → FAISS ANN → fetch metadata.
    Typical latency: 30–80ms on CPU for a 100k-doc corpus.
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query must not be blank.")

    t0 = time.perf_counter()
    results = _cached_semantic_search(q.strip().lower(), k)
    latency_ms = (time.perf_counter() - t0) * 1000
    record_latency(latency_ms)

    return SearchResponse(
        query=q,
        results=results,
        latency_ms=round(latency_ms, 2),
        total_hits=len(results),
        method="semantic",
    )


@app.get("/search/bm25", response_model=SearchResponse)
def bm25_search(
    q: str = Query(..., min_length=1, max_length=500),
    k: int = Query(10, ge=1, le=50),
):
    """
    BM25 keyword baseline. Use /search/compare to see both side by side.
    """
    t0 = time.perf_counter()
    results = bm25_index.search(q, k)
    latency_ms = (time.perf_counter() - t0) * 1000

    return SearchResponse(
        query=q,
        results=results,
        latency_ms=round(latency_ms, 2),
        total_hits=len(results),
        method="bm25",
    )


@app.get("/search/compare", response_model=CompareResponse)
def compare_search(
    q: str = Query(..., min_length=1, max_length=500),
    k: int = Query(5, ge=1, le=20),
):
    """
    Run both methods and return results side by side.
    Useful for the frontend toggle and for your benchmark README.
    """
    t0 = time.perf_counter()
    semantic_results = _cached_semantic_search(q.strip().lower(), k)
    bm25_results = bm25_index.search(q, k)
    total_ms = (time.perf_counter() - t0) * 1000

    return CompareResponse(
        query=q,
        semantic=semantic_results,
        bm25=bm25_results,
        latency_ms=round(total_ms, 2),
    )


@app.get("/metrics", response_model=MetricsResponse)
def metrics():
    """
    Rolling latency percentiles over the last 10,000 requests.
    Wire this into Prometheus/Grafana for production monitoring.
    """
    if not latency_log:
        return MetricsResponse(p50=0, p95=0, p99=0, total_requests=0)

    arr = np.array(latency_log)
    return MetricsResponse(
        p50=round(float(np.percentile(arr, 50)), 2),
        p95=round(float(np.percentile(arr, 95)), 2),
        p99=round(float(np.percentile(arr, 99)), 2),
        total_requests=len(latency_log),
    )


# ---------------------------------------------------------------------------
# Cache — avoid re-embedding identical queries
# ---------------------------------------------------------------------------

@lru_cache(maxsize=512)
def _cached_semantic_search(query: str, k: int) -> tuple[SearchResult, ...]:
    """
    LRU cache keyed on (query, k). Returns a tuple so it's hashable.
    In production, swap this for Redis with a TTL.
    """
    return tuple(semantic_index.search(query, k))
