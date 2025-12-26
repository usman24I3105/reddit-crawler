# Migration Guide - Reddit Crawler Refactor

## Overview

This guide will help you migrate from the old crawler implementation to the new refactored version.

## Step 1: Update Environment Variables

Create a `.env` file (or update your existing one) with the new configuration variables. See `.env.example` for all available options.

**Key changes:**
- Add `CRAWL_INTERVAL_HOURS=12` (was hardcoded to 10 seconds)
- Add `FILTER_KEYWORDS` for keyword filtering
- Add `MIN_UPVOTES` and `MIN_COMMENTS` for engagement filtering
- Update database credentials if needed

## Step 2: Database Migration

The `SubredditPost` model has been significantly updated. You need to create and run migrations:

```bash
cd core
python manage.py makemigrations crawler
python manage.py migrate
```

**Important:** The new model includes:
- `post_id` (unique, indexed) - replaces title-based deduplication
- `permalink` (indexed) - for fallback deduplication
- `body` - post content
- `upvotes`, `num_comments`, `score` - engagement metrics
- `status` - pending, in_progress, replied
- `assigned_to` - worker assignment
- `fetched_at` - timestamp

## Step 3: Update Celery Configuration

The Celery app name has changed. Update your Celery worker startup:

**Old:**
```bash
celery -A crawler_soup worker -l info
celery -A crawler_soup beat -l info
```

**New:**
```bash
celery -A core worker -l info
celery -A core beat -l info
```

Or use the new scheduler module:
```bash
celery -A src.scheduler.celery_app worker -l info
celery -A src.scheduler.celery_app beat -l info
```

## Step 4: Update URLs

The API endpoints have changed:

**Old:**
- `/postsSoup/` - Get all posts

**New:**
- `/api/posts/pending/` - Get pending posts (requires auth)
- `/api/posts/assign/` - Assign post to worker
- `/api/posts/mark-replied/` - Mark post as replied
- `/api/posts/comment/` - Post comment to Reddit

## Step 5: Data Migration (Optional)

If you have existing data in the old `SubredditPost` model, you may need to migrate it:

1. Export existing data
2. Map old fields to new fields
3. Import into new schema

**Field mapping:**
- `title` → `title` (same)
- `author` → `author` (same)
- `created_utc` → `created_utc` (same)
- `url` → `url` (same)
- `subreddit` → `subreddit` (same)
- **New:** `post_id` - You'll need to extract from URL or fetch from Reddit
- **New:** `permalink` - Extract from URL
- **New:** `body` - May need to fetch from Reddit API
- **New:** `upvotes`, `num_comments`, `score` - Fetch from Reddit API
- **New:** `status` - Set to 'pending' for existing posts

## Step 6: Update Code References

If you have custom code that uses the old crawler:

**Old imports:**
```python
from crawler_soup.api.task import getposts
from crawler_soup.models import SubredditPost
```

**New imports:**
```python
from src.pipeline.crawler_pipeline import CrawlerPipeline
from crawler.models import SubredditPost
from src.scheduler.tasks import crawl_reddit_posts
```

## Step 7: Test the System

1. **Test the pipeline manually:**
```python
from src.pipeline.crawler_pipeline import CrawlerPipeline

pipeline = CrawlerPipeline()
results = pipeline.run()
print(results)
```

2. **Test the scheduler:**
```bash
# Start Celery worker
celery -A core worker -l info

# In another terminal, start beat
celery -A core beat -l info

# Check logs to see if task runs every 12 hours
```

3. **Test the API:**
```bash
# Get pending posts (requires authentication)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/posts/pending/
```

## Step 8: Configuration Checklist

- [ ] Reddit API credentials configured
- [ ] Database credentials updated
- [ ] Celery broker URL configured
- [ ] Subreddits list configured
- [ ] Keywords configured (if using keyword filtering)
- [ ] Engagement thresholds configured
- [ ] Comment posting enabled (if needed)
- [ ] Environment variables loaded

## Troubleshooting

### Import Errors

If you see import errors like `ModuleNotFoundError: No module named 'src'`:

1. Ensure you're running from the `core` directory
2. Check that `src` folder exists in `core/src`
3. Verify Python path includes the project root

### Celery Task Not Running

1. Check Celery Beat is running
2. Verify task is registered: `celery -A core inspect registered`
3. Check Celery logs for errors
4. Verify `CELERY_BEAT_SCHEDULE` in settings.py

### Database Errors

1. Run migrations: `python manage.py migrate`
2. Check database connection settings
3. Verify model fields match migration

### API Authentication Errors

1. Ensure user is authenticated
2. Check `IsAuthenticated` permission class
3. Verify token/credentials are valid

## Rollback Plan

If you need to rollback:

1. Revert to previous git commit
2. Restore old database backup
3. Use old Celery configuration
4. Restore old environment variables

## Support

For issues or questions:
1. Check logs in Celery worker output
2. Review Django logs
3. Check Reddit API rate limits
4. Verify all environment variables are set

