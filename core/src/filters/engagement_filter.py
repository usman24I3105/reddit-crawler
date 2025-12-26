"""
Engagement-based filtering for Reddit posts.
"""
from typing import List, Dict, Any, Optional
from ..config.settings import FilterConfig
from ..utils.logging import get_logger
from ..utils.exceptions import FilterException

logger = get_logger(__name__)


class EngagementFilter:
    """Filters posts based on engagement metrics (upvotes, comments)"""
    
    def __init__(
        self,
        min_upvotes: Optional[int] = None,
        min_comments: Optional[int] = None,
        use_score_weighting: Optional[bool] = None,
        score_weight: Optional[float] = None
    ):
        """
        Initialize the engagement filter.
        
        Args:
            min_upvotes: Minimum upvotes required (default: from config)
            min_comments: Minimum comments required (default: from config)
            use_score_weighting: Whether to use score weighting (default: from config)
            score_weight: Score weight multiplier (default: from config)
        """
        self.min_upvotes = min_upvotes if min_upvotes is not None else FilterConfig.MIN_UPVOTES
        self.min_comments = min_comments if min_comments is not None else FilterConfig.MIN_COMMENTS
        self.use_score_weighting = use_score_weighting if use_score_weighting is not None else FilterConfig.USE_SCORE_WEIGHTING
        self.score_weight = score_weight if score_weight is not None else FilterConfig.SCORE_WEIGHT
        
        logger.info(
            f"EngagementFilter initialized: min_upvotes={self.min_upvotes}, "
            f"min_comments={self.min_comments}, score_weighting={self.use_score_weighting}"
        )
    
    def matches(self, post: Dict[str, Any]) -> bool:
        """
        Check if a post meets engagement thresholds.
        
        Args:
            post: Normalized post dictionary
        
        Returns:
            True if post meets thresholds, False otherwise
        """
        upvotes = post.get('upvotes', 0) or 0
        num_comments = post.get('num_comments', 0) or 0
        
        # Check basic thresholds
        if upvotes < self.min_upvotes:
            logger.debug(f"Post {post.get('post_id')} rejected: upvotes ({upvotes}) < min ({self.min_upvotes})")
            return False
        
        if num_comments < self.min_comments:
            logger.debug(f"Post {post.get('post_id')} rejected: comments ({num_comments}) < min ({self.min_comments})")
            return False
        
        # Optional score weighting
        if self.use_score_weighting:
            score = post.get('score', 0) or 0
            weighted_score = score * self.score_weight
            # You can add additional logic here based on weighted score
            logger.debug(f"Post {post.get('post_id')} weighted score: {weighted_score}")
        
        logger.debug(f"Post {post.get('post_id')} passed engagement filter")
        return True
    
    def filter_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter a list of posts by engagement metrics.
        
        Args:
            posts: List of normalized post dictionaries
        
        Returns:
            Filtered list of posts that meet engagement thresholds
        """
        filtered = [post for post in posts if self.matches(post)]
        logger.info(f"Engagement filter: {len(filtered)}/{len(posts)} posts met engagement thresholds")
        return filtered

