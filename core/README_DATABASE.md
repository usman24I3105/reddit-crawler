# Database Migration Guide

This document describes the migration from Django ORM to SQLAlchemy with SQLite.

## Overview

The system has been refactored to use SQLAlchemy ORM with SQLite as the primary database. The architecture is designed to be easily switchable to PostgreSQL in the future.

## Structure

```
src/
 ├── db/
 │    ├── base.py          # SQLAlchemy declarative base
 │    ├── session.py       # Database session management
 │    ├── models.py        # SQLAlchemy models
 │    ├── repository.py    # Repository pattern for DB operations
 │    └── migrations/      # Alembic migrations
 ├── storage/
 │    └── sqlalchemy_storage.py  # Storage backend implementation
```

## Configuration

### Environment Variables

- `DATABASE_URL`: Database connection string
  - SQLite: `sqlite:///./reddit_crawler.db` (default)
  - PostgreSQL: `postgresql://user:password@localhost/dbname`
  
- `SQLITE_DB_PATH`: Alternative way to specify SQLite path
  - Example: `sqlite:///./data/crawler.db`

### Database Schema

The `posts` table includes:
- `reddit_post_id` (UNIQUE) - for automatic deduplication
- `subreddit`, `title`, `body`, `author`, `permalink`
- `upvotes`, `comments`, `score`
- `status` (pending, in_progress, replied)
- `assigned_to` (nullable)
- `created_at`, `created_utc`, `fetched_at`

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
# Create initial migration
cd core
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 3. Migrate Existing Data (Optional)

If you have existing Django data to migrate:

```bash
python scripts/migrate_django_to_sqlite.py
```

## Usage

### Repository Pattern

All database operations go through the repository:

```python
from src.db.session import SessionLocal
from src.db.repository import PostRepository

db = SessionLocal()
repository = PostRepository(db)

# Create a post
post_data = {
    'post_id': 'abc123',
    'subreddit': 'python',
    'title': 'Example Post',
    # ... other fields
}
post = repository.create_post(post_data)

# Get pending posts
pending = repository.get_pending_posts(limit=50)

# Assign post
repository.assign_post('abc123', 'worker1')

# Mark as replied
repository.mark_replied('abc123', 'worker1')
```

### Storage Backend

The storage backend automatically uses SQLAlchemy:

```python
from src.storage.factory import get_storage_backend

storage = get_storage_backend()
posts = storage.get_pending_posts(limit=10)
```

## Deduplication

Deduplication is handled automatically at the database level:
- `reddit_post_id` has a UNIQUE constraint
- Attempts to insert duplicates are handled gracefully
- The repository returns the existing post if a duplicate is detected

## Migrating to PostgreSQL

To switch to PostgreSQL:

1. Update `DATABASE_URL` environment variable:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/reddit_crawler"
   ```

2. The session management in `src/db/session.py` automatically detects PostgreSQL and uses appropriate connection pooling.

3. No code changes needed in business logic - the repository pattern abstracts the database differences.

## Alembic Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

## Production Considerations

1. **Backup**: SQLite databases should be backed up regularly
2. **Concurrency**: SQLite works well for single-process applications. For multi-process, consider PostgreSQL
3. **Performance**: For high-volume scenarios, PostgreSQL is recommended
4. **Connection Pooling**: Already configured for PostgreSQL in `session.py`





