# PhantomAI Backend Dockerfile
FROM python:3.11-slim

LABEL maintainer="PhantomAI"
LABEL description="PhantomAI OSINT Backend"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies including nmap
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    nmap \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
