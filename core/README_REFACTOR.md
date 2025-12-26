# Reddit Crawler - Refactored Architecture

## Overview

This is a production-ready Reddit crawler system that fetches, filters, and manages Reddit posts on a scheduled basis. The system has been fully refactored to meet production requirements with a clean, modular architecture.

## Architecture

### Folder Structure

```
src/
 ├── scheduler/          # Celery task scheduling
 ├── reddit/            # Reddit API integration
 │    ├── auth.py       # Authentication management
 │    ├── fetcher.py    # Post fetching
 │    └── commenter.py  # Comment posting
 ├── filters/           # Post filtering
 │    ├── keyword_filter.py
 │    └── engagement_filter.py
 ├── deduplication/     # Duplicate prevention
 ├── storage/           # Abstracted storage layer
 │    ├── base.py       # Storage interface
 │    ├── database.py   # Django ORM backend
 │    └── factory.py    # Backend factory
 ├── pipeline/          # Main crawler pipeline
 ├── api/              # Worker dashboard APIs
 ├── config/           # Configuration management
 └── utils/            # Utilities (logging, exceptions)
```

## Features

### ✅ Scheduled Crawling (12 Hours)
- Automatically runs every 12 hours (configurable via `CRAWL_INTERVAL_HOURS`)
- Uses Celery Beat for scheduling
- Can be triggered via webhook or cron

### ✅ Keyword-Based Filtering
- Case-insensitive keyword matching
- Matches against title and body text
- Configurable via `FILTER_KEYWORDS` environment variable

### ✅ Engagement Filtering
- Minimum upvotes threshold (`MIN_UPVOTES`)
- Minimum comments threshold (`MIN_COMMENTS`)
- Optional score weighting

### ✅ Deduplication (Critical)
- Uses `post_id` (primary) and `permalink` (fallback)
- Prevents duplicates across multiple crawler runs
- Database-backed deduplication

### ✅ Clean Data Pipeline
1. **Fetch**: Get posts from Reddit API
2. **Normalize**: Standardize post format
3. **Filter**: Apply keyword and engagement filters
4. **Deduplicate**: Remove duplicates
5. **Enrich**: Placeholder for future processing
6. **Persist**: Save to storage

### ✅ Storage Abstraction
- Database backend (PostgreSQL via Django ORM)
- Prepared for Google Sheets and MongoDB
- Easy to add new backends

### ✅ Worker Dashboard APIs
- `GET /api/posts/pending/` - Get pending posts
- `POST /api/posts/assign/` - Assign post to worker
- `POST /api/posts/mark-replied/` - Mark post as replied
- `POST /api/posts/comment/` - Post comment and mark as replied

### ✅ Reddit Comment Posting
- OAuth authentication
- Rate limit handling
- Automatic retries with exponential backoff
- Configurable via environment variables

### ✅ Production Hardening
- Centralized logging
- Error boundaries and exception handling
- Environment-based configuration
- Graceful failure handling

## Configuration

All configuration is done via environment variables. See `.env.example` for all available options.

### Key Environment Variables

```bash
# Reddit API
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=...

# Crawler
CRAWL_INTERVAL_HOURS=12
SUBREDDITS=Home,technology
POST_LIMIT=100

# Filters
FILTER_KEYWORDS=python,reddit,api
MIN_UPVOTES=5
MIN_COMMENTS=2

# Storage
STORAGE_BACKEND=database
```

## Database Model

The `SubredditPost` model includes:
- `post_id` (unique) - Reddit post ID
- `permalink` - Reddit permalink
- `subreddit`, `title`, `body`, `author`
- `upvotes`, `num_comments`, `score`
- `status` - pending, in_progress, replied
- `assigned_to` - Worker username
- `fetched_at`, `created_utc`

## Usage

### Running the Crawler

The crawler runs automatically via Celery Beat. To start:

```bash
# Start Celery worker
celery -A core worker -l info

# Start Celery Beat (scheduler)
celery -A core beat -l info
```

### Manual Trigger

You can also trigger the crawler manually:

```python
from src.pipeline.crawler_pipeline import CrawlerPipeline

pipeline = CrawlerPipeline()
results = pipeline.run()
```

### API Usage

```bash
# Get pending posts
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/posts/pending/

# Assign a post
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"post_id": "abc123"}' \
  http://localhost:8000/api/posts/assign/

# Post a comment
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"post_id": "abc123", "comment_text": "Great post!"}' \
  http://localhost:8000/api/posts/comment/
```

## Migration

To apply the new database schema:

```bash
python manage.py makemigrations crawler
python manage.py migrate
```

## Testing

The system is designed to be testable. Each component can be tested independently:

```python
from src.filters.keyword_filter import KeywordFilter

filter = KeywordFilter(keywords=['python', 'django'])
post = {'title': 'Python tutorial', 'body': 'Learn Python'}
assert filter.matches(post) == True
```

## Production Deployment

1. Set all environment variables
2. Run migrations
3. Start Celery worker and beat
4. Configure reverse proxy (nginx)
5. Set up monitoring and logging
6. Configure backups

## Notes

- The system uses PRAW (Python Reddit API Wrapper) for Reddit access
- All hard-coded values have been moved to configuration
- The codebase is modular and maintainable
- Error handling is comprehensive
- Logging is centralized and structured

