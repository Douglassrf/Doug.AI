# Registra o treino automatico do DogEye no Agendador de Tarefas do Windows.
# Rode este script UMA VEZ (PowerShell normal, nao precisa ser admin para tarefas do usuario atual).
#   cd C:\Users\USUARIO\Desktop\DOUG.AI
#   .\register_scheduled_tasks.ps1
#
# Cria 3 tarefas:
#   DougAI_Treino_Diario   -> todo dia as 07:00
#   DougAI_Treino_Semanal  -> toda segunda as 07:30
#   DougAI_Treino_Mensal   -> dia 1 de cada mes as 08:00
#
# A Torre de Controle (run_orchestrator.ps1) e outras automacoes (Edge Training,
# Noticias, Autocycle) tem tarefas proprias registradas fora deste arquivo — ver
# Agendador de Tarefas do Windows para a lista completa.
#
# Todas rodam 100% em modo demo/testnet (paper-trading). Nenhuma ordem real e enviada.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$root = $PSScriptRoot
$prevEap = $ErrorActionPreference

function Register-DougTask {
    param(
        [string]$Name,
        [string]$ScriptFile,
        [string]$Schedule,   # DAILY | WEEKLY | MONTHLY | MINUTE
        [string]$StartTime,  # HH:mm
        [int]$EveryMinutes = 0,   # so usado quando Schedule = MINUTE
        [string]$ExtraArgs = ""
    )
    $scriptPath = Join-Path $root $ScriptFile
    $action = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""

    $ErrorActionPreference = "SilentlyContinue"
    schtasks /Query /TN $Name > $null 2>&1
    $ErrorActionPreference = $prevEap
    $taskExists = ($LASTEXITCODE -eq 0)
    if ($taskExists) {
        Write-Host "Tarefa '$Name' ja existe - removendo para recriar com config atual." -ForegroundColor Yellow
        schtasks /Delete /TN $Name /F > $null 2>&1
    }

    if ($Schedule -eq "MONTHLY") {
        schtasks /Create /TN $Name /TR $action /SC MONTHLY /D 1 /ST $StartTime /F | Out-Null
    } elseif ($Schedule -eq "WEEKLY") {
        schtasks /Create /TN $Name /TR $action /SC WEEKLY /D MON /ST $StartTime /F | Out-Null
    } elseif ($Schedule -eq "MINUTE") {
        # Repete a cada N minutos, o dia inteiro (00:00-23:59) — para "ficar rodando
        # sozinho", nao so uma vez por dia.
        schtasks /Create /TN $Name /TR $action /SC MINUTE /MO $EveryMinutes /ST "00:00" /F | Out-Null
    } else {
        schtasks /Create /TN $Name /TR $action /SC DAILY /ST $StartTime /F | Out-Null
    }
    if ($Schedule -eq "MINUTE") {
        Write-Host "Tarefa registrada: $Name (a cada $EveryMinutes min, o dia todo)" -ForegroundColor Green
    } else {
        Write-Host "Tarefa registrada: $Name ($Schedule as $StartTime)" -ForegroundColor Green
    }

    # StartWhenAvailable: se o PC estiver desligado/bloqueado no horario exato
    # (comum em maquina pessoal), a tarefa roda assim que possivel depois em vez
    # de simplesmente falhar/pular o dia (achado real 2026-07-09: Treino_Diario e
    # Autocycle_Diario falhando todo dia com erro 0x800710E0 por causa disso).
    try {
        $task = Get-ScheduledTask -TaskName $Name -ErrorAction Stop
        $task.Settings.StartWhenAvailable = $true
        Set-ScheduledTask -TaskName $Name -Settings $task.Settings -ErrorAction Stop | Out-Null
    } catch {
        Write-Host "Aviso: nao foi possivel definir StartWhenAvailable em '$Name' ($_)" -ForegroundColor Yellow
    }
}

Write-Host "Registrando treino automatico DogEye / Doug.AI (paper-trading, demo/testnet apenas)" -ForegroundColor Cyan
Write-Host ""

Register-DougTask -Name "DougAI_Treino_Diario"  -ScriptFile "train_daily.ps1"   -Schedule "DAILY"   -StartTime "07:00"
Register-DougTask -Name "DougAI_Treino_Semanal" -ScriptFile "train_weekly.ps1"  -Schedule "WEEKLY"  -StartTime "07:30"
Register-DougTask -Name "DougAI_Treino_Mensal"  -ScriptFile "train_monthly.ps1" -Schedule "MONTHLY" -StartTime "08:00"
# Nota 2026-07-07: a Torre de Controle (run_orchestrator.ps1) ja tem tarefa
# propria fora deste script -> "DougAI_Torre_Controle" (a cada 2h). Nao
# duplicar aqui. Ver Agendador de Tarefas do Windows para a lista completa
# (DougAI_Torre_Controle, DougAI_Edge_Training, DougAI_Noticias_3h,
# DougAI_Autocycle_Diario tambem existem e nao sao geridos por este arquivo).

Write-Host ""
Write-Host "Pronto. Para conferir: schtasks /Query /TN DougAI_TorreDeControle /V /FO LIST" -ForegroundColor Cyan
Write-Host "Para desativar uma tarefa: schtasks /Change /TN <nome> /DISABLE" -ForegroundColor Cyan
Write-Host "Para remover: schtasks /Delete /TN <nome> /F" -ForegroundColor Cyan
Write-Host ""
Write-Host "Lembrete: essas tarefas so rodam com o computador ligado. Elas nunca habilitam trading real (guarda de seguranca em cada script)." -ForegroundColor Yellow
