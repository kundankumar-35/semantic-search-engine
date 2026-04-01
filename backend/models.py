"""
Pydantic models — request/response schemas
"""

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    doc_id: str
    title: str
    snippet: str
    url: str | None = None
    score: float = Field(..., description="Cosine similarity (0–1) or BM25 score")


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    latency_ms: float
    total_hits: int
    method: str   # "semantic" | "bm25"


class CompareResponse(BaseModel):
    query: str
    semantic: list[SearchResult]
    bm25: list[SearchResult]
    latency_ms: float


class MetricsResponse(BaseModel):
    p50: float
    p95: float
    p99: float
    total_requests: int
