"""
Phase 1: Set-based keyword matcher for 200-500 keywords.

Uses efficient set operations for fast matching.
Future: Can be swapped with Trie/Aho-Corasick/FTS5 implementations.
"""
from typing import Set, Optional
from .matcher import KeywordMatcher, MatchResult
from .repository import KeywordRepository
from ..db.session import SessionLocal
from ..utils.logging import get_logger

logger = get_logger(__name__)


class SetKeywordMatcher(KeywordMatcher):
    """
    Set-based keyword matcher (Phase 1).
    
    Efficient for 200-500 keywords using Python sets.
    Loads keywords once at startup, uses set intersection for matching.
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        db: Optional[SessionLocal] = None
    ):
        """
        Initialize set-based keyword matcher.
        
        Args:
            client_id: Optional client identifier
            db: Optional database session (creates new if not provided)
        """
        self.client_id = client_id
        self.db = db
        self._primary_keywords: Set[str] = set()
        self._secondary_keywords: Set[str] = set()
        
        # Load keywords at initialization
        self.reload()
    
    def reload(self) -> None:
        """Reload keywords from database."""
        try:
            # Use provided session or create new one
            if self.db:
                repository = KeywordRepository(self.db)
            else:
                db = SessionLocal()
                try:
                    repository = KeywordRepository(db)
                    keywords = repository.get_all_keywords(
                        client_id=self.client_id,
                        enabled_only=True
                    )
                    self._primary_keywords = set(keywords['primary'])
                    self._secondary_keywords = set(keywords['secondary'])
                finally:
                    db.close()
                return
            
            keywords = repository.get_all_keywords(
                client_id=self.client_id,
                enabled_only=True
            )
            self._primary_keywords = set(keywords['primary'])
            self._secondary_keywords = set(keywords['secondary'])
            
            logger.info(
                f"Reloaded keywords: {len(self._primary_keywords)} primary, "
                f"{len(self._secondary_keywords)} secondary"
            )
            
        except Exception as e:
            logger.error(f"Failed to reload keywords: {str(e)}")
            # Keep existing keywords on error
    
    def match(self, text: str) -> MatchResult:
        """
        Match text against keywords using set operations.
        
        Matching rule: Post is valid ONLY IF:
        - (at least 1 primary keyword) AND
        - (at least 1 secondary keyword)
        
        Args:
            text: Text to match (should be normalized to lowercase)
        
        Returns:
            MatchResult with matched status and matched keywords
        """
        # Normalize text to lowercase
        text_lower = text.lower()
        
        # Split text into words for matching
        # Simple word boundary matching (can be enhanced)
        words = set(text_lower.split())
        
        # Also check for substring matches (for phrases like "how to")
        # This handles multi-word keywords
        matched_primary = set()
        matched_secondary = set()
        
        # Check primary keywords
        for keyword in self._primary_keywords:
            if keyword in text_lower:
                matched_primary.add(keyword)
        
        # Check secondary keywords
        for keyword in self._secondary_keywords:
            if keyword in text_lower:
                matched_secondary.add(keyword)
        
        # Apply strict matching rule: (at least 1 primary) AND (at least 1 secondary)
        matched = len(matched_primary) > 0 and len(matched_secondary) > 0
        
        return MatchResult(
            matched=matched,
            matched_primary=matched_primary,
            matched_secondary=matched_secondary
        )
    
    def get_keyword_count(self) -> dict:
        """
        Get count of loaded keywords by type.
        
        Returns:
            Dictionary with 'primary' and 'secondary' counts
        """
        return {
            'primary': len(self._primary_keywords),
            'secondary': len(self._secondary_keywords),
            'total': len(self._primary_keywords) + len(self._secondary_keywords),
        }


