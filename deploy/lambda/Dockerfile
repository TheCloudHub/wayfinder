# Lean Lambda container image for the Developer Onboarding RAG API.
# Deps exceed the Lambda zip limit, so we ship a container image (Firecracker
# microVM under the hood). Clients are cached at module scope for warm reuse.
FROM public.ecr.aws/lambda/python:3.14

# Install dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code and static UI (served via FileResponse).
COPY backend/ ${LAMBDA_TASK_ROOT}/backend/
COPY frontend/ ${LAMBDA_TASK_ROOT}/frontend/

# Lambda calls this ASGI handler (Mangum-wrapped FastAPI app).
CMD [ "backend.app.lambda_handler.handler" ]
