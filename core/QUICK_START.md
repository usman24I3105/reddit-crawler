# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Get Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..." or "create app"
3. Choose "script" type
4. Note down:
   - Client ID (under the app name)
   - Secret (the "secret" field)

### Step 2: Configure Environment

```bash
cd core
cp .env.example .env
```

Edit `.env` and paste your Reddit credentials:
```bash
REDDIT_CLIENT_ID=paste_your_client_id_here
REDDIT_CLIENT_SECRET=paste_your_secret_here
REDDIT_USER_AGENT=MyRedditCrawler/1.0 by YourUsername
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

### Step 3: Install & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py
```

### Step 4: Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Step 5: Test

Open browser: http://localhost:8000/docs

Try:
- `GET /posts?status=pending` - See pending posts
- `POST /admin/run-crawler` - Trigger crawler manually

## ✅ That's It!

The crawler will:
- Run automatically every 12 hours
- Fetch posts from configured subreddits
- Filter by keywords and engagement
- Store in SQLite database
- Be ready for workers to reply

## 📝 Next Steps

1. Configure subreddits: `SUBREDDITS=python,technology` in `.env`
2. Set keywords: `FILTER_KEYWORDS=python,api,automation` in `.env`
3. Build frontend (API is ready!)
4. Implement JWT auth for workers

See `README_SYSTEM.md` for full documentation.





