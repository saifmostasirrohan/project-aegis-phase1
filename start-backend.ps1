$ErrorActionPreference = "Stop"

$port = 8001
$conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    $pidVal = $conn.OwningProcess
    Write-Host "Port $port is in use by PID $pidVal. Stopping it..."
    Stop-Process -Id $pidVal -Force -ErrorAction SilentlyContinue
    taskkill /PID $pidVal /T /F | Out-Null
}

# Run uvicorn from inside backend/ so relative imports and DB path resolve correctly
Set-Location (Join-Path $PSScriptRoot "backend")

Write-Host "Starting FastAPI backend on http://127.0.0.1:$port"
& "$PSScriptRoot\.venv\Scripts\uvicorn.exe" server:app --port $port
