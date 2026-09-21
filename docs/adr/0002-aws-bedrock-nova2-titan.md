# ADR 0002 — AWS Bedrock (Nova 2 Lite + Titan v2) for LLM & embeddings

- **Status:** Accepted
- **Date:** 2026-09-21

## Context

The system needs a generation model and an embedding model. The target
environment is AWS, and we want a single provider for auth, billing, and data
residency rather than mixing in a third-party LLM API. During setup we found:

- Titan embeddings were already enabled on the account.
- Anthropic Claude models required a separate use-case approval that was **not**
  submitted (`ResourceNotFoundException: Model use case details have not been
  submitted`), so Claude was not callable.
- Amazon Nova models (including **Nova 2 Lite**) were approved and callable via
  inference profiles.

## Decision

Use **Amazon Bedrock** for both models via the boto3 `bedrock-runtime` client:

- **Generation:** `us.amazon.nova-2-lite-v1:0` through the **Converse API**.
- **Embeddings:** `amazon.titan-embed-text-v2:0` (1024 dimensions).

Model IDs are configurable via `BEDROCK_LLM_MODEL_ID` / `BEDROCK_EMBED_MODEL_ID`
so we can swap models (e.g., to Nova Pro or an approved Claude) without code
changes.

## Consequences

- One provider for LLM + embeddings: unified IAM, region, and cost controls.
- No static API keys; uses the AWS credential chain / task roles.
- Nova 2 Lite is low-cost and fast, suitable for grounded Q&A.
- Nova requires **inference-profile** model IDs (the `us.` prefix), not
  on-demand IDs — encoded in defaults and `.env`.
- Vendor coupling to Bedrock; mitigated by keeping the client behind
  `bedrock.py` and model IDs in config.

## Alternatives considered

- **Anthropic Claude on Bedrock:** preferred quality, but blocked by pending
  model-access approval on this account. Left as an easy config swap once
  enabled.
- **OpenAI / public APIs:** rejected to avoid a second provider and to keep data
  within AWS.
- **Local/Ollama:** good for dev but not aligned with the AWS-native target and
  adds ops burden.
