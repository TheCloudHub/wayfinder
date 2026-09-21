"""FastAPI application: REST API + static chat UI."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import ROOT_DIR, settings
from .ingest import ingest_directory, ingest_urls
from .models import ChatRequest, ChatResponse, IngestResponse, IngestUrlsRequest
from .rag import answer

app = FastAPI(title="Developer Onboarding RAG", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = ROOT_DIR / "frontend"


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "vector_backend": settings.vector_backend, "llm": settings.bedrock_llm_model_id}


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest) -> ChatResponse:
    try:
        result = answer(req.question, top_k=req.top_k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Generation failed: {exc}") from exc
    return ChatResponse(**result)


@app.post("/api/ingest/local", response_model=IngestResponse)
def ingest_local_endpoint() -> IngestResponse:
    return IngestResponse(**ingest_directory())


@app.post("/api/ingest/urls", response_model=IngestResponse)
def ingest_urls_endpoint(req: IngestUrlsRequest) -> IngestResponse:
    return IngestResponse(**ingest_urls(req.urls, category=req.category))


# ── Static chat UI ───────────────────────────────────────────────────────────
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(str(FRONTEND_DIR / "index.html"))


def main() -> None:
    import uvicorn

    uvicorn.run("backend.app.main:app", host=settings.host, port=settings.port, reload=True)


if __name__ == "__main__":
    main()
