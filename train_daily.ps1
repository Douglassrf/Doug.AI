# DogEye - treino DIARIO: 100 pares Deriv + 100 Binance TODO DIA
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONPATH = $PSScriptRoot
$env:DOUG_MODE = "demo"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    $liveOn = Select-String -Path $envFile -Pattern "LIVE_ENABLED\s*=\s*true" -Quiet
    if ($liveOn) {
        Write-Error "ABORTADO: *_LIVE_ENABLED=true no .env."
        exit 1
    }
}

$reportsDir = Join-Path $PSScriptRoot "data\training\reports"
New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null
$stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$reportFile = Join-Path $reportsDir "daily_$stamp.md"

Write-Host "DogEye - 100+100 pares TODO DIA ($stamp)" -ForegroundColor Cyan
Write-Host "Estimativa: ~1000 simulacoes (5 por par x 200 pares) - aguarde..." -ForegroundColor Yellow

$curriculum = & $python scripts/dogeye_curriculum_training.py --samples-per-pair 5 2>&1 | Out-String
$coachReport = & $python scripts/dogeye_continuous_training.py --coach 2>&1 | Out-String

$out = @()
$out += "# DogEye - Treino Diario COMPLETO - $stamp"
$out += ""
$out += "**100 pares Deriv + 100 pares Binance todo dia** | demo/testnet"
$out += ""
$out += "## Sessao"
$out += '```'
$out += $curriculum
$out += '```'
$out += ""
$out += "## Professor"
$out += '```'
$out += $coachReport
$out += '```'
$out -join "`r`n" | Out-File -FilePath $reportFile -Encoding utf8

Write-Host "Relatorio: $reportFile" -ForegroundColor Green
