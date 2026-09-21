"""RAG evaluation harness.

Measures three things over a small labelled dataset (``evals/dataset.jsonl``):

- retrieval recall@k: did the expected source doc appear in the retrieved set
- groundedness: is the answer fully supported by the retrieved context (LLM judge)
- answer relevance: does the answer actually address the question (LLM judge)

Runs against whatever ``VECTOR_BACKEND`` is configured. Requires AWS Bedrock
access (it embeds queries, generates answers, and uses the LLM as a judge), so
it costs tokens; keep it manual / gated rather than on every push.

Usage:
    python -m scripts.eval                 # run, print report
    python -m scripts.eval --check         # exit non-zero if below thresholds
    python -m scripts.eval --top-k 5 --limit 5
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from backend.app.bedrock import chat, embed_text
from backend.app.config import ROOT_DIR, settings
from backend.app.ingest import ingest_directory
from backend.app.rag import SYSTEM_PROMPT, _format_context
from backend.app.vectorstore import get_vector_store

DATASET = ROOT_DIR / "evals" / "dataset.jsonl"

# Gate thresholds.
MIN_RECALL = 0.80
MIN_GROUNDEDNESS = 4.0
MIN_RELEVANCE = 4.0

JUDGE_SYSTEM = """You are a strict evaluator of a retrieval-augmented answer.
You are given a QUESTION, the CONTEXT that was retrieved, and the ANSWER.
Score two dimensions on an integer scale of 1 to 5:
- groundedness: 5 = every claim is supported by the context; 1 = mostly unsupported/hallucinated.
- relevance: 5 = directly and fully answers the question; 1 = off-topic.
Respond with ONLY a JSON object: {"groundedness": <1-5>, "relevance": <1-5>, "reason": "<short>"}."""


def _judge(question: str, context: str, answer_text: str) -> dict:
    prompt = (
        f"QUESTION:\n{question}\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"ANSWER:\n{answer_text}\n\n"
        "Return the JSON now."
    )
    raw = chat(JUDGE_SYSTEM, prompt)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"groundedness": 0, "relevance": 0, "reason": f"unparseable: {raw[:80]}"}
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"groundedness": 0, "relevance": 0, "reason": f"bad json: {raw[:80]}"}
    return data


def _load_dataset(limit: int | None) -> list[dict]:
    items = [json.loads(line) for line in DATASET.read_text().splitlines() if line.strip()]
    return items[:limit] if limit else items


def run(top_k: int, limit: int | None) -> dict:
    store = get_vector_store()
    store.ensure_ready()

    # Populate a local store on demand so the harness is runnable out of the box.
    if settings.vector_backend == "local":
        store_path = Path(settings.local_store_abspath)
        if not store_path.exists() or store_path.stat().st_size <= 2:
            print("Local vector store empty; ingesting knowledge base ...")
            ingest_directory()

    items = _load_dataset(limit)
    rows = []
    for item in items:
        question = item["question"]
        expected = item["expected_source"]

        hits = store.search(embed_text(question), top_k=top_k)
        retrieved = [h.metadata.get("source", "unknown") for h in hits]
        recall_hit = expected in retrieved

        context = _format_context(hits)
        answer_text = chat(SYSTEM_PROMPT, f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:")
        scores = _judge(question, context, answer_text)

        rows.append(
            {
                "question": question,
                "expected": expected,
                "retrieved": retrieved,
                "recall_hit": recall_hit,
                "groundedness": scores.get("groundedness", 0),
                "relevance": scores.get("relevance", 0),
            }
        )

    n = len(rows) or 1
    summary = {
        "count": len(rows),
        "recall_at_k": sum(r["recall_hit"] for r in rows) / n,
        "mean_groundedness": sum(r["groundedness"] for r in rows) / n,
        "mean_relevance": sum(r["relevance"] for r in rows) / n,
    }
    return {"rows": rows, "summary": summary, "top_k": top_k}


def _print_report(result: dict) -> None:
    print(f"\nRAG eval  (top_k={result['top_k']}, backend={settings.vector_backend})\n")
    print(f"{'recall':^7}{'ground':^7}{'relev':^7}  question")
    print("-" * 72)
    for r in result["rows"]:
        mark = "  ok " if r["recall_hit"] else " MISS"
        print(f"{mark:^7}{r['groundedness']:^7}{r['relevance']:^7}  {r['question'][:44]}")
    s = result["summary"]
    print("-" * 72)
    print(
        f"recall@k={s['recall_at_k']:.0%}  "
        f"groundedness={s['mean_groundedness']:.2f}/5  "
        f"relevance={s['mean_relevance']:.2f}/5  (n={s['count']})"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the RAG pipeline.")
    parser.add_argument("--top-k", type=int, default=settings.retrieval_top_k)
    parser.add_argument("--limit", type=int, default=None, help="Only run the first N items.")
    parser.add_argument("--check", action="store_true", help="Exit non-zero if below thresholds.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = run(top_k=args.top_k, limit=args.limit)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_report(result)

    if args.check:
        s = result["summary"]
        failures = []
        if s["recall_at_k"] < MIN_RECALL:
            failures.append(f"recall@k {s['recall_at_k']:.0%} < {MIN_RECALL:.0%}")
        if s["mean_groundedness"] < MIN_GROUNDEDNESS:
            failures.append(f"groundedness {s['mean_groundedness']:.2f} < {MIN_GROUNDEDNESS}")
        if s["mean_relevance"] < MIN_RELEVANCE:
            failures.append(f"relevance {s['mean_relevance']:.2f} < {MIN_RELEVANCE}")
        if failures:
            print("\nFAIL: " + "; ".join(failures))
            return 1
        print("\nPASS: all thresholds met")
    return 0


if __name__ == "__main__":
    sys.exit(main())
