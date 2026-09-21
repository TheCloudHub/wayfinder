"""Application configuration loaded from environment variables."""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # AWS / Bedrock
    aws_region: str = "us-east-1"
    aws_profile: str | None = None
    bedrock_llm_model_id: str = "us.amazon.nova-2-lite-v1:0"
    bedrock_embed_model_id: str = "amazon.titan-embed-text-v2:0"
    bedrock_embed_dim: int = 1024

    # Vector store
    vector_backend: str = "local"  # "local" | "s3vectors"
    s3_vector_bucket: str = "devonboarding-rag"
    s3_vector_index: str = "knowledge-base"
    local_store_path: str = "data/vector_store.json"

    # Retrieval / generation
    retrieval_top_k: int = 5
    chunk_size: int = 1200
    chunk_overlap: int = 150
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Security: comma-separated allowed CORS origins. Empty = same-origin only
    # (the UI is served by this app, so no cross-origin access is needed).
    cors_allow_origins: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]

    @property
    def local_store_abspath(self) -> Path:
        p = Path(self.local_store_path)
        return p if p.is_absolute() else ROOT_DIR / p


settings = Settings()
