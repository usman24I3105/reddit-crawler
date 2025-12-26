"""
Keyword-based filtering for Reddit posts.

Uses scalable KeywordMatcher interface with primary/secondary keyword matching.
Matching rule: Post is valid ONLY IF (at least 1 primary) AND (at least 1 secondary)
"""
from typing import List, Dict, Any, Optional
from ..keywords import KeywordMatcher, SetKeywordMatcher
from ..utils.logging import get_logger
from ..utils.exceptions import FilterException

logger = get_logger(__name__)


class KeywordFilter:
    """
    Filters posts based on keyword matching using scalable KeywordMatcher.
    
    Uses primary/secondary keyword system:
    - Primary: Intent keywords (e.g., "how to", "need help")
    - Secondary: Domain/topic keywords (e.g., "fastapi", "react")
    
    Matching rule: Post is valid ONLY IF (at least 1 primary) AND (at least 1 secondary)
    """
    
    def __init__(self, matcher: Optional[KeywordMatcher] = None, client_id: Optional[str] = None):
        """
        Initialize the keyword filter.
        
        Args:
            matcher: Optional KeywordMatcher instance (creates SetKeywordMatcher if not provided)
            client_id: Optional client identifier for multi-tenant support
        """
        if matcher is None:
            # Phase 1: Use set-based matcher (can be swapped later)
            self.matcher = SetKeywordMatcher(client_id=client_id)
        else:
            self.matcher = matcher
        
        counts = self.matcher.get_keyword_count()
        logger.info(
            f"KeywordFilter initialized: {counts['primary']} primary, "
            f"{counts['secondary']} secondary keywords"
        )
    
    def matches(self, post: Dict[str, Any]) -> bool:
        """
        Check if a post matches keyword rules.
        
        Matching rule: (at least 1 primary) AND (at least 1 secondary)
        
        Args:
            post: Normalized post dictionary
        
        Returns:
            True if post matches keyword rules, False otherwise
        """
        # Combine title and body for matching
        title = (post.get('title') or '').lower()
        body = (post.get('body') or '').lower()
        combined_text = f"{title} {body}"
        
        # Use matcher to check
        result = self.matcher.match(combined_text)
        
        if result.matched:
            logger.info(
                f"Post {post.get('post_id')} matched: "
                f"{len(result.matched_primary)} primary, "
                f"{len(result.matched_secondary)} secondary keywords"
            )
            if result.matched_primary:
                logger.info(f"  Matched primary: {list(result.matched_primary)[:3]}")
            if result.matched_secondary:
                logger.info(f"  Matched secondary: {list(result.matched_secondary)[:3]}")
        else:
            # Log first few non-matching posts for debugging
            if len(result.matched_primary) == 0 and len(result.matched_secondary) == 0:
                logger.debug(
                    f"Post {post.get('post_id')} did not match: no keywords found. "
                    f"Title: {post.get('title', '')[:50]}"
                )
            else:
                logger.debug(
                    f"Post {post.get('post_id')} did not match: "
                    f"primary={len(result.matched_primary)}, "
                    f"secondary={len(result.matched_secondary)}"
                )
        
        return result.matched
    
    def filter_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of posts by keywords.
        
        Args:
            posts: List of normalized post dictionaries
        
        Returns:
            Filtered list of posts that match keyword rules
        """
        counts = self.matcher.get_keyword_count()
        if counts['total'] == 0:
            logger.warning("No keywords configured, accepting all posts")
            return posts
        
        filtered = [post for post in posts if self.matches(post)]
        logger.info(f"Keyword filter: {len(filtered)}/{len(posts)} posts matched keyword rules")
        return filtered
    
    def reload_keywords(self) -> None:
        """
        Reload keywords from database.
        Useful when keywords are updated.
        """
        self.matcher.reload()
        counts = self.matcher.get_keyword_count()
        logger.info(f"Keywords reloaded: {counts['primary']} primary, {counts['secondary']} secondary")

