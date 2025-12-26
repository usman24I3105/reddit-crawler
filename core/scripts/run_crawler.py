#!/usr/bin/env python3
"""
Manually run the crawler pipeline to fetch posts.

This script runs the crawler immediately, bypassing the scheduler.
Useful for testing or manual data collection.

Usage:
    python scripts/run_crawler.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.crawler_pipeline import CrawlerPipeline
from src.utils.logging import get_logger

logger = get_logger(__name__)


def main():
    """Run the crawler pipeline"""
    try:
        logger.info("=" * 60)
        logger.info("Starting manual crawler run")
        logger.info("=" * 60)
        
        # Initialize and run pipeline
        pipeline = CrawlerPipeline()
        result = pipeline.run()
        
        logger.info("=" * 60)
        logger.info("Crawler run completed")
        logger.info(f"Total fetched: {result.get('total_fetched', 0)}")
        logger.info(f"Total saved: {result.get('total_saved', 0)}")
        logger.info(f"Duplicates skipped: {result.get('duplicates_skipped', 0)}")
        logger.info(f"Old posts deleted: {result.get('old_posts_deleted', 0)}")
        logger.info("=" * 60)
        
        return result
        
    except Exception as e:
        logger.error(f"Crawler run failed: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    main()

