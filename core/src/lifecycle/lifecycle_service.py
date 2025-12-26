"""
Post lifecycle service with strict state machine validation.

States: fetched → pending → assigned → replied → archived

All transitions must be validated server-side.
"""
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy.orm import Session
from ..db.models import Post, PostStatusLog
from ..utils.logging import get_logger

logger = get_logger(__name__)


class PostStatus(Enum):
    """Post lifecycle states"""
    FETCHED = 'fetched'
    PENDING = 'pending'
    ASSIGNED = 'assigned'
    REPLIED = 'replied'
    ARCHIVED = 'archived'


class LifecycleException(Exception):
    """Exception raised for invalid lifecycle transitions"""
    pass


class PostLifecycleService:
    """
    Service for managing post lifecycle with strict state machine.
    
    Valid transitions:
    - fetched → pending (automatic on save)
    - pending → assigned (worker assignment)
    - assigned → replied (after reply)
    - replied → archived (manual archive)
    - pending → archived (auto-expire)
    - assigned → pending (auto-unassign timeout)
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        PostStatus.FETCHED: {PostStatus.PENDING},
        PostStatus.PENDING: {PostStatus.ASSIGNED, PostStatus.ARCHIVED},
        PostStatus.ASSIGNED: {PostStatus.REPLIED, PostStatus.PENDING},
        PostStatus.REPLIED: {PostStatus.ARCHIVED},
        PostStatus.ARCHIVED: set(),  # Terminal state, no transitions
    }
    
    def __init__(self, db: Session):
        """
        Initialize lifecycle service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def validate_transition(
        self,
        current_status: str,
        new_status: str
    ) -> bool:
        """
        Validate if a state transition is allowed.
        
        Args:
            current_status: Current post status
            new_status: Desired new status
        
        Returns:
            True if transition is valid, False otherwise
        
        Raises:
            LifecycleException: If transition is invalid
        """
        try:
            current = PostStatus(current_status.lower())
            new = PostStatus(new_status.lower())
        except ValueError:
            raise LifecycleException(f"Invalid status: {current_status} or {new_status}")
        
        # Same status is always valid (idempotent)
        if current == new:
            return True
        
        # Check if transition is allowed
        allowed = self.VALID_TRANSITIONS.get(current, set())
        if new not in allowed:
            raise LifecycleException(
                f"Invalid transition: {current.value} → {new.value}. "
                f"Allowed transitions from {current.value}: {[s.value for s in allowed]}"
            )
        
        return True
    
    def transition_status(
        self,
        post: Post,
        new_status: str,
        changed_by: Optional[str] = None,
        change_reason: Optional[str] = None
    ) -> bool:
        """
        Transition post to new status with validation and logging.
        
        Args:
            post: Post instance
            new_status: New status to transition to
            changed_by: Who/what made the change (user or 'system')
            change_reason: Reason for change (e.g., 'auto_expire', 'manual_assign')
        
        Returns:
            True if transition successful, False otherwise
        
        Raises:
            LifecycleException: If transition is invalid
        """
        old_status = post.status
        
        # Validate transition
        self.validate_transition(old_status, new_status)
        
        # Update post status
        post.status = new_status.lower()
        
        # Log status change
        self._log_status_change(
            post=post,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by or 'system',
            change_reason=change_reason or 'manual'
        )
        
        try:
            self.db.commit()
            logger.info(
                f"Post {post.reddit_post_id} status changed: "
                f"{old_status} → {new_status} (by: {changed_by}, reason: {change_reason})"
            )
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to transition post status: {str(e)}")
            raise LifecycleException(f"Failed to update status: {str(e)}")
    
    def _log_status_change(
        self,
        post: Post,
        old_status: str,
        new_status: str,
        changed_by: str,
        change_reason: str
    ) -> None:
        """
        Log status change to audit trail.
        
        Args:
            post: Post instance
            old_status: Previous status
            new_status: New status
            changed_by: Who made the change
            change_reason: Reason for change
        """
        try:
            log_entry = PostStatusLog(
                post_id=post.id,
                reddit_post_id=post.reddit_post_id,
                old_status=old_status,
                new_status=new_status.lower(),
                changed_by=changed_by,
                change_reason=change_reason
            )
            self.db.add(log_entry)
        except Exception as e:
            logger.warning(f"Failed to log status change: {str(e)}")
            # Don't fail the transaction if logging fails
    
    def assign_post(
        self,
        post: Post,
        assigned_to: str,
        changed_by: Optional[str] = None
    ) -> bool:
        """
        Assign post to worker (pending → assigned).
        
        Args:
            post: Post instance
            assigned_to: Worker identifier
            changed_by: Who assigned the post
        
        Returns:
            True if assignment successful
        
        Raises:
            LifecycleException: If post is not in pending status
        """
        if post.status != PostStatus.PENDING.value:
            raise LifecycleException(
                f"Cannot assign post in status '{post.status}'. "
                f"Post must be in 'pending' status."
            )
        
        post.assigned_to = assigned_to
        return self.transition_status(
            post=post,
            new_status=PostStatus.ASSIGNED.value,
            changed_by=changed_by or assigned_to,
            change_reason='manual_assign'
        )
    
    def mark_replied(
        self,
        post: Post,
        changed_by: Optional[str] = None
    ) -> bool:
        """
        Mark post as replied (assigned → replied).
        
        Args:
            post: Post instance
            changed_by: Who marked as replied
        
        Returns:
            True if successful
        
        Raises:
            LifecycleException: If post is not in assigned status
        """
        if post.status != PostStatus.ASSIGNED.value:
            raise LifecycleException(
                f"Cannot mark post as replied in status '{post.status}'. "
                f"Post must be in 'assigned' status."
            )
        
        return self.transition_status(
            post=post,
            new_status=PostStatus.REPLIED.value,
            changed_by=changed_by or 'system',
            change_reason='reply_posted'
        )
    
    def archive_post(
        self,
        post: Post,
        changed_by: Optional[str] = None
    ) -> bool:
        """
        Archive post (replied → archived or pending → archived).
        
        Args:
            post: Post instance
            changed_by: Who archived the post
        
        Returns:
            True if successful
        
        Raises:
            LifecycleException: If post cannot be archived from current status
        """
        if post.status not in {PostStatus.REPLIED.value, PostStatus.PENDING.value}:
            raise LifecycleException(
                f"Cannot archive post in status '{post.status}'. "
                f"Post must be in 'replied' or 'pending' status."
            )
        
        return self.transition_status(
            post=post,
            new_status=PostStatus.ARCHIVED.value,
            changed_by=changed_by or 'system',
            change_reason='manual_archive'
        )
    
    def auto_expire(
        self,
        post: Post
    ) -> bool:
        """
        Auto-expire pending post (pending → archived).
        
        Args:
            post: Post instance
        
        Returns:
            True if expired, False if post not in pending status
        """
        if post.status != PostStatus.PENDING.value:
            return False
        
        return self.transition_status(
            post=post,
            new_status=PostStatus.ARCHIVED.value,
            changed_by='system',
            change_reason='auto_expire'
        )
    
    def auto_unassign(
        self,
        post: Post
    ) -> bool:
        """
        Auto-unassign assigned post (assigned → pending).
        
        Args:
            post: Post instance
        
        Returns:
            True if unassigned, False if post not in assigned status
        """
        if post.status != PostStatus.ASSIGNED.value:
            return False
        
        post.assigned_to = None
        return self.transition_status(
            post=post,
            new_status=PostStatus.PENDING.value,
            changed_by='system',
            change_reason='auto_unassign'
        )


