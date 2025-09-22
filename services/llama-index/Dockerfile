FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies with explicit pip upgrade
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt && \
  pip install --no-cache-dir pydantic==1.10.13 psycopg2-binary==2.9.9 llama-index-vector-stores-postgres

# Create storage directory
RUN mkdir -p /app/storage

# Copy the application
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"] 