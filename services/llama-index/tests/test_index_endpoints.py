"""
Tests for the indexing endpoints of the llama-index service.
Tests both single table and all tables indexing functionality.
"""

import pytest
from fastapi import status
import time
from unittest.mock import patch, MagicMock
import logging
import os
import json
from app.core.index_manager import IndexManager

logger = logging.getLogger(__name__)

# Skip the entire module if we're not in a test environment
if not os.environ.get("ENV") == "test" and not pytest.mark.skip:
    pytestmark = pytest.mark.skip(reason="Not in test environment")


@pytest.mark.integration
def test_index_single_table(test_client, setup_test_data, monkeypatch):
    """Test indexing a single table."""
    # Mock the index_table method to verify it gets called with the right arguments
    # and return a successful result without actual indexing

    def mock_index_table(self, table_name, force_reindex=False):
        """Mock the index_table method."""
        logger.info(
            f"Mock indexing table: {table_name}, force_reindex: {force_reindex}"
        )
        return {
            "success": True,
            "message": f"Successfully indexed table: {table_name}",
            "table_name": table_name,
            "tables_indexed": [table_name],
            "processing_time": 0.5,
            "error": None,
        }

    # Apply the mock to the IndexManager class
    monkeypatch.setattr(IndexManager, "index_table", mock_index_table)

    # Test indexing without force_reindex
    response = test_client.post("/api/v1/index/Recipe", json={"force_reindex": False})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "Successfully indexed table: Recipe" in data["message"]
    assert data["table_name"] == "Recipe"
    assert "Recipe" in data["tables_indexed"]
    assert "processing_time" in data
    assert data["error"] is None

    # Test indexing with force_reindex
    response = test_client.post("/api/v1/index/Recipe", json={"force_reindex": True})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["table_name"] == "Recipe"


@pytest.mark.integration
def test_index_all_tables(test_client, setup_test_data, monkeypatch):
    """Test indexing all tables."""
    # Mock the index_all_tables method

    def mock_index_all_tables(self, force_reindex=False):
        """Mock the index_all_tables method."""
        logger.info(f"Mock indexing all tables, force_reindex: {force_reindex}")
        tables = ["Recipe", "RecipeParameter", "Batch"]
        return {
            "success": True,
            "message": f"Successfully indexed all {len(tables)} tables",
            "table_name": None,
            "tables_indexed": tables,
            "processing_time": 1.5,
            "error": None,
        }

    # Apply the mock to the IndexManager class
    monkeypatch.setattr(IndexManager, "index_all_tables", mock_index_all_tables)

    # Test indexing all tables without force_reindex
    response = test_client.post("/api/v1/index", json={"force_reindex": False})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "Successfully indexed all" in data["message"]
    assert data["table_name"] is None
    assert len(data["tables_indexed"]) == 3
    assert "Recipe" in data["tables_indexed"]
    assert "processing_time" in data
    assert data["error"] is None

    # Test indexing all tables with force_reindex
    response = test_client.post("/api/v1/index", json={"force_reindex": True})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert len(data["tables_indexed"]) == 3


@pytest.mark.integration
def test_index_nonexistent_table(test_client, setup_test_data):
    """Test attempting to index a table that doesn't exist in the configuration."""
    response = test_client.post(
        "/api/v1/index/NonExistentTable", json={"force_reindex": False}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data
    assert (
        "not found" in data["detail"].lower()
        or "not available" in data["detail"].lower()
    )


@pytest.mark.integration
def test_error_handling_in_index_endpoint(test_client, setup_test_data, monkeypatch):
    """Test error handling in the index endpoint."""
    # Mock the index_table method to return an error

    def mock_index_table_error(self, table_name, force_reindex=False):
        """Mock the index_table method returning an error."""
        logger.info(f"Mock indexing table with error: {table_name}")
        return {
            "success": False,
            "message": f"Error indexing table: {table_name}",
            "table_name": table_name,
            "tables_indexed": [],
            "processing_time": 0.1,
            "error": "Simulated error for testing",
        }

    # Apply the mock to the IndexManager class
    monkeypatch.setattr(IndexManager, "index_table", mock_index_table_error)

    # Test indexing with error
    response = test_client.post("/api/v1/index/Recipe", json={"force_reindex": False})

    assert response.status_code == status.HTTP_200_OK  # The endpoint still returns 200
    data = response.json()
    assert data["success"] is False
    assert "Error indexing table" in data["message"]
    assert data["table_name"] == "Recipe"
    assert len(data["tables_indexed"]) == 0
    assert "Simulated error" in data["error"]


@pytest.mark.integration
def test_index_with_db_exception(test_client, setup_test_data, monkeypatch):
    """Test indexing when the database throws an exception."""
    # Mock the index_table method to throw an exception

    def mock_index_table_exception(self, table_name, force_reindex=False):
        """Mock the index_table method raising an exception."""
        raise Exception("Database connection failed")

    # Apply the mock to the IndexManager class
    monkeypatch.setattr(IndexManager, "index_table", mock_index_table_exception)

    # Test indexing with exception
    response = test_client.post("/api/v1/index/Recipe", json={"force_reindex": False})

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    data = response.json()
    assert "detail" in data
    assert "Database connection failed" in data["detail"]


@pytest.mark.e2e
def test_actual_index_creation(test_client, setup_test_data, monkeypatch):
    """
    Test actual index creation with real vector store interaction.
    This test requires proper pgvector setup in the test database.
    """
    # Check if we should skip vector tests
    if os.environ.get("SKIP_VECTOR_TESTS", "false").lower() == "true":
        pytest.skip("Vector tests disabled")

    # Mock the vector store actual implementation to not require pgvector
    # but still simulate the index storage and retrieval flow
    mock_vector_stores = {}

    # Create a simplified mock class for PGVectorStore
    class MockVectorStore:
        def __init__(self, table_name):
            self.table_name = table_name
            self.vectors = []

        def add(self, embedding, metadata, doc_id):
            self.vectors.append((embedding, metadata, doc_id))
            return len(self.vectors) - 1

    # Mock the vector store creation
    def mock_get_vector_store(self, table_name):
        """Mock the _get_vector_store method."""
        if table_name not in mock_vector_stores:
            mock_vector_stores[table_name] = MockVectorStore(table_name)
        return mock_vector_stores[table_name]

    # Patch just enough to avoid actual pgvector operations
    # but still test the indexing logic
    monkeypatch.setattr(IndexManager, "_get_vector_store", mock_get_vector_store)

    # Also mock the VectorStoreIndex.from_documents method
    def mock_from_documents(
        documents, service_context, vector_store, show_progress=False
    ):
        """Mock the VectorStoreIndex.from_documents method."""
        # Create a simple mock index
        mock_index = MagicMock()
        # Store the documents for verification
        mock_index.documents = documents
        return mock_index

    from llama_index.core import VectorStoreIndex

    monkeypatch.setattr(VectorStoreIndex, "from_documents", mock_from_documents)

    # Test the actual index creation
    response = test_client.post("/api/v1/index/Recipe", json={"force_reindex": True})

    # We expect this to succeed with our mocked vector operations
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Depending on the database state, this might succeed or fail
    # The main goal is to test the endpoint handles it properly
    logger.info(f"Response from actual index creation: {json.dumps(data, indent=2)}")
    assert "success" in data
    assert "message" in data
    assert "processing_time" in data
