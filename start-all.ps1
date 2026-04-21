$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$backendScript = Join-Path $PSScriptRoot "start-backend.ps1"
$frontendScript = Join-Path $PSScriptRoot "start-frontend.ps1"

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$backendScript`""
)

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$frontendScript`""
)

Write-Host "Launched backend and frontend in separate terminals."
Write-Host "Backend: http://127.0.0.1:8001"
Write-Host "Frontend: http://localhost:8501"
