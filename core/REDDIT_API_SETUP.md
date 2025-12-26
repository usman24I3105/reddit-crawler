# Reddit API Setup Guide

## 🔑 Where to Add Reddit API Credentials

### Step 1: Get Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Scroll down and click **"create another app..."** or **"create app"**
3. Fill in the form:
   - **Name**: Your app name (e.g., "Reddit Crawler")
   - **App type**: Select **"script"**
   - **Description**: Optional
   - **About URL**: Optional
   - **Redirect URI**: `http://localhost:8000` (can be anything for script type)
4. Click **"create app"**
5. You'll see:
   - **Client ID**: The string under your app name (looks like: `abc123def456`)
   - **Secret**: The "secret" field (looks like: `xyz789_secret_key`)

### Step 2: Add Credentials to .env File

Open `core/.env` file and replace the placeholder values:

```bash
REDDIT_CLIENT_ID=paste_your_client_id_here
REDDIT_CLIENT_SECRET=paste_your_secret_here
REDDIT_USER_AGENT=RedditCrawler/1.0 by YourRedditUsername
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

**Important Notes:**
- `REDDIT_USER_AGENT` format: `AppName/Version by YourUsername`
- `REDDIT_USERNAME` and `REDDIT_PASSWORD` are only needed if you want to post comments
- For just fetching posts, you only need `CLIENT_ID`, `CLIENT_SECRET`, and `USER_AGENT`

### Step 3: Configure Keywords

In the same `.env` file, set keywords to search for:

```bash
FILTER_KEYWORDS=python,reddit,api,automation,fastapi,react,webdev
```

The crawler will:
1. Fetch posts from configured subreddits
2. Filter posts that contain these keywords in title or body
3. Store matching posts in the database

### Step 4: Configure Subreddits

Set which subreddits to crawl:

```bash
SUBREDDITS=Home,technology,python,webdev,reactjs
```

### Step 5: Restart Backend

After updating `.env`, restart the backend:

```bash
# Stop the current backend (Ctrl+C)
# Then restart:
cd core
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📝 Example .env File

```bash
# Reddit API - REQUIRED
REDDIT_CLIENT_ID=abc123def456ghi789
REDDIT_CLIENT_SECRET=xyz789_secret_key_here
REDDIT_USER_AGENT=RedditCrawler/1.0 by myusername
REDDIT_USERNAME=myusername
REDDIT_PASSWORD=mypassword

# Keywords to search for
FILTER_KEYWORDS=python,api,automation,webdev,react

# Subreddits to crawl
SUBREDDITS=python,webdev,technology

# Other settings
CRAWLER_INTERVAL_HOURS=12
POST_LIMIT=100
MIN_UPVOTES=5
MIN_COMMENTS=2
```

## 🔍 How Keyword Filtering Works

1. **Fetch Phase**: Crawler fetches posts from configured subreddits
2. **Filter Phase**: Keyword filter checks if post title or body contains any keyword
3. **Case-insensitive**: Matching is case-insensitive
4. **Storage**: Only matching posts are saved to database

## ✅ Testing

After adding credentials, test the crawler:

```bash
# Manual trigger via API
curl -X POST http://localhost:8000/admin/run-crawler
```

Or use the API docs: http://localhost:8000/docs

## ⚠️ Troubleshooting

### "Reddit authentication failed"
- Check `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` are correct
- Verify `REDDIT_USER_AGENT` format is correct
- Make sure app type is "script" on Reddit

### "No posts found"
- Check subreddit names are correct (no r/ prefix needed)
- Verify keywords aren't too restrictive
- Check MIN_UPVOTES and MIN_COMMENTS thresholds

### "Rate limit exceeded"
- Reddit API has rate limits
- Wait a few minutes and try again
- Reduce POST_LIMIT if needed





