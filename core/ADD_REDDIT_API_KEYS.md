# 🔑 How to Add Reddit API Keys

## Quick Steps

### 1. Get Reddit API Credentials

1. **Go to**: https://www.reddit.com/prefs/apps
2. **Scroll down** and click **"create another app..."** or **"create app"**
3. **Fill the form**:
   - **Name**: `Reddit Crawler` (or any name)
   - **App type**: Select **"script"** ⚠️ IMPORTANT
   - **Description**: (optional)
   - **About URL**: (optional)
   - **Redirect URI**: `http://localhost:8000` (can be anything)
4. **Click "create app"**
5. **Copy your credentials**:
   - **Client ID**: The string under your app name (looks like: `abc123def456ghi`)
   - **Secret**: The "secret" field (looks like: `xyz789_secret_key_here`)

### 2. Add to .env File

Open `core/.env` file and replace these lines:

```bash
REDDIT_CLIENT_ID=PASTE_YOUR_CLIENT_ID_HERE
REDDIT_CLIENT_SECRET=PASTE_YOUR_SECRET_HERE
REDDIT_USER_AGENT=RedditCrawler/1.0 by YourRedditUsername
```

**Example:**
```bash
REDDIT_CLIENT_ID=abc123def456ghi789
REDDIT_CLIENT_SECRET=xyz789_secret_key_here
REDDIT_USER_AGENT=RedditCrawler/1.0 by john_doe
```

### 3. Configure Keywords

In the same `.env` file, set keywords:

```bash
FILTER_KEYWORDS=python,api,automation,fastapi,react,webdev
```

### 4. Configure Subreddits

Set which subreddits to search:

```bash
SUBREDDITS=python,webdev,technology,reactjs
```

### 5. Restart Backend

After saving `.env`, restart the backend:

```bash
# Stop current backend (Ctrl+C)
# Then restart:
cd core
uvicorn main:app --host 0.0.0.0 --port 8000
```

## ✅ How It Works

1. **Fetches posts** from configured subreddits
2. **Searches for keywords** using Reddit search API (if keywords configured)
3. **Filters locally** by keywords in title/body
4. **Applies engagement filters** (min upvotes/comments)
5. **Saves to database** (SQLite)

## 🧪 Test After Adding Keys

```bash
# Manual trigger
curl -X POST http://localhost:8000/admin/run-crawler
```

Check logs to see if posts are being fetched!

## ⚠️ Important Notes

- **Client ID** and **Secret** are required for fetching posts
- **Username/Password** are only needed if you want to post comments
- **User Agent** format: `AppName/Version by YourUsername`
- App type must be **"script"** (not web app)

## 📍 File Location

Credentials go in: `core/.env`





