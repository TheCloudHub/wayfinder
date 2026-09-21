"""Ingestion pipeline: read local docs or fetch web docs, chunk, embed, upsert."""
from __future__ import annotations

from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .bedrock import embed_batch
from .config import ROOT_DIR, settings
from .vectorstore import Chunk, get_vector_store

TEXT_EXTENSIONS = {".md", ".markdown", ".txt", ".rst"}


def _splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    )


def _chunk(text: str, source: str, extra: dict | None = None) -> list[Chunk]:
    docs = _splitter().split_text(text)
    chunks: list[Chunk] = []
    for i, piece in enumerate(docs):
        meta = {"source": source, "chunk": i}
        if extra:
            meta.update(extra)
        chunks.append(Chunk(text=piece, metadata=meta))
    return chunks


def _embed_and_store(chunks: list[Chunk]) -> int:
    if not chunks:
        return 0
    store = get_vector_store()
    store.ensure_ready()
    embeddings = embed_batch([c.text for c in chunks])
    store.upsert(chunks, embeddings)
    return len(chunks)


def ingest_directory(directory: str | Path | None = None) -> dict:
    """Ingest every supported text file under ``directory`` (recursively)."""
    base = Path(directory) if directory else ROOT_DIR / "data" / "knowledge_base"
    if not base.exists():
        return {"files": 0, "chunks": 0, "message": f"No such directory: {base}"}

    all_chunks: list[Chunk] = []
    files = 0
    for path in sorted(base.rglob("*")):
        if path.suffix.lower() not in TEXT_EXTENSIONS or not path.is_file():
            continue
        files += 1
        rel = path.relative_to(base)
        category = rel.parts[0] if len(rel.parts) > 1 else "general"
        all_chunks.extend(
            _chunk(path.read_text(encoding="utf-8"), source=str(rel), extra={"category": category})
        )

    stored = _embed_and_store(all_chunks)
    return {"files": files, "chunks": stored}


def fetch_url_text(url: str) -> str:
    """Fetch a web page and return readable text content."""
    resp = httpx.get(url, follow_redirects=True, timeout=30.0, headers={"User-Agent": "rag-onboarding/1.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    return "\n".join(line.strip() for line in main.get_text("\n").splitlines() if line.strip())


def ingest_urls(urls: list[str], category: str = "web") -> dict:
    """Fetch and ingest a list of documentation URLs."""
    all_chunks: list[Chunk] = []
    ingested: list[str] = []
    errors: list[dict] = []
    for url in urls:
        try:
            text = fetch_url_text(url)
            all_chunks.extend(_chunk(text, source=url, extra={"category": category}))
            ingested.append(url)
        except Exception as exc:  # noqa: BLE001 - surface per-URL failures
            errors.append({"url": url, "error": str(exc)})

    stored = _embed_and_store(all_chunks)
    return {"ingested": ingested, "chunks": stored, "errors": errors}
