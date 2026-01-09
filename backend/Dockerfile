FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Set default PORT (Railway overrides this)
ENV PORT=8000

# Expose port
EXPOSE $PORT

# Run the application using shell form to expand $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
