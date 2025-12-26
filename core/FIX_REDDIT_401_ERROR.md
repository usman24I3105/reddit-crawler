# Fix: Reddit API 401 Error (Authentication Failed)

## 🔴 Problem

The Reddit API is returning **401 Unauthorized**, which means your credentials are not working.

## ✅ Solution

### Step 1: Verify Your Reddit App Settings

1. Go to: https://www.reddit.com/prefs/apps
2. Find your app (or create a new one)
3. **Check these settings:**
   - **App type**: Must be **"script"** (not web app)
   - **Client ID**: Should be visible under app name
   - **Secret**: Should be visible in the "secret" field

### Step 2: Fix USER_AGENT Format

Your USER_AGENT must be in this exact format:
```
AppName/Version by YourRedditUsername
```

**Example:**
```
RedditCrawler/1.0 by john_doe
```

**NOT:**
- ❌ `Crown Coastal` (missing format)
- ❌ `MyApp` (missing version and username)
- ❌ `RedditCrawler` (missing version and username)

### Step 3: Update .env File

Edit `core/.env` and make sure:

```bash
REDDIT_CLIENT_ID=your_actual_client_id_here
REDDIT_CLIENT_SECRET=your_actual_secret_here
REDDIT_USER_AGENT=RedditCrawler/1.0 by YourRedditUsername
```

**Important:**
- Replace `YourRedditUsername` with your **actual Reddit username**
- Use the format: `AppName/Version by Username`
- No spaces before/after "by"

### Step 4: Verify Credentials

Run the test script again:

```bash
cd core
python scripts/test_reddit_connection.py
```

You should see:
- `[OK] Connection successful!`
- `[OK] Fetched X raw posts`

### Step 5: Restart Backend

After fixing `.env`, restart the backend:

```bash
# Stop backend (Ctrl+C)
# Then restart:
cd core
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Step 6: Trigger Crawler

```bash
curl -X POST http://localhost:8000/admin/run-crawler
```

## 🔍 Common Issues

### Issue 1: Wrong App Type
- **Problem**: App is "web app" instead of "script"
- **Fix**: Create a new app with type "script"

### Issue 2: Wrong USER_AGENT Format
- **Problem**: USER_AGENT doesn't match format
- **Fix**: Use `AppName/Version by Username` format

### Issue 3: Wrong Credentials
- **Problem**: CLIENT_ID or SECRET are incorrect
- **Fix**: Double-check from Reddit apps page

### Issue 4: Credentials Not Loaded
- **Problem**: Backend didn't reload .env file
- **Fix**: Restart backend after changing .env

## 📝 Example .env

```bash
# Correct format
REDDIT_CLIENT_ID=abc123def456ghi789
REDDIT_CLIENT_SECRET=xyz789_secret_key_here
REDDIT_USER_AGENT=RedditCrawler/1.0 by john_doe

# Your Reddit username (for posting comments - optional)
REDDIT_USERNAME=john_doe
REDDIT_PASSWORD=your_password
```

## ✅ After Fixing

Once credentials work:
1. Test script should show `[OK] Connection successful!`
2. Crawler should fetch posts
3. Database should have posts
4. Frontend should display posts

## 🆘 Still Not Working?

1. **Create a new Reddit app** (sometimes old apps have issues)
2. **Check Reddit username** matches USER_AGENT
3. **Verify no extra spaces** in .env file
4. **Check backend logs** for detailed error messages





