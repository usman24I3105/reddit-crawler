"""
Repository pattern for database operations.
Clean separation of database logic from business logic.
"""
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from datetime import datetime, timezone
from .models import Post, Comment
from ..lifecycle import PostLifecycleService
from ..utils.logging import get_logger
from ..utils.exceptions import StorageException

logger = get_logger(__name__)


class PostRepository:
    """
    Repository for Post model operations.
    Provides clean interface for database access.
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.lifecycle_service = PostLifecycleService(db)
    
    def create_post(self, post_data: Dict[str, Any]) -> Post:
        """
        Create a new post.
        Handles duplicate reddit_post_id gracefully.
        
        Args:
            post_data: Dictionary with post fields
            
        Returns:
            Post instance (existing if duplicate, new if created)
            
        Raises:
            StorageException: If save fails for non-duplicate reasons
        """
        try:
            # Map field names from pipeline format to model format
            post = Post(
                reddit_post_id=post_data.get('post_id'),
                subreddit=post_data.get('subreddit'),
                title=post_data.get('title'),
                body=post_data.get('body', ''),
                author=post_data.get('author', '[deleted]'),
                permalink=post_data.get('permalink', ''),
                url=post_data.get('url', ''),
                upvotes=post_data.get('upvotes', 0),
                comments=post_data.get('num_comments', 0),  # Map num_comments to comments
                score=post_data.get('score', 0),
                status='fetched',  # Initial state: fetched
                created_utc=post_data.get('created_utc'),
                fetched_at=post_data.get('fetched_at', datetime.now(timezone.utc)),
            )
            
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            
            # Transition to pending (fetched → pending)
            try:
                self.lifecycle_service.transition_status(
                    post=post,
                    new_status='pending',
                    changed_by='system',
                    change_reason='post_created'
                )
            except Exception as e:
                logger.warning(f"Failed to transition post to pending: {str(e)}")
                # Post is still created, just in 'fetched' state
            
            logger.debug(f"Created post {post.reddit_post_id} (status: {post.status})")
            return post
            
        except IntegrityError as e:
            # Handle duplicate reddit_post_id gracefully
            self.db.rollback()
            
            # Try to get existing post
            if post_data.get('post_id'):
                existing = self.db.query(Post).filter(
                    Post.reddit_post_id == post_data.get('post_id')
                ).first()
                if existing:
                    logger.debug(f"Post {post_data.get('post_id')} already exists, returning existing")
                    return existing
            
            # If we can't find existing, log and re-raise
            logger.warning(f"Integrity error on post {post_data.get('post_id')}: {str(e)}")
            raise StorageException(f"Failed to create post due to constraint violation: {str(e)}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create post {post_data.get('post_id')}: {str(e)}")
            raise StorageException(f"Failed to create post: {str(e)}")
    
    def create_posts(self, posts_data: List[Dict[str, Any]]) -> List[Post]:
        """
        Create multiple posts.
        Handles duplicates gracefully, continuing with other posts.
        
        Args:
            posts_data: List of post dictionaries
            
        Returns:
            List of Post instances (created or existing)
        """
        saved_posts = []
        for post_data in posts_data:
            try:
                post = self.create_post(post_data)
                saved_posts.append(post)
            except StorageException as e:
                logger.warning(f"Skipping post due to error: {str(e)}")
                continue
        
        logger.info(f"Created {len(saved_posts)}/{len(posts_data)} posts")
        return saved_posts
    
    def get_pending_posts(
        self,
        limit: Optional[int] = None,
        subreddit: Optional[str] = None
    ) -> List[Post]:
        """
        Get pending posts for worker dashboard.
        
        Args:
            limit: Maximum number of posts to return
            subreddit: Optional filter by subreddit
            
        Returns:
            List of Post instances
        """
        try:
            query = self.db.query(Post).filter(Post.status == 'pending')
            
            if subreddit:
                query = query.filter(Post.subreddit == subreddit)
            
            query = query.order_by(Post.fetched_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            posts = query.all()
            logger.info(f"Retrieved {len(posts)} pending posts")
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get pending posts: {str(e)}")
            return []
    
    def assign_post(self, reddit_post_id: str, assigned_to: str) -> bool:
        """
        Assign a post to a worker (pending → assigned).
        Uses lifecycle service for validation.
        
        Args:
            reddit_post_id: Reddit post ID
            assigned_to: Worker identifier
        
        Returns:
            True if successful, False if post not found or invalid transition
        """
        try:
            post = self.db.query(Post).filter(
                Post.reddit_post_id == reddit_post_id
            ).first()
            
            if not post:
                logger.warning(f"Post {reddit_post_id} not found for assignment")
                return False
            
            # Use lifecycle service for validated transition
            self.lifecycle_service.assign_post(
                post=post,
                assigned_to=assigned_to,
                changed_by=assigned_to
            )
            
            logger.info(f"Assigned post {reddit_post_id} to {assigned_to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign post {reddit_post_id}: {str(e)}")
            return False
    
    def mark_replied(self, reddit_post_id: str, assigned_to: Optional[str] = None) -> bool:
        """
        Mark a post as replied (assigned → replied).
        
        Uses lifecycle service to enforce state machine rules.
        
        Args:
            reddit_post_id: Reddit post ID
            assigned_to: Optional worker identifier (for verification)
            
        Returns:
            True if successful, False if post not found or invalid transition
        
        Raises:
            LifecycleException: If post is not in assigned status
        """
        try:
            post = self.db.query(Post).filter(
                Post.reddit_post_id == reddit_post_id
            ).first()
            
            if not post:
                logger.warning(f"Post {reddit_post_id} not found")
                return False
            
            # Verify assignment if assigned_to is provided
            if assigned_to and post.assigned_to != assigned_to:
                logger.warning(
                    f"Post {reddit_post_id} is assigned to {post.assigned_to}, "
                    f"not {assigned_to}"
                )
                return False
            
            # Use lifecycle service to mark as replied (validates transition)
            self.lifecycle_service.mark_replied(
                post=post,
                changed_by=assigned_to or 'system'
            )
            
            logger.info(f"Marked post {reddit_post_id} as replied")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to mark post {reddit_post_id} as replied: {str(e)}")
            return False
    
    def get_existing_post_ids(self) -> Set[str]:
        """
        Get set of existing post IDs for deduplication.
        
        Returns:
            Set of reddit_post_id strings (excluding None)
        """
        try:
            post_ids = set(
                self.db.query(Post.reddit_post_id)
                .filter(Post.reddit_post_id.isnot(None))
                .all()
            )
            # Unpack tuples from query result
            post_ids = {pid[0] for pid in post_ids if pid[0]}
            logger.debug(f"Retrieved {len(post_ids)} existing post IDs")
            return post_ids
        except Exception as e:
            logger.error(f"Failed to get existing post IDs: {str(e)}")
            return set()
    
    def get_existing_permalinks(self) -> Set[str]:
        """
        Get set of existing permalinks for deduplication.
        
        Returns:
            Set of permalink strings (excluding empty/None)
        """
        try:
            permalinks = set(
                self.db.query(Post.permalink)
                .filter(
                    and_(
                        Post.permalink.isnot(None),
                        Post.permalink != ''
                    )
                )
                .all()
            )
            # Unpack tuples from query result
            permalinks = {pl[0] for pl in permalinks if pl[0]}
            logger.debug(f"Retrieved {len(permalinks)} existing permalinks")
            return permalinks
        except Exception as e:
            logger.error(f"Failed to get existing permalinks: {str(e)}")
            return set()
    
    def get_post_by_id(self, reddit_post_id: str) -> Optional[Post]:
        """
        Get a post by reddit_post_id.
        
        Args:
            reddit_post_id: Reddit post ID
            
        Returns:
            Post instance or None if not found
        """
        return self.db.query(Post).filter(
            Post.reddit_post_id == reddit_post_id
        ).first()
    
    def get_total_count(self) -> int:
        """
        Get total number of posts in database.
        
        Returns:
            Total count of posts
        """
        try:
            return self.db.query(Post).count()
        except Exception as e:
            logger.error(f"Failed to get post count: {str(e)}")
            return 0
    
    def delete_oldest_posts(self, max_posts: int) -> int:
        """
        Delete oldest posts when database exceeds max_posts limit.
        Deletes posts starting with the oldest (by fetched_at timestamp).
        
        Args:
            max_posts: Maximum number of posts to keep
        
        Returns:
            Number of posts deleted
        """
        try:
            total_count = self.get_total_count()
            
            if total_count <= max_posts:
                logger.debug(f"Database has {total_count} posts, limit is {max_posts}. No cleanup needed.")
                return 0
            
            # Calculate how many posts to delete
            posts_to_delete = total_count - max_posts
            
            # Get oldest posts (ordered by fetched_at ascending)
            oldest_posts = (
                self.db.query(Post)
                .order_by(Post.fetched_at.asc())
                .limit(posts_to_delete)
                .all()
            )
            
            if not oldest_posts:
                logger.warning("No posts found to delete despite count exceeding limit")
                return 0
            
            # Delete the oldest posts
            deleted_count = 0
            for post in oldest_posts:
                try:
                    self.db.delete(post)
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete post {post.reddit_post_id}: {str(e)}")
                    continue
            
            self.db.commit()
            
            logger.info(
                f"Database cleanup: Deleted {deleted_count} oldest posts. "
                f"Database now has {total_count - deleted_count} posts (limit: {max_posts})"
            )
            
            return deleted_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete oldest posts: {str(e)}")
            return 0
    
    def create_comment(self, comment_data: Dict[str, Any]) -> Comment:
        """
        Create a new comment.
        Handles duplicate reddit_comment_id gracefully.
        
        Args:
            comment_data: Dictionary with comment fields
            
        Returns:
            Comment instance (existing if duplicate, new if created)
        """
        try:
            # Get post_id from reddit_post_id if needed
            reddit_post_id = comment_data.get('post_id') or comment_data.get('reddit_post_id')
            if not reddit_post_id:
                raise StorageException("reddit_post_id is required to create comment")
            
            # Get the post to get the database post_id
            post = self.get_post_by_id(reddit_post_id)
            if not post:
                raise StorageException(f"Post {reddit_post_id} not found")
            
            comment = Comment(
                reddit_comment_id=comment_data.get('comment_id'),
                post_id=post.id,
                reddit_post_id=reddit_post_id,
                body=comment_data.get('body', ''),
                author=comment_data.get('author', '[deleted]'),
                permalink=comment_data.get('permalink', ''),
                upvotes=comment_data.get('upvotes', 0),
                score=comment_data.get('score', 0),
                created_utc=comment_data.get('created_utc'),
                fetched_at=comment_data.get('fetched_at', datetime.now(timezone.utc)),
            )
            
            self.db.add(comment)
            self.db.commit()
            self.db.refresh(comment)
            
            logger.debug(f"Created comment {comment.reddit_comment_id}")
            return comment
            
        except IntegrityError as e:
            # Handle duplicate reddit_comment_id gracefully
            self.db.rollback()
            
            # Try to get existing comment
            if comment_data.get('comment_id'):
                existing = self.db.query(Comment).filter(
                    Comment.reddit_comment_id == comment_data.get('comment_id')
                ).first()
                if existing:
                    logger.debug(f"Comment {comment_data.get('comment_id')} already exists, returning existing")
                    return existing
            
            logger.warning(f"Integrity error on comment {comment_data.get('comment_id')}: {str(e)}")
            raise StorageException(f"Failed to create comment due to constraint violation: {str(e)}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create comment {comment_data.get('comment_id')}: {str(e)}")
            raise StorageException(f"Failed to create comment: {str(e)}")
    
    def create_comments(self, comments_data: List[Dict[str, Any]]) -> List[Comment]:
        """
        Create multiple comments.
        Handles duplicates gracefully, continuing with other comments.
        
        Args:
            comments_data: List of comment dictionaries
            
        Returns:
            List of Comment instances (created or existing)
        """
        saved_comments = []
        for comment_data in comments_data:
            try:
                comment = self.create_comment(comment_data)
                saved_comments.append(comment)
            except StorageException as e:
                logger.warning(f"Skipping comment due to error: {str(e)}")
                continue
        
        logger.info(f"Created {len(saved_comments)}/{len(comments_data)} comments")
        return saved_comments
    
    def get_comments_for_post(
        self,
        reddit_post_id: str,
        limit: Optional[int] = None
    ) -> List[Comment]:
        """
        Get comments for a specific post.
        
        Args:
            reddit_post_id: Reddit post ID
            limit: Maximum number of comments to return
            
        Returns:
            List of Comment instances
        """
        try:
            query = self.db.query(Comment).filter(
                Comment.reddit_post_id == reddit_post_id
            ).order_by(Comment.created_utc.desc() if Comment.created_utc else Comment.fetched_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            comments = query.all()
            logger.info(f"Retrieved {len(comments)} comments for post {reddit_post_id}")
            return comments
            
        except Exception as e:
            logger.error(f"Failed to get comments for post {reddit_post_id}: {str(e)}")
            return []

