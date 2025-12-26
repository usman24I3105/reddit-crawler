"""
Script to initialize keywords in the database.

Creates sample primary and secondary keywords for testing.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.session import SessionLocal, init_db
from src.db.models import Keyword
from src.keywords.repository import KeywordRepository
from src.utils.logging import get_logger

logger = get_logger(__name__)


def init_keywords():
    """Initialize keywords in database"""
    db = SessionLocal()
    try:
        # Initialize database tables
        init_db()
        logger.info("Database tables initialized")
        
        repository = KeywordRepository(db)
        
        # Sample primary keywords (intent)
        primary_keywords = [
            "how to",
            "need help",
            "looking for",
            "any advice",
            "problem with",
            "stuck on",
            "can't figure out",
            "help me",
            "trying to",
            "want to",
        ]
        
        # Sample secondary keywords (domain/topic)
        secondary_keywords = [
            "fastapi",
            "react",
            "api",
            "database",
            "deployment",
            "python",
            "javascript",
            "sql",
            "docker",
            "aws",
            "frontend",
            "backend",
            "authentication",
            "error",
            "bug",
        ]
        
        # Create primary keywords
        created_primary = 0
        for keyword in primary_keywords:
            existing = db.query(Keyword).filter(
                Keyword.word == keyword.lower(),
                Keyword.type == 'primary'
            ).first()
            
            if not existing:
                result = repository.create_keyword(
                    word=keyword,
                    keyword_type='primary',
                    enabled=True
                )
                if result:
                    created_primary += 1
                    logger.info(f"Created primary keyword: {keyword}")
        
        # Create secondary keywords
        created_secondary = 0
        for keyword in secondary_keywords:
            existing = db.query(Keyword).filter(
                Keyword.word == keyword.lower(),
                Keyword.type == 'secondary'
            ).first()
            
            if not existing:
                result = repository.create_keyword(
                    word=keyword,
                    keyword_type='secondary',
                    enabled=True
                )
                if result:
                    created_secondary += 1
                    logger.info(f"Created secondary keyword: {keyword}")
        
        # Get counts
        counts = repository.get_keyword_count()
        
        logger.info("=" * 60)
        logger.info("Keyword initialization complete")
        logger.info(f"Created {created_primary} new primary keywords")
        logger.info(f"Created {created_secondary} new secondary keywords")
        logger.info(f"Total keywords: {counts['total']} ({counts['primary']} primary, {counts['secondary']} secondary)")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Failed to initialize keywords: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == '__main__':
    init_keywords()

