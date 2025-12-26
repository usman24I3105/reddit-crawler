# Login Details for Worker Dashboard

## 🔐 Authentication

The backend now has a simple login endpoint that accepts any email and password for development purposes.

## 📝 Login Credentials

**You can use ANY email and password!**

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

## 🚀 How to Login

1. **Start the backend** (if not already running):
   ```bash
   cd core
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open browser**: http://localhost:3000

4. **Login with any credentials**:
   - Enter any email (e.g., `worker1@example.com`)
   - Enter any password (e.g., `password`)
   - Click "Sign in"

## 🔑 How It Works

- The backend `/auth/login` endpoint accepts any email/password
- It generates a unique token for each login
- The worker_id is extracted from the email (part before @)
- Token is stored in localStorage

## 📍 Backend Endpoints

- **Login**: `POST http://localhost:8000/auth/login`
- **Get Posts**: `GET http://localhost:8000/posts?status=pending`
- **Assign Post**: `POST http://localhost:8000/posts/{id}/assign`
- **Reply**: `POST http://localhost:8000/posts/{id}/reply`

## 🎯 Quick Test

You can test the login endpoint directly:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test"}'
```

Response:
```json
{
  "token": "worker_token_...",
  "worker_id": "test",
  "message": "Login successful"
}
```

## ⚠️ Note

This is a **development-only** authentication system. For production, implement:
- Real user database
- Password hashing
- JWT token validation
- Role-based access control





