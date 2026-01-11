# VendorAuditAI - Unified Docker Container
# Multi-stage build: React frontend + FastAPI backend

# ============================================
# Stage 1: Build React frontend
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package*.json ./
RUN npm ci --silent

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# ============================================
# Stage 2: Python backend with embedded frontend
# ============================================
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini .

# Copy frontend build from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./static

# Create required directories
RUN mkdir -p /app/uploads /app/data

# Environment defaults
ENV PORT=8000
ENV STATIC_FILES_DIR=/app/static
ENV LOCAL_STORAGE_PATH=/app/uploads
ENV APP_ENV=production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
