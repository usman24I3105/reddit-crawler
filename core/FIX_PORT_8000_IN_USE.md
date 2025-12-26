# Fix: Port 8000 Already in Use

## 🔴 Problem

Error: `[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): only one usage of each socket address (protocol/network address/port) is normally permitted`

This means another process is already using port 8000.

## ✅ Solution 1: Kill Process Using Port 8000 (Windows)

### PowerShell:
```powershell
# Find and kill process
$process = Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess
Stop-Process -Id $process -Force

# Or use the script:
.\KILL_PORT_8000.ps1
```

### CMD:
```cmd
# Find process
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /F /PID <PID>

# Or use the batch file:
KILL_PORT_8000.bat
```

## ✅ Solution 2: Use Different Port

If you can't kill the process, use a different port:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

Then update frontend `.env`:
```bash
VITE_API_URL=http://localhost:8001
```

## ✅ Solution 3: Find What's Using Port 8000

### PowerShell:
```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object LocalPort, State, OwningProcess
Get-Process -Id <PID> | Select-Object ProcessName, Id
```

### CMD:
```cmd
netstat -ano | findstr :8000
tasklist | findstr <PID>
```

## 🚀 After Fixing

1. **Kill the process** (Solution 1)
2. **Wait 2 seconds**
3. **Start backend**:
   ```bash
   cd core
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## 📝 Quick Commands

### Kill and Restart (PowerShell):
```powershell
cd "D:\Projects\reddit scraping\core"
.\KILL_PORT_8000.ps1
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Kill and Restart (CMD):
```cmd
cd "D:\Projects\reddit scraping\core"
KILL_PORT_8000.bat
uvicorn main:app --host 0.0.0.0 --port 8000
```

## ⚠️ Common Causes

1. **Previous backend instance** still running
2. **Another application** using port 8000
3. **Backend crashed** but process didn't exit

## ✅ Verify Port is Free

```powershell
# Should return nothing if port is free
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```





