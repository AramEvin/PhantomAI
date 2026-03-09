FROM python:3.11-slim

# LABEL — metadata about this image (optional but good practice)
LABEL maintainer="PhantomAI"
LABEL description="PhantomAI OSINT Backend"

# ENV — set environment variables inside the container
# PYTHONDONTWRITEBYTECODE=1 → don't create .pyc cache files (keeps image clean)
# PYTHONUNBUFFERED=1 → print logs immediately (don't buffer them)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# WORKDIR — set the working directory inside the container
# All future commands run from this path
# Creates the directory if it doesn't exist
WORKDIR /app

# Install system dependencies needed by some Python packages
# --no-install-recommends = only install what's needed (smaller image)
# rm -rf /var/lib/apt/lists/* = clean up apt cache after install
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# COPY requirements first — before copying code
# WHY: Docker caches each layer. If requirements.txt hasn't changed,
# Docker skips the pip install step on rebuild = much faster builds
COPY requirements.txt .

# RUN — execute a command during build
# Install all Python dependencies
# --no-cache-dir = don't store pip download cache (smaller image)
RUN pip install --no-cache-dir -r requirements.txt

# COPY — copy files from your machine into the container
# COPY <source on your machine> <destination in container>
# Copy the entire backend app code
COPY . .

# EXPOSE — document which port this container listens on
# This doesn't actually open the port — it's documentation
# The real port mapping happens in docker-compose.yml
EXPOSE 8000

# HEALTHCHECK — Docker will run this command periodically
# to check if the container is healthy
# --interval=30s  → check every 30 seconds
# --timeout=10s   → fail if no response in 10 seconds
# --retries=3     → mark unhealthy after 3 failures
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# CMD — the command to run when container starts
# This starts the FastAPI server
# --host 0.0.0.0 = listen on all interfaces (required in Docker)
# --port 8000 = port inside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
