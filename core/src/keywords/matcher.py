"""
Abstract interface for keyword matching engines.

This interface allows swapping implementations:
- Phase 1: Set-based matching (200-500 keywords)
- Phase 2: Trie/Aho-Corasick (thousands)
- Phase 3: FTS5/Elasticsearch (millions)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Set, Optional


@dataclass
class MatchResult:
    """
    Result of keyword matching operation.
    
    Attributes:
        matched: True if post matches keyword rules
        matched_primary: Set of matched primary keywords
        matched_secondary: Set of matched secondary keywords
    """
    matched: bool
    matched_primary: Set[str]
    matched_secondary: Set[str]
    
    def __repr__(self):
        return (
            f"MatchResult(matched={self.matched}, "
            f"primary={len(self.matched_primary)}, "
            f"secondary={len(self.matched_secondary)})"
        )


class KeywordMatcher(ABC):
    """
    Abstract base class for keyword matching engines.
    
    This interface allows swapping implementations without changing crawler logic.
    """
    
    @abstractmethod
    def match(self, text: str) -> MatchResult:
        """
        Match text against primary and secondary keywords.
        
        Matching rule: Post is valid ONLY IF:
        - (at least 1 primary keyword) AND
        - (at least 1 secondary keyword)
        
        Args:
            text: Text to match (title + body, normalized to lowercase)
        
        Returns:
            MatchResult with matched status and matched keywords
        """
        pass
    
    @abstractmethod
    def reload(self) -> None:
        """
        Reload keywords from database.
        Called at startup and when keywords are updated.
        """
        pass
    
    @abstractmethod
    def get_keyword_count(self) -> dict:
        """
        Get count of loaded keywords by type.
        
        Returns:
            Dictionary with 'primary' and 'secondary' counts
        """
        pass


