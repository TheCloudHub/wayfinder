# ADR 0003 — Amazon S3 Vectors with a local fallback backend

- **Status:** Accepted
- **Date:** 2026-09-21

## Context

We need a vector store for retrieval. Requirements: run locally with zero infra
during development, but scale to a managed AWS-native store in production without
rewriting the pipeline. The user explicitly chose **Amazon S3 Vectors** as the
production target.

## Decision

Define a small `VectorStore` interface (`ensure_ready`, `upsert`, `search`) with
two implementations selected by `VECTOR_BACKEND`:

- **`local`** — a JSON file plus NumPy cosine similarity. Default for dev/tests.
- **`s3vectors`** — Amazon S3 Vectors via the boto3 `s3vectors` client. The
  vector bucket and cosine index are created on first ingest; chunk text is
  stored as non-filterable metadata.

## Consequences

- Developers and CI can run the full pipeline with no external services.
- Switching to production is a config change (`VECTOR_BACKEND=s3vectors`), not a
  code change.
- The interface hides backend differences (distance vs. score normalization,
  batch limits like 500 vectors per `PutVectors`).
- The local backend is O(n) per query and not meant for large corpora — it is a
  dev/test convenience, not a scale target.

## Alternatives considered

- **pgvector / Postgres:** solid and portable, but adds a database to run and
  operate; not the chosen AWS-native path.
- **Pinecone / Weaviate / Chroma:** capable managed/self-hosted options, but
  introduce another vendor or service versus staying within AWS.
- **FAISS in-memory:** fast for dev, but no persistence story and still not the
  production target.
