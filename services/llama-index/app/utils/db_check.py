import logging
import time

import psycopg2
from psycopg2 import OperationalError
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.config import settings

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(60), wait=wait_fixed(1))
def check_postgres_connection():
    """Check if the PostgreSQL database is available."""
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dbname=settings.MES_DB_NAME,
        )
        conn.close()
        logger.info("Successfully connected to PostgreSQL")
        return True
    except OperationalError as e:
        logger.warning(f"Could not connect to PostgreSQL: {e}")
        raise e


def check_all_connections():
    """Check all necessary database connections"""
    try:
        # First check the main PostgreSQL database
        check_postgres_connection()

        # Add other connection checks if needed (e.g., Redis)

        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


if __name__ == "__main__":
    # Basic logging setup for standalone execution
    logging.basicConfig(level=logging.INFO)

    logger.info("Checking database connections...")
    max_retries = 30
    retry_interval = 2

    for i in range(max_retries):
        try:
            if check_all_connections():
                logger.info("All database connections are available")
                break
        except Exception as e:
            logger.warning(f"Attempt {i+1}/{max_retries}: {e}")
            if i < max_retries - 1:
                logger.info(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                logger.error("Max retries reached. Could not connect to database(s)")
                raise
