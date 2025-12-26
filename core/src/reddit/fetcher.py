"""
Reddit post fetching service.
"""
from typing import List, Dict, Any, Optional
import praw
from datetime import datetime
from ..config.settings import CrawlerConfig
from .auth import RedditAuth
from ..utils.logging import get_logger
from ..utils.exceptions import RedditAPIException

logger = get_logger(__name__)


class RedditFetcher:
    """Fetches posts from Reddit subreddits using PRAW"""
    
    def __init__(self, reddit_client: Optional[praw.Reddit] = None):
        """
        Initialize the fetcher.
        
        Args:
            reddit_client: Optional Reddit client (creates new one if not provided)
        """
        self.reddit = reddit_client or RedditAuth.get_readonly_client()
    
    def fetch_posts_from_subreddit(
        self, 
        subreddit_name: str, 
        limit: Optional[int] = None,
        sort_by: str = 'new',
        hours_back: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Fetch posts from a specific subreddit.
        Filters posts to only include those from the last N hours.
        
        Args:
            subreddit_name: Name of the subreddit
            limit: Maximum number of posts to fetch (default: from config)
            sort_by: Sort order ('new', 'hot', 'top')
            hours_back: Only fetch posts from last N hours (default: 24)
        
        Returns:
            List of normalized post dictionaries (filtered by time)
        
        Raises:
            RedditAPIException: If fetching fails
        """
        from datetime import timedelta
        
        # No limit - fetch all posts from last N hours
        # Use a high limit to get all posts (Reddit API allows up to 1000)
        fetch_limit = 1000  # Maximum allowed by Reddit API
        
        try:
            logger.info(
                f"Fetching up to {fetch_limit} posts from r/{subreddit_name} "
                f"(sort: {sort_by}, last {hours_back} hours)"
            )
            
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Get posts based on sort order
            if sort_by == 'new':
                posts = subreddit.new(limit=fetch_limit)
            elif sort_by == 'hot':
                posts = subreddit.hot(limit=fetch_limit)
            elif sort_by == 'top':
                posts = subreddit.top(limit=fetch_limit, time_filter='day')
            else:
                posts = subreddit.new(limit=fetch_limit)
            
            normalized_posts = []
            for post in posts:
                try:
                    # Check if post is within time window
                    post_time = datetime.utcfromtimestamp(post.created_utc) if post.created_utc else None
                    if post_time and post_time < cutoff_time:
                        continue  # Skip posts older than cutoff
                    
                    normalized = self._normalize_post(post, subreddit_name)
                    normalized_posts.append(normalized)
                    
                    # No limit - collect all posts within time window
                        
                except Exception as e:
                    logger.warning(f"Failed to normalize post {post.id}: {str(e)}")
                    continue
            
            logger.info(
                f"Successfully fetched {len(normalized_posts)} posts from r/{subreddit_name} "
                f"(filtered to last {hours_back} hours)"
            )
            return normalized_posts
            
        except Exception as e:
            logger.error(f"Failed to fetch posts from r/{subreddit_name}: {str(e)}")
            raise RedditAPIException(f"Failed to fetch posts: {str(e)}")
    
    def search_posts_by_keywords(
        self,
        keywords: List[str],
        subreddit_name: Optional[str] = None,
        limit: Optional[int] = None,
        hours_back: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Search for posts using Reddit search API with keywords.
        This is more efficient than fetching all posts and filtering.
        
        Args:
            keywords: List of keywords to search for
            subreddit_name: Optional subreddit to search in (searches all if None)
            limit: Maximum number of posts to return
            hours_back: Only return posts from last N hours
        
        Returns:
            List of normalized post dictionaries matching keywords
        """
        from datetime import timedelta
        from ..config.settings import FilterConfig
        
        # No limit - fetch all matching posts
        all_posts = []
        
        # Build search query - Reddit search has limitations, so we'll search in batches
        # Reddit search API has a limit, so we'll use multiple smaller queries
        batch_size = 25  # Reddit search works best with smaller queries
        all_keywords = keywords[:100]  # Limit to 100 keywords to avoid query too long
        
        try:
            logger.info(f"Searching Reddit for {len(all_keywords)} keywords (last {hours_back} hours)")
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Search in batches
            for i in range(0, len(all_keywords), batch_size):
                batch = all_keywords[i:i+batch_size]
                query = ' OR '.join(batch)
                
                try:
                    if subreddit_name:
                        # Search in specific subreddit
                        subreddit = self.reddit.subreddit(subreddit_name)
                        search_results = subreddit.search(
                            query,
                            sort='new',
                            time_filter='day',
                            limit=1000  # Maximum allowed
                        )
                    else:
                        # Search across all Reddit
                        search_results = self.reddit.subreddit('all').search(
                            query,
                            sort='new',
                            time_filter='day',
                            limit=1000
                        )
                    
                    for post in search_results:
                        try:
                            # Check if post is within time window
                            post_time = datetime.utcfromtimestamp(post.created_utc) if post.created_utc else None
                            if post_time and post_time < cutoff_time:
                                continue
                            
                            # Get subreddit name
                            subreddit_name_found = post.subreddit.display_name if hasattr(post.subreddit, 'display_name') else 'unknown'
                            
                            normalized = self._normalize_post(post, subreddit_name_found)
                            all_posts.append(normalized)
                        except Exception as e:
                            logger.warning(f"Failed to normalize search result {post.id}: {str(e)}")
                            continue
                except Exception as e:
                    logger.warning(f"Search batch failed: {str(e)}")
                    continue
                        
                except Exception as e:
                    logger.warning(f"Failed to normalize search result {post.id}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(all_posts)} posts matching keywords: {query}")
            return all_posts
            
        except Exception as e:
            logger.error(f"Reddit search failed: {str(e)}")
            # Fallback to regular fetching if search fails
            logger.info("Falling back to regular subreddit fetching")
            return []
    
    def fetch_all_configured_subreddits(self) -> List[Dict[str, Any]]:
        """
        Fetch posts from all configured subreddits.
        Fetches all posts from last 12 hours (no limit).
        Keyword filtering is handled by the pipeline's KeywordFilter.
        
        Returns:
            List of all normalized posts from all subreddits
        """
        all_posts = []
        
        # Fetch all posts from subreddits (no limit, last 12 hours)
        # Keyword filtering will be done by the pipeline
        logger.info("Fetching all posts from configured subreddits (last 12 hours, no limit)")
        for subreddit_name in CrawlerConfig.SUBREDDITS:
            try:
                posts = self.fetch_posts_from_subreddit(
                    subreddit_name=subreddit_name,
                    limit=None,  # No limit
                    sort_by='new',
                    hours_back=12  # Last 12 hours
                )
                all_posts.extend(posts)
                logger.info(f"Fetched {len(posts)} posts from r/{subreddit_name}")
            except RedditAPIException as e:
                logger.error(f"Skipping r/{subreddit_name} due to error: {str(e)}")
                continue
        
        logger.info(f"Total posts fetched from all subreddits: {len(all_posts)}")
        return all_posts
    
    def _normalize_post(self, post: praw.models.Submission, subreddit_name: str) -> Dict[str, Any]:
        """
        Normalize a Reddit post to a standard dictionary format.
        
        Args:
            post: PRAW Submission object
            subreddit_name: Name of the subreddit
        
        Returns:
            Normalized post dictionary
        """
        # Get post body (selftext)
        body = post.selftext or ""
        
        # Get engagement metrics
        upvotes = post.score or 0
        num_comments = post.num_comments or 0
        
        # Get permalink (relative URL)
        permalink = post.permalink
        
        # Get created datetime
        created_utc = datetime.utcfromtimestamp(post.created_utc) if post.created_utc else datetime.utcnow()
        
        return {
            'post_id': post.id,
            'subreddit': subreddit_name,
            'title': post.title,
            'body': body,
            'author': post.author.name if post.author else '[deleted]',
            'permalink': permalink,
            'url': post.url,
            'upvotes': upvotes,
            'num_comments': num_comments,
            'score': post.score or 0,
            'created_utc': created_utc,
            'is_self': post.is_self,
            'over_18': post.over_18,
            'fetched_at': datetime.utcnow(),
        }
    
    def fetch_comments_for_post(
        self,
        post_id: str,
        limit: Optional[int] = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch comments for a specific Reddit post.
        
        Args:
            post_id: Reddit post ID
            limit: Maximum number of comments to fetch (default: 50)
        
        Returns:
            List of normalized comment dictionaries
        
        Raises:
            RedditAPIException: If fetching fails
        """
        try:
            logger.info(f"Fetching comments for post {post_id} (limit: {limit})")
            
            # Get the submission object
            submission = self.reddit.submission(id=post_id)
            
            # Replace "more" comments with actual comments
            submission.comments.replace_more(limit=0)  # Remove "load more" placeholders
            
            # Get top-level comments
            comments = submission.comments.list()[:limit]
            
            normalized_comments = []
            for comment in comments:
                try:
                    # Skip if it's a MoreComments object (shouldn't happen after replace_more)
                    if hasattr(comment, 'body'):
                        normalized = self._normalize_comment(comment, post_id)
                        normalized_comments.append(normalized)
                except Exception as e:
                    logger.warning(f"Failed to normalize comment {comment.id if hasattr(comment, 'id') else 'unknown'}: {str(e)}")
                    continue
            
            logger.info(f"Successfully fetched {len(normalized_comments)} comments for post {post_id}")
            return normalized_comments
            
        except Exception as e:
            logger.error(f"Failed to fetch comments for post {post_id}: {str(e)}")
            raise RedditAPIException(f"Failed to fetch comments: {str(e)}")
    
    def _normalize_comment(self, comment: praw.models.Comment, post_id: str) -> Dict[str, Any]:
        """
        Normalize a Reddit comment to a standard dictionary format.
        
        Args:
            comment: PRAW Comment object
            post_id: Reddit post ID this comment belongs to
        
        Returns:
            Normalized comment dictionary
        """
        # Get comment body
        body = comment.body or ""
        
        # Get engagement metrics
        upvotes = comment.score or 0
        
        # Get permalink (relative URL)
        permalink = comment.permalink
        
        # Get created datetime
        created_utc = datetime.utcfromtimestamp(comment.created_utc) if comment.created_utc else datetime.utcnow()
        
        return {
            'comment_id': comment.id,
            'post_id': post_id,
            'body': body,
            'author': comment.author.name if comment.author else '[deleted]',
            'permalink': permalink,
            'upvotes': upvotes,
            'score': comment.score or 0,
            'created_utc': created_utc,
            'fetched_at': datetime.utcnow(),
        }

