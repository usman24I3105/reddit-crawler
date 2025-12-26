# Kill process using port 8000
Write-Host "Finding process using port 8000..."

$connection = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($connection) {
    $processId = $connection.OwningProcess
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    
    if ($process) {
        Write-Host "Found process: $($process.ProcessName) (PID: $processId)"
        Write-Host "Killing process..."
        Stop-Process -Id $processId -Force
        Write-Host "Process killed. Waiting 2 seconds..."
        Start-Sleep -Seconds 2
        Write-Host "✅ Port 8000 is now free!"
    } else {
        Write-Host "Process not found, but port may still be in use."
    }
} else {
    Write-Host "No process found on port 8000"
}

Write-Host "`nYou can now start the backend:"
Write-Host "  uvicorn main:app --host 0.0.0.0 --port 8000"





