"""AWS Bedrock clients for embeddings and chat generation.

Uses the boto3 ``bedrock-runtime`` client directly so the system works even
when higher-level LangChain integrations lag behind new model versions.
"""
from __future__ import annotations

import json
from functools import lru_cache

import boto3
from botocore.config import Config
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings


@lru_cache(maxsize=1)
def _bedrock_runtime():
    session = boto3.Session(
        profile_name=settings.aws_profile or None,
        region_name=settings.aws_region,
    )
    return session.client(
        "bedrock-runtime",
        config=Config(retries={"max_attempts": 3, "mode": "adaptive"}),
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def embed_text(text: str) -> list[float]:
    """Return an embedding vector for a single piece of text (Titan v2)."""
    body = json.dumps({"inputText": text, "dimensions": settings.bedrock_embed_dim})
    resp = _bedrock_runtime().invoke_model(
        modelId=settings.bedrock_embed_model_id,
        body=body,
        accept="application/json",
        contentType="application/json",
    )
    payload = json.loads(resp["body"].read())
    return payload["embedding"]


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts. Titan embeds one input at a time."""
    return [embed_text(t) for t in texts]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def chat(system_prompt: str, user_prompt: str) -> str:
    """Generate an answer using the Bedrock Converse API (Anthropic Claude)."""
    resp = _bedrock_runtime().converse(
        modelId=settings.bedrock_llm_model_id,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_prompt}]}],
        inferenceConfig={
            "temperature": settings.llm_temperature,
            "maxTokens": settings.llm_max_tokens,
        },
    )
    parts = resp["output"]["message"]["content"]
    return "".join(p.get("text", "") for p in parts).strip()
