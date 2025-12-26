# Fix: Posts Not Loading

## 🔍 Problem Diagnosis

The database has **0 posts**, which is why nothing is showing in the frontend.

## ✅ Solutions

### Solution 1: Lower Filter Thresholds

Your filters might be too strict. Edit `core/.env`:

```bash
# Lower these values to get more posts
MIN_UPVOTES=0
MIN_COMMENTS=0
```

### Solution 2: Remove Keywords Temporarily

To test if keywords are the issue, temporarily remove them:

```bash
FILTER_KEYWORDS=
```

Or set very common keywords:

```bash
FILTER_KEYWORDS=the,is,are
```

### Solution 3: Test Reddit Connection

Run the test script:

```bash
cd core
python scripts/test_reddit_connection.py
```

This will show:
- ✅ If Reddit API is working
- ✅ If posts are being fetched
- ✅ Why they're being filtered out

### Solution 4: Manually Trigger Crawler

After fixing filters, trigger crawler:

```bash
curl -X POST http://localhost:8000/admin/run-crawler
```

Or use PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/admin/run-crawler -Method POST
```

### Solution 5: Check Backend Logs

Look at backend terminal output for errors like:
- Reddit API authentication errors
- Filter messages
- Fetch errors

## 🎯 Quick Fix

1. **Edit `core/.env`**:
   ```bash
   MIN_UPVOTES=0
   MIN_COMMENTS=0
   FILTER_KEYWORDS=python,api,webdev
   ```

2. **Restart backend** (to load new .env values)

3. **Trigger crawler**:
   ```bash
   curl -X POST http://localhost:8000/admin/run-crawler
   ```

4. **Check database**:
   ```bash
   python -c "from src.db.session import SessionLocal; from src.db.models import Post; db = SessionLocal(); print(f'Posts: {db.query(Post).count()}'); db.close()"
   ```

## 📊 Expected Results

After fixing:
- Database should have posts
- Frontend should show posts
- API endpoint should return data

## ⚠️ Common Issues

1. **Reddit API credentials wrong** → Check `.env` file
2. **Filters too strict** → Lower MIN_UPVOTES/MIN_COMMENTS
3. **Keywords too specific** → Use broader keywords
4. **Subreddit has no recent posts** → Try different subreddits
5. **Backend not restarted** → Restart after changing .env





