"""
SQLAlchemy-based storage backend.
Implements the StorageBackend interface using the new repository pattern.
"""
from typing import List, Dict, Any, Optional, Set
from .base import StorageBackend
from ..db.repository import PostRepository
from ..db.session import SessionLocal
from ..utils.logging import get_logger
from ..utils.exceptions import StorageException

logger = get_logger(__name__)


class SQLAlchemyStorage(StorageBackend):
    """
    SQLAlchemy-based storage backend using repository pattern.
    Creates a new session for each operation to ensure thread safety.
    """
    
    def __init__(self):
        """Initialize SQLAlchemy storage backend"""
        logger.info("SQLAlchemyStorage initialized")
    
    def _get_repository(self):
        """Get a new repository instance with a fresh session"""
        db = SessionLocal()
        return PostRepository(db), db
    
    def save_post(self, post: Dict[str, Any]) -> Any:
        """Save a single post to database"""
        repository, db = self._get_repository()
        try:
            return repository.create_post(post)
        except StorageException as e:
            logger.error(f"Failed to save post: {str(e)}")
            raise
        finally:
            db.close()
    
    def save_posts(self, posts: List[Dict[str, Any]]) -> List[Any]:
        """Save multiple posts to database"""
        repository, db = self._get_repository()
        try:
            return repository.create_posts(posts)
        finally:
            db.close()
    
    def get_existing_post_ids(self) -> Set[str]:
        """Get set of existing post IDs"""
        repository, db = self._get_repository()
        try:
            return repository.get_existing_post_ids()
        finally:
            db.close()
    
    def get_existing_permalinks(self) -> Set[str]:
        """Get set of existing permalinks"""
        repository, db = self._get_repository()
        try:
            return repository.get_existing_permalinks()
        finally:
            db.close()
    
    def update_post_status(
        self,
        post_id: str,
        status: str,
        assigned_to: Optional[str] = None
    ) -> bool:
        """Update post status and assignment"""
        repository, db = self._get_repository()
        try:
            if status == 'in_progress' and assigned_to:
                return repository.assign_post(post_id, assigned_to)
            elif status == 'replied':
                return repository.mark_replied(post_id, assigned_to)
            else:
                # Generic status update
                post = repository.get_post_by_id(post_id)
                if not post:
                    return False
                post.status = status
                if assigned_to is not None:
                    post.assigned_to = assigned_to
                db.commit()
                return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update post status: {str(e)}")
            return False
        finally:
            db.close()
    
    def get_pending_posts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get pending posts for worker dashboard"""
        repository, db = self._get_repository()
        try:
            posts = repository.get_pending_posts(limit=limit)
            return [post.to_dict() for post in posts]
        finally:
            db.close()
    
    def cleanup_old_posts(self, max_posts: int) -> int:
        """
        Clean up old posts when database exceeds max_posts limit.
        Deletes oldest posts first (by fetched_at timestamp).
        
        Args:
            max_posts: Maximum number of posts to keep in database
        
        Returns:
            Number of posts deleted
        """
        repository, db = self._get_repository()
        try:
            return repository.delete_oldest_posts(max_posts)
        finally:
            db.close()