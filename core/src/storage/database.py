"""
Database storage backend using Django ORM.
"""
from typing import List, Dict, Any, Optional, Set
from django.utils import timezone
from .base import StorageBackend
from ..utils.logging import get_logger
from ..utils.exceptions import StorageException

logger = get_logger(__name__)


class DatabaseStorage(StorageBackend):
    """Django ORM-based storage backend"""
    
    def __init__(self, model_class):
        """
        Initialize database storage.
        
        Args:
            model_class: Django model class for posts
        """
        self.model = model_class
        logger.info(f"DatabaseStorage initialized with model: {model_class.__name__}")
    
    def save_post(self, post: Dict[str, Any]) -> Any:
        """Save a single post to database"""
        try:
            # Check if post already exists (additional safety check)
            existing = self.model.objects.filter(post_id=post.get('post_id')).first()
            if existing:
                logger.debug(f"Post {post.get('post_id')} already exists, skipping")
                return existing
            
            # Create new post
            db_post = self.model.objects.create(
                post_id=post.get('post_id'),
                subreddit=post.get('subreddit'),
                title=post.get('title'),
                body=post.get('body', ''),
                author=post.get('author', '[deleted]'),
                permalink=post.get('permalink', ''),
                url=post.get('url', ''),
                upvotes=post.get('upvotes', 0),
                num_comments=post.get('num_comments', 0),
                score=post.get('score', 0),
                created_utc=post.get('created_utc'),
                fetched_at=post.get('fetched_at', timezone.now()),
                status='pending',
            )
            
            logger.debug(f"Saved post {db_post.post_id} to database")
            return db_post
            
        except Exception as e:
            logger.error(f"Failed to save post {post.get('post_id')}: {str(e)}")
            raise StorageException(f"Failed to save post: {str(e)}")
    
    def save_posts(self, posts: List[Dict[str, Any]]) -> List[Any]:
        """Save multiple posts to database"""
        saved_posts = []
        for post in posts:
            try:
                saved = self.save_post(post)
                saved_posts.append(saved)
            except StorageException as e:
                logger.warning(f"Skipping post due to error: {str(e)}")
                continue
        
        logger.info(f"Saved {len(saved_posts)}/{len(posts)} posts to database")
        return saved_posts
    
    def get_existing_post_ids(self) -> Set[str]:
        """Get set of existing post IDs"""
        try:
            post_ids = set(
                self.model.objects.values_list('post_id', flat=True)
            )
            logger.debug(f"Retrieved {len(post_ids)} existing post IDs")
            return post_ids
        except Exception as e:
            logger.error(f"Failed to get existing post IDs: {str(e)}")
            return set()
    
    def get_existing_permalinks(self) -> Set[str]:
        """Get set of existing permalinks"""
        try:
            permalinks = set(
                self.model.objects.exclude(permalink='').values_list('permalink', flat=True)
            )
            logger.debug(f"Retrieved {len(permalinks)} existing permalinks")
            return permalinks
        except Exception as e:
            logger.error(f"Failed to get existing permalinks: {str(e)}")
            return set()
    
    def update_post_status(
        self, 
        post_id: str, 
        status: str, 
        assigned_to: Optional[str] = None
    ) -> bool:
        """Update post status and assignment"""
        try:
            post = self.model.objects.filter(post_id=post_id).first()
            if not post:
                logger.warning(f"Post {post_id} not found for status update")
                return False
            
            post.status = status
            if assigned_to is not None:
                post.assigned_to = assigned_to
            post.save()
            
            logger.info(f"Updated post {post_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update post {post_id} status: {str(e)}")
            return False
    
    def get_pending_posts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get pending posts for worker dashboard"""
        try:
            queryset = self.model.objects.filter(status='pending').order_by('-fetched_at')
            if limit:
                queryset = queryset[:limit]
            
            posts = []
            for post in queryset:
                posts.append({
                    'post_id': post.post_id,
                    'subreddit': post.subreddit,
                    'title': post.title,
                    'body': post.body,
                    'author': post.author,
                    'permalink': post.permalink,
                    'url': post.url,
                    'upvotes': post.upvotes,
                    'num_comments': post.num_comments,
                    'score': post.score,
                    'created_utc': post.created_utc,
                    'fetched_at': post.fetched_at,
                    'status': post.status,
                    'assigned_to': post.assigned_to,
                })
            
            logger.info(f"Retrieved {len(posts)} pending posts")
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get pending posts: {str(e)}")
            return []

