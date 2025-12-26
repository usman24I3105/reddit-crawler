"""
Centralized configuration management using environment variables.
"""
import os
from pathlib import Path
from typing import List, Optional
try:
    from dotenv import load_dotenv
    # Load .env file from core directory
    # Try multiple possible locations for .env file
    current_file = Path(__file__).resolve()
    # Look for .env in core directory (3 levels up from src/config/settings.py)
    env_path = current_file.parent.parent.parent / '.env'
    if not env_path.exists():
        # Alternative: look in current directory or parent
        env_path = Path('.env')
        if not env_path.exists():
            env_path = Path('..') / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, will use system env vars
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

try:
    from django.conf import settings
except ImportError:
    settings = None


class RedditConfig:
    """Reddit API configuration"""
    # Support both REDDIT_CLIENT_ID and CLIENT_ID for compatibility
    CLIENT_ID = os.getenv('REDDIT_CLIENT_ID') or os.getenv('CLIENT_ID') or getattr(settings, 'REDDIT_CLIENT_ID', '') or getattr(settings, 'CLIENT_ID', '')
    CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET') or os.getenv('CLIENT_SECRET') or getattr(settings, 'REDDIT_CLIENT_SECRET', '') or getattr(settings, 'CLIENT_SECRET', '')
    USER_AGENT = os.getenv('REDDIT_USER_AGENT') or os.getenv('USER_AGENT') or getattr(settings, 'REDDIT_USER_AGENT', '') or getattr(settings, 'USER_AGENT', '')
    USERNAME = os.getenv('REDDIT_USERNAME') or os.getenv('USERNAME', '')
    PASSWORD = os.getenv('REDDIT_PASSWORD') or os.getenv('PASSWORD', '')


class CrawlerConfig:
    """Crawler configuration"""
    # Schedule configuration (in hours)
    # Note: CRAWLER_INTERVAL_HOURS is used by APScheduler
    CRAWL_INTERVAL_HOURS = int(os.getenv('CRAWLER_INTERVAL_HOURS', '12'))
    
    # Subreddits to crawl (comma-separated)
    # Default: California real estate and home buying subreddits
    DEFAULT_SUBREDDITS = 'RealEstate,FirstTimeHomeBuyer,personalfinance,LosAngeles,SanFrancisco,OrangeCounty,Sacramento,SanDiego,AskLosAngeles,AskSF,bayarea,InlandEmpire,SanJose,LongBeach,Fresno,Oakland,RealEstateInvesting,homeowners'
    SUBREDDITS = [
        sub.strip() 
        for sub in os.getenv('SUBREDDITS', DEFAULT_SUBREDDITS).split(',')
        if sub.strip()
    ]
    
    # Post limit per subreddit
    POST_LIMIT = int(os.getenv('POST_LIMIT', '100'))


class FilterConfig:
    """Filtering configuration"""
    # Keywords (comma-separated, case-insensitive)
    KEYWORDS = [
        keyword.strip().lower()
        for keyword in os.getenv('FILTER_KEYWORDS', '').split(',')
        if keyword.strip()
    ]
    
    # Engagement thresholds
    MIN_UPVOTES = int(os.getenv('MIN_UPVOTES', '0'))
    MIN_COMMENTS = int(os.getenv('MIN_COMMENTS', '0'))
    
    # Optional score weighting
    USE_SCORE_WEIGHTING = os.getenv('USE_SCORE_WEIGHTING', 'false').lower() == 'true'
    SCORE_WEIGHT = float(os.getenv('SCORE_WEIGHT', '1.0'))


class StorageConfig:
    """Storage configuration"""
    STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'sqlalchemy')  # sqlalchemy, sheets, mongodb
    
    # Database cleanup configuration
    # Maximum number of posts to keep in database (oldest posts deleted when limit exceeded)
    DB_MAX_POSTS = int(os.getenv('DB_MAX_POSTS', '10000'))  # Default: 10,000 posts
    
    # Google Sheets (if using)
    GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', '')
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '')


class CommentConfig:
    """Reddit comment posting configuration"""
    ENABLE_COMMENT_POSTING = os.getenv('ENABLE_COMMENT_POSTING', 'false').lower() == 'true'
    COMMENT_RATE_LIMIT_DELAY = int(os.getenv('COMMENT_RATE_LIMIT_DELAY', '10'))  # seconds
    COMMENT_MAX_RETRIES = int(os.getenv('COMMENT_MAX_RETRIES', '3'))


def get_keywords() -> List[str]:
    """Get configured keywords"""
    return FilterConfig.KEYWORDS


def get_subreddits() -> List[str]:
    """Get configured subreddits"""
    return CrawlerConfig.SUBREDDITS

