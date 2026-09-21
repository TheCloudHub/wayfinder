# Architecture Decision Records

This directory records the significant architectural decisions for the Developer
Onboarding RAG system, using lightweight [ADRs](https://adr.github.io/).

| ADR | Title | Status |
| --- | --- | --- |
| [0001](0001-python-fastapi-langchain.md) | Python + FastAPI + LangChain stack | Accepted |
| [0002](0002-aws-bedrock-nova2-titan.md) | AWS Bedrock (Nova 2 Lite + Titan v2) for LLM & embeddings | Accepted |
| [0003](0003-s3-vectors-with-local-fallback.md) | Amazon S3 Vectors with a local fallback backend | Accepted |
| [0004](0004-grounded-generation.md) | Strictly grounded generation with source citations | Accepted |
| [0005](0005-offline-ingestion.md) | Offline ingestion of docs and URLs (no live tool calls) | Accepted |

## Format

Each ADR captures: **Context**, **Decision**, **Consequences**, and
**Alternatives considered**. Status is one of Proposed / Accepted / Superseded.
