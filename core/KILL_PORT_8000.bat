@echo off
echo Finding process using port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a...
    taskkill /F /PID %%a
    echo Process killed. Waiting 2 seconds...
    timeout /t 2 /nobreak >nul
)
echo Port 8000 should now be free.
echo You can now start the backend:
echo   uvicorn main:app --host 0.0.0.0 --port 8000





