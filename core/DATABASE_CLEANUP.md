# Database Cleanup Feature

## Overview

The crawler now automatically cleans up old posts from the database at the start of each run. When the database exceeds a configured limit, the oldest posts (by `fetched_at` timestamp) are automatically deleted to keep the database size manageable.

## How It Works

1. **At the start of each crawler run** (before fetching new posts), the system checks the total number of posts in the database
2. **If the count exceeds the limit**, the oldest posts are deleted (ordered by `fetched_at` timestamp, ascending)
3. **Only the excess posts are deleted** - if you have 10,100 posts and the limit is 10,000, only 100 oldest posts will be deleted
4. **The cleanup happens before fetching**, ensuring the database doesn't grow unbounded

## Configuration

The maximum number of posts to keep is controlled by the `DB_MAX_POSTS` environment variable.

### Default Value
- **Default**: 10,000 posts
- If not set, the system uses 10,000 as the default limit

### Setting the Limit

Add to your `.env` file in the `core` directory:

```env
# Maximum number of posts to keep in database (oldest deleted when exceeded)
DB_MAX_POSTS=10000
```

### Examples

```env
# Keep only 1,000 posts (more aggressive cleanup)
DB_MAX_POSTS=1000

# Keep 50,000 posts (less aggressive cleanup)
DB_MAX_POSTS=50000

# Keep 100,000 posts (very large database)
DB_MAX_POSTS=100000
```

## Pipeline Stages

The cleanup happens in **Stage 0** of the crawler pipeline:

1. **Stage 0**: Database cleanup (if needed)
2. **Stage 1**: Fetch posts from Reddit
3. **Stage 2**: Normalize posts
4. **Stage 3**: Filter by keywords
5. **Stage 4**: Filter by engagement
6. **Stage 5**: Deduplicate
7. **Stage 6**: Enrich
8. **Stage 7**: Persist to database

## Logging

The cleanup process is logged:

- **When cleanup runs**: `Database cleanup: Deleted X oldest posts. Database now has Y posts (limit: Z)`
- **When no cleanup needed**: `Database size check: No cleanup needed (max limit: X)`

## API Response

The crawler API response now includes cleanup information:

```json
{
  "status": "success",
  "total_fetched": 14,
  "total_saved": 9,
  "duplicates_skipped": 5,
  "old_posts_deleted": 0,  // Number of old posts deleted in this run
  "started_at": "2025-12-25T12:30:00",
  "completed_at": "2025-12-25T12:30:05",
  "next_run": "2025-12-26T00:30:05"
}
```

## Benefits

1. **Prevents database bloat**: Automatically manages database size
2. **Maintains performance**: Keeps database queries fast
3. **Configurable**: Adjust the limit based on your needs
4. **Automatic**: No manual intervention required
5. **Safe**: Only deletes oldest posts, preserving recent data

## Notes

- Posts are deleted based on `fetched_at` timestamp (oldest first)
- The cleanup happens **before** fetching new posts, not after
- If the database is below the limit, no cleanup occurs
- The cleanup is logged for monitoring and debugging



