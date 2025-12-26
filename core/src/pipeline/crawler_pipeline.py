"""
Main crawler pipeline: Fetch → Normalize → Filter → Deduplicate → Enrich → Persist
"""
from typing import Dict, Any, List
from ..reddit.fetcher import RedditFetcher
from ..filters.keyword_filter import KeywordFilter
from ..filters.engagement_filter import EngagementFilter
from ..filters.intent_filter import IntentFilter
from ..deduplication.deduplicator import Deduplicator
from ..storage.factory import get_storage_backend
from ..config.settings import StorageConfig
from ..utils.logging import get_logger
from ..utils.exceptions import CrawlerException

logger = get_logger(__name__)


class CrawlerPipeline:
    """Main pipeline orchestrating all crawler stages"""
    
    def __init__(self):
        """Initialize the pipeline with all components"""
        # Initialize fetcher
        self.fetcher = RedditFetcher()
        
        # Initialize filters
        self.keyword_filter = KeywordFilter()
        self.engagement_filter = EngagementFilter()
        self.intent_filter = IntentFilter()
        
        # Initialize storage (will get existing IDs/links for deduplication)
        # Now uses SQLAlchemy storage backend
        self.storage = get_storage_backend()
        
        # Initialize deduplicator with existing posts
        existing_post_ids = self.storage.get_existing_post_ids()
        existing_permalinks = self.storage.get_existing_permalinks()
        self.deduplicator = Deduplicator(existing_post_ids, existing_permalinks)
        
        logger.info("CrawlerPipeline initialized")
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the full pipeline.
        
        Returns:
            Dictionary with pipeline execution results
        """
        try:
            logger.info("Starting crawler pipeline")
            
            # Stage 0: Database cleanup (before fetching new posts)
            logger.info("Stage 0: Checking database size and cleaning up old posts if needed")
            max_posts = StorageConfig.DB_MAX_POSTS
            deleted_count = self.storage.cleanup_old_posts(max_posts)
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old posts (max limit: {max_posts})")
            else:
                logger.debug(f"Database size check: No cleanup needed (max limit: {max_posts})")
            
            # Stage 1: Fetch
            logger.info("Stage 1: Fetching posts from Reddit")
            raw_posts = self.fetcher.fetch_all_configured_subreddits()
            logger.info(f"Fetched {len(raw_posts)} posts")
            
            if not raw_posts:
                logger.warning("No posts fetched, pipeline ending early")
                return {
                    'total_fetched': 0,
                    'total_saved': 0,
                    'duplicates_skipped': 0,
                }
            
            # Stage 2: Normalize (already done in fetcher)
            normalized_posts = raw_posts
            logger.info(f"Stage 2: Normalized {len(normalized_posts)} posts")
            
            # TEMPORARY: Skip all filters and save all fetched posts directly
            # User requested: load all 300 posts into DB without filtering
            logger.info("Stage 3-5: SKIPPING FILTERS - Saving all fetched posts directly to database")
            logger.info(f"Saving all {len(normalized_posts)} posts without filtering")
            
            # Stage 5: Deduplicate only (to avoid duplicates)
            logger.info("Stage 5: Deduplicating posts")
            unique_posts = self.deduplicator.filter_duplicates(normalized_posts)
            duplicates_skipped = len(normalized_posts) - len(unique_posts)
            logger.info(f"After deduplication: {len(unique_posts)} unique posts")
            
            # Stage 6: Enrich (placeholder for future AI processing)
            enriched_posts = unique_posts
            logger.info(f"Stage 6: Enriched {len(enriched_posts)} posts")
            
            # Stage 7: Persist
            logger.info("Stage 7: Persisting posts to storage")
            saved_posts = self.storage.save_posts(enriched_posts)
            logger.info(f"Persisted {len(saved_posts)} posts")
            
            return {
                'total_fetched': len(raw_posts),
                'total_saved': len(saved_posts),
                'duplicates_skipped': duplicates_skipped,
                'old_posts_deleted': deleted_count,
            }
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            raise CrawlerException(f"Pipeline failed: {str(e)}")

