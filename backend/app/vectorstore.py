"""Vector store abstraction.

Two backends are supported:

* ``s3vectors`` – Amazon S3 Vectors (native AWS vector storage).
* ``local``     – a JSON file + numpy cosine similarity, for dev without AWS.

Both expose the same small interface: ``ensure_ready``, ``upsert`` and
``search``.
"""
from __future__ import annotations

import json
import math
import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol

import boto3
from botocore.exceptions import ClientError

from .config import settings


@dataclass
class Chunk:
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)


@dataclass
class SearchHit:
    text: str
    score: float
    metadata: dict[str, Any]


class VectorStore(Protocol):
    def ensure_ready(self) -> None: ...
    def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None: ...
    def search(self, embedding: list[float], top_k: int) -> list[SearchHit]: ...


# ── Local JSON / numpy fallback ──────────────────────────────────────────────
class LocalVectorStore:
    def __init__(self, path: Path):
        self.path = path
        self._records: list[dict[str, Any]] = []
        self._loaded = False

    def ensure_ready(self) -> None:
        if self._loaded:
            return
        if self.path.exists():
            self._records = json.loads(self.path.read_text())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._loaded = True

    def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self.ensure_ready()
        for chunk, vector in zip(chunks, embeddings):
            self._records.append(
                {
                    "id": chunk.id,
                    "vector": vector,
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                }
            )
        self.path.write_text(json.dumps(self._records))

    def search(self, embedding: list[float], top_k: int) -> list[SearchHit]:
        self.ensure_ready()
        scored: list[SearchHit] = []
        for rec in self._records:
            score = _cosine(embedding, rec["vector"])
            scored.append(SearchHit(text=rec["text"], score=score, metadata=rec["metadata"]))
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# ── Amazon S3 Vectors backend ────────────────────────────────────────────────
class S3VectorsStore:
    def __init__(self, bucket: str, index: str, dim: int):
        self.bucket = bucket
        self.index = index
        self.dim = dim
        session = boto3.Session(
            profile_name=settings.aws_profile or None,
            region_name=settings.aws_region,
        )
        self._client = session.client("s3vectors")

    def ensure_ready(self) -> None:
        try:
            self._client.create_vector_bucket(vectorBucketName=self.bucket)
        except ClientError as exc:
            if exc.response["Error"]["Code"] not in ("ConflictException", "BucketAlreadyOwnedByYou"):
                raise
        try:
            self._client.create_index(
                vectorBucketName=self.bucket,
                indexName=self.index,
                dataType="float32",
                dimension=self.dim,
                distanceMetric="cosine",
                metadataConfiguration={"nonFilterableMetadataKeys": ["text"]},
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "ConflictException":
                raise

    def upsert(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self.ensure_ready()
        vectors = [
            {
                "key": chunk.id,
                "data": {"float32": [float(x) for x in vector]},
                "metadata": {**chunk.metadata, "text": chunk.text},
            }
            for chunk, vector in zip(chunks, embeddings)
        ]
        # S3 Vectors accepts up to 500 vectors per PutVectors call.
        for i in range(0, len(vectors), 500):
            self._client.put_vectors(
                vectorBucketName=self.bucket,
                indexName=self.index,
                vectors=vectors[i : i + 500],
            )

    def search(self, embedding: list[float], top_k: int) -> list[SearchHit]:
        resp = self._client.query_vectors(
            vectorBucketName=self.bucket,
            indexName=self.index,
            queryVector={"float32": [float(x) for x in embedding]},
            topK=top_k,
            returnMetadata=True,
            returnDistance=True,
        )
        hits: list[SearchHit] = []
        for item in resp.get("vectors", []):
            meta = dict(item.get("metadata", {}))
            text = meta.pop("text", "")
            distance = item.get("distance", 1.0)
            hits.append(SearchHit(text=text, score=1.0 - distance, metadata=meta))
        return hits


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    if settings.vector_backend == "s3vectors":
        return S3VectorsStore(
            bucket=settings.s3_vector_bucket,
            index=settings.s3_vector_index,
            dim=settings.bedrock_embed_dim,
        )
    return LocalVectorStore(settings.local_store_abspath)
