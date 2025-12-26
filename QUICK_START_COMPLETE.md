# 🚀 Quick Start - Complete Guide

## ✅ Both Issues Fixed!

### 1️⃣ Reddit API Keys Location

**File**: `core/.env`

Add your Reddit API credentials here:

```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=RedditCrawler/1.0 by YourUsername
```

**How to get keys:**
1. Go to: https://www.reddit.com/prefs/apps
2. Click "create app"
3. Choose "script" type
4. Copy Client ID and Secret
5. Paste in `core/.env`

**Keywords configuration** (same file):
```bash
FILTER_KEYWORDS=python,api,automation,fastapi,react
SUBREDDITS=python,webdev,technology
```

### 2️⃣ Frontend Display Fix

**File**: `frontend/.env` (already created)

```bash
VITE_USE_MOCK_API=false
VITE_API_URL=http://localhost:8000
```

This ensures frontend uses **real backend** (not mock).

## 🎯 Complete Setup Steps

### Step 1: Add Reddit API Keys

1. Open `core/.env`
2. Replace `PASTE_YOUR_REDDIT_CLIENT_ID_HERE` with your actual Client ID
3. Replace `PASTE_YOUR_REDDIT_CLIENT_SECRET_HERE` with your actual Secret
4. Update `REDDIT_USER_AGENT` with your Reddit username

### Step 2: Start Backend

```bash
cd core
uvicorn main:app --host 0.0.0.0 --port 8000
```

✅ Backend running at: http://localhost:8000

### Step 3: Start Frontend

**New terminal:**
```bash
cd frontend
npm run dev
```

✅ Frontend running at: http://localhost:3000

### Step 4: Login & Use

1. Open: http://localhost:3000
2. Login with **any email/password** (e.g., `test@test.com` / `test`)
3. You should see:
   - ✅ Dashboard with posts
   - ✅ "View" buttons
   - ✅ "Refresh" button
   - ✅ "Logout" button

### Step 5: Fetch Posts

Trigger crawler to fetch posts with keywords:

```bash
curl -X POST http://localhost:8000/admin/run-crawler
```

Or use API docs: http://localhost:8000/docs

## 📋 What You Should See

### Frontend Features:
- ✅ Login page (email/password)
- ✅ Dashboard with post cards
- ✅ Post detail page
- ✅ Assign button
- ✅ Reply form
- ✅ All buttons and options visible

### If Frontend Still Not Working:

1. **Check browser console** (F12) for errors
2. **Verify backend is running**: http://localhost:8000/health
3. **Clear browser cache**: Ctrl+Shift+Delete
4. **Check frontend .env**: Should have `VITE_USE_MOCK_API=false`
5. **Restart frontend**: Stop and run `npm run dev` again

## 🔑 Login Details

**Use ANY email and password!**

Examples:
- `worker1@test.com` / `password`
- `admin@test.com` / `admin123`
- `test@test.com` / `test`

## 📍 File Locations Summary

- **Reddit API Keys**: `core/.env`
- **Frontend Config**: `frontend/.env` (already set to use real backend)
- **Backend Code**: `core/main.py`
- **Frontend Code**: `frontend/src/`

## 🎉 You're All Set!

1. ✅ Add Reddit API keys to `core/.env`
2. ✅ Backend is running
3. ✅ Frontend configured to use real backend
4. ✅ Login and start using!

If you still see issues, check:
- Browser console (F12) for errors
- Backend logs for Reddit API errors
- Network tab to see API calls





