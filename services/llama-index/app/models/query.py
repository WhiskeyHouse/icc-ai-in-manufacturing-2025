from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for the query endpoint"""

    query: str = Field(..., description="The query text to process")
    model: Optional[str] = Field(None, description="OpenAI model to use for the query")
    table_name: Optional[str] = Field(None, description="Specific table to query")
    similarity_top_k: Optional[int] = Field(
        5, description="Number of similar documents to retrieve"
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "What are the steps in the mashing process for rye bourbon?",
                "model": "gpt-4o-mini",
                "table_name": None,
                "similarity_top_k": 5,
            }
        }


class SourceNode(BaseModel):
    """Model for a source node in a query response"""

    text: str = Field(..., description="The text of the source document")
    score: Optional[float] = Field(None, description="Similarity score")
    metadata: Dict[str, Any] = Field({}, description="Metadata for the source document")


class QueryResponse(BaseModel):
    """Response model for the query endpoint"""

    query: str = Field(..., description="The original query text")
    response: str = Field(..., description="The generated response")
    source_nodes: List[SourceNode] = Field(
        [], description="Source documents used for the response"
    )
    model: str = Field(..., description="The model used for the query")
    processing_time: float = Field(
        ..., description="Time taken to process the query in seconds"
    )
    error: Optional[str] = Field(None, description="Error message if the query failed")


class HealthResponse(BaseModel):
    """Response model for the health endpoint"""

    status: str = Field(..., description="Health status of the service")
    version: str = Field(..., description="Service version")
    database_connected: bool = Field(
        ..., description="Status of the database connection"
    )
    redis_connected: bool = Field(..., description="Status of the Redis connection")
    available_tables: List[str] = Field(
        [], description="List of available tables for querying"
    )


class TablesResponse(BaseModel):
    """Response model for the available tables endpoint"""

    tables: List[str] = Field(..., description="List of available tables for querying")


class IndexRequest(BaseModel):
    """Request model for the index endpoint"""

    force_reindex: bool = Field(
        False,
        description="Whether to force reindex even if the table is already indexed",
    )


class IndexResponse(BaseModel):
    """Response model for the index endpoint"""

    success: bool = Field(..., description="Whether the indexing was successful")
    message: str = Field(
        ..., description="Description of the indexing operation result"
    )
    table_name: Optional[str] = Field(None, description="The name of the indexed table")
    tables_indexed: List[str] = Field(
        [], description="List of tables that were indexed"
    )
    processing_time: float = Field(
        ..., description="Time taken to process the indexing in seconds"
    )
    error: Optional[str] = Field(
        None, description="Error message if the indexing failed"
    )
