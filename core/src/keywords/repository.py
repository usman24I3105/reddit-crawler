"""
Repository for keyword database operations.
"""
from typing import List, Set, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..db.models import Keyword
from ..utils.logging import get_logger

logger = get_logger(__name__)


class KeywordRepository:
    """
    Repository for Keyword model operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_primary_keywords(
        self,
        client_id: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[str]:
        """
        Get all primary keywords.
        
        Args:
            client_id: Optional client identifier filter
            enabled_only: Only return enabled keywords
        
        Returns:
            List of keyword strings (normalized to lowercase)
        """
        try:
            query = self.db.query(Keyword).filter(Keyword.type == 'primary')
            
            if enabled_only:
                query = query.filter(Keyword.enabled == True)
            
            if client_id:
                query = query.filter(Keyword.client_id == client_id)
            
            keywords = query.all()
            return [kw.word.lower() for kw in keywords]
            
        except Exception as e:
            logger.error(f"Failed to get primary keywords: {str(e)}")
            return []
    
    def get_secondary_keywords(
        self,
        client_id: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[str]:
        """
        Get all secondary keywords.
        
        Args:
            client_id: Optional client identifier filter
            enabled_only: Only return enabled keywords
        
        Returns:
            List of keyword strings (normalized to lowercase)
        """
        try:
            query = self.db.query(Keyword).filter(Keyword.type == 'secondary')
            
            if enabled_only:
                query = query.filter(Keyword.enabled == True)
            
            if client_id:
                query = query.filter(Keyword.client_id == client_id)
            
            keywords = query.all()
            return [kw.word.lower() for kw in keywords]
            
        except Exception as e:
            logger.error(f"Failed to get secondary keywords: {str(e)}")
            return []
    
    def get_all_keywords(
        self,
        client_id: Optional[str] = None,
        enabled_only: bool = True
    ) -> dict:
        """
        Get all keywords grouped by type.
        
        Args:
            client_id: Optional client identifier filter
            enabled_only: Only return enabled keywords
        
        Returns:
            Dictionary with 'primary' and 'secondary' lists
        """
        return {
            'primary': self.get_primary_keywords(client_id, enabled_only),
            'secondary': self.get_secondary_keywords(client_id, enabled_only),
        }
    
    def create_keyword(
        self,
        word: str,
        keyword_type: str,
        client_id: Optional[str] = None,
        enabled: bool = True
    ) -> Optional[Keyword]:
        """
        Create a new keyword.
        
        Args:
            word: Keyword text (will be normalized to lowercase)
            keyword_type: 'primary' or 'secondary'
            client_id: Optional client identifier
            enabled: Whether keyword is enabled
        
        Returns:
            Created Keyword instance or None if failed
        """
        try:
            keyword = Keyword(
                word=word.lower().strip(),
                type=keyword_type.lower(),
                client_id=client_id or 'default',
                enabled=enabled
            )
            
            self.db.add(keyword)
            self.db.commit()
            self.db.refresh(keyword)
            
            logger.info(f"Created keyword: {keyword.word} (type: {keyword.type})")
            return keyword
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create keyword {word}: {str(e)}")
            return None
    
    def get_keyword_count(self, client_id: Optional[str] = None) -> dict:
        """
        Get count of keywords by type.
        
        Args:
            client_id: Optional client identifier filter
        
        Returns:
            Dictionary with 'primary' and 'secondary' counts
        """
        try:
            query = self.db.query(Keyword).filter(Keyword.enabled == True)
            
            if client_id:
                query = query.filter(Keyword.client_id == client_id)
            
            primary_count = query.filter(Keyword.type == 'primary').count()
            secondary_count = query.filter(Keyword.type == 'secondary').count()
            
            return {
                'primary': primary_count,
                'secondary': secondary_count,
                'total': primary_count + secondary_count,
            }
            
        except Exception as e:
            logger.error(f"Failed to get keyword count: {str(e)}")
            return {'primary': 0, 'secondary': 0, 'total': 0}


