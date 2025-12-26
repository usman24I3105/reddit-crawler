# 🚨 Quick Fix Summary

## Problem: Posts Not Loading

**Root Cause**: Reddit API returning 401 (authentication failed)

## ✅ Fix Steps (5 minutes)

### 1. Check Reddit App
- Go to: https://www.reddit.com/prefs/apps
- Verify app type is **"script"**
- Copy Client ID and Secret

### 2. Fix .env File

Edit `core/.env`:

```bash
REDDIT_CLIENT_ID=paste_your_client_id
REDDIT_CLIENT_SECRET=paste_your_secret
REDDIT_USER_AGENT=RedditCrawler/1.0 by YourRedditUsername
```

**⚠️ IMPORTANT**: 
- Replace `YourRedditUsername` with your **actual Reddit username**
- Format must be: `AppName/Version by Username`

### 3. Test Connection

```bash
cd core
python scripts/test_reddit_connection.py
```

Should show: `[OK] Connection successful!`

### 4. Restart Backend

```bash
cd core
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Trigger Crawler

```bash
curl -X POST http://localhost:8000/admin/run-crawler
```

### 6. Check Frontend

Open: http://localhost:3000
- Login with any email/password
- Should see posts in dashboard

## 📊 Current Status

- ✅ Reddit credentials: SET
- ❌ Reddit API: 401 Error (authentication failed)
- ❌ Database: 0 posts
- ✅ Frontend: Configured correctly
- ✅ API endpoint: Working (returns empty array)

## 🎯 After Fix

- ✅ Reddit API: Should work
- ✅ Database: Should have posts
- ✅ Frontend: Should display posts

## 🔑 Key Issue

**USER_AGENT format is wrong!**

Current: `Crown Coastal`  
Should be: `RedditCrawler/1.0 by YourRedditUsername`

Fix this in `core/.env` and restart backend!





