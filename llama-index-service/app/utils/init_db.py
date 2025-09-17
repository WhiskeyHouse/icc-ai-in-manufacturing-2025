import logging
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
import urllib.parse

from app.core.config import settings

logger = logging.getLogger(__name__)


def init_vector_db():
    """Initialize the vector database if it doesn't exist"""
    try:
        # Get the host from settings but encode it safely for URI
        host_to_use = settings.VECTOR_DB_HOST
        logger.info(
            f"Using vector database host: {host_to_use} port: {settings.VECTOR_DB_PORT}"
        )

        # Connect to default PostgreSQL database
        conn = psycopg2.connect(
            host=host_to_use,
            port=settings.VECTOR_DB_PORT,
            user=settings.VECTOR_DB_USER,
            password=settings.VECTOR_DB_PASSWORD,
            dbname="postgres",  # Connect to default DB first
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if vector database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (settings.VECTOR_DB_NAME,)
        )
        db_exists = cursor.fetchone()

        # Create vector database if it doesn't exist
        if not db_exists:
            logger.info(f"Creating vector database: {settings.VECTOR_DB_NAME}")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(settings.VECTOR_DB_NAME)
                )
            )

        cursor.close()
        conn.close()

        # Now connect to the vector database and install pgvector extension
        # Build connection string manually to avoid IDNA encoding issues
        # URL encode the password to handle special characters
        password_encoded = urllib.parse.quote_plus(settings.VECTOR_DB_PASSWORD)
        conn_str = f"postgresql+psycopg://{settings.VECTOR_DB_USER}:{password_encoded}@{host_to_use}:{settings.VECTOR_DB_PORT}/{settings.VECTOR_DB_NAME}"
        vector_engine = create_engine(conn_str)

        with vector_engine.connect() as conn:
            # Check if pgvector extension exists
            result = conn.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            )
            extension_exists = result.fetchone()

            # Create pgvector extension if it doesn't exist
            if not extension_exists:
                logger.info("Creating pgvector extension")
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()

        logger.info("Vector database initialization complete")
        return True
    except Exception as e:
        logger.error(f"Error initializing vector database: {e}")
        raise


if __name__ == "__main__":
    # Basic logging setup for standalone execution
    logging.basicConfig(level=logging.INFO)

    logger.info("Initializing databases...")
    try:
        init_vector_db()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
