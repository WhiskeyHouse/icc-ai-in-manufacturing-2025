"""
Tests for the embedding model configuration.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.core.index_manager import IndexManager
from llama_index.embeddings.openai import OpenAIEmbedding


@pytest.mark.unit
def test_embed_model_configuration():
    """Test that the embedding model is configured correctly."""
    # Get IndexManager instance
    instance = IndexManager.get_instance()

    # Check that the service context has the correct embedding model
    assert instance.service_context is not None
    assert instance.service_context.embed_model is not None

    # Check the type of the embedding model
    assert isinstance(instance.service_context.embed_model, OpenAIEmbedding)


@pytest.mark.unit
def test_embed_model_using_correct_model():
    """Test that the embedding model is using the correct model."""
    # Get IndexManager instance
    instance = IndexManager.get_instance()

    # Extract the embedding model
    embed_model = instance.service_context.embed_model

    # Check the model name - the newer OpenAIEmbedding uses model_name instead of model
    assert hasattr(embed_model, "model_name")
    assert embed_model.model_name == "text-embedding-ada-002"


@pytest.mark.integration
def test_embedding_model_basic_configuration():
    """Test that the embedding model has the correct basic configuration."""
    # Get IndexManager instance
    instance = IndexManager.get_instance()

    # Extract the embedding model
    embed_model = instance.service_context.embed_model

    # Check basic properties of the embedding model
    assert hasattr(embed_model, "model_name")
    assert embed_model.model_name == "text-embedding-ada-002"

    # Check dimensions
    assert hasattr(embed_model, "dimensions")
    assert embed_model.dimensions == 1536  # Ada-002 produces 1536-dimensional vectors
