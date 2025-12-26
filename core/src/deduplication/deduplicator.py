"""
Deduplication service to prevent duplicate posts.
"""
from typing import List, Dict, Any, Set
from ..utils.logging import get_logger
from ..utils.exceptions import DeduplicationException

logger = get_logger(__name__)


class Deduplicator:
    """Handles deduplication of Reddit posts using post_id and permalink"""
    
    def __init__(self, existing_post_ids: Set[str] = None, existing_permalinks: Set[str] = None):
        """
        Initialize the deduplicator.
        
        Args:
            existing_post_ids: Set of existing post IDs (from database)
            existing_permalinks: Set of existing permalinks (from database)
        """
        self.existing_post_ids = existing_post_ids or set()
        self.existing_permalinks = existing_permalinks or set()
        logger.info(
            f"Deduplicator initialized: {len(self.existing_post_ids)} existing post IDs, "
            f"{len(self.existing_permalinks)} existing permalinks"
        )
    
    def is_duplicate(self, post: Dict[str, Any]) -> bool:
        """
        Check if a post is a duplicate.
        
        Args:
            post: Normalized post dictionary
        
        Returns:
            True if post is duplicate, False otherwise
        """
        post_id = post.get('post_id')
        permalink = post.get('permalink')
        
        # Check by post_id (preferred method)
        if post_id and post_id in self.existing_post_ids:
            logger.debug(f"Post {post_id} is duplicate (matched by post_id)")
            return True
        
        # Check by permalink (fallback)
        if permalink and permalink in self.existing_permalinks:
            logger.debug(f"Post {post_id} is duplicate (matched by permalink)")
            return True
        
        return False
    
    def filter_duplicates(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out duplicate posts from a list.
        
        Args:
            posts: List of normalized post dictionaries
        
        Returns:
            List of unique posts (duplicates removed)
        """
        unique_posts = []
        seen_post_ids = set()
        seen_permalinks = set()
        
        for post in posts:
            post_id = post.get('post_id')
            permalink = post.get('permalink')
            
            # Check if already seen in this batch
            if post_id and post_id in seen_post_ids:
                logger.debug(f"Post {post_id} skipped (duplicate in batch)")
                continue
            
            if permalink and permalink in seen_permalinks:
                logger.debug(f"Post {post_id} skipped (duplicate permalink in batch)")
                continue
            
            # Check against existing posts
            if self.is_duplicate(post):
                continue
            
            # Add to unique list and track
            unique_posts.append(post)
            if post_id:
                seen_post_ids.add(post_id)
            if permalink:
                seen_permalinks.add(permalink)
        
        duplicates_removed = len(posts) - len(unique_posts)
        logger.info(f"Deduplication: {duplicates_removed} duplicates removed, {len(unique_posts)} unique posts")
        return unique_posts

