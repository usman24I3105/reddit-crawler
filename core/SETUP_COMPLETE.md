# ✅ Complete Setup Guide

## 🔑 Step 1: Add Reddit API Keys

### Get Your Reddit API Credentials

1. Visit: **https://www.reddit.com/prefs/apps**
2. Click **"create another app..."** or **"create app"**
3. Fill in:
   - **Name**: `Reddit Crawler`
   - **Type**: **"script"** ⚠️ (Important!)
   - **Redirect URI**: `http://localhost:8000`
4. Click **"create app"**
5. Copy:
   - **Client ID** (under app name)
   - **Secret** (the secret field)

### Add to .env File

Open `core/.env` and replace:

```bash
REDDIT_CLIENT_ID=your_actual_client_id_here
REDDIT_CLIENT_SECRET=your_actual_secret_here
REDDIT_USER_AGENT=RedditCrawler/1.0 by YourRedditUsername
```

**Example:**
```bash
REDDIT_CLIENT_ID=abc123def456ghi789
REDDIT_CLIENT_SECRET=xyz789_secret_key_here
REDDIT_USER_AGENT=RedditCrawler/1.0 by john_doe
```

### Configure Keywords

In `core/.env`, set keywords to search for:

```bash
FILTER_KEYWORDS=python,api,automation,fastapi,react,webdev
```

### Configure Subreddits

```bash
SUBREDDITS=python,webdev,technology,reactjs
```

## 🚀 Step 2: Start Backend

```bash
cd core
uvicorn main:app --host 0.0.0.0 --port 8000
```

Backend will be at: **http://localhost:8000**

## 🎨 Step 3: Start Frontend

**In a NEW terminal:**

```bash
cd frontend
npm install  # If not done already
npm run dev
```

Frontend will be at: **http://localhost:3000**

## 🔐 Step 4: Login

1. Open: **http://localhost:3000**
2. **Use ANY email/password** (e.g., `test@test.com` / `test`)
3. Click "Sign in"

## 📊 Step 5: Test the System

### Option A: Manual Crawler Trigger

```bash
curl -X POST http://localhost:8000/admin/run-crawler
```

### Option B: Wait for Scheduled Run

Crawler runs automatically every 12 hours.

## ✅ What You Should See

### Frontend Dashboard:
- ✅ Login page
- ✅ Dashboard with post list
- ✅ "View" button on each post
- ✅ "Refresh" button
- ✅ "Logout" button

### Post Detail Page:
- ✅ Full post title and body
- ✅ Engagement stats
- ✅ "Assign to Me" button
- ✅ "Reply" button (after assigning)
- ✅ Reddit permalink

## 🐛 Troubleshooting

### Frontend shows "No pending posts"
- Run crawler manually: `POST /admin/run-crawler`
- Check backend logs for errors
- Verify Reddit API credentials are correct

### Frontend not loading
- Check `frontend/.env` has `VITE_USE_MOCK_API=false`
- Restart frontend dev server
- Clear browser cache

### Reddit API errors
- Verify credentials in `core/.env`
- Check app type is "script" on Reddit
- Verify USER_AGENT format is correct

## 📝 Quick Reference

### Backend URLs:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Frontend URLs:
- App: http://localhost:3000
- Login: http://localhost:3000/login

### Login Credentials:
- **Any email/password works!**
- Example: `worker1@test.com` / `password`

## 🎯 Next Steps

1. ✅ Add Reddit API keys to `core/.env`
2. ✅ Start backend
3. ✅ Start frontend
4. ✅ Login and test
5. ✅ Trigger crawler to fetch posts
6. ✅ View posts in dashboard
7. ✅ Assign and reply to posts

Everything is ready! Just add your Reddit API keys and you're good to go! 🚀





