"""
Database session management.
Designed to be easily switchable between SQLite and PostgreSQL.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Get database URL from environment variable
# Format: sqlite:///path/to/db.sqlite or postgresql://user:pass@host/dbname
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    os.getenv('SQLITE_DB_PATH', 'sqlite:///./reddit_crawler.db')
)

# Determine if we're using SQLite or PostgreSQL
IS_SQLITE = DATABASE_URL.startswith('sqlite')

# Engine configuration
if IS_SQLITE:
    # SQLite-specific configuration
    # Use StaticPool for single-threaded apps, NullPool for multi-threaded
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite-specific
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL query logging
    )
    logger.info(f"Using SQLite database: {DATABASE_URL}")
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20,
        echo=False,  # Set to True for SQL query logging
    )
    logger.info(f"Using PostgreSQL database")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency function to get database session.
    Use this in FastAPI route dependencies.
    
    Example:
        @app.get("/posts")
        def get_posts(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Call this after Alembic migrations or for testing.
    """
    from .base import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")





