"""
Base storage interface for abstracting storage backends.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..utils.logging import get_logger

logger = get_logger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def save_post(self, post: Dict[str, Any]) -> Any:
        """
        Save a single post to storage.
        
        Args:
            post: Normalized post dictionary
        
        Returns:
            Saved post object (implementation-specific)
        """
        pass
    
    @abstractmethod
    def save_posts(self, posts: List[Dict[str, Any]]) -> List[Any]:
        """
        Save multiple posts to storage.
        
        Args:
            posts: List of normalized post dictionaries
        
        Returns:
            List of saved post objects
        """
        pass
    
    @abstractmethod
    def get_existing_post_ids(self) -> set:
        """
        Get set of existing post IDs for deduplication.
        
        Returns:
            Set of post IDs (strings)
        """
        pass
    
    @abstractmethod
    def get_existing_permalinks(self) -> set:
        """
        Get set of existing permalinks for deduplication.
        
        Returns:
            Set of permalinks (strings)
        """
        pass
    
    @abstractmethod
    def update_post_status(self, post_id: str, status: str, assigned_to: Optional[str] = None) -> bool:
        """
        Update post status and optionally assign to worker.
        
        Args:
            post_id: Reddit post ID
            status: New status (pending, in_progress, replied)
            assigned_to: Optional worker identifier
        
        Returns:
            True if update successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_pending_posts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get pending posts for worker dashboard.
        
        Args:
            limit: Maximum number of posts to return
        
        Returns:
            List of pending post dictionaries
        """
        pass
    
    def cleanup_old_posts(self, max_posts: int) -> int:
        """
        Clean up old posts when database exceeds max_posts limit.
        Deletes oldest posts first (by fetched_at timestamp).
        
        This is a default implementation that can be overridden.
        Not all storage backends may support this operation.
        
        Args:
            max_posts: Maximum number of posts to keep in database
        
        Returns:
            Number of posts deleted (0 if not supported or no cleanup needed)
        """
        # Default implementation: no-op (subclasses should override)
        return 0

