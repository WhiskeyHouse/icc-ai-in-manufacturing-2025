import logging
import time
from typing import Dict, List, Any, Optional
import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, status, Path
import redis
import sqlalchemy as sa

from app.core.config import settings
from app.core.index_manager import IndexManager, get_redis_client
from app.models.query import (
    QueryRequest,
    QueryResponse,
    HealthResponse,
    TablesResponse,
    IndexRequest,
    IndexResponse,
)
from app.utils.db_check import check_postgres_connection

logger = logging.getLogger(__name__)

api_router = APIRouter()


@api_router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query(request: QueryRequest):
    """
    Query the RAG system to get information from the manufacturing database.
    """
    try:
        logger.info(f"Processing query: {request.query}")
        # Get the IndexManager instance
        index_manager = IndexManager.get_instance()

        # Execute the query
        result = index_manager.query(
            query_text=request.query,
            model_name=request.model,
            table_name=request.table_name,
            similarity_top_k=request.similarity_top_k or 5,
        )

        logger.info(
            f"Query processed successfully in {result.get('processing_time', 0):.2f} seconds"
        )
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}",
        )


@api_router.post(
    "/query/{table_name}", response_model=QueryResponse, status_code=status.HTTP_200_OK
)
async def query_table(
    table_name: str = Path(..., description="The name of the table to query"),
    request: QueryRequest = None,
):
    """
    Query the RAG system for information from a specific table in the manufacturing database.
    """
    if not request:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Request body is required",
        )

    # Validate that the table exists in our known tables
    if table_name not in settings.TABLES_TO_INDEX:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' not found or not available for querying",
        )

    try:
        logger.info(f"Processing query for table {table_name}: {request.query}")
        # Get the IndexManager instance
        index_manager = IndexManager.get_instance()

        # Override table_name in the request with the path parameter
        request_with_table = request.dict()
        request_with_table["table_name"] = table_name

        # Execute the query
        result = index_manager.query(
            query_text=request.query,
            model_name=request.model,
            table_name=table_name,
            similarity_top_k=request.similarity_top_k or 5,
        )

        logger.info(
            f"Table-specific query processed successfully in {result.get('processing_time', 0):.2f} seconds"
        )
        return result
    except Exception as e:
        logger.error(f"Error processing table-specific query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}",
        )


@api_router.post("/index", response_model=IndexResponse, status_code=status.HTTP_200_OK)
async def index_all_tables(request: IndexRequest = None):
    """
    Index all tables in the database.
    """
    try:
        force_reindex = False
        if request and hasattr(request, "force_reindex"):
            force_reindex = request.force_reindex

        logger.info(f"Starting indexing for all tables, force_reindex={force_reindex}")

        # Get the IndexManager instance
        index_manager = IndexManager.get_instance()

        # Execute the indexing operation
        result = index_manager.index_all_tables(force_reindex=force_reindex)

        logger.info(
            f"Indexing completed in {result.get('processing_time', 0):.2f} seconds"
        )

        return result
    except Exception as e:
        logger.error(f"Error indexing all tables: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing all tables: {str(e)}",
        )


@api_router.post(
    "/index/{table_name}", response_model=IndexResponse, status_code=status.HTTP_200_OK
)
async def index_table(
    table_name: str = Path(..., description="The name of the table to index"),
    request: IndexRequest = None,
):
    """
    Index a specific table in the database.
    """
    # Validate that the table exists in our known tables
    if table_name not in settings.TABLES_TO_INDEX:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' not found or not available for indexing",
        )

    try:
        force_reindex = False
        if request and hasattr(request, "force_reindex"):
            force_reindex = request.force_reindex

        logger.info(
            f"Starting indexing for table {table_name}, force_reindex={force_reindex}"
        )

        # Get the IndexManager instance
        index_manager = IndexManager.get_instance()

        # Execute the indexing operation
        result = index_manager.index_table(
            table_name=table_name, force_reindex=force_reindex
        )

        logger.info(
            f"Table indexing completed in {result.get('processing_time', 0):.2f} seconds"
        )

        return result
    except Exception as e:
        logger.error(f"Error indexing table {table_name}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing table: {str(e)}",
        )


