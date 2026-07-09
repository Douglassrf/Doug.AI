# DogEye - treino SEMANAL automatico (paper-trading, nunca dinheiro real)
# Registrado no Agendador de Tarefas do Windows por register_scheduled_tasks.ps1
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
        Write-Error "ABORTADO: encontrado *_LIVE_ENABLED=true no .env. Treino automatico so roda com tudo em modo demo/testnet."
        exit 1
    }
}

$reportsDir = Join-Path $PSScriptRoot "data\training\reports"
New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null
$stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$reportFile = Join-Path $reportsDir "weekly_$stamp.md"

Write-Host "DogEye - treino semanal ($stamp)" -ForegroundColor Cyan

# Lote semanal: 100+100 pares com mais amostras por par
$curriculum1 = & $python scripts/dogeye_curriculum_training.py --samples-per-pair 8 2>&1 | Out-String
$reportCmd = & $python scripts/dogeye_continuous_training.py --report 2>&1 | Out-String
$coachReport = & $python scripts/dogeye_continuous_training.py --coach 2>&1 | Out-String

$out = @()
$out += "# DogEye - Treino Semanal - $stamp"
$out += ""
$out += "100+100 pares | 8 sims/par | demo/testnet"
$out += ""
$out += "## Sessao semanal completa"
$out += '```'
$out += $curriculum1
$out += '```'
$out += ""
$out += "## Leaderboard - melhores por cenario"
$out += '```'
$out += $reportCmd
$out += '```'
$out += ""
$out += "## Professor (coach) - mastery report da semana"
$out += '```'
$out += $coachReport
$out += '```'
$out -join "`r`n" | Out-File -FilePath $reportFile -Encoding utf8

Write-Host "Relatorio salvo em: $reportFile" -ForegroundColor Green
