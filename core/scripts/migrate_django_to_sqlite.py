#!/usr/bin/env python
"""
Migration script to migrate data from Django ORM to SQLite/SQLAlchemy.

Usage:
    python scripts/migrate_django_to_sqlite.py

This script:
1. Reads all posts from Django SubredditPost model
2. Migrates them to SQLAlchemy Post model
3. Handles duplicates gracefully
"""
import os
import sys
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from crawler.models import SubredditPost as DjangoPost
from src.db.session import SessionLocal, init_db
from src.db.repository import PostRepository
from src.utils.logging import get_logger

logger = get_logger(__name__)


def migrate_posts():
    """Migrate posts from Django to SQLAlchemy"""
    db = SessionLocal()
    repository = PostRepository(db)
    
    try:
        # Get all Django posts
        django_posts = DjangoPost.objects.all()
        total = django_posts.count()
        
        logger.info(f"Starting migration of {total} posts from Django to SQLAlchemy")
        
        migrated = 0
        skipped = 0
        errors = 0
        
        for django_post in django_posts:
            try:
                # Convert Django post to dictionary format
                post_data = {
                    'post_id': django_post.post_id,
                    'subreddit': django_post.subreddit,
                    'title': django_post.title,
                    'body': django_post.body or '',
                    'author': django_post.author or '[deleted]',
                    'permalink': django_post.permalink or '',
                    'url': django_post.url or '',
                    'upvotes': django_post.upvotes or 0,
                    'num_comments': django_post.num_comments or 0,
                    'score': django_post.score or 0,
                    'created_utc': django_post.created_utc,
                    'fetched_at': django_post.fetched_at,
                }
                
                # Try to create post (will handle duplicates)
                try:
                    repository.create_post(post_data)
                    migrated += 1
                except Exception as e:
                    # Check if it's a duplicate
                    if 'UNIQUE constraint' in str(e) or 'already exists' in str(e).lower():
                        skipped += 1
                        logger.debug(f"Skipped duplicate post: {django_post.post_id}")
                    else:
                        raise
                
                # Update status and assignment if needed
                if django_post.status != 'pending' or django_post.assigned_to:
                    post = repository.get_post_by_id(django_post.post_id)
                    if post:
                        post.status = django_post.status
                        post.assigned_to = django_post.assigned_to
                        db.commit()
                
                if (migrated + skipped + errors) % 100 == 0:
                    logger.info(f"Progress: {migrated} migrated, {skipped} skipped, {errors} errors")
                    
            except Exception as e:
                errors += 1
                logger.error(f"Error migrating post {django_post.post_id}: {str(e)}")
                continue
        
        logger.info("=" * 60)
        logger.info("Migration completed!")
        logger.info(f"Total: {total}")
        logger.info(f"Migrated: {migrated}")
        logger.info(f"Skipped (duplicates): {skipped}")
        logger.info(f"Errors: {errors}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    # Initialize database tables
    logger.info("Initializing database tables...")
    init_db()
    
    # Run migration
    migrate_posts()





