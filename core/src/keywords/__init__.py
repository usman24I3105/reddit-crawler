"""
Keyword matching system for scalable keyword filtering.
"""
from .matcher import KeywordMatcher, MatchResult
from .set_matcher import SetKeywordMatcher
from .repository import KeywordRepository

__all__ = [
    'KeywordMatcher',
    'MatchResult',
    'SetKeywordMatcher',
    'KeywordRepository',
]


