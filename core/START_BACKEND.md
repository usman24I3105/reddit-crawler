# Backend Startup Guide

## ✅ Backend is Running!

The backend server has been started successfully.

## 🌐 Access Points

- **API Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root Endpoint**: http://localhost:8000/

## 🔐 Login Details

### **You can use ANY email and password!**

The authentication system accepts any credentials for development.

### Example Credentials:

```
Email: worker1@example.com
Password: password
```

OR

```
Email: admin@test.com
Password: admin123
```

OR

```
Email: test@test.com
Password: test
```

**Any email/password combination will work!**

## 📡 API Endpoints

### Authentication
- **Login**: `POST http://localhost:8000/auth/login`
  ```json
  {
    "email": "worker1@example.com",
    "password": "password"
  }
  ```
  Response:
  ```json
  {
    "token": "worker_token_...",
    "worker_id": "worker1",
    "message": "Login successful"
  }
  ```

### Posts
- **Get Posts**: `GET http://localhost:8000/posts?status=pending`
- **Assign Post**: `POST http://localhost:8000/posts/{id}/assign`
- **Reply to Post**: `POST http://localhost:8000/posts/{id}/reply`

### Admin
- **Run Crawler**: `POST http://localhost:8000/admin/run-crawler`
- **Scheduler Status**: `GET http://localhost:8000/admin/scheduler/status`

## 🧪 Quick Test

Test the login endpoint:

```bash
curl -X POST http://localhost:8000/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"test@test.com\", \"password\": \"test\"}"
```

Or using PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/auth/login `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"test@test.com","password":"test"}'
```

## 🚀 Using with Frontend

1. **Start Frontend** (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

2. **Open Browser**: http://localhost:3000

3. **Login** with any email/password

4. **Use the Dashboard** to view and manage posts

## 📊 Database

- **Type**: SQLite
- **Location**: `core/reddit_crawler.db`
- **Status**: Initialized and ready

## ⚙️ Configuration

The backend uses environment variables. Key settings:

- `CRAWLER_INTERVAL_HOURS=12` - Crawler runs every 12 hours
- `DATABASE_URL=sqlite:///./reddit_crawler.db` - Database location
- `REDDIT_CLIENT_ID` - Your Reddit API credentials (optional for testing)

## 🛑 Stopping the Backend

Press `Ctrl+C` in the terminal where uvicorn is running.

## 📝 Notes

- The backend runs on port 8000
- Scheduler starts automatically
- Database is SQLite (no separate database server needed)
- CORS is enabled for frontend access
- All logs are written to stdout





