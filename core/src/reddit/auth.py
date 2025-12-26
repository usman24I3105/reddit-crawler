"""
Reddit authentication and client management.
"""
import praw
from typing import Optional
from ..config.settings import RedditConfig
from ..utils.logging import get_logger
from ..utils.exceptions import RedditAPIException

logger = get_logger(__name__)


class RedditAuth:
    """Manages Reddit API authentication and client creation"""
    
    @staticmethod
    def get_readonly_client() -> praw.Reddit:
        """
        Get a read-only Reddit client (for fetching posts).
        
        Returns:
            Authenticated Reddit client
        
        Raises:
            RedditAPIException: If authentication fails
        """
        try:
            reddit = praw.Reddit(
                client_id=RedditConfig.CLIENT_ID,
                client_secret=RedditConfig.CLIENT_SECRET,
                user_agent=RedditConfig.USER_AGENT
            )
            
            # Verify authentication
            if not reddit.read_only:
                logger.warning("Reddit client is not in read-only mode")
            
            logger.info("Reddit read-only client created successfully")
            return reddit
            
        except Exception as e:
            logger.error(f"Failed to create Reddit client: {str(e)}")
            raise RedditAPIException(f"Reddit authentication failed: {str(e)}")
    
    @staticmethod
    def get_authenticated_client() -> Optional[praw.Reddit]:
        """
        Get an authenticated Reddit client (for posting comments).
        Requires username and password in config.
        
        Returns:
            Authenticated Reddit client or None if credentials missing
        
        Raises:
            RedditAPIException: If authentication fails
        """
        if not RedditConfig.USERNAME or not RedditConfig.PASSWORD:
            logger.warning("Reddit username/password not configured. Comment posting disabled.")
            return None
        
        try:
            reddit = praw.Reddit(
                client_id=RedditConfig.CLIENT_ID,
                client_secret=RedditConfig.CLIENT_SECRET,
                user_agent=RedditConfig.USER_AGENT,
                username=RedditConfig.USERNAME,
                password=RedditConfig.PASSWORD
            )
            
            # Verify authentication by accessing user info
            try:
                _ = reddit.user.me()
                logger.info(f"Reddit authenticated client created for user: {reddit.user.me()}")
            except Exception as e:
                logger.error(f"Failed to verify Reddit authentication: {str(e)}")
                raise RedditAPIException(f"Reddit authentication verification failed: {str(e)}")
            
            return reddit
            
        except RedditAPIException:
            raise
        except Exception as e:
            logger.error(f"Failed to create authenticated Reddit client: {str(e)}")
            raise RedditAPIException(f"Reddit authentication failed: {str(e)}")

