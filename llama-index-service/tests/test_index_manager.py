"""
Tests for the IndexManager class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.core.index_manager import IndexManager


@pytest.mark.unit
def test_index_manager_singleton():
    """Test that IndexManager is a singleton."""
    # Get two instances of IndexManager
    instance1 = IndexManager.get_instance()
    instance2 = IndexManager.get_instance()

    # Both instances should be the same object
    assert instance1 is instance2


@pytest.mark.unit
def test_service_context_creation():
    """Test that service context is created correctly."""
    instance = IndexManager.get_instance()
    assert instance.service_context is not None


@pytest.mark.integration
def test_query_disabled_vector_store():
    """Test query method with disabled vector store."""
    instance = IndexManager.get_instance()

    # Test a query
    query_text = "What is the formula for water?"
    result = instance.query(query_text)

    # Since vector store is disabled, we expect a placeholder response
    assert result is not None
    assert "query" in result
    assert "response" in result
    assert "processing_time" in result
    assert "source_nodes" in result

    # Check the values
    assert result["query"] == query_text
    assert "disabled" in result["response"].lower()
    assert "compatibility" in result["response"].lower()
    assert len(result["source_nodes"]) == 0  # No source nodes with disabled store
    assert result["processing_time"] > 0


@pytest.mark.unit
def test_get_llm():
    """Test the get_llm method."""
    instance = IndexManager.get_instance()

    # Mock the OpenAI initialization to avoid actual API calls
    with patch("app.core.index_manager.OpenAI") as mock_openai:
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm

        # Test with default model
        llm = instance.get_llm()
        assert llm is mock_llm
        mock_openai.assert_called_once()

        # Reset the mock and test with specific model
        mock_openai.reset_mock()
        custom_model = "gpt-4o"
        llm = instance.get_llm(custom_model)
        assert llm is mock_llm
        mock_openai.assert_called_once()
        # Check that the model was passed correctly
        called_kwargs = mock_openai.call_args.kwargs
        assert called_kwargs.get("model") == custom_model
