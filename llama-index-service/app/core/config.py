import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, validator, BaseSettings


class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]

    # Environment settings
    ENVIRONMENT: str = os.getenv("ENV", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # PostgreSQL settings from whk-mes
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin")
    DB_HOST: str = os.getenv("DB_HOST", "db")  # Use container name in docker-compose
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    MES_DB_NAME: str = os.getenv("MES_DB_NAME", "whk-mes")

    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_OPENAI_MODEL: str = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")

    # Llama Index settings
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 20
    PRELOAD_INDEXES: bool = (
        os.getenv("PRELOAD_INDEXES", "false").lower() == "true"
    )  # Default to false
    BATCH_SIZE: int = int(
        os.getenv("BATCH_SIZE", "10")
    )  # Number of documents to process in each batch
    MAX_RETRIES: int = int(
        os.getenv("MAX_RETRIES", "5")
    )  # Maximum number of retries for rate limits
    INITIAL_BACKOFF: float = float(
        os.getenv("INITIAL_BACKOFF", "1")
    )  # Initial backoff time in seconds
    MAX_BACKOFF: float = float(
        os.getenv("MAX_BACKOFF", "60")
    )  # Maximum backoff time in seconds
    MIN_BATCH_DELAY: float = float(
        os.getenv("MIN_BATCH_DELAY", "0.5")
    )  # Minimum delay between batches
    MAX_BATCH_DELAY: float = float(
        os.getenv("MAX_BATCH_DELAY", "2.0")
    )  # Maximum delay between batches
    MIN_TABLE_DELAY: float = float(
        os.getenv("MIN_TABLE_DELAY", "5")
    )  # Minimum delay between tables
    MAX_TABLE_DELAY: float = float(
        os.getenv("MAX_TABLE_DELAY", "15")
    )  # Maximum delay between tables

    # Database URI
    POSTGRES_SERVER: str = DB_HOST
    POSTGRES_USER: str = DB_USER
    POSTGRES_PASSWORD: str = DB_PASSWORD
    POSTGRES_DB: str = MES_DB_NAME
    POSTGRES_PORT: str = DB_PORT

    # Vector database settings (using same PostgreSQL instance)
    VECTOR_DB_NAME: str = os.getenv("VECTOR_DB_NAME", "whk_vectors")
    VECTOR_DB_USER: str = DB_USER
    VECTOR_DB_PASSWORD: str = DB_PASSWORD
    VECTOR_DB_HOST: str = DB_HOST
    VECTOR_DB_PORT: str = DB_PORT

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = 0
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "5000"))

    # Monitoring settings
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN", "")

    # Tables to index (default is to index all main tables)
    TABLES_TO_INDEX: List[str] = [
        "Recipe",
        "RecipeParameter",
        "PhaseParameter",
        "Operation",
        "EquipmentPhase",
        "Procedure",
        "UnitProcedure",
        "Bom",
        "BomItem",
        "ProductionOrder",
        "ScheduleOrder",
        "Item",
        "TestParameter",
        "FermentationChemistry",
        "FermentationDayDatum",
        "MashingDatum",
        "Customer",
        "Lot",
        "Batch",
    ]

    # Derived database connection strings
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    VECTOR_DB_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    @validator("VECTOR_DB_URI", pre=True)
    def assemble_vector_db_connection(cls, v: Optional[str], values) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            user=values.get("VECTOR_DB_USER"),
            password=values.get("VECTOR_DB_PASSWORD"),
            host=values.get("VECTOR_DB_HOST"),
            port=values.get("VECTOR_DB_PORT"),
            path=f"/{values.get('VECTOR_DB_NAME') or ''}",
        )

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
