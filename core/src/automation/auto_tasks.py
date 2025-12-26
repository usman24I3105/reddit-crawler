"""
Automated background tasks for post lifecycle management.

- Auto-expire pending posts after X days
- Auto-unassign assigned posts after Y hours
"""
from typing import List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..db.models import Post
from ..db.session import SessionLocal
from ..lifecycle import PostLifecycleService
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AutoExpireService:
    """
    Service for auto-expiring pending posts after configured days.
    
    Transitions: pending → archived (after X days)
    """
    
    def __init__(
        self,
        expire_days: int = 7,
        db: Session = None
    ):
        """
        Initialize auto-expire service.
        
        Args:
            expire_days: Number of days before pending posts are auto-expired
            db: Optional database session (creates new if not provided)
        """
        self.expire_days = expire_days
        self.db = db
    
    def expire_old_pending_posts(self) -> int:
        """
        Expire pending posts older than configured days.
        
        Returns:
            Number of posts expired
        """
        db = self.db or SessionLocal()
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.expire_days)
            
            # Find pending posts older than cutoff
            old_posts = db.query(Post).filter(
                and_(
                    Post.status == 'pending',
                    Post.fetched_at < cutoff_date
                )
            ).all()
            
            if not old_posts:
                logger.debug(f"No pending posts to expire (cutoff: {cutoff_date})")
                return 0
            
            # Expire each post using lifecycle service
            lifecycle_service = PostLifecycleService(db)
            expired_count = 0
            
            for post in old_posts:
                try:
                    success = lifecycle_service.auto_expire(post)
                    if success:
                        expired_count += 1
                except Exception as e:
                    logger.warning(f"Failed to expire post {post.reddit_post_id}: {str(e)}")
                    continue
            
            if expired_count > 0:
                logger.info(
                    f"Auto-expired {expired_count} pending posts "
                    f"(older than {self.expire_days} days)"
                )
            
            return expired_count
            
        except Exception as e:
            logger.error(f"Error in auto-expire task: {str(e)}")
            return 0
        finally:
            if not self.db:
                db.close()


class AutoUnassignService:
    """
    Service for auto-unassigning assigned posts after configured hours.
    
    Transitions: assigned → pending (after Y hours of no activity)
    """
    
    def __init__(
        self,
        unassign_hours: int = 24,
        db: Session = None
    ):
        """
        Initialize auto-unassign service.
        
        Args:
            unassign_hours: Number of hours before assigned posts are auto-unassigned
            db: Optional database session (creates new if not provided)
        """
        self.unassign_hours = unassign_hours
        self.db = db
    
    def unassign_old_assigned_posts(self) -> int:
        """
        Unassign assigned posts older than configured hours.
        
        Uses fetched_at timestamp as proxy for assignment time.
        In production, you might want a separate assigned_at field.
        
        Returns:
            Number of posts unassigned
        """
        db = self.db or SessionLocal()
        try:
            # Calculate cutoff time
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.unassign_hours)
            
            # Find assigned posts older than cutoff
            old_posts = db.query(Post).filter(
                and_(
                    Post.status == 'assigned',
                    Post.fetched_at < cutoff_time
                )
            ).all()
            
            if not old_posts:
                logger.debug(f"No assigned posts to unassign (cutoff: {cutoff_time})")
                return 0
            
            # Unassign each post using lifecycle service
            lifecycle_service = PostLifecycleService(db)
            unassigned_count = 0
            
            for post in old_posts:
                try:
                    success = lifecycle_service.auto_unassign(post)
                    if success:
                        unassigned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to unassign post {post.reddit_post_id}: {str(e)}")
                    continue
            
            if unassigned_count > 0:
                logger.info(
                    f"Auto-unassigned {unassigned_count} assigned posts "
                    f"(older than {self.unassign_hours} hours)"
                )
            
            return unassigned_count
            
        except Exception as e:
            logger.error(f"Error in auto-unassign task: {str(e)}")
            return 0
        finally:
            if not self.db:
                db.close()

