"""
Reddit comment posting service with rate limiting and retry logic.
"""
import time
from typing import Optional
import praw
from ..config.settings import CommentConfig, RedditConfig
from .auth import RedditAuth
from ..utils.logging import get_logger
from ..utils.exceptions import CommentPostingException, RedditAPIException

logger = get_logger(__name__)


class RedditCommenter:
    """Handles posting comments to Reddit posts with rate limiting and error handling"""
    
    def __init__(self, reddit_client: Optional[praw.Reddit] = None):
        """
        Initialize the commenter.
        
        Args:
            reddit_client: Optional authenticated Reddit client
        """
        if not CommentConfig.ENABLE_COMMENT_POSTING:
            logger.info("Comment posting is disabled in configuration")
            self.reddit = None
            return
        
        self.reddit = reddit_client or RedditAuth.get_authenticated_client()
        if not self.reddit:
            logger.warning("Comment posting requested but authentication failed")
    
    def post_comment(
        self, 
        post_id: str, 
        comment_text: str,
        retries: Optional[int] = None
    ) -> Optional[praw.models.Comment]:
        """
        Post a comment to a Reddit post.
        
        Args:
            post_id: Reddit post ID
            comment_text: Text of the comment to post
            retries: Number of retry attempts (default: from config)
        
        Returns:
            Posted comment object or None if posting is disabled
        
        Raises:
            CommentPostingException: If posting fails after retries
        """
        if not self.reddit:
            logger.warning("Comment posting is disabled or authentication failed")
            return None
        
        retries = retries or CommentConfig.COMMENT_MAX_RETRIES
        
        for attempt in range(retries):
            try:
                logger.info(f"Posting comment to post {post_id} (attempt {attempt + 1}/{retries})")
                
                # Get the submission
                submission = self.reddit.submission(id=post_id)
                
                # Post the comment
                comment = submission.reply(comment_text)
                
                # Rate limiting delay
                time.sleep(CommentConfig.COMMENT_RATE_LIMIT_DELAY)
                
                logger.info(f"Successfully posted comment {comment.id} to post {post_id}")
                return comment
                
            except praw.exceptions.RedditAPIException as e:
                error_message = str(e)
                
                # Handle rate limiting
                if 'RATELIMIT' in error_message.upper():
                    wait_time = self._extract_rate_limit_time(error_message)
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                # Handle other API errors
                logger.error(f"Reddit API error on attempt {attempt + 1}: {error_message}")
                if attempt == retries - 1:
                    raise CommentPostingException(f"Failed to post comment after {retries} attempts: {error_message}")
                
            except Exception as e:
                logger.error(f"Unexpected error posting comment (attempt {attempt + 1}): {str(e)}")
                if attempt == retries - 1:
                    raise CommentPostingException(f"Failed to post comment after {retries} attempts: {str(e)}")
                
                # Exponential backoff
                time.sleep(2 ** attempt)
        
        return None
    
    def _extract_rate_limit_time(self, error_message: str) -> int:
        """
        Extract wait time from Reddit rate limit error message.
        
        Args:
            error_message: Error message from Reddit API
        
        Returns:
            Wait time in seconds (default: configured delay)
        """
        # Reddit rate limit messages often contain time like "try again in 10 minutes"
        # This is a simple parser - can be enhanced
        import re
        match = re.search(r'(\d+)\s*(minute|second|hour)', error_message.lower())
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            if 'minute' in unit:
                return value * 60
            elif 'hour' in unit:
                return value * 3600
            else:
                return value
        
        return CommentConfig.COMMENT_RATE_LIMIT_DELAY

