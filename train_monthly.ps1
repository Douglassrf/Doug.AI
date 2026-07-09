# DogEye - auditoria e consolidacao MENSAL (paper-trading, nunca dinheiro real)
# Registrado no Agendador de Tarefas do Windows por register_scheduled_tasks.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONPATH = $PSScriptRoot
$env:DOUG_MODE = "demo"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

$envFile = Join-Path $PSScriptRoot ".env"
$liveStatus = "OK - nenhum LIVE_ENABLED=true encontrado"
if (Test-Path $envFile) {
    $liveOn = Select-String -Path $envFile -Pattern "LIVE_ENABLED\s*=\s*true" -Quiet
    if ($liveOn) {
        $liveStatus = "ALERTA: *_LIVE_ENABLED=true encontrado no .env - revisar antes de qualquer treino real"
    }
}

$reportsDir = Join-Path $PSScriptRoot "data\training\reports"
New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null
$stamp = Get-Date -Format "yyyy-MM"
$reportFile = Join-Path $reportsDir "monthly_$stamp.md"

Write-Host "DogEye - auditoria mensal ($stamp)" -ForegroundColor Cyan

$coachReport = & $python scripts/dogeye_continuous_training.py --coach 2>&1 | Out-String
$reportCmd = & $python scripts/dogeye_continuous_training.py --report 2>&1 | Out-String

$cutoff = (Get-Date).AddDays(-31)
$recent = Get-ChildItem -Path $reportsDir -Filter "*.md" | Where-Object {
    $_.Name -ne (Split-Path $reportFile -Leaf) -and $_.LastWriteTime -ge $cutoff
} | Sort-Object LastWriteTime

$out = @()
$out += "# DogEye - Auditoria Mensal - $stamp"
$out += ""
$out += "Verificacao de seguranca: $liveStatus"
$out += ""
$out += "Relatorios diarios/semanais encontrados no ultimo mes: $($recent.Count)"
foreach ($f in $recent) { $out += "- $($f.Name)" }
$out += ""
$out += "## Leaderboard consolidado (estado atual)"
$out += '```'
$out += $reportCmd
$out += '```'
$out += ""
$out += "## Professor (coach) - mastery report do mes"
$out += '```'
$out += $coachReport
$out += '```'
$out += ""
$out += "## Pendencia para Douglas"
$out += "- Revisar se o volume de treinos diarios/semanais do mes esta de acordo com o esperado (contagem acima)."
$out += "- Confirmar que nenhum ciclo tentou live trading (ver verificacao de seguranca acima)."
$out -join "`r`n" | Out-File -FilePath $reportFile -Encoding utf8

Write-Host "Relatorio salvo em: $reportFile" -ForegroundColor Green
