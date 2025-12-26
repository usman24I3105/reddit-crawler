# Backend Startup Commands

## 🚀 Quick Start

### Windows (PowerShell/CMD):
```bash
cd core
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Or use the batch file:
```bash
cd core
START_BACKEND.bat
```

### Linux/Mac:
```bash
cd core
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Or use the shell script:
```bash
cd core
chmod +x START_BACKEND.sh
./START_BACKEND.sh
```

## 📝 Command Breakdown

- `uvicorn` - ASGI server for FastAPI
- `main:app` - Points to `main.py` file and `app` variable
- `--host 0.0.0.0` - Listen on all network interfaces
- `--port 8000` - Port number
- `--reload` - Auto-reload on code changes (development)

## ✅ What You'll See

When backend starts successfully:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     APScheduler started successfully
```

## 🌐 Access Points

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🛑 Stop Backend

Press `Ctrl+C` in the terminal

## ⚠️ Troubleshooting

### Port already in use
```bash
# Use different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Module not found
```bash
# Make sure you're in core directory
cd core
# Install dependencies
pip install -r requirements.txt
```

### Database errors
```bash
# Initialize database first
python scripts/init_db.py
```





