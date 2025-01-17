FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ src/
COPY .env .env

# Create data directories
RUN mkdir -p data/transcripts data/processed

# Set Python path to recognize our modules
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8001

# Run the FastAPI service with reload and trace-level logging
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--log-level=trace", "--access-log", "--use-colors"] 