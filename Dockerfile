# Ozark Finances - Dockerfile for Raspberry Pi 3B+
# Multi-stage build optimized for ARM architecture
# Created: August 15, 2025

# =============================================================================
# STAGE 1: Base Python Image for ARM
# =============================================================================
FROM python:3.9-slim-bullseye as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create application user (security best practice)
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# =============================================================================
# STAGE 2: Dependencies Installation
# =============================================================================
FROM base as dependencies

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# STAGE 3: Application
# =============================================================================
FROM base as application

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/uploads /app/generated /app/logs && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Create SQLite databases directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Default command
CMD ["python", "app.py"]
