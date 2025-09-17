"""
Tests for database connections and configuration.
"""

import pytest
import psycopg2
from app.core.config import settings
from app.utils.db_check import check_postgres_connection
from app.core.index_manager import get_redis_client


@pytest.mark.integration
def test_postgres_connection(postgres_container):
    """Test that we can connect to PostgreSQL."""
    # The host and port should be set by the fixture
    assert check_postgres_connection() is True

    # Try to create a direct connection
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        dbname=settings.MES_DB_NAME,
    )
    assert conn is not None
    conn.close()


@pytest.mark.integration
def test_redis_connection(redis_container):
    """Test that we can connect to Redis."""
    # Create a Redis client
    redis_client = get_redis_client()

    # Basic functionality test
    test_key = "test_key"
    test_value = "test_value"
    redis_client.set(test_key, test_value)
    retrieved_value = redis_client.get(test_key)

    assert retrieved_value == test_value

    # Clean up
    redis_client.delete(test_key)


@pytest.mark.integration
def test_vector_db_connection(postgres_container):
    """Test that we can connect to the vector database."""
    # The vector database is the same as the regular database in our test setup
    conn = psycopg2.connect(
        host=settings.VECTOR_DB_HOST,
        port=settings.VECTOR_DB_PORT,
        user=settings.VECTOR_DB_USER,
        password=settings.VECTOR_DB_PASSWORD,
        dbname=settings.VECTOR_DB_NAME,
    )
    assert conn is not None

    # Check if we can create a table (basic operation)
    cursor = conn.cursor()

    # Drop the test table if it exists
    cursor.execute("DROP TABLE IF EXISTS test_vector_table")

    # Create a simple test table
    cursor.execute(
        """
        CREATE TABLE test_vector_table (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        )
    """
    )

    # Insert some data
    cursor.execute(
        "INSERT INTO test_vector_table (name) VALUES (%s) RETURNING id", ("Test Item",)
    )

    # Commit and clean up
    conn.commit()
    cursor.close()
    conn.close()
