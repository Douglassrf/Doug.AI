# Doug.AI Dashboard — local launch (Windows, no Docker)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$env:PYTHONPATH = $PSScriptRoot
$env:DOUG_MODE = "paper"
$env:DEMO_MODE = "1"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Virtualenv not found. Run: python -m venv .venv && .\.venv\Scripts\pip install -r requirements-dashboard.txt"
}

& $python -m streamlit run dashboard/app.py --server.port 8501
