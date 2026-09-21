"""AWS Lambda entrypoint.

The heavy objects (FastAPI app, Bedrock clients, vector store) are created at
import time / cached with ``lru_cache``, so they are initialized once per
execution environment and reused across warm invocations. Mangum adapts the
ASGI app to the Lambda + Function URL / API Gateway event model.
"""
from __future__ import annotations

from mangum import Mangum

from .main import app

# Module scope: created once per warm microVM, reused across invocations.
handler = Mangum(app, lifespan="off")
