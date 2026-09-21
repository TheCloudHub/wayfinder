"""Retrieval-augmented generation chain."""
from __future__ import annotations

from .bedrock import chat, embed_text
from .config import settings
from .vectorstore import SearchHit, get_vector_store

SYSTEM_PROMPT = """You are the Developer Onboarding Assistant for our engineering org.
You help new and existing developers with:
- org-wide engineering knowledge base, standards and processes
- Azure, GCP and AWS cloud usage guidance
- AWS FinOps cost guardrails

Rules:
- Answer ONLY from the provided context. If the context does not contain the
  answer, say you don't have that documented yet and suggest where to look.
- Be concise and practical. Prefer bullet points and concrete steps.
- Cite the sources you used by their file/URL names in a "Sources" list.
- Never invent commands, cost numbers, or policy that is not in the context.
"""


def _format_context(hits: list[SearchHit]) -> str:
    blocks = []
    for i, hit in enumerate(hits, 1):
        source = hit.metadata.get("source", "unknown")
        blocks.append(f"[{i}] source: {source}\n{hit.text}")
    return "\n\n---\n\n".join(blocks)


def answer(question: str, top_k: int | None = None) -> dict:
    k = top_k or settings.retrieval_top_k
    store = get_vector_store()
    store.ensure_ready()

    query_embedding = embed_text(question)
    hits = store.search(query_embedding, top_k=k)

    if not hits:
        return {
            "answer": "The knowledge base is empty. Ingest documents first via /ingest.",
            "sources": [],
        }

    context = _format_context(hits)
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    reply = chat(SYSTEM_PROMPT, user_prompt)

    sources = []
    seen = set()
    for hit in hits:
        src = hit.metadata.get("source", "unknown")
        if src not in seen:
            seen.add(src)
            sources.append(
                {
                    "source": src,
                    "category": hit.metadata.get("category", "general"),
                    "score": round(hit.score, 4),
                }
            )
    return {"answer": reply, "sources": sources}
