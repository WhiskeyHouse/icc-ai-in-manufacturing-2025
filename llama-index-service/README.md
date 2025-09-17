# Llama Index RAG Service

A microservice for Retrieval-Augmented Generation (RAG) using LlamaIndex and OpenAI.

## Overview

This service provides an API for querying data from a PostgreSQL database using natural language. It uses LlamaIndex to create and manage vector embeddings of the data, enabling semantic search and retrieval.

## Features

- REST API for querying data using natural language
- Integration with PostgreSQL for data storage
- Vector embeddings using OpenAI's embedding models
- Caching of results with Redis
- Support for querying specific tables or global data
- Health check endpoint

## Requirements

- Python 3.11+
- PostgreSQL 12+ with pgvector extension
- Redis 7+
- OpenAI API key

## Installation

### Using Docker

```bash
# Build the Docker image
docker-compose build llama-index-service

# Start the service
docker-compose up -d llama-index-service
```

### Local Development

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key"
export ENV="development"

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `DEFAULT_OPENAI_MODEL` | Default OpenAI model for queries | `gpt-4o-mini` |
| `EMBED_MODEL` | Embedding model | `text-embedding-ada-002` |
| `DB_HOST` | PostgreSQL host | `db` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_USER` | PostgreSQL username | `admin` |
| `DB_PASSWORD` | PostgreSQL password | `admin` |
| `MES_DB_NAME` | Main database name | `whk-mes` |
| `VECTOR_DB_HOST` | Vector database host | Same as `DB_HOST` |
| `VECTOR_DB_PORT` | Vector database port | Same as `DB_PORT` |
| `VECTOR_DB_USER` | Vector database username | Same as `DB_USER` |
| `VECTOR_DB_PASSWORD` | Vector database password | Same as `DB_PASSWORD` |
| `VECTOR_DB_NAME` | Vector database name | `whk_vectors` |
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_PASSWORD` | Redis password | - |
| `REDIS_TTL` | Redis cache TTL in seconds | `5000` |
| `PRELOAD_INDEXES` | Whether to preload indexes at startup | `true` |
| `ENV` | Environment | `development` |

## API Endpoints

### Health Check

```
GET /health
```

Returns a simple health check status.

### General Query

```
POST /api/v1/query
```

Body:
```json
{
  "query": "What is the recipe for bourbon whiskey?",
  "model": "gpt-4o-mini",
  "similarity_top_k": 5
}
```

### Table-Specific Query

```
POST /api/v1/query/{table_name}
```

Body:
```json
{
  "query": "What are the parameters for the bourbon whiskey recipe?",
  "model": "gpt-4o-mini",
  "similarity_top_k": 5
}
```

## Running Tests

The service comes with a comprehensive test suite covering unit tests, integration tests, and end-to-end tests.

### Using Docker

```bash
# Build and run tests in a container
docker build -f Dockerfile.test -t llama-index-service-test .
docker run llama-index-service-test
```

### Using Docker Compose for Integration Tests

```bash
# Start the test environment with all dependencies
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

### Local Testing

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m slow

# Run with coverage report
pytest --cov=app --cov-report=term-missing
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test complete workflows from API request to response
- **Performance Tests**: Benchmark API response times and throughput

### Mock Data

The test suite includes a mock data generator that creates sample data for testing:

```bash
# Generate test data manually
python -m tests.data.mock_data
```

## Debugging

The service logs information to stdout. When running in a Docker container, you can view the logs with:

```bash
docker-compose logs -f llama-index-service
```

## License

This project is licensed under the MIT License. 