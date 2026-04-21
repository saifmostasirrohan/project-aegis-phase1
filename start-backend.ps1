$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$port = 8001
$conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    $pidVal = $conn.OwningProcess
    Write-Host "Port $port is in use by PID $pidVal. Stopping it..."
    Stop-Process -Id $pidVal -Force -ErrorAction SilentlyContinue
    taskkill /PID $pidVal /T /F | Out-Null
}

Write-Host "Starting FastAPI backend on http://127.0.0.1:$port"
& ".\.venv\Scripts\uvicorn.exe" server:app --port $port
