"""Pydantic request/response schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The user's question")
    top_k: int | None = Field(None, ge=1, le=20)


class Source(BaseModel):
    source: str
    category: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


class IngestUrlsRequest(BaseModel):
    urls: list[str] = Field(..., min_length=1)
    category: str = "web"


class IngestResponse(BaseModel):
    chunks: int
    files: int | None = None
    ingested: list[str] | None = None
    errors: list[dict] | None = None
    message: str | None = None
