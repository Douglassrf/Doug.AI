# Doug.AI — Torre de Controle (as 4 camadas como um so sistema). Um ciclo por execucao.
$root = $PSScriptRoot
Set-Location $root
$py = Join-Path $root ".venv\Scripts\python.exe"
$log = Join-Path $root "data\orchestrator.log"
New-Item -ItemType Directory -Force -Path (Split-Path $log) | Out-Null
"[{0}] Ciclo da Torre de Controle..." -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss") | Tee-Object -FilePath $log -Append
# Sem --symbols: a Torre monitora automaticamente os pares que tem edge
# comprovado no Playbook (ver scripts/doug_orchestrate.py::pairs_with_proven_edge).
& $py scripts\doug_orchestrate.py *>&1 | Tee-Object -FilePath $log -Append
