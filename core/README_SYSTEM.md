# Reddit Crawler System - Complete Architecture

## 🎯 System Overview

Automatically discover relevant Reddit posts every 12 hours, filter them intelligently, store them safely, and allow human workers to log in and reply through a clean web interface.

## 📐 High-Level Architecture

```
[ Scheduler (12h) ]
        ↓
[ Reddit Crawler Service ]
        ↓
[ Filter + Deduplication ]
        ↓
[ SQLite Database ]
        ↓
[ FastAPI Backend ]
        ↓
[ Worker Web Dashboard ]
        ↓
[ Reddit Comment API ]
```

## 🔧 Components

### 1. Scheduler (12h Update)
- **Technology**: FastAPI + APScheduler
- **Frequency**: Every 12 hours (configurable via `CRAWLER_INTERVAL_HOURS`)
- **Features**:
  - Automatic startup with FastAPI
  - Graceful shutdown
  - Job locking to prevent overlap
  - Manual trigger endpoint: `POST /admin/run-crawler`

### 2. Reddit Crawler Service
- **Technology**: PRAW (Python Reddit API Wrapper)
- **Strategy**:
  - Fetches from configured subreddits
  - Last 12-24 hours only (configurable)
  - Uses `new`, `hot`, or `top` sorting
  - Fetches slightly more posts, filters locally
- **Fields Captured**:
  - `title`, `body`, `score`, `comments`, `permalink`
  - `upvotes`, `author`, `subreddit`, `created_utc`

### 3. Filtering Layer

#### Keyword Filter (MANDATORY)
- Case-insensitive matching
- Searches in `title` + `body`
- Keywords from config: `FILTER_KEYWORDS`
- Example: `FILTER_KEYWORDS=python,reddit,api`

#### Engagement Filter
- Minimum upvotes: `MIN_UPVOTES` (default: 0)
- Minimum comments: `MIN_COMMENTS` (default: 0)
- Prevents low-quality posts
- Keeps worker workload manageable

### 4. Deduplication
- **Strategy**: Database-level UNIQUE constraint on `reddit_post_id`
- **Behavior**: Duplicates are automatically ignored
- **Why**: Simple, bulletproof, no extra logic needed

### 5. Database (SQLite)
- **Schema**: `posts` table with all required fields
- **Features**:
  - UNIQUE constraint on `reddit_post_id`
  - Indexes for common queries
  - PostgreSQL-ready (just change `DATABASE_URL`)

### 6. FastAPI Backend
- **Endpoints**:
  - `GET /posts?status=pending` - Get pending posts
  - `POST /posts/{id}/assign` - Assign post to worker
  - `POST /posts/{id}/reply` - Submit reply
  - `POST /admin/run-crawler` - Manual trigger
  - `GET /admin/scheduler/status` - Scheduler status

### 7. Worker Dashboard
- **Status**: API ready, frontend can be built
- **Flow**:
  1. Worker logs in (JWT auth - TODO)
  2. See list of pending posts
  3. Click post → Read summary + link
  4. Write reply
  5. Submit → Backend posts to Reddit

### 8. Reddit Comment API
- **Features**:
  - Rate-limit aware
  - Retry on failure
  - On success: `status → replied`
  - Prevents spam & bans

## 🚀 Quick Start

### 1. Configuration

Copy `.env.example` to `.env` and fill in your Reddit API credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=your_app_name/1.0 by your_username
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

### 2. Install Dependencies

```bash
cd core
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
# Create database and tables
python scripts/init_db.py

# Or use Alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Run the Application

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The crawler will:
- Start automatically
- Run every 12 hours
- Log all operations

## 📊 API Endpoints

### Worker Dashboard

#### Get Pending Posts
```http
GET /posts?status=pending&limit=50&subreddit=python
```

Response:
```json
[
  {
    "id": 1,
    "reddit_post_id": "abc123",
    "subreddit": "python",
    "title": "Post Title",
    "body": "Post body text...",
    "author": "username",
    "permalink": "/r/python/comments/abc123/...",
    "upvotes": 10,
    "comments": 5,
    "score": 10,
    "status": "pending",
    "assigned_to": null,
    "created_at": "2024-01-01T12:00:00Z",
    "fetched_at": "2024-01-01T13:00:00Z"
  }
]
```

#### Assign Post
```http
POST /posts/{post_id}/assign
Content-Type: application/json
Authorization: Bearer <token>

{
  "worker_id": "worker1"
}
```

#### Reply to Post
```http
POST /posts/{post_id}/reply
Content-Type: application/json
Authorization: Bearer <token>

