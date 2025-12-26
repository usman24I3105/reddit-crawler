#!/usr/bin/env python
"""
Test database cleanup functionality.
"""
import os
import sys
from pathlib import Path

# Setup Django before importing anything else
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from src.db.session import SessionLocal
from src.db.models import Post
from src.db.repository import PostRepository
from src.config.settings import StorageConfig

def test_cleanup():
    """Test database cleanup"""
    print("=" * 60)
    print("TESTING DATABASE CLEANUP")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        repository = PostRepository(db)
        
        # Get current count
        current_count = repository.get_total_count()
        print(f"\nCurrent posts in database: {current_count}")
        print(f"Max posts limit: {StorageConfig.DB_MAX_POSTS}")
        
        # Test cleanup with a lower limit (if we have more than 5 posts)
        if current_count > 5:
            test_limit = 5
            print(f"\nTesting cleanup with limit: {test_limit}")
            deleted = repository.delete_oldest_posts(test_limit)
            print(f"Deleted {deleted} posts")
            
            # Check new count
            new_count = repository.get_total_count()
            print(f"New post count: {new_count}")
        else:
            print("\nNot enough posts to test cleanup (need more than 5)")
            
    finally:
        db.close()

if __name__ == '__main__':
    test_cleanup()