@api_router.get("/health", response_model=HealthResponse)
async def health():
    """
    Check the health of the RAG service and its dependencies.
    """
    start_time = time.time()

    db_connected = False
    redis_connected = False
    available_tables = []

    # Check database connection
    try:
        db_connected = check_postgres_connection()
        available_tables = settings.TABLES_TO_INDEX
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")

    # Check Redis connection
    try:
        redis_client = get_redis_client()
        redis_connected = redis_client.ping()
    except Exception as e:
        logger.warning(f"Redis connection check failed: {e}")

    return {
        "status": "healthy" if (db_connected and redis_connected) else "degraded",
        "version": "1.0.0",
        "database_connected": db_connected,
        "redis_connected": redis_connected,
        "available_tables": available_tables,
    }


@api_router.get("/tables", response_model=TablesResponse)
async def get_available_tables():
    """
    Get a list of available tables that can be queried.
    """
    return {"tables": settings.TABLES_TO_INDEX}


@api_router.post(
    "/test_vector_store", response_model=Dict[str, Any], status_code=status.HTTP_200_OK
)
async def test_vector_store():
    """
    Test the vector store setup by creating and querying a test record.
    """
    try:
        logger.info("Testing vector store setup...")

        # Get the IndexManager instance
        index_manager = IndexManager.get_instance()

        # Execute the test
        result = index_manager.test_vector_store()

        logger.info(
            f"Vector store test completed in {result.get('processing_time', 0):.2f} seconds"
        )

        return result
    except Exception as e:
        logger.error(f"Error testing vector store: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing vector store: {str(e)}",
        )


@api_router.get(
    "/debug/pgvector", response_model=Dict[str, Any], status_code=status.HTTP_200_OK
)
async def check_pgvector():
    """
    Check if the pgvector extension is properly installed.
    """
    try:
        logger.info("Checking pgvector extension...")

        # Get the IndexManager instance
        index_manager = IndexManager.get_instance()

        # URL encode the password to handle special characters
        password_encoded = urllib.parse.quote_plus(settings.VECTOR_DB_PASSWORD)
        conn_str = f"postgresql://{settings.VECTOR_DB_USER}:{password_encoded}@{settings.VECTOR_DB_HOST}:{settings.VECTOR_DB_PORT}/{settings.VECTOR_DB_NAME}"

        debug_info = {}

        # Check if pgvector extension is installed
        try:
            with sa.create_engine(conn_str).connect() as connection:
                # Check installed extensions
                result = connection.execute(
                    sa.text("SELECT extname, extversion FROM pg_extension")
                ).fetchall()
                debug_info["extensions"] = [
                    {"name": ext[0], "version": ext[1]} for ext in result
                ]

                # Check if pgvector is installed
                vector_result = connection.execute(
                    sa.text(
                        "SELECT EXISTS (SELECT FROM pg_extension WHERE extname = 'vector')"
                    )
                ).scalar()
                debug_info["pgvector_installed"] = vector_result

                # Try to create a small test vector
                try:
                    connection.execute(sa.text("SELECT '[1,2,3]'::vector"))
                    debug_info["vector_test"] = "success"
                except Exception as e:
                    debug_info["vector_test"] = f"failed: {str(e)}"

                # List available tables
                tables = connection.execute(
                    sa.text(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                    )
                ).fetchall()
                debug_info["tables"] = [table[0] for table in tables]

                return {
                    "success": vector_result,
                    "debug_info": debug_info,
                    "message": (
                        "pgvector is properly installed"
                        if vector_result
                        else "pgvector is NOT installed"
                    ),
                }
        except Exception as e:
            logger.error(f"Error checking pgvector: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Error connecting to database: {str(e)}",
            }

    except Exception as e:
        logger.error(f"Error in pgvector debug endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in pgvector debug endpoint: {str(e)}",
        )
