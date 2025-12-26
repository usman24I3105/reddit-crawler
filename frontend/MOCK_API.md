# Mock API Guide

## Quick Start

1. **Enable mock API:**
   ```bash
   # In .env file
   VITE_USE_MOCK_API=true
   ```

2. **Start frontend:**
   ```bash
   npm run dev
   ```

3. **Use the app:**
   - Login with any email/password
   - View mock posts
   - Assign and reply to posts
   - Everything works without backend!

## Mock Data

The mock API includes 5 sample posts:
- 2 from `webdev` subreddit
- 2 from `python` subreddit
- 1 from `reactjs` subreddit

All posts start with `status: 'pending'`.

## Testing Error States

Set failure rate in `.env`:
```bash
VITE_MOCK_FAIL_RATE=0.2  # 20% failure rate
```

This simulates:
- Network errors
- Server errors
- Authentication failures

## Mock Behavior

### Login
- **Any email/password works**
- Returns mock JWT token
- Stores in localStorage

### Get Posts
- Returns filtered posts
- Simulates 300-800ms delay
- Supports status and subreddit filters

### Assign Post
- Updates post status to `in_progress`
- Sets `assigned_to` field
- Returns success message

### Reply to Post
- Updates post status to `replied`
- Post disappears from pending list
- Returns success with comment ID

## Switching to Real API

1. Set `VITE_USE_MOCK_API=false` in `.env`
2. Ensure backend is running
3. Restart dev server

No code changes needed!

## Development Tips

- Mock data resets on page refresh
- Use browser console to inspect mock data
- Adjust `VITE_MOCK_FAIL_RATE` to test error handling
- Mock delays simulate real network conditions





