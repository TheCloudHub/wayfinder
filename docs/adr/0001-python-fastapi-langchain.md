# ADR 0001 — Python + FastAPI + LangChain stack

- **Status:** Accepted
- **Date:** 2026-09-21

## Context

We need a RAG backend that is fast to build, easy to read, and well supported by
the AI/ML ecosystem. The team is comfortable with Python, and the AWS SDK
(boto3) and document-processing libraries are first-class in Python.

## Decision

Use **Python** with **FastAPI** for the HTTP API and **LangChain** utilities
for RAG plumbing (text splitting today, with room to adopt more of its
retrieval/document abstractions later). Serve the chat UI as static files from
the same FastAPI app to keep the deployment single-process.

## Consequences

- Single language across ingestion, retrieval, and API — low cognitive overhead.
- FastAPI gives async I/O, automatic OpenAPI docs, and Pydantic validation.
- LangChain provides a battle-tested `RecursiveCharacterTextSplitter` and an
  upgrade path to richer retrievers without rewriting the pipeline.
- Adds LangChain as a dependency surface; we use only a small, stable part of it
  to limit churn risk.

## Alternatives considered

- **TypeScript + LangChain.js:** viable, but the AWS Bedrock/boto3 story and
  doc-processing libraries are stronger in Python.
- **No framework (raw ASGI):** less boilerplate to learn but loses OpenAPI,
  validation, and static hosting conveniences.
- **LlamaIndex:** capable, but LangChain’s splitter plus our thin custom
  retrieval kept the surface minimal for this scope.
