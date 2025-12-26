"""
Action validator for post lifecycle.

Enforces allowed actions per status:
- pending: view, assign_to_worker, auto_expire (block: reply, reassign)
- assigned: view, reply, auto_unassign (block: assign_to_another_worker)
- replied: view, archive, internal_note (block: reply_again, edit_reply)
- archived: view only (block: all mutations)
"""
from typing import Set, Optional
from enum import Enum
from ..db.models import Post
from ..utils.logging import get_logger

logger = get_logger(__name__)


class PostAction(Enum):
    """Allowed post actions"""
    VIEW = 'view'
    ASSIGN_TO_WORKER = 'assign_to_worker'
    REPLY = 'reply'
    ARCHIVE = 'archive'
    INTERNAL_NOTE = 'internal_note'
    AUTO_EXPIRE = 'auto_expire'
    AUTO_UNASSIGN = 'auto_unassign'
    REASSIGN = 'reassign'
    REPLY_AGAIN = 'reply_again'
    EDIT_REPLY = 'edit_reply'


class ActionException(Exception):
    """Exception raised for invalid actions"""
    pass


class ActionValidator:
    """
    Validates allowed actions per post status.
    
    Enforces strict rules:
    - pending: view, assign_to_worker, auto_expire
    - assigned: view, reply, auto_unassign
    - replied: view, archive, internal_note
    - archived: view only
    """
    
    # Allowed actions per status
    ALLOWED_ACTIONS = {
        'fetched': {PostAction.VIEW},  # Initial state, minimal actions
        'pending': {
            PostAction.VIEW,
            PostAction.ASSIGN_TO_WORKER,
            PostAction.AUTO_EXPIRE,
        },
        'assigned': {
            PostAction.VIEW,
            PostAction.REPLY,
            PostAction.AUTO_UNASSIGN,
        },
        'replied': {
            PostAction.VIEW,
            PostAction.ARCHIVE,
            PostAction.INTERNAL_NOTE,
        },
        'archived': {
            PostAction.VIEW,
        },
    }
    
    # Blocked actions per status (for clearer error messages)
    BLOCKED_ACTIONS = {
        'pending': {
            PostAction.REPLY,
            PostAction.REASSIGN,
        },
        'assigned': {
            PostAction.ASSIGN_TO_WORKER,  # Cannot reassign
        },
        'replied': {
            PostAction.REPLY_AGAIN,
            PostAction.EDIT_REPLY,
        },
        'archived': {
            PostAction.ASSIGN_TO_WORKER,
            PostAction.REPLY,
            PostAction.ARCHIVE,
            PostAction.INTERNAL_NOTE,
            PostAction.AUTO_EXPIRE,
            PostAction.AUTO_UNASSIGN,
            PostAction.REASSIGN,
            PostAction.REPLY_AGAIN,
            PostAction.EDIT_REPLY,
        },
    }
    
    @classmethod
    def validate_action(
        cls,
        post: Post,
        action: PostAction,
        user: Optional[str] = None
    ) -> bool:
        """
        Validate if action is allowed for post status.
        
        Args:
            post: Post instance
            action: Action to validate
            user: Optional user identifier (for ownership checks)
        
        Returns:
            True if action is allowed
        
        Raises:
            ActionException: If action is not allowed
        """
        status = post.status.lower()
        
        # Check if action is allowed
        allowed = cls.ALLOWED_ACTIONS.get(status, set())
        if action not in allowed:
            blocked = cls.BLOCKED_ACTIONS.get(status, set())
            if action in blocked:
                raise ActionException(
                    f"Action '{action.value}' is blocked for posts in '{status}' status. "
                    f"Allowed actions: {[a.value for a in allowed]}"
                )
            else:
                raise ActionException(
                    f"Action '{action.value}' is not allowed for posts in '{status}' status. "
                    f"Allowed actions: {[a.value for a in allowed]}"
                )
        
        # Additional validation for specific actions
        if action == PostAction.REPLY:
            if post.assigned_to != user:
                raise ActionException(
                    f"Post is assigned to '{post.assigned_to}', not '{user}'. "
                    f"Cannot reply to post assigned to another worker."
                )
        
        if action == PostAction.ASSIGN_TO_WORKER:
            if post.assigned_to and post.assigned_to != user:
                raise ActionException(
                    f"Post is already assigned to '{post.assigned_to}'. "
                    f"Cannot reassign."
                )
        
        return True
    
    @classmethod
    def get_allowed_actions(cls, post: Post) -> Set[PostAction]:
        """
        Get set of allowed actions for post status.
        
        Args:
            post: Post instance
        
        Returns:
            Set of allowed PostAction enums
        """
        status = post.status.lower()
        return cls.ALLOWED_ACTIONS.get(status, set())
    
    @classmethod
    def can_perform_action(
        cls,
        post: Post,
        action: PostAction,
        user: Optional[str] = None
    ) -> bool:
        """
        Check if action can be performed (non-raising version).
        
        Args:
            post: Post instance
            action: Action to check
            user: Optional user identifier
        
        Returns:
            True if action is allowed, False otherwise
        """
        try:
            cls.validate_action(post, action, user)
            return True
        except ActionException:
            return False


