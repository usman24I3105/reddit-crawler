#!/usr/bin/env python
"""
Test script to add sample posts to database without Reddit API.
Useful for testing frontend when Reddit API is not working.
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from src.db.session import SessionLocal
from src.db.models import Post
from src.db.repository import PostRepository

def create_sample_posts():
    """Create sample posts for testing"""
    db = SessionLocal()
    repository = PostRepository(db)
    
    sample_posts = [
        {
            'reddit_post_id': 'test1',
            'subreddit': 'python',
            'title': 'How to use FastAPI with SQLAlchemy?',
            'body': 'I am learning FastAPI and want to integrate SQLAlchemy. Any tips?',
            'author': 'test_user1',
            'permalink': '/r/python/comments/test1/',
            'url': 'https://reddit.com/r/python/comments/test1/',
            'upvotes': 15,
            'comments': 8,
            'score': 15,
            'status': 'pending',
            'created_utc': datetime.utcnow() - timedelta(hours=2),
            'fetched_at': datetime.utcnow(),
        },
        {
            'reddit_post_id': 'test2',
            'subreddit': 'webdev',
            'title': 'React hooks best practices',
            'body': 'What are the best practices for using React hooks in 2024?',
            'author': 'test_user2',
            'permalink': '/r/webdev/comments/test2/',
            'url': 'https://reddit.com/r/webdev/comments/test2/',
            'upvotes': 25,
            'comments': 12,
            'score': 25,
            'status': 'pending',
            'created_utc': datetime.utcnow() - timedelta(hours=1),
            'fetched_at': datetime.utcnow(),
        },
        {
            'reddit_post_id': 'test3',
            'subreddit': 'technology',
            'title': 'API automation with Python',
            'body': 'I built an automation tool using Python and REST APIs. Here is how...',
            'author': 'test_user3',
            'permalink': '/r/technology/comments/test3/',
            'url': 'https://reddit.com/r/technology/comments/test3/',
            'upvotes': 30,
            'comments': 5,
            'score': 30,
            'status': 'pending',
            'created_utc': datetime.utcnow() - timedelta(hours=3),
            'fetched_at': datetime.utcnow(),
        },
    ]
    
    print("Creating sample posts...")
    created = 0
    for post_data in sample_posts:
        try:
            # Check if already exists
            existing = db.query(Post).filter(Post.reddit_post_id == post_data['reddit_post_id']).first()
            if existing:
                print(f"  Post {post_data['reddit_post_id']} already exists, skipping")
                continue
            
            post = Post(**post_data)
            db.add(post)
            created += 1
            print(f"  Created: {post_data['title'][:50]}...")
        except Exception as e:
            print(f"  Error creating post {post_data['reddit_post_id']}: {str(e)}")
    
    try:
        db.commit()
        print(f"\n[OK] Created {created} sample posts")
        print(f"Total posts in database: {db.query(Post).count()}")
    except Exception as e:
        db.rollback()
        print(f"\n[X] Error committing: {str(e)}")
    finally:
        db.close()

if __name__ == '__main__':
    create_sample_posts()





