#!/usr/bin/env python
"""
Check posts in database.
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

def check_database():
    """Check posts in database"""
    db = SessionLocal()
    try:
        total = db.query(Post).count()
        print(f"Total posts in database: {total}")
        
        if total > 0:
            recent = db.query(Post).order_by(Post.fetched_at.desc()).limit(5).all()
            print(f"\nRecent posts:")
            for p in recent:
                print(f"  - r/{p.subreddit}: {p.title[:60]}...")
                print(f"    Status: {p.status}, Upvotes: {p.upvotes}, Comments: {p.comments}")
        else:
            print("\nNo posts in database yet.")
    finally:
        db.close()

if __name__ == '__main__':
    check_database()



