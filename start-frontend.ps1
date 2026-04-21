$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "frontend")

Write-Host "Starting Streamlit frontend on http://localhost:8501"
& "..\.venv\Scripts\streamlit.exe" run app.py --browser.gatherUsageStats false
