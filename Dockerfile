# ==============================================================================
# Stage 1: Builder — install Python dependencies into a clean virtual env
# ==============================================================================
FROM python:3.13-slim AS builder

# System packages needed to compile Python extensions (psycopg, cryptography, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment in /opt/venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for Docker layer caching
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies + Gunicorn (not in requirements.txt, runtime-only)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir gunicorn==23.0.0


# ==============================================================================
# Stage 2: Production runtime — minimal image, non-root user
# ==============================================================================
FROM python:3.13-slim AS production

LABEL maintainer="CodePilot AI Team"
LABEL version="0.1.0"
LABEL description="CodePilot AI Production-grade code review backend"

# Runtime system dependencies (libpq for asyncpg, curl for healthcheck, postgresql-client for pg_isready, redis-tools for redis-cli)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root application user
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Create persistent directories with correct ownership
RUN mkdir -p \
    /app/app/uploads/temp \
    /app/app/reports \
    /app/logs \
    /app/backups \
    /app/uploads \
    /app/reports \
    && chown -R appuser:appgroup /app

# Copy application source code (after dir creation so ownership is correct)
COPY --chown=appuser:appgroup . /app/

# Copy shell scripts and ensure they are executable
COPY --chown=appuser:appgroup scripts/start.sh /app/scripts/start.sh
COPY --chown=appuser:appgroup scripts/wait_for_db.sh /app/scripts/wait_for_db.sh
COPY --chown=appuser:appgroup scripts/migrate.sh /app/scripts/migrate.sh
COPY --chown=appuser:appgroup scripts/healthcheck.sh /app/scripts/healthcheck.sh

# Fix line endings + make scripts executable (important for cross-platform Windows->Linux)
RUN sed -i 's/\r//' /app/scripts/*.sh && \
    chmod +x /app/scripts/*.sh

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Docker built-in healthcheck (polls /health every 30s, 3 retries before unhealthy)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default entrypoint: the startup orchestration script
ENTRYPOINT ["/app/scripts/start.sh"]
