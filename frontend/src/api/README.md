# API Client Documentation

## Overview

The API client supports both real backend and mock API modes, switchable via environment variables.

## Configuration

### Environment Variables

Create a `.env` file in the frontend root:

```bash
# Backend API URL (only used when VITE_USE_MOCK_API=false)
VITE_API_URL=http://localhost:8000

# Enable mock API
VITE_USE_MOCK_API=true

# Mock failure rate (0.0 to 1.0)
# 0.0 = never fail, 1.0 = always fail
VITE_MOCK_FAIL_RATE=0
```

## Usage

### Using Mock API (Development)

1. Set `VITE_USE_MOCK_API=true` in `.env`
2. Start frontend: `npm run dev`
3. Frontend works without backend running

### Using Real API (Production)

1. Set `VITE_USE_MOCK_API=false` or remove the variable
2. Ensure backend is running on `VITE_API_URL`
3. Frontend connects to real FastAPI backend

## API Methods

### `api.login(email, password)`

Authenticates user and returns token.

**Mock behavior:**
- Accepts any email/password
- Returns mock JWT token
- Stores token in localStorage

**Real behavior:**
- Calls `POST /auth/login`
- Returns real JWT token

### `api.getPosts(status, subreddit, limit)`

Fetches posts from backend.

**Mock behavior:**
- Returns in-memory mock posts
- Filters by status and subreddit
- Simulates 300-800ms delay

**Real behavior:**
- Calls `GET /posts?status={status}&subreddit={subreddit}&limit={limit}`
- Returns real posts from database

### `api.assignPost(postId, workerId)`

Assigns a post to a worker.

**Mock behavior:**
- Updates post status to 'in_progress'
- Sets assigned_to field
- Simulates network delay

**Real behavior:**
- Calls `POST /posts/{postId}/assign`
- Updates database

### `api.replyToPost(postId, commentText, workerId)`

Submits a reply to a post.

**Mock behavior:**
- Updates post status to 'replied'
- Removes post from pending list
- Returns success message

**Real behavior:**
- Calls `POST /posts/{postId}/reply`
- Posts comment to Reddit
- Updates database

## Error Simulation

Set `VITE_MOCK_FAIL_RATE` to simulate errors:

- `0.0` - Never fail (default)
- `0.1` - 10% failure rate
- `0.5` - 50% failure rate
- `1.0` - Always fail

Errors simulated:
- 401 Unauthorized (login)
- 403 Forbidden (reply without assignment)
- 404 Not Found (invalid post ID)
- 500 Server Error (random failures)

## Mock Data

Mock data is stored in `mockData.js`:
- 5 sample posts
- In-memory storage (resets on page refresh)
- Supports CRUD operations

## Switching Between Modes

No code changes needed! Just update `.env`:

```bash
# Development (mock)
VITE_USE_MOCK_API=true

# Production (real)
VITE_USE_MOCK_API=false
```

Restart dev server after changing `.env`.





