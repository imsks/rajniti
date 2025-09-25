# Production Dockerfile for Rajniti Election Data API
FROM python:3.9-slim

LABEL maintainer="Rajniti Team <rajniti@example.com>"
LABEL description="Indian Election Data API - Comprehensive REST API for ECI data"
LABEL version="2.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        curl \
        postgresql-client \
        redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1001 app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8080

# Health check for container health monitoring
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/api/v2/elections/overview || exit 1

# Run application with Gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--worker-connections", "1000", \
     "--timeout", "30", \
     "--keep-alive", "2", \
     "--max-requests", "1000", \
     "--preload", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:create_app()"]
