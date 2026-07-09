# DogEye — monitor ao vivo (Douglas abre isto)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONPATH = $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

Write-Host "DogEye LIVE -> http://localhost:8502" -ForegroundColor Green
& $python -m streamlit run dashboard/tip_to_tip_live.py --server.port 8502 --server.headless true
