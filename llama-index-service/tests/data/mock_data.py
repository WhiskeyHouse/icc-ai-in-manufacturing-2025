"""
Module for generating mock data for testing.
This script can be run standalone to populate test databases with sample data.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def connect_to_db(host, port, user, password, dbname):
    """Connect to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=dbname
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info(f"Connected to database {dbname} at {host}:{port}")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None


def create_schema(conn):
    """Create the necessary tables and schema for testing."""
    try:
        with conn.cursor() as cursor:
            # Drop existing tables if they exist
            cursor.execute(
                """
                DROP TABLE IF EXISTS "Recipe" CASCADE;
                DROP TABLE IF EXISTS "RecipeParameter" CASCADE;
                DROP TABLE IF EXISTS "Batch" CASCADE;
                """
            )

            # Create Recipe table
            cursor.execute(
                """
                CREATE TABLE "Recipe" (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # Create RecipeParameter table
            cursor.execute(
                """
                CREATE TABLE "RecipeParameter" (
                    id SERIAL PRIMARY KEY,
                    recipe_id INTEGER REFERENCES "Recipe"(id),
                    name VARCHAR(255) NOT NULL,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # Create Batch table
            cursor.execute(
                """
                CREATE TABLE "Batch" (
                    id SERIAL PRIMARY KEY,
                    recipe_id INTEGER REFERENCES "Recipe"(id),
                    batch_number VARCHAR(50) NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

        logger.info("Created test schema successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating schema: {e}")
        return False


def insert_mock_data(conn):
    """Insert mock data for testing."""
    try:
        with conn.cursor() as cursor:
            # Insert sample recipes
            cursor.execute(
                """
                INSERT INTO "Recipe" (name, description)
                VALUES 
                ('Bourbon Whiskey', 'Classic Kentucky bourbon with 70% corn mash'),
                ('Rye Whiskey', 'Traditional rye whiskey with spicy notes'),
                ('Single Malt', 'Single malt whiskey aged in oak barrels');
                """
            )

            # Insert sample recipe parameters
            cursor.execute(
                """
                INSERT INTO "RecipeParameter" (recipe_id, name, value)
                VALUES 
                (1, 'Corn Percentage', '70'),
                (1, 'Aging Time', '4 years'),
                (1, 'Barrel Type', 'New American Oak'),
                (2, 'Rye Percentage', '95'),
                (2, 'Aging Time', '2 years'),
                (2, 'Barrel Type', 'Charred Oak'),
                (3, 'Barley Percentage', '100'),
                (3, 'Aging Time', '10 years'),
                (3, 'Barrel Type', 'Ex-Bourbon Casks');
                """
            )

            # Insert sample batches
            cursor.execute(
                """
                INSERT INTO "Batch" (recipe_id, batch_number, status, start_date, notes)
                VALUES 
                (1, 'B001-2024', 'in_progress', '2024-01-15', 'First batch of the year'),
                (2, 'B002-2024', 'pending', '2024-02-20', 'Experimental rye batch'),
                (3, 'B003-2024', 'completed', '2023-10-10', 'Special anniversary edition');
                """
            )

        logger.info("Inserted mock data successfully")
        return True
    except Exception as e:
        logger.error(f"Error inserting mock data: {e}")
        return False


def setup_vector_extension(conn):
    """Set up pgvector extension if available."""
    try:
        with conn.cursor() as cursor:
            # Try to create the pgvector extension
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                logger.info("Successfully enabled pgvector extension")

                # Create a test vector table
                cursor.execute("DROP TABLE IF EXISTS vector_test;")
                cursor.execute(
                    """
                    CREATE TABLE vector_test (
                        id SERIAL PRIMARY KEY,
                        embedding vector(1536)
                    );
                    """
                )
                # Insert a sample vector
                cursor.execute(
                    "INSERT INTO vector_test (embedding) VALUES ('{0,0,0,0}');",
                )
                logger.info("Created test vector table successfully")
            except Exception as e:
                logger.warning(f"Could not enable pgvector extension: {e}")
                logger.warning("Vector store tests will be limited")

        return True
    except Exception as e:
        logger.error(f"Error setting up vector extension: {e}")
        return False


def generate_test_data(host, port, user, password, dbname):
    """Generate test data for the specified database."""
    conn = connect_to_db(host, port, user, password, dbname)
    if not conn:
        return False

    success = (
        create_schema(conn) and insert_mock_data(conn) and setup_vector_extension(conn)
    )

    conn.close()
    return success


def main():
    """Main function when run as a script."""
    # Use environment variables or defaults
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    user = os.environ.get("DB_USER", "testuser")
    password = os.environ.get("DB_PASSWORD", "testpassword")
    dbname = os.environ.get("MES_DB_NAME", "testdb")

    logger.info(f"Generating test data for {dbname} database at {host}:{port}")

    if generate_test_data(host, port, user, password, dbname):
        logger.info("Test data generation completed successfully")
        return 0
    else:
        logger.error("Failed to generate test data")
        return 1


if __name__ == "__main__":
    sys.exit(main())
