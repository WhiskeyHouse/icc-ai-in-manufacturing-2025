"""
Pytest configuration file for the llama-index service tests.
Contains fixtures for setting up test environments.
"""

import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
import httpx
from fastapi.testclient import TestClient
import time
import logging
from urllib.parse import urlparse, parse_qs

# Import the application directly
from app.main import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if Docker is available and testcontainers should be used
try:
    import docker
    from testcontainers.postgres import PostgresContainer
    from testcontainers.redis import RedisContainer

    DOCKER_AVAILABLE = True
    try:
        client = docker.from_env()
        client.ping()  # Test connection
        logger.info("Docker is available, will use testcontainers")
    except Exception as e:
        logger.warning(f"Docker is installed but not available: {e}")
        DOCKER_AVAILABLE = False
except ImportError:
    logger.warning("testcontainers or docker package not available")
    DOCKER_AVAILABLE = False


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def _setup_mock_env():
    """Helper function to set mock environment variables for testing."""
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "5432"
    os.environ["DB_USER"] = "testuser"
    os.environ["DB_PASSWORD"] = "testpassword"
    os.environ["MES_DB_NAME"] = "testdb"

    # Also set vector DB variables
    os.environ["VECTOR_DB_HOST"] = "localhost"
    os.environ["VECTOR_DB_PORT"] = "5432"
    os.environ["VECTOR_DB_USER"] = "testuser"
    os.environ["VECTOR_DB_PASSWORD"] = "testpassword"
    os.environ["VECTOR_DB_NAME"] = "testdb"

    # Redis settings
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["REDIS_PASSWORD"] = ""


@pytest.fixture(scope="session")
def mock_db_env():
    """Set mock environment variables for database when Docker is not available."""
    _setup_mock_env()
    yield


@pytest.fixture(scope="session")
def postgres_container() -> Generator:
    """Start a PostgreSQL container for testing or use mock environment."""
    if DOCKER_AVAILABLE:
        try:
            # Custom image with pgvector extension would be better in real-world tests
            with PostgresContainer("postgres:12") as postgres:
                # Wait a bit for the container to be ready
                time.sleep(2)
                # Get connection details
                connection_url = postgres.get_connection_url()

                # Parse the connection URL to get the credentials
                # Format is typically: postgresql://username:password@host:port/database
                parsed_url = urlparse(connection_url)

                # Extract credentials from the connection URL
                host = postgres.get_container_host_ip()
                port = postgres.get_exposed_port(5432)
                user = parsed_url.username
                password = parsed_url.password
                database = parsed_url.path.lstrip("/")

                # Set environment variables for the test
                os.environ["DB_HOST"] = host
                os.environ["DB_PORT"] = str(port)
                os.environ["DB_USER"] = user
                os.environ["DB_PASSWORD"] = password
                os.environ["MES_DB_NAME"] = database

                # Also set vector DB variables to the same database (for simplicity in testing)
                os.environ["VECTOR_DB_HOST"] = host
                os.environ["VECTOR_DB_PORT"] = str(port)
                os.environ["VECTOR_DB_USER"] = user
                os.environ["VECTOR_DB_PASSWORD"] = password
                os.environ["VECTOR_DB_NAME"] = database

                yield postgres
        except Exception as e:
            logger.error(f"Failed to start PostgreSQL container: {e}")
            # Use mock environment instead
            _setup_mock_env()
            yield None
    else:
        # Use mock environment
        _setup_mock_env()
        yield None


@pytest.fixture(scope="session")
def redis_container() -> Generator:
    """Start a Redis container for testing or use mock environment."""
    if DOCKER_AVAILABLE:
        try:
            with RedisContainer("redis:7") as redis:
                # Wait a bit for the container to be ready
                time.sleep(2)
                # Set environment variables for the test
                os.environ["REDIS_HOST"] = redis.get_container_host_ip()
                os.environ["REDIS_PORT"] = str(redis.get_exposed_port(6379))
                os.environ["REDIS_PASSWORD"] = ""  # No password in test container

                yield redis
        except Exception as e:
            logger.error(f"Failed to start Redis container: {e}")
            # Redis variables already set in _setup_mock_env
            yield None
    else:
        # Redis variables already set in _setup_mock_env
        yield None


@pytest.fixture(scope="session")
def openai_api_key() -> Generator:
    """Set a dummy OpenAI API key for testing."""
    original_key = os.environ.get("OPENAI_API_KEY", "")
    os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key"
    yield
    # Restore the original key after tests
    if original_key:
        os.environ["OPENAI_API_KEY"] = original_key
    else:
        del os.environ["OPENAI_API_KEY"]


@pytest.fixture(scope="function")
def test_client(postgres_container, redis_container, openai_api_key) -> Generator:
    """
    Create a FastAPI TestClient that uses the test database.
    """
    # Set app config for testing
    os.environ["ENV"] = "test"
    os.environ["PRELOAD_INDEXES"] = "false"  # Don't preload indexes for faster tests
    os.environ["EMBED_MODEL"] = "text-embedding-ada-002"
    os.environ["DEFAULT_OPENAI_MODEL"] = "gpt-4o-mini"

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def setup_test_data(postgres_container):
    """Generate test data for the tests."""
    try:
        # Import the mock data generator
        import sys
        from tests.data.mock_data import generate_test_data

        # Check if we're using a real container or mock environment
        if postgres_container and DOCKER_AVAILABLE:
            # Get connection details from the container
            host = postgres_container.get_container_host_ip()
            port = postgres_container.get_exposed_port(5432)

            # Get database credentials - using environment variables as we set them above
            user = os.environ.get("DB_USER")
            password = os.environ.get("DB_PASSWORD")
            dbname = os.environ.get("MES_DB_NAME")
        else:
            # Using mock environment
            host = os.environ.get("DB_HOST", "localhost")
            port = os.environ.get("DB_PORT", "5432")
            user = os.environ.get("DB_USER", "testuser")
            password = os.environ.get("DB_PASSWORD", "testpassword")
            dbname = os.environ.get("MES_DB_NAME", "testdb")

        # Try to generate test data, but don't fail the test if it doesn't work
        try:
            generate_test_data(host, port, user, password, dbname)
            logger.info("Test data generated successfully")
        except Exception as e:
            logger.warning(f"Could not generate test data: {e}")
            # We'll continue with the tests anyway, they should handle missing data gracefully
    except ImportError:
        logger.warning("Could not import mock_data module, skipping data generation")

    yield
