# Doug.AI — Ciclo automatico diario (paper):
#   1. Backtest walk-forward em candles reais (alimenta a memoria evolutiva)
#   2. Rodada de decisoes ao vivo (registra no log auditavel)
# Agendar via Task Scheduler (ex.: todo dia 06:00) ou rodar manualmente.
param(
    [int]$Pairs = 20,
    [int]$Candles = 1000,
    [int]$Granularity = 60,
    [int]$Horizon = 3,
    [int]$DecidePairs = 10
)

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$py = Join-Path $root ".venv\Scripts\python.exe"

Write-Host "[Doug.AI autocycle] $(Get-Date -Format 'yyyy-MM-dd HH:mm') — radar de noticias..."
& $py scripts\fetch_news.py

Write-Host "`n[Doug.AI autocycle] Backtest de $Pairs pares..."
& $py scripts\run_backtest.py --pairs $Pairs --candles $Candles --granularity $Granularity --horizon $Horizon

Write-Host "`n[Doug.AI autocycle] Rodada de decisoes ao vivo ($DecidePairs pares)..."
& $py scripts\doug_decide.py --pairs $DecidePairs

Write-Host "`n[Doug.AI autocycle] Concluido. Scorecard: data\training\backtest_scorecard.json"
