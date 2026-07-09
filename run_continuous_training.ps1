# DogEye — treino continuo automatico (deixe rodando a semana toda)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONPATH = $PSScriptRoot
$env:DOUG_MODE = "demo"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

Write-Host "DogEye TREINO CONTINUO — 15 pares x 10 estrategias" -ForegroundColor Cyan
Write-Host "Ctrl+C para parar | Relatorio: python scripts/dogeye_continuous_training.py --report" -ForegroundColor Yellow
& $python scripts/dogeye_continuous_training.py --interval 90 --samples 25
