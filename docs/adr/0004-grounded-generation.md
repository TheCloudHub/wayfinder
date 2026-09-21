# ADR 0004 — Strictly grounded generation with source citations

- **Status:** Accepted
- **Date:** 2026-09-21

## Context

This is an onboarding assistant answering questions about org policy, cloud
usage, and FinOps guardrails. Wrong answers (invented commands, cost numbers, or
policy) are worse than "I don't know". Users need to trust and verify answers.

## Decision

Constrain the model to answer **only from retrieved context** and to cite the
sources it used:

- A system prompt (`SYSTEM_PROMPT` in `rag.py`) instructs the model to answer
  only from the provided context, to say when something is not documented, to be
  concise, and to never invent commands, cost numbers, or policy.
- Low temperature (`0.1`) to reduce drift.
- The API returns a `sources` list (file/URL, category, similarity score) so the
  UI can display provenance.
- If retrieval returns nothing, the system responds that the knowledge base is
  empty / undocumented instead of guessing.

## Consequences

- Higher trust and verifiability; answers point back to source docs.
- The assistant will decline or defer when coverage is missing — this is the
  desired behavior, but requires keeping the knowledge base current.
- Answer quality is bounded by retrieval quality (see ADR 0003 and future
  re-ranking work).

## Alternatives considered

- **Open-ended generation with citations as a hint:** rejected — too easy for
  the model to fill gaps with plausible but wrong content.
- **Extractive-only answers (return raw chunks):** safest but poor UX; loses
  synthesis across multiple sources.
