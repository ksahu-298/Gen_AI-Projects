import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from app.config import settings

logger = logging.getLogger("text_to_sql.db")

_engine: Engine = None


def get_db_engine() -> Engine:
    """
    Returns or initializes the SQLAlchemy Engine.
    Supports PostgreSQL or zero-config SQLite fallback.
    """
    global _engine
    if _engine is not None:
        return _engine

    database_url = settings.DATABASE_URL
    logger.info(f"Connecting to database: {database_url.split('@')[-1] if '@' in database_url else database_url}")

    try:
        if database_url.startswith("postgresql"):
            _engine = create_engine(
                database_url,
                echo=settings.DB_ECHO,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 5}
            )
            # Verify connectivity
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to PostgreSQL instance.")
        else:
            # Fallback to SQLite
            _engine = create_engine(
                database_url,
                echo=settings.DB_ECHO,
                connect_args={"check_same_thread": False}
            )
            logger.info("Using SQLite database engine.")
    except Exception as e:
        logger.warning(f"Could not connect to target database ({e}). Falling back to local SQLite database.")
        fallback_url = "sqlite:///./ecommerce.db"
        _engine = create_engine(
            fallback_url,
            echo=settings.DB_ECHO,
            connect_args={"check_same_thread": False}
        )

    return _engine


def get_db_type() -> str:
    """Returns 'postgresql' or 'sqlite' depending on the active dialect."""
    engine = get_db_engine()
    return engine.dialect.name
