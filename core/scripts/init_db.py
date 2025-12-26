#!/usr/bin/env python
"""
Initialize SQLite database with tables.
This script creates the database and tables if they don't exist.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.db.session import init_db, engine
from src.db.base import Base
from src.utils.logging import get_logger

logger = get_logger(__name__)


def main():
    """Initialize database"""
    logger.info("Initializing database...")
    
    # Create all tables
    init_db()
    
    logger.info("Database initialized successfully!")
    logger.info(f"Database location: {engine.url}")


if __name__ == '__main__':
    main()





