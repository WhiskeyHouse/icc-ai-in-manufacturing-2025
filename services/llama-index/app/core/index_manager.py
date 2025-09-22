import logging
import time
from functools import lru_cache
import json
import os
import threading
import urllib.parse
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import RateLimitError

import sqlalchemy as sa
from llama_index.core import ServiceContext
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.indices.vector_store import VectorStoreIndex

# Updated import for PGVectorStore
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.indices.loading import load_index_from_storage
from llama_index.core.storage.storage_context import StorageContext
import redis
import psycopg2
import uuid

from app.core.config import settings
from app.utils.db_check import check_postgres_connection

logger = logging.getLogger(__name__)

# Rate limit settings
MAX_RETRIES = settings.MAX_RETRIES
INITIAL_BACKOFF = settings.INITIAL_BACKOFF
MAX_BACKOFF = settings.MAX_BACKOFF
BATCH_SIZE = settings.BATCH_SIZE


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def get_redis_client():
    """Get Redis client connection"""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


class IndexManager:
    """
    Manages the creation, storage, and retrieval of indexes for the whk-mes database.
    Uses a singleton pattern to ensure only one instance exists.
    """

    _instance = None
    _lock = threading.Lock()
    _index_locks = {}  # Locks for individual tables
    _global_lock = threading.Lock()  # Lock for global index operations

    @classmethod
    def get_instance(cls):
        """Get singleton instance of IndexManager"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the IndexManager"""
        self.indexes = {}
        self.service_context = self._create_service_context()
        self.storage_dir = os.path.join(os.getcwd(), "storage")
        os.makedirs(self.storage_dir, exist_ok=True)

        # Initialize locks for each table
        for table in settings.TABLES_TO_INDEX:
            self._index_locks[table] = threading.Lock()

        # Load or create global index
        self.global_index = None
        if settings.PRELOAD_INDEXES:
            self.global_index = self._load_or_create_global_index()

    def _create_service_context(self) -> ServiceContext:
        """Create a service context with the configured settings"""
        # Configure OpenAI embedding model
        embed_model = OpenAIEmbedding(
            model_name=settings.EMBED_MODEL,  # Using the model from settings
            api_key=settings.OPENAI_API_KEY,
        )

        # Configure node parser
        node_parser = SentenceSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        return ServiceContext.from_defaults(
            llm=None,  # We'll specify the LLM at query time
            embed_model=embed_model,
            node_parser=node_parser,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

    def get_llm(self, model_name: Optional[str] = None) -> OpenAI:
        """Get an OpenAI LLM instance with the specified model"""
        model = model_name or settings.DEFAULT_OPENAI_MODEL
        return OpenAI(
            model=model,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.1,
        )

    def _get_connection_string(self) -> str:
        """Get the PostgreSQL connection string"""
        # URL encode the password to handle special characters
        password_encoded = urllib.parse.quote_plus(settings.DB_PASSWORD)
        return f"postgresql://{settings.DB_USER}:{password_encoded}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.MES_DB_NAME}"

    def _get_vector_store(self, table_name: str) -> PGVectorStore:
        """Get a PostgreSQL vector store for the specified table"""
        # URL encode the password to handle special characters
        password_encoded = urllib.parse.quote_plus(settings.VECTOR_DB_PASSWORD)

        conn_str = f"postgresql://{settings.VECTOR_DB_USER}:{password_encoded}@{settings.VECTOR_DB_HOST}:{settings.VECTOR_DB_PORT}/{settings.VECTOR_DB_NAME}"
        async_conn_str = f"postgresql+asyncpg://{settings.VECTOR_DB_USER}:{password_encoded}@{settings.VECTOR_DB_HOST}:{settings.VECTOR_DB_PORT}/{settings.VECTOR_DB_NAME}"

        # Set the actual table name - note: PGVectorStore adds 'data_' prefix automatically
        table_db_name = f"{table_name.lower()}"  # Underlying name before PGVectorStore adds 'data_vectors_'

        # Ensure pgvector extension is installed
        try:
            with sa.create_engine(conn_str).connect() as connection:
                # Check if pgvector extension is installed
                result = connection.execute(
                    sa.text(
                        """
                        SELECT EXISTS (
                            SELECT FROM pg_extension WHERE extname = 'vector'
                        );
                        """
                    )
                ).scalar()

                if not result:
                    # Create the pgvector extension
                    connection.execute(
                        sa.text("CREATE EXTENSION IF NOT EXISTS vector;")
                    )
                    connection.commit()
                    logger.info("Created pgvector extension")
        except Exception as e:
            logger.error(f"Error checking/creating pgvector extension: {e}")
            raise

        # Create the vector store instance
        vector_store = PGVectorStore(
            connection_string=conn_str,
            async_connection_string=async_conn_str,
            table_name=table_db_name,  # Will become data_vectors_table_name
            schema_name="public",
            embed_dim=1536,  # Still needed for postgres schema
        )

        # Ensure the table exists with the correct schema
        try:
            with sa.create_engine(conn_str).connect() as connection:
                # Check if the table exists
                actual_table_name = f"data_vectors_{table_db_name}"  # This is how PGVectorStore creates table names
                result = connection.execute(
                    sa.text(
                        f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = '{actual_table_name}'
                        );
                        """
                    )
                ).scalar()

                if not result:
                    # Create the table with the correct schema
                    connection.execute(
                        sa.text(
                            f"""
                            CREATE TABLE IF NOT EXISTS "{actual_table_name}" (
                                id SERIAL PRIMARY KEY,
                                embedding vector(1536),
                                metadata JSONB,
                                doc_id TEXT,
                                text TEXT
                            );
                            """
                        )
                    )
                    connection.commit()
                    logger.info(f"Created vector table: {actual_table_name}")

                # Verify the table was created
                verify_result = connection.execute(
                    sa.text(f'SELECT COUNT(*) FROM "{actual_table_name}"')
                ).scalar()
                logger.info(
                    f"Vector table {actual_table_name} has {verify_result} rows"
                )

        except Exception as e:
            logger.error(f"Error ensuring vector table exists: {e}")
            raise

        return vector_store

    def _load_or_create_global_index(self) -> Optional[VectorStoreIndex]:
        """Load or create the global index from all tables."""
        # Get the global vector store
        vector_store = self._get_vector_store("global")

        # Ensure the global vector table exists
        try:
            with sa.create_engine(
                vector_store.connection_string
            ).connect() as connection:
                # Check if the table exists
                actual_table_name = "data_vectors_global"
                result = connection.execute(
                    sa.text(
                        f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = '{actual_table_name}'
                        );
                        """
                    )
                ).scalar()

                if not result:
                    # Create the table with the correct schema
                    logger.info(f"Creating global vector table {actual_table_name}")
                    connection.execute(
                        sa.text(
                            f"""
                            CREATE TABLE IF NOT EXISTS "{actual_table_name}" (
                                id SERIAL PRIMARY KEY,
                                embedding vector(1536),
                                metadata JSONB,
                                doc_id TEXT UNIQUE,
                                text TEXT
                            );
                            """
                        )
                    )
                    connection.commit()
                    logger.info(f"Created global vector table: {actual_table_name}")
                else:
                    # Check if the table has any data
                    count = connection.execute(
                        sa.text(f'SELECT COUNT(*) FROM "{actual_table_name}"')
                    ).scalar()
                    logger.info(
                        f"Global vector table {actual_table_name} has {count} rows"
                    )

                    if count > 0:
                        # Table exists and has data, create index from it
                        index = VectorStoreIndex.from_vector_store(
                            vector_store,
                            service_context=self.service_context,
                        )
                        self.indexes["global"] = index
                        logger.info(
                            "Successfully loaded global index from existing vector store"
                        )
                        return index
        except Exception as e:
            logger.error(f"Error checking/creating global vector table: {e}")
            # Continue with index creation since we'll recreate the table as needed

        # Now try to create the global index by pooling all indexed tables
        try:
            logger.info("Creating global index from all indexed tables...")

            # Count of nodes added to global index
            nodes_added = 0

            # Get all nodes from each table's vector store
            for table_name in settings.TABLES_TO_INDEX:
                try:
                    # Check if the table's vector store exists and has data
                    with sa.create_engine(
                        vector_store.connection_string
                    ).connect() as connection:
                        table_vector_name = f"data_vectors_{table_name.lower()}"
                        # Check if table exists
                        result = connection.execute(
                            sa.text(
                                f"""
                                SELECT EXISTS (
                                    SELECT FROM information_schema.tables 
                                    WHERE table_schema = 'public' 
                                    AND table_name = '{table_vector_name}'
                                );
                                """
                            )
                        ).scalar()

                        if result:
                            # Check if it has data
                            count = connection.execute(
                                sa.text(f'SELECT COUNT(*) FROM "{table_vector_name}"')
                            ).scalar()
                            logger.info(f"Table {table_vector_name} has {count} rows")

                            if count > 0:
                                # Get data from table in batches to avoid memory issues
                                batch_size = 100
                                offset = 0

                                while True:
                                    # Get a batch of rows
                                    rows = connection.execute(
                                        sa.text(
                                            f"""
                                            SELECT embedding, metadata, doc_id, text 
                                            FROM "{table_vector_name}"
                                            LIMIT {batch_size} OFFSET {offset}
                                            """
                                        )
                                    ).fetchall()

                                    # Exit loop if no more rows
                                    if not rows:
                                        break

                                    logger.info(
                                        f"Processing {len(rows)} rows from {table_vector_name} (offset {offset})"
                                    )

                                    # Process this batch
                                    batch_nodes_added = 0
                                    for row in rows:
                                        embedding = row[0]
                                        metadata = row[1] or {}
                                        doc_id = row[2]
                                        text = row[3]

                                        # Add table source to metadata if it doesn't exist
                                        if isinstance(metadata, dict):
                                            if "source_table" not in metadata:
                                                metadata["source_table"] = table_name
                                        else:
                                            metadata = {"source_table": table_name}

                                        # Insert into global table
                                        try:
                                            connection.execute(
                                                sa.text(
                                                    f"""
                                                    INSERT INTO "data_vectors_global" (embedding, metadata, doc_id, text)
                                                    VALUES (
                                                        $${json.dumps(embedding)}$$::vector,
                                                        $${json.dumps(metadata)}$$::jsonb,
                                                        $${doc_id}$$,
                                                        $${text}$$
                                                    )
                                                    ON CONFLICT (doc_id) DO UPDATE
                                                    SET embedding = $${json.dumps(embedding)}$$::vector,
                                                        metadata = $${json.dumps(metadata)}$$::jsonb,
                                                        text = $${text}$$
                                                    """
                                                )
                                            )
                                            batch_nodes_added += 1
                                        except Exception as e:
                                            logger.warning(
                                                f"Error inserting node {doc_id}: {e}"
                                            )

                                    # Commit after each batch
                                    connection.commit()
                                    logger.info(
                                        f"Added {batch_nodes_added} nodes to global table from batch"
                                    )
                                    nodes_added += batch_nodes_added

                                    # Move to next batch
                                    offset += batch_size

                                    # Add a small delay between batches to avoid database overload
                                    time.sleep(0.1)
                except Exception as e:
                    logger.warning(f"Error copying data from table {table_name}: {e}")
                    continue

            # Check if we added any data
            try:
                with sa.create_engine(
                    vector_store.connection_string
                ).connect() as connection:
                    count = connection.execute(
                        sa.text('SELECT COUNT(*) FROM "data_vectors_global"')
                    ).scalar()
                    logger.info(
                        f"Global vector store has {count} rows after build (added {nodes_added} nodes)"
                    )

                    if count > 0:
                        # Create index from the global vector store
                        index = VectorStoreIndex.from_vector_store(
                            vector_store,
                            service_context=self.service_context,
                        )
                        self.indexes["global"] = index
                        logger.info(
                            "Successfully created global index with data from all tables"
                        )
                        return index
            except Exception as e:
                logger.error(f"Error checking global vector store after build: {e}")

        except Exception as e:
            logger.error(f"Error building global index: {e}")

        # If we get here, we couldn't load or create a global index
        logger.warning("Could not create global index, returning None")
        return None

    def get_index_for_table(self, table_name: str) -> VectorStoreIndex:
        """Get or create an index for a specific table"""
        # Use the table-specific lock
        with self._index_locks.get(table_name, threading.Lock()):
            if table_name in self.indexes:
                return self.indexes[table_name]

            try:
                logger.info(f"Creating index for table: {table_name}")

                # Create vector store for the table
                vector_store = self._get_vector_store(table_name)

                # Create vector store index
                index = VectorStoreIndex.from_vector_store(
                    vector_store,
                    service_context=self.service_context,
                )

                # Cache the index
                self.indexes[table_name] = index

                return index
            except Exception as e:
                logger.error(f"Error creating index for table {table_name}: {e}")
                return None

    def _fetch_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Fetch data from a specified table in the database"""
        logger.info(f"Fetching data from table: {table_name}")
        conn = None
        try:
            conn_string = self._get_connection_string()
            conn = psycopg2.connect(conn_string)
            cur = conn.cursor()

            # First check if the table exists
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """,
                (table_name,),
            )

            table_exists = cur.fetchone()[0]
            if not table_exists:
                logger.warning(f"Table '{table_name}' does not exist")
                return []

            # Safely quote the table name to prevent SQL injection
            cur.execute(f'SELECT * FROM "{table_name}" LIMIT 1000')

            # Get column names
            columns = [desc[0] for desc in cur.description]

            # Fetch the records
            records = cur.fetchall()

            # Convert to list of dicts
            result = []
            for row in records:
                record_dict = {}
                for i, col in enumerate(columns):
                    record_dict[col] = row[i]
                result.append(record_dict)

            logger.info(f"Fetched {len(result)} records from {table_name}")
            return result

        except Exception as e:
            logger.error(f"Error fetching data from table {table_name}: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def index_table(
        self, table_name: str, force_reindex: bool = False
    ) -> Dict[str, Any]:
        """Index a single table into the vector database"""
        start_time = time.time()

        if table_name not in settings.TABLES_TO_INDEX:
            error_message = (
                f"Table '{table_name}' is not in the list of tables to index"
            )
            logger.error(error_message)
            return {
                "success": False,
                "message": error_message,
                "table_name": table_name,
                "tables_indexed": [],
                "processing_time": time.time() - start_time,
                "error": error_message,
            }

        try:
            logger.info(f"Indexing table: {table_name}")

            # Get vector store for the table
            vector_store = self._get_vector_store(table_name)

            # Fetch the data from the table
            records = self._fetch_table_data(table_name)

            if not records:
                error_message = (
                    f"No data found in table '{table_name}' or table does not exist"
                )
                logger.error(error_message)
                return {
                    "success": False,
                    "message": error_message,
                    "table_name": table_name,
                    "tables_indexed": [],
                    "processing_time": time.time() - start_time,
                    "error": error_message,
                }

            # Prepare documents for indexing
            from llama_index.core import Document

            documents = []
            for record in records:
                # Convert record to string with formatting using the custom encoder
                record_str = json.dumps(record, indent=2, cls=DateTimeEncoder)
                # Create a document with metadata
                doc = Document(
                    text=record_str,
                    metadata={
                        "table_name": table_name,
                        "record_id": str(record.get("id", "unknown")),
                    },
                )
                documents.append(doc)

            logger.info(f"Created {len(documents)} documents for indexing")

            # If force_reindex, delete the existing vector store table
            if force_reindex:
                try:
                    # Connect to vector DB and drop the table if it exists
                    password_encoded = urllib.parse.quote_plus(
                        settings.VECTOR_DB_PASSWORD
                    )
                    conn_str = f"postgresql://{settings.VECTOR_DB_USER}:{password_encoded}@{settings.VECTOR_DB_HOST}:{settings.VECTOR_DB_PORT}/{settings.VECTOR_DB_NAME}"

                    # Use SQLAlchemy for managing the connection
                    engine = sa.create_engine(conn_str)
                    vector_table_name = f"data_vectors_{table_name.lower()}"

                    with engine.connect() as connection:
                        if engine.dialect.has_table(connection, vector_table_name):
                            # Drop the table if it exists
                            logger.info(
                                f"Dropping existing vector table: {vector_table_name}"
                            )
                            connection.execute(
                                sa.text(f'DROP TABLE IF EXISTS "{vector_table_name}"')
                            )
                            connection.commit()

                except Exception as e:
                    logger.warning(
                        f"Error dropping existing vector table: {e}", exc_info=True
                    )

            # Process documents in batches
            all_nodes = []

            # First ensure the vector table exists
            try:
                with sa.create_engine(
                    vector_store.connection_string
                ).connect() as connection:
                    # Check if the table exists
                    actual_table_name = f"data_vectors_{table_name.lower()}"
                    result = connection.execute(
                        sa.text(
                            f"""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = '{actual_table_name}'
                            );
                            """
                        )
                    ).scalar()

                    if not result:
                        # Create the table with the correct schema
                        logger.info(
                            f"Creating table {actual_table_name} with vector schema"
                        )
                        connection.execute(
                            sa.text(
                                f"""
                                CREATE TABLE IF NOT EXISTS "{actual_table_name}" (
                                    id SERIAL PRIMARY KEY,
                                    embedding vector(1536),
                                    metadata JSONB,
                                    doc_id TEXT UNIQUE,
                                    text TEXT
                                );
                                """
                            )
                        )
                        connection.commit()
                        logger.info(f"Created vector table: {actual_table_name}")
                    else:
                        logger.info(f"Table {actual_table_name} already exists")
            except Exception as e:
                logger.error(f"Error creating vector table: {e}")
                raise

            for i in range(0, len(documents), BATCH_SIZE):
                batch = documents[i : i + BATCH_SIZE]
                try:
                    # Add exponential backoff for rate limit handling
                    @retry(
                        stop=stop_after_attempt(MAX_RETRIES),
                        wait=wait_exponential(
                            multiplier=INITIAL_BACKOFF, max=MAX_BACKOFF
                        ),
                        retry=retry_if_exception_type(RateLimitError),
                    )
                    def process_batch(batch_docs):
                        # Create a temporary index for the batch
                        from llama_index.core import VectorStoreIndex as VSIdx
                        from llama_index.core.schema import TextNode

                        # Generate embeddings for documents and create nodes directly
                        nodes = []
                        for doc in batch_docs:
                            # Create a unique ID for the node
                            node_id = str(uuid.uuid4())

                            # Generate embedding using the service context's embed model
                            embedding = (
                                self.service_context.embed_model.get_text_embedding(
                                    doc.text
                                )
                            )

                            # Create a TextNode with embedding
                            node = TextNode(
                                text=doc.text,
                                metadata=doc.metadata,
                                id_=node_id,
                                embedding=embedding,
                            )
                            nodes.append(node)

                        return nodes

                    # Process the batch with retry logic
                    batch_nodes = process_batch(batch)
                    logger.info(f"Generated {len(batch_nodes)} nodes with embeddings")

                    # Add nodes to all_nodes
                    all_nodes.extend(batch_nodes)

                    # Add nodes to vector store
                    if batch_nodes:
                        try:
                            # First try using the PGVectorStore add method
                            vector_store.add(nodes=batch_nodes)
                            logger.info(
                                f"Called vector_store.add() with {len(batch_nodes)} nodes"
                            )

                            # Then manually insert into database to ensure data is saved
                            logger.info("Manually inserting nodes into database...")
                            with sa.create_engine(
                                vector_store.connection_string
                            ).connect() as connection:
                                for node in batch_nodes:
                                    # Skip nodes without embeddings
                                    if not hasattr(node, "embedding"):
                                        logger.warning(
                                            f"Skipping node with no embedding: {node.id_}"
                                        )
                                        continue

                                    # Get node attributes
                                    embedding = node.embedding
                                    metadata = (
                                        node.metadata
                                        if hasattr(node, "metadata")
                                        else {}
                                    )
                                    doc_id = (
                                        node.id_
                                        if hasattr(node, "id_")
                                        else str(uuid.uuid4())
                                    )
                                    text = node.text if hasattr(node, "text") else ""

                                    # Insert into database
                                    try:
                                        connection.execute(
                                            sa.text(
                                                f"""
                                                INSERT INTO "data_vectors_{table_name.lower()}" (embedding, metadata, doc_id, text)
                                                VALUES (
                                                    $${json.dumps(embedding)}$$::vector,
                                                    $${json.dumps(metadata)}$$::jsonb,
                                                    $${doc_id}$$,
                                                    $${text}$$
                                                )
                                                ON CONFLICT (doc_id) DO UPDATE
                                                SET embedding = $${json.dumps(embedding)}$$::vector,
                                                    metadata = $${json.dumps(metadata)}$$::jsonb,
                                                    text = $${text}$$
                                                """
                                            )
                                        )
                                    except Exception as e:
                                        logger.warning(
                                            f"Error inserting node {doc_id}: {e}"
                                        )
                                connection.commit()
                                logger.info(
                                    f"Manually inserted {len(batch_nodes)} nodes into database"
                                )
                        except Exception as e:
                            logger.warning(f"Error adding nodes to vector store: {e}")

                    # Add a delay between batches to avoid rate limits
                    if i + BATCH_SIZE < len(documents):
                        delay = random.uniform(
                            settings.MIN_BATCH_DELAY, settings.MAX_BATCH_DELAY
                        )
                        logger.info(f"Waiting {delay:.2f} seconds before next batch...")
                        time.sleep(delay)

                except Exception as e:
                    logger.error(f"Error processing batch: {e}")
                    continue

            # Create the final index from the vector store
            logger.info(f"Creating final index for table: {table_name}")
            final_index = VectorStoreIndex.from_vector_store(
                vector_store,
                service_context=self.service_context,
            )

            # Cache the index
            self.indexes[table_name] = final_index

            # Verify that nodes were added to the vector store
            try:
                with sa.create_engine(
                    vector_store.connection_string
                ).connect() as connection:
                    actual_table_name = f"data_vectors_{table_name.lower()}"
                    result = connection.execute(
                        sa.text(f'SELECT COUNT(*) FROM "{actual_table_name}"')
                    ).scalar()
                    logger.info(f"Total nodes in vector store: {result}")
            except Exception as e:
                logger.warning(f"Error verifying vector store count: {e}")

            logger.info(f"Successfully indexed table: {table_name}")
            return {
                "success": True,
                "message": f"Successfully indexed table '{table_name}'",
                "table_name": table_name,
                "tables_indexed": [table_name],
                "processing_time": time.time() - start_time,
                "error": None,
            }

        except Exception as e:
            error_message = f"Error indexing table {table_name}: {str(e)}"
            logger.error(error_message, exc_info=True)
            return {
                "success": False,
                "message": error_message,
                "table_name": table_name,
                "tables_indexed": [],
                "processing_time": time.time() - start_time,
                "error": str(e),
            }

    def index_all_tables(self, force_reindex: bool = False) -> Dict[str, Any]:
        """Index all tables into the vector database"""
        start_time = time.time()
        tables_indexed = []
        failures = []

        logger.info(f"Indexing all tables: {settings.TABLES_TO_INDEX}")

        for table_name in settings.TABLES_TO_INDEX:
            try:
                result = self.index_table(table_name, force_reindex)
                if result["success"]:
                    tables_indexed.append(table_name)
                else:
                    failures.append({"table": table_name, "error": result["error"]})
            except Exception as e:
                failures.append({"table": table_name, "error": str(e)})
                logger.error(f"Error indexing table {table_name}: {e}", exc_info=True)

        # After indexing all tables, recreate the global index
        try:
            if tables_indexed:
                # Clear the existing global index
                if self.global_index is not None:
                    del self.global_index

                # Recreate the global index
                self.global_index = self._load_or_create_global_index()
        except Exception as e:
            logger.error(f"Error recreating global index: {e}", exc_info=True)
            failures.append({"table": "global", "error": str(e)})

        processing_time = time.time() - start_time

        if failures:
            error_message = (
                f"Indexed {len(tables_indexed)} tables with {len(failures)} failures"
            )
            logger.warning(error_message)
            return {
                "success": len(tables_indexed) > 0,
                "message": error_message,
                "table_name": None,
                "tables_indexed": tables_indexed,
                "processing_time": processing_time,
                "error": str(failures),
            }
        else:
            success_message = f"Successfully indexed all {len(tables_indexed)} tables"
            logger.info(success_message)
            return {
                "success": True,
                "message": success_message,
                "table_name": None,
                "tables_indexed": tables_indexed,
                "processing_time": processing_time,
                "error": None,
            }

    def query(
        self,
        query_text: str,
        model_name: str = None,
        table_name: str = None,
        similarity_top_k: int = 5,
    ) -> Dict[str, Any]:
        """Query the index for information."""
        try:
            start_time = time.time()
            logger.info(f"Processing query: {query_text}")

            # Try to load or use the specific table index if provided
            index = None
            if table_name:
                logger.info(f"Using table index: {table_name}")

                # Check if we already have this index loaded
                if table_name in self.indexes:
                    index = self.indexes[table_name]
                    logger.info(f"Using cached index for table: {table_name}")
                else:
                    # Check if the vector store table exists before creating
                    vector_store = self._get_vector_store(table_name)

                    # Use password encoding for special characters
                    vector_store_url = f"postgresql://{settings.VECTOR_DB_USER}:{urllib.parse.quote_plus(settings.VECTOR_DB_PASSWORD)}@{settings.VECTOR_DB_HOST}:{settings.VECTOR_DB_PORT}/{settings.VECTOR_DB_NAME}"

                    with sa.create_engine(vector_store_url).connect() as connection:
                        # Check if the table exists
                        table_vector_name = f"data_vectors_{table_name.lower()}"
                        result = connection.execute(
                            sa.text(
                                f"""
                                SELECT EXISTS (
                                    SELECT FROM information_schema.tables 
                                    WHERE table_schema = 'public' 
                                    AND table_name = '{table_vector_name}'
                                );
                                """
                            )
                        ).scalar()

                        if result:
                            # Check if it has data
                            count = connection.execute(
                                sa.text(f'SELECT COUNT(*) FROM "{table_vector_name}"')
                            ).scalar()
                            logger.info(f"Table {table_vector_name} has {count} rows")

                            if count > 0:
                                # Create index from vector store
                                index = VectorStoreIndex.from_vector_store(
                                    vector_store,
                                    service_context=self.service_context,
                                )
                                self.indexes[table_name] = index
                                logger.info(
                                    f"Created index from existing vector store: {table_name}"
                                )

            # If we don't have a specific index, try to use global
            if index is None:
                logger.info(
                    "No specific table index specified or found, trying global index"
                )
                if "global" in self.indexes:
                    index = self.indexes["global"]
                    logger.info("Using global index")
                else:
                    # Try to load global index
                    global_index = self._load_or_create_global_index()
                    if global_index:
                        index = global_index
                        logger.info("Loaded global index successfully")

            # If we still don't have an index, return error
            if index is None:
                logger.error("No suitable index found for query")
                return {
                    "query": query_text,
                    "response": "No indexed data available. Please index tables first.",
                    "source_nodes": [],
                    "model": model_name or "none",
                    "processing_time": time.time() - start_time,
                    "table_name": table_name,
                    "success": False,
                    "error": "No suitable index found for query",
                }

            # Set up the query engine to use retrieval only, without LLM
            retriever = index.as_retriever(similarity_top_k=similarity_top_k)

            try:
                # Execute retrieval query
                retrieval_results = retriever.retrieve(query_text)
                logger.info(f"Retrieved {len(retrieval_results)} nodes")

                # Format source nodes for response
                source_nodes = []
                for node in retrieval_results:
                    source_nodes.append(
                        {
                            "text": node.text,
                            "score": node.score if hasattr(node, "score") else 0,
                            "metadata": (
                                node.metadata if hasattr(node, "metadata") else {}
                            ),
                        }
                    )

                # Build response
                response = {
                    "query": query_text,
                    "response": "Retrieved information successfully. Use the source_nodes for details.",
                    "source_nodes": source_nodes,
                    "model": model_name or "none",
                    "processing_time": time.time() - start_time,
                    "table_name": table_name,
                    "success": True,
                    "error": None,
                }

                return response
            except Exception as e:
                logger.error(f"Error during retrieval: {e}")
                return {
                    "query": query_text,
                    "response": "Error during retrieval process.",
                    "source_nodes": [],
                    "model": model_name or "none",
                    "processing_time": time.time() - start_time,
                    "table_name": table_name,
                    "success": False,
                    "error": str(e),
                }

        except Exception as e:
            logger.error(f"Error during query: {e}")
            return {
                "query": query_text,
                "response": "An error occurred during query processing.",
                "source_nodes": [],
                "model": model_name or "none",
                "processing_time": (
                    time.time() - start_time if "start_time" in locals() else 0
                ),
                "error": str(e),
            }

    def test_vector_store(self, table_name: str = "test") -> Dict[str, Any]:
        """Test the vector store setup by creating a test record and querying it"""
        try:
            start_time = time.time()
            logger.info(f"Testing vector store setup for table: {table_name}")

            # Get vector store for the table
            vector_store = self._get_vector_store(table_name)

            # Log connection string without password for debugging
            conn_redacted = vector_store.connection_string.replace(
                urllib.parse.quote_plus(settings.VECTOR_DB_PASSWORD), "REDACTED"
            )
            logger.info(f"Using vector store with connection: {conn_redacted}")
            logger.info(f"Table name in vector store: {vector_store.table_name}")

            # First check if the table exists and has the correct schema
            try:
                with sa.create_engine(
                    vector_store.connection_string
                ).connect() as connection:
                    actual_table_name = f"data_vectors_{table_name.lower()}"
                    logger.info(f"Checking if table {actual_table_name} exists...")

                    # Check if the table exists
                    result = connection.execute(
                        sa.text(
                            f"""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = '{actual_table_name}'
                            );
                            """
                        )
                    ).scalar()

                    if not result:
                        logger.error(f"Table {actual_table_name} does not exist!")
                        # Create the table explicitly
                        connection.execute(
                            sa.text(
                                f"""
                                CREATE TABLE IF NOT EXISTS "{actual_table_name}" (
                                    id SERIAL PRIMARY KEY,
                                    embedding vector(1536),
                                    metadata JSONB,
                                    doc_id TEXT,
                                    text TEXT
                                );
                                """
                            )
                        )
                        connection.commit()
                        logger.info(f"Created vector table: {actual_table_name}")
                    else:
                        logger.info(f"Table {actual_table_name} exists.")
            except Exception as e:
                logger.error(
                    f"Error checking or creating table: {str(e)}", exc_info=True
                )
                raise

            # Create a test embedding vector (1536 dimensions filled with random values)
            import numpy as np
            from llama_index.core.schema import TextNode

            # Create a test node
            test_embedding = (
                np.random.rand(1536).astype(np.float32).tolist()
            )  # Convert to list
            test_metadata = {"test": True, "timestamp": datetime.now().isoformat()}
            test_doc_id = f"test-{int(time.time())}"
            test_text = "This is a test document to verify vector store functionality."

            logger.info(f"Created test node with id: {test_doc_id}")
            logger.info(
                f"Embedding type: {type(test_embedding)}, length: {len(test_embedding)}"
            )

            # Create a TextNode with the test data
            node = TextNode(
                text=test_text,
                metadata=test_metadata,
                id_=test_doc_id,
            )
            # Set the embedding manually - must be a list, not a numpy array
            node.embedding = test_embedding

            # Log node attributes for debugging
            logger.info(f"TextNode created with id: {node.id_}")
            logger.info(
                f"Node attributes: text={len(node.text)}, metadata={node.metadata}"
            )

            # Try to add the node to the vector store
            try:
                logger.info("Adding node to vector store...")
                vector_store.add(nodes=[node])
                logger.info("Successfully called vector_store.add()")

                # Manually commit the transaction to ensure data is saved
                try:
                    with sa.create_engine(
                        vector_store.connection_string
                    ).connect() as connection:
                        # Explicitly create an insert statement
                        logger.info("Manually inserting node into database...")
                        connection.execute(
                            sa.text(
                                f"""
                                INSERT INTO "data_vectors_{table_name.lower()}" (embedding, metadata, doc_id, text)
                                VALUES (
                                    $${test_embedding}$$::vector,
                                    $${json.dumps(test_metadata)}$$::jsonb,
                                    $${test_doc_id}$$,
                                    $${test_text}$$
                                )
                                """
                            )
                        )
                        connection.commit()
                        logger.info("Manual insert completed and committed")
                except Exception as e:
                    logger.error(
                        f"Error manually inserting node: {str(e)}", exc_info=True
                    )
            except Exception as e:
                logger.error(
                    f"Error adding node to vector store: {str(e)}", exc_info=True
                )
                raise

            # Verify the record was added
            try:
                with sa.create_engine(
                    vector_store.connection_string
                ).connect() as connection:
                    actual_table_name = f"data_vectors_{table_name.lower()}"
                    logger.info(
                        f"Verifying record in table {actual_table_name} with doc_id={test_doc_id}"
                    )
                    result = connection.execute(
                        sa.text(
                            f"SELECT COUNT(*) FROM \"{actual_table_name}\" WHERE doc_id = '{test_doc_id}'"
                        )
                    ).scalar()
                    logger.info(f"Query result: {result}")

                    if result > 0:
                        logger.info(f"Successfully added test record to vector store")

                        # Delete the test record
                        connection.execute(
                            sa.text(
                                f"DELETE FROM \"{actual_table_name}\" WHERE doc_id = '{test_doc_id}'"
                            )
                        )
                        connection.commit()
                        logger.info(f"Cleaned up test record from vector store")

                        return {
                            "success": True,
                            "message": "Vector store setup is working correctly",
                            "processing_time": time.time() - start_time,
                            "error": None,
                        }
                    else:
                        # Try to check the table structure
                        try:
                            columns = connection.execute(
                                sa.text(
                                    f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{actual_table_name}'"
                                )
                            ).fetchall()
                            logger.error(f"Table columns: {columns}")
                        except Exception as e:
                            logger.error(f"Error checking table structure: {e}")

                        error_message = f"Failed to add test record to vector store. Record with doc_id={test_doc_id} not found."
                        logger.error(error_message)
                        return {
                            "success": False,
                            "message": error_message,
                            "processing_time": time.time() - start_time,
                            "error": error_message,
                        }
            except Exception as e:
                error_message = f"Error verifying record: {str(e)}"
                logger.error(error_message, exc_info=True)
                return {
                    "success": False,
                    "message": error_message,
                    "processing_time": time.time() - start_time,
                    "error": error_message,
                }

        except Exception as e:
            error_message = f"Error testing vector store: {str(e)}"
            logger.error(error_message, exc_info=True)
            return {
                "success": False,
                "message": error_message,
                "processing_time": (
                    time.time() - start_time if "start_time" in locals() else 0
                ),
                "error": str(e),
            }
