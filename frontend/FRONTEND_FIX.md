# Frontend Configuration Fix

## Issue: Frontend Not Displaying Options

The frontend might be using mock API instead of the real backend.

## ✅ Solution

### Step 1: Check Frontend .env File

Create or update `frontend/.env`:

```bash
# Use REAL backend (not mock)
VITE_USE_MOCK_API=false

# Backend URL
VITE_API_URL=http://localhost:8000
```

### Step 2: Restart Frontend

After updating `.env`, restart the frontend:

```bash
cd frontend
npm run dev
```

### Step 3: Clear Browser Cache

- Open browser DevTools (F12)
- Right-click refresh button
- Select "Empty Cache and Hard Reload"

### Step 4: Verify Backend is Running

Check backend is running:
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy","scheduler":"active"}`

## 🔍 Troubleshooting

### Frontend shows "No pending posts"

1. **Check backend has data:**
   ```bash
   # Trigger crawler manually
   curl -X POST http://localhost:8000/admin/run-crawler
   ```

2. **Check API directly:**
   ```bash
   curl http://localhost:8000/posts?status=pending
   ```

3. **Check browser console** for errors (F12)

### Frontend shows mock data

- Ensure `VITE_USE_MOCK_API=false` in `frontend/.env`
- Restart frontend dev server
- Clear browser localStorage:
  ```javascript
  localStorage.clear()
  ```

### CORS Errors

Backend CORS is already configured. If you see CORS errors:
- Check backend is running on port 8000
- Check frontend is using correct API URL
- Verify CORS middleware in `main.py`

## 📋 Expected Frontend Features

After fixing, you should see:

1. **Login Page** - Email/password form
2. **Dashboard** - List of pending posts with:
   - Subreddit badge
   - Post title (truncated)
   - Upvotes and comments count
   - "View" button
   - Refresh button
   - Logout button
3. **Post Detail** - When clicking "View":
   - Full post title and body
   - Engagement stats
   - "Assign to Me" button
   - "Reply" button (after assigning)
   - Reddit permalink
4. **Reply Form** - Textarea with character counter

## 🧪 Test Frontend

1. Login with any email/password
2. Should see dashboard with posts (if any exist)
3. Click "View" on a post
4. Click "Assign to Me"
5. Click "Reply"
6. Write reply and submit

If any step fails, check browser console for errors.





