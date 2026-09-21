# Developer Onboarding RAG

A retrieval-augmented generation (RAG) assistant for developer onboarding. It
answers questions from your org-wide knowledge base plus Azure, GCP, AWS usage
guides and AWS FinOps guardrails.

- **Stack:** Python, FastAPI, LangChain
- **LLM + embeddings:** AWS Bedrock (Anthropic Claude + Titan Embeddings)
- **Vector store:** Amazon S3 Vectors, with a local JSON/numpy fallback for dev
- **UI:** REST API + a Claude/Zara-inspired chat interface

## Architecture

```
frontend/ (chat UI)  ──▶  FastAPI  ──▶  rag.py ──▶ Bedrock (Claude)
                                          │
                             embed (Titan)│
                                          ▼
                              vector store (S3 Vectors | local)
                                          ▲
                              ingest.py (docs + live URLs)
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # edit as needed
```

By default `VECTOR_BACKEND=local`, so you can run everything without any AWS
vector setup. Bedrock (LLM + embeddings) still requires AWS credentials with
Bedrock model access.

### AWS credentials

Use the standard AWS credential chain (SSO, profile, env vars, or role):

```bash
aws sso login --profile dev
export AWS_PROFILE=dev          # or set AWS_PROFILE in .env
```

Ensure the Claude and Titan models are enabled in the Bedrock console for your
region.

## Ingest the knowledge base

```bash
# ingest the seed docs under data/knowledge_base/
python scripts/ingest_docs.py

# ingest live tool documentation from URLs
python scripts/ingest_docs.py --url https://docs.aws.amazon.com/... --category aws
```

You can also trigger ingestion via the API (`POST /api/ingest/local`,
`POST /api/ingest/urls`).

## Run

```bash
uvicorn backend.app.main:app --reload
# open http://localhost:8000
```

## API

| Method | Path                | Description                          |
| ------ | ------------------- | ------------------------------------ |
| GET    | `/api/health`       | Health + active backend/model        |
| POST   | `/api/chat`         | `{ "question": "...", "top_k": 5 }`  |
| POST   | `/api/ingest/local` | Ingest `data/knowledge_base/`        |
| POST   | `/api/ingest/urls`  | `{ "urls": [...], "category": "..." }` |

## Switching to Amazon S3 Vectors

Set in `.env`:

```
VECTOR_BACKEND=s3vectors
S3_VECTOR_BUCKET=devonboarding-rag
S3_VECTOR_INDEX=knowledge-base
```

The bucket and index are created automatically on first ingest. The IAM
principal needs `s3vectors:*` (or scoped equivalents) plus `bedrock:InvokeModel`.

## Knowledge base layout

```
data/knowledge_base/
  org/      engineering standards, security, onboarding overview
  azure/    Azure usage & guardrails
  gcp/      GCP usage & guardrails
  aws/      AWS usage & guardrails
  finops/   AWS FinOps cost guardrails
```

Drop in your own `.md` / `.txt` files under these folders (or new ones) and
re-run ingestion. The subfolder name becomes the `category` tag.

## Notes

- Answers are grounded strictly in retrieved context; the assistant is
  instructed to say when something isn't documented rather than guess.
- For live tool docs, prefer official documentation URLs and re-ingest
  periodically to keep answers current.
