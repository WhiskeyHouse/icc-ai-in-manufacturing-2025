"""
Tests for the indexing methods of the IndexManager class.
These tests focus on the internal logic of the indexing methods,
complementing the API endpoint tests.
"""

import pytest
import time
import os
from unittest.mock import patch, MagicMock, mock_open
import logging
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.core.index_manager import IndexManager

logger = logging.getLogger(__name__)

# Skip the entire module if we're not in a test environment
if not os.environ.get("ENV") == "test" and not pytest.mark.skip:
    pytestmark = pytest.mark.skip(reason="Not in test environment")


@pytest.fixture
def mock_db_connection(monkeypatch):
    """Mock database connection for testing."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Mock fetchall to return some test data
    mock_cursor.fetchall.return_value = [
        (1, "Bourbon Whiskey", "Classic Kentucky bourbon"),
        (2, "Rye Whiskey", "Spicy rye whiskey"),
    ]

    # Mock description to provide column names
    mock_cursor.description = [
        ("id", None, None, None, None, None, None),
        ("name", None, None, None, None, None, None),
        ("description", None, None, None, None, None, None),
    ]

    # Mock the psycopg2.connect function
    def mock_connect(*args, **kwargs):
        return mock_conn

    monkeypatch.setattr(psycopg2, "connect", mock_connect)
    return mock_conn


@pytest.mark.unit
def test_fetch_table_data(mock_db_connection, monkeypatch):
    """Test the _fetch_table_data method."""
    # Create an instance of IndexManager
    manager = IndexManager.get_instance()

    # Call the method being tested
    result = manager._fetch_table_data("Recipe")

    # Verify that connect was called with the right arguments
    psycopg2.connect.assert_called_once()

    # Verify that execute was called with the right SQL
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.execute.assert_called_once_with('SELECT * FROM "Recipe" LIMIT 1000')

    # Verify that fetchall was called
    mock_cursor.fetchall.assert_called_once()

    # Verify the result data structure
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["name"] == "Bourbon Whiskey"
    assert result[0]["description"] == "Classic Kentucky bourbon"
    assert result[1]["id"] == 2
    assert result[1]["name"] == "Rye Whiskey"
    assert result[1]["description"] == "Spicy rye whiskey"


@pytest.mark.unit
def test_index_table(monkeypatch):
    """Test the index_table method."""
    # Create an instance of IndexManager
    manager = IndexManager.get_instance()

    # Mock dependencies to isolate the unit test
    # 1. Mock _fetch_table_data
    def mock_fetch_table_data(self, table_name):
        return [
            {
                "id": 1,
                "name": "Bourbon Whiskey",
                "description": "Classic Kentucky bourbon",
            },
            {"id": 2, "name": "Rye Whiskey", "description": "Spicy rye whiskey"},
        ]

    monkeypatch.setattr(IndexManager, "_fetch_table_data", mock_fetch_table_data)

    # 2. Mock _get_vector_store
    mock_vector_store = MagicMock()

    def mock_get_vector_store(self, table_name):
        return mock_vector_store

    monkeypatch.setattr(IndexManager, "_get_vector_store", mock_get_vector_store)

    # 3. Mock VectorStoreIndex.from_documents
    mock_index = MagicMock()

    def mock_from_documents(documents, service_context, vector_store, show_progress):
        return mock_index

    from llama_index.core import VectorStoreIndex

    monkeypatch.setattr(VectorStoreIndex, "from_documents", mock_from_documents)

    # Call the method being tested
    result = manager.index_table("Recipe", force_reindex=True)

    # Verify the results
    assert result["success"] is True
    assert "Successfully indexed table: Recipe" in result["message"]
    assert result["table_name"] == "Recipe"
    assert result["tables_indexed"] == ["Recipe"]
    assert result["processing_time"] > 0
    assert result["error"] is None


@pytest.mark.unit
def test_index_table_no_data(monkeypatch):
    """Test the index_table method when no data is found."""
    # Create an instance of IndexManager
    manager = IndexManager.get_instance()

    # Mock dependencies to isolate the unit test
    # 1. Mock _fetch_table_data to return empty list
    def mock_fetch_table_data(self, table_name):
        return []

    monkeypatch.setattr(IndexManager, "_fetch_table_data", mock_fetch_table_data)

    # 2. Mock _get_vector_store
    mock_vector_store = MagicMock()

    def mock_get_vector_store(self, table_name):
        return mock_vector_store

    monkeypatch.setattr(IndexManager, "_get_vector_store", mock_get_vector_store)

    # Call the method being tested
    result = manager.index_table("Recipe", force_reindex=False)

    # Verify the results
    assert result["success"] is False
    assert "No data found in table 'Recipe'" in result["message"]
    assert result["table_name"] == "Recipe"
    assert len(result["tables_indexed"]) == 0
    assert result["processing_time"] > 0
    assert result["error"] is not None


@pytest.mark.unit
def test_index_table_invalid_table(monkeypatch):
    """Test the index_table method with an invalid table name."""
    # Create an instance of IndexManager
    manager = IndexManager.get_instance()

    # Modify settings.TABLES_TO_INDEX for this test
    from app.core.config import settings

    original_tables = settings.TABLES_TO_INDEX
    settings.TABLES_TO_INDEX = ["Recipe", "Batch"]

    # Call the method being tested with a non-existent table
    result = manager.index_table("NonExistentTable", force_reindex=False)

    # Restore original settings
    settings.TABLES_TO_INDEX = original_tables

    # Verify the results
    assert result["success"] is False
    assert "not in the list of tables to index" in result["message"]
    assert result["table_name"] == "NonExistentTable"
    assert len(result["tables_indexed"]) == 0
    assert result["processing_time"] > 0
    assert result["error"] is not None


@pytest.mark.unit
def test_index_all_tables(monkeypatch):
    """Test the index_all_tables method."""
    # Create an instance of IndexManager
    manager = IndexManager.get_instance()

    # Mock the index_table method to track calls and return success
    mock_results = {}

    def mock_index_table(self, table_name, force_reindex=False):
        mock_results[table_name] = {"force_reindex": force_reindex}
        return {
            "success": True,
            "message": f"Successfully indexed table: {table_name}",
            "table_name": table_name,
            "tables_indexed": [table_name],
            "processing_time": 0.1,
            "error": None,
        }

    monkeypatch.setattr(IndexManager, "index_table", mock_index_table)

    # Mock the _load_or_create_global_index method
    mock_global_index = MagicMock()

    def mock_load_or_create_global_index(self):
        return mock_global_index

    monkeypatch.setattr(
        IndexManager, "_load_or_create_global_index", mock_load_or_create_global_index
    )

    # Modify settings.TABLES_TO_INDEX for a smaller test set
    from app.core.config import settings

    original_tables = settings.TABLES_TO_INDEX
    settings.TABLES_TO_INDEX = ["Recipe", "Batch", "RecipeParameter"]

    # Call the method being tested
    result = manager.index_all_tables(force_reindex=True)

    # Restore original settings
    settings.TABLES_TO_INDEX = original_tables

    # Verify the results
    assert result["success"] is True
    assert "Successfully indexed all" in result["message"]
    assert result["table_name"] is None
    assert len(result["tables_indexed"]) == 3
    assert "Recipe" in result["tables_indexed"]
    assert "Batch" in result["tables_indexed"]
    assert "RecipeParameter" in result["tables_indexed"]
    assert result["processing_time"] > 0
    assert result["error"] is None

    # Verify that index_table was called for each table
    assert len(mock_results) == 3
    assert "Recipe" in mock_results
    assert "Batch" in mock_results
    assert "RecipeParameter" in mock_results
    assert mock_results["Recipe"]["force_reindex"] is True
    assert mock_results["Batch"]["force_reindex"] is True
    assert mock_results["RecipeParameter"]["force_reindex"] is True


@pytest.mark.unit
def test_index_all_tables_partial_failure(monkeypatch):
    """Test the index_all_tables method with some table failures."""
    # Create an instance of IndexManager
    manager = IndexManager.get_instance()

    # Mock the index_table method to return success for some tables and failure for others
    def mock_index_table(self, table_name, force_reindex=False):
        if table_name == "Recipe":
            return {
                "success": True,
                "message": f"Successfully indexed table: {table_name}",
                "table_name": table_name,
                "tables_indexed": [table_name],
                "processing_time": 0.1,
                "error": None,
            }
        else:
            return {
                "success": False,
                "message": f"Error indexing table: {table_name}",
                "table_name": table_name,
                "tables_indexed": [],
                "processing_time": 0.1,
                "error": f"Mock error for {table_name}",
            }

    monkeypatch.setattr(IndexManager, "index_table", mock_index_table)

    # Mock the _load_or_create_global_index method
    mock_global_index = MagicMock()

    def mock_load_or_create_global_index(self):
        return mock_global_index

    monkeypatch.setattr(
        IndexManager, "_load_or_create_global_index", mock_load_or_create_global_index
    )

    # Modify settings.TABLES_TO_INDEX for a smaller test set
    from app.core.config import settings

    original_tables = settings.TABLES_TO_INDEX
    settings.TABLES_TO_INDEX = ["Recipe", "Batch", "RecipeParameter"]

    # Call the method being tested
    result = manager.index_all_tables(force_reindex=False)

    # Restore original settings
    settings.TABLES_TO_INDEX = original_tables

    # Verify the results
    assert result["success"] is True  # Still True because at least one table succeeded
    assert "tables with" in result["message"]
    assert "failures" in result["message"]
    assert result["table_name"] is None
    assert len(result["tables_indexed"]) == 1
    assert "Recipe" in result["tables_indexed"]
    assert "Batch" not in result["tables_indexed"]
    assert "RecipeParameter" not in result["tables_indexed"]
    assert result["processing_time"] > 0
    assert result["error"] is not None
    assert "Batch" in result["error"]
    assert "RecipeParameter" in result["error"]