{
  "comment_text": "Your reply here",
  "worker_id": "worker1"
}
```

### Admin Endpoints

#### Manual Crawler Trigger
```http
POST /admin/run-crawler
```

#### Scheduler Status
```http
GET /admin/scheduler/status
```

## 🔐 Authentication

Currently using placeholder JWT authentication. To implement:

1. Add JWT token generation on login
2. Validate tokens in `get_current_worker()` dependency
3. Extract user info from token

## 📝 Logging

All operations are logged:
- Crawler start/end
- Number of posts fetched
- Number saved
- Errors and warnings

Logs are written to stdout with timestamps.

## ⚙️ Configuration

All configuration via environment variables (see `.env.example`):

### Reddit API
- `REDDIT_CLIENT_ID` - Your Reddit app client ID
- `REDDIT_CLIENT_SECRET` - Your Reddit app secret
- `REDDIT_USER_AGENT` - App identifier
- `REDDIT_USERNAME` - Reddit username (for posting)
- `REDDIT_PASSWORD` - Reddit password (for posting)

### Crawler
- `CRAWLER_INTERVAL_HOURS` - Schedule interval (default: 12)
- `SUBREDDITS` - Comma-separated list (default: Home)
- `POST_LIMIT` - Max posts per subreddit (default: 100)

### Filters
- `FILTER_KEYWORDS` - Comma-separated keywords
- `MIN_UPVOTES` - Minimum upvotes (default: 0)
- `MIN_COMMENTS` - Minimum comments (default: 0)

### Database
- `DATABASE_URL` - Database connection string
  - SQLite: `sqlite:///./reddit_crawler.db`
  - PostgreSQL: `postgresql://user:pass@host/dbname`

## 🎨 Frontend (TODO)

The API is ready for a frontend. Suggested stack:
- React + TypeScript
- JWT authentication
- Simple UI for:
  - Login
  - Post list
  - Post detail view
  - Reply form

## 🔄 Migration from Django

If you have existing Django data:

```bash
python scripts/migrate_django_to_sqlite.py
```

## 📈 Monitoring

Check scheduler status:
```bash
curl http://localhost:8000/admin/scheduler/status
```

View logs:
- All logs go to stdout
- Check application output for crawler operations

## 🛡️ Production Considerations

1. **Security**:
   - Implement proper JWT authentication
   - Use environment variables for secrets
   - Enable HTTPS
   - Configure CORS properly

2. **Database**:
   - Regular backups for SQLite
   - Consider PostgreSQL for high volume
   - Monitor database size

3. **Rate Limiting**:
   - Reddit API has rate limits
   - Comment posting includes delays
   - Monitor for rate limit errors

4. **Error Handling**:
   - All errors are logged
   - Failed posts are skipped, not crashed
   - Scheduler continues on errors

## 📚 File Structure

```
core/
├── main.py                    # FastAPI application
├── src/
│   ├── db/                    # SQLAlchemy database layer
│   │   ├── models.py          # Post model
│   │   ├── repository.py     # Repository pattern
│   │   └── migrations/        # Alembic migrations
│   ├── api/
│   │   ├── fastapi_routes.py  # FastAPI endpoints
│   │   └── views.py          # Django REST views (legacy)
│   ├── reddit/
│   │   ├── fetcher.py        # Post fetching
│   │   ├── commenter.py      # Comment posting
│   │   └── auth.py           # Reddit authentication
│   ├── filters/              # Filtering logic
│   ├── pipeline/             # Crawler pipeline
│   └── scheduler/            # APScheduler service
├── scripts/
│   ├── init_db.py            # Database initialization
│   └── migrate_django_to_sqlite.py
└── .env.example              # Configuration template
```

## ✅ Requirements Checklist

- ✅ 12-hour scheduled crawling
- ✅ Reddit API integration
- ✅ Keyword filtering (case-insensitive)
- ✅ Engagement filtering
- ✅ Database deduplication (UNIQUE constraint)
- ✅ SQLite with SQLAlchemy
- ✅ FastAPI REST API
- ✅ Worker dashboard APIs
- ✅ Reddit comment posting
- ✅ Logging and monitoring
- ⚠️ JWT authentication (placeholder)
- ⚠️ Frontend UI (API ready)

## 🐛 Troubleshooting

### Crawler not running
- Check scheduler status: `GET /admin/scheduler/status`
- Check logs for errors
- Verify Reddit API credentials

### No posts fetched
- Check subreddit names in config
- Verify Reddit API credentials
- Check filter settings (may be too strict)

### Database errors
- Ensure database is initialized
- Check `DATABASE_URL` configuration
- Run migrations if needed

## 📞 Support

Check logs first - all operations are logged with timestamps and error details.





