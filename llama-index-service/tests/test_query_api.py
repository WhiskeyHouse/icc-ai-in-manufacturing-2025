"""
Tests for the RAG query API endpoints.
"""

import pytest
from fastapi import status


@pytest.mark.integration
def test_query_endpoint_exists(test_client):
    """Test that the query endpoint exists and accepts POST requests."""
    payload = {
        "query": "What is the meaning of life?",
        "model": "gpt-4o-mini",  # Use a valid model name
    }
    response = test_client.post("/api/v1/query", json=payload)
    assert response.status_code in (status.HTTP_200_OK, status.HTTP_202_ACCEPTED)

    # Since vector store is disabled, we expect a message about it
    response_data = response.json()
    assert "query" in response_data
    assert "response" in response_data
    assert "processing_time" in response_data
    assert payload["query"] == response_data["query"]
    # We're expecting the vector store disabled message
    assert "disabled" in response_data["response"].lower()
    assert "compatibility" in response_data["response"].lower()


@pytest.mark.integration
def test_query_endpoint_bad_request(test_client):
    """Test that the query endpoint returns 422 for invalid requests."""
    # Missing required query field
    payload = {
        "model": "gpt-4o-mini",
    }
    response = test_client.post("/api/v1/query", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_table_query_endpoint(test_client):
    """Test the table-specific query endpoint."""
    payload = {
        "query": "Show me Recipe information",
        "model": "gpt-4o-mini",
    }
    response = test_client.post("/api/v1/query/Recipe", json=payload)
    assert response.status_code in (status.HTTP_200_OK, status.HTTP_202_ACCEPTED)

    # Check response format
    response_data = response.json()
    assert "query" in response_data
    assert "response" in response_data
    assert payload["query"] == response_data["query"]
