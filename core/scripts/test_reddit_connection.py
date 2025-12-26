#!/usr/bin/env python
"""
Test Reddit API connection and fetch posts.
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

from dotenv import load_dotenv
load_dotenv()

from src.config.settings import RedditConfig, CrawlerConfig, FilterConfig
from src.reddit.auth import RedditAuth
from src.reddit.fetcher import RedditFetcher

def test_reddit_connection():
    """Test Reddit API connection"""
    print("=" * 60)
    print("REDDIT API CONNECTION TEST")
    print("=" * 60)
    
    # Check configuration
    print("\n1. Configuration Check:")
    print(f"   CLIENT_ID: {'[OK] SET' if RedditConfig.CLIENT_ID and 'PASTE' not in RedditConfig.CLIENT_ID else '[X] NOT SET'}")
    print(f"   CLIENT_SECRET: {'[OK] SET' if RedditConfig.CLIENT_SECRET and 'PASTE' not in RedditConfig.CLIENT_SECRET else '[X] NOT SET'}")
    print(f"   USER_AGENT: {RedditConfig.USER_AGENT or '[X] NOT SET'}")
    print(f"   SUBREDDITS: {CrawlerConfig.SUBREDDITS}")
    print(f"   KEYWORDS: {FilterConfig.KEYWORDS or 'NONE'}")
    print(f"   MIN_UPVOTES: {FilterConfig.MIN_UPVOTES}")
    print(f"   MIN_COMMENTS: {FilterConfig.MIN_COMMENTS}")
    
    # Test connection
    print("\n2. Testing Reddit API Connection:")
    try:
        client = RedditAuth.get_readonly_client()
        print(f"   [OK] Connection successful!")
        print(f"   Read-only mode: {client.read_only}")
    except Exception as e:
        print(f"   [X] Connection failed: {str(e)}")
        return False
    
    # Test fetching posts
    print("\n3. Testing Post Fetching:")
    try:
        fetcher = RedditFetcher()
        subreddit = CrawlerConfig.SUBREDDITS[0] if CrawlerConfig.SUBREDDITS else 'Home'
        print(f"   Fetching from r/{subreddit}...")
        
        # Fetch without filters first
        posts = fetcher.fetch_posts_from_subreddit(subreddit, limit=10, hours_back=24)
        print(f"   [OK] Fetched {len(posts)} raw posts")
        
        if posts:
            print(f"\n   Sample post:")
            post = posts[0]
            print(f"   - Title: {post['title'][:60]}...")
            print(f"   - Upvotes: {post['upvotes']}")
            print(f"   - Comments: {post['comments']}")
            print(f"   - Subreddit: {post['subreddit']}")
            
            # Check if it matches keywords
            if FilterConfig.KEYWORDS:
                title_lower = post['title'].lower()
                body_lower = (post.get('body') or '').lower()
                combined = f"{title_lower} {body_lower}"
                matches = [kw for kw in FilterConfig.KEYWORDS if kw in combined]
                print(f"   - Keyword matches: {matches if matches else 'NONE'}")
            
            # Check engagement filter
            passes_engagement = (
                post['upvotes'] >= FilterConfig.MIN_UPVOTES and
                post['comments'] >= FilterConfig.MIN_COMMENTS
            )
            print(f"   - Passes engagement filter: {'[OK] YES' if passes_engagement else '[X] NO'}")
        else:
            print("   [WARNING] No posts fetched - check subreddit name and Reddit API")
            
    except Exception as e:
        print(f"   [X] Fetch failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    test_reddit_connection()

