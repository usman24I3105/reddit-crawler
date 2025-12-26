#!/usr/bin/env python
"""
Comprehensive diagnostic script to find why posts aren't being fetched.
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

from dotenv import load_dotenv
load_dotenv()

from src.config.settings import RedditConfig, CrawlerConfig, FilterConfig
from src.db.session import SessionLocal
from src.db.models import Post

print("=" * 70)
print("DIAGNOSTIC: Why Posts Are Not Being Fetched")
print("=" * 70)

# 1. Check Reddit API Configuration
print("\n[1] Reddit API Configuration:")
print(f"    CLIENT_ID: {'[OK] Set' if RedditConfig.CLIENT_ID and 'PASTE' not in RedditConfig.CLIENT_ID else '[X] NOT SET or placeholder'}")
print(f"    CLIENT_SECRET: {'[OK] Set' if RedditConfig.CLIENT_SECRET and 'PASTE' not in RedditConfig.CLIENT_SECRET else '[X] NOT SET or placeholder'}")
print(f"    USER_AGENT: {RedditConfig.USER_AGENT or '[X] NOT SET'}")
if RedditConfig.USER_AGENT:
    # Check format
    if ' by ' in RedditConfig.USER_AGENT and '/' in RedditConfig.USER_AGENT:
        print(f"    USER_AGENT Format: [OK] Correct format")
    else:
        print(f"    USER_AGENT Format: [X] WRONG! Should be: 'AppName/Version by Username'")

# 2. Test Reddit Connection
print("\n[2] Testing Reddit API Connection:")
try:
    from src.reddit.auth import RedditAuth
    client = RedditAuth.get_readonly_client()
    print(f"    [OK] Connection successful!")
    print(f"    Read-only mode: {client.read_only}")
    reddit_ok = True
except Exception as e:
    print(f"    [X] Connection FAILED: {str(e)}")
    print(f"    [FIX] This is why no posts are being fetched!")
    print(f"    [FIX] Check your Reddit API credentials in .env file")
    reddit_ok = False

# 3. Check Crawler Configuration
print("\n[3] Crawler Configuration:")
print(f"    SUBREDDITS: {CrawlerConfig.SUBREDDITS}")
print(f"    POST_LIMIT: {CrawlerConfig.POST_LIMIT}")
print(f"    KEYWORDS: {FilterConfig.KEYWORDS if FilterConfig.KEYWORDS else '[NONE - will accept all posts]'}")
print(f"    MIN_UPVOTES: {FilterConfig.MIN_UPVOTES}")
print(f"    MIN_COMMENTS: {FilterConfig.MIN_COMMENTS}")

# 4. Test Fetching (if Reddit OK)
if reddit_ok:
    print("\n[4] Testing Post Fetching:")
    try:
        from src.reddit.fetcher import RedditFetcher
        fetcher = RedditFetcher()
        subreddit = CrawlerConfig.SUBREDDITS[0] if CrawlerConfig.SUBREDDITS else 'Home'
        print(f"    Fetching from r/{subreddit}...")
        posts = fetcher.fetch_posts_from_subreddit(subreddit, limit=5, hours_back=24)
        print(f"    [OK] Fetched {len(posts)} raw posts")
        
        if posts:
            post = posts[0]
            print(f"    Sample post:")
            print(f"      - Title: {post['title'][:60]}...")
            print(f"      - Upvotes: {post['upvotes']}")
            print(f"      - Comments: {post.get('num_comments', post.get('comments', 0))}")
            
            # Check keyword match
            if FilterConfig.KEYWORDS:
                title_lower = post['title'].lower()
                body_lower = (post.get('body') or '').lower()
                combined = f"{title_lower} {body_lower}"
                matches = [kw for kw in FilterConfig.KEYWORDS if kw in combined]
                print(f"      - Keyword matches: {matches if matches else '[NONE - will be filtered out]'}")
            
            # Check engagement
            upvotes = post['upvotes']
            comments = post.get('num_comments', post.get('comments', 0))
            passes = upvotes >= FilterConfig.MIN_UPVOTES and comments >= FilterConfig.MIN_COMMENTS
            print(f"      - Passes engagement filter: {'[OK] YES' if passes else '[X] NO (will be filtered out)'}")
        else:
            print(f"    [WARNING] No posts fetched from r/{subreddit}")
    except Exception as e:
        print(f"    [X] Fetch failed: {str(e)}")
        import traceback
        traceback.print_exc()

# 5. Check Database
print("\n[5] Database Status:")
db = SessionLocal()
try:
    total = db.query(Post).count()
    pending = db.query(Post).filter(Post.status == 'pending').count()
    print(f"    Total posts in DB: {total}")
    print(f"    Pending posts: {pending}")
    if total == 0:
        print(f"    [X] Database is empty - no posts have been saved")
finally:
    db.close()

# 6. Summary and Recommendations
print("\n" + "=" * 70)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 70)

if not reddit_ok:
    print("\n[CRITICAL] Reddit API authentication is failing!")
    print("  Fix:")
    print("  1. Check core/.env file")
    print("  2. Verify REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET are correct")
    print("  3. Fix REDDIT_USER_AGENT format: 'AppName/Version by YourUsername'")
    print("  4. Restart backend after fixing")
elif db.query(Post).count() == 0:
    print("\n[ISSUE] No posts in database")
    print("  Possible causes:")
    print("  1. Filters too strict (keywords/engagement)")
    print("  2. No posts match criteria")
    print("  3. Subreddits have no recent posts")
    print("  Fix:")
    print("  1. Lower MIN_UPVOTES and MIN_COMMENTS to 0")
    print("  2. Use broader keywords or remove keywords temporarily")
    print("  3. Try different subreddits")
else:
    print("\n[OK] System appears to be working!")

print("\n" + "=" * 70)





