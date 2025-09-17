"""
Tests for the health check endpoint and basic API functionality.
"""

import pytest
from fastapi import status


@pytest.mark.integration
def test_health_endpoint(test_client):
    """Test that the health endpoint returns a 200 status code."""
    response = test_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


@pytest.mark.integration
def test_api_version_endpoint(test_client):
    """Test that the API version endpoint is accessible."""
    # Use the tables endpoint which should be accessible
    response = test_client.get("/api/v1/tables")
    assert response.status_code == status.HTTP_200_OK
    # Check that the response contains tables information
    assert "tables" in response.json()
