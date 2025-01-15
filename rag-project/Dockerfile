FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the scheduler
CMD ["python", "-m", "src.processing.run_characters"] 