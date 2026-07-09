# Doug.AI — Treino de EDGE REAL diario (M38 + Professor honesto).
# Alimenta o Playbook com vantagens comprovadas (nivel BOM 60-80% + ELITE 80%+).
param(
    [int]$Pairs = 15,
    [int]$Candles = 1000
)
$root = $PSScriptRoot
Set-Location $root
$py = Join-Path $root ".venv\Scripts\python.exe"
$log = Join-Path $root "data\edge_training.log"
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
"[{0}] Treino de edge ($Pairs pares, $Candles candles)..." -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss") | Tee-Object -FilePath $log -Append
& $py scripts\dogeye_edge_training.py --pairs $Pairs --candles $Candles *>&1 | Tee-Object -FilePath $log -Append
