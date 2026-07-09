# Cole chaves Binance testnet no .env (local, seguro — nao vai pro chat)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) { Copy-Item ".env.example" $envFile }

Write-Host "Binance Testnet — colar chaves (demo, dinheiro falso)" -ForegroundColor Cyan
Write-Host "Pagina: https://testnet.binance.vision/key/generate"
Write-Host ""

$apiKey = Read-Host "Cole BINANCE API Key"
$secret = Read-Host "Cole BINANCE Secret" -AsSecureString
$plainSecret = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
)

if (-not $apiKey -or -not $plainSecret) {
    Write-Error "Key ou Secret vazio."
}

$lines = Get-Content $envFile -Encoding UTF8
$out = @()
$seenKey = $seenSecret = $seenTestnet = $seenLive = $seenMock = $false

foreach ($line in $lines) {
    if ($line -match '^BINANCE_API_KEY=') { $out += "BINANCE_API_KEY=$apiKey"; $seenKey = $true; continue }
    if ($line -match '^BINANCE_API_SECRET=') { $out += "BINANCE_API_SECRET=$plainSecret"; $seenSecret = $true; continue }
    if ($line -match '^BINANCE_USE_TESTNET=') { $out += "BINANCE_USE_TESTNET=true"; $seenTestnet = $true; continue }
    if ($line -match '^BINANCE_LIVE_ENABLED=') { $out += "BINANCE_LIVE_ENABLED=false"; $seenLive = $true; continue }
    if ($line -match '^BINANCE_MOCK_ENABLED=') { $out += "BINANCE_MOCK_ENABLED=false"; $seenMock = $true; continue }
    $out += $line
}

if (-not $seenKey) { $out += "BINANCE_API_KEY=$apiKey" }
if (-not $seenSecret) { $out += "BINANCE_API_SECRET=$plainSecret" }
if (-not $seenTestnet) { $out += "BINANCE_USE_TESTNET=true" }
if (-not $seenLive) { $out += "BINANCE_LIVE_ENABLED=false" }
if (-not $seenMock) { $out += "BINANCE_MOCK_ENABLED=false" }

$out | Set-Content $envFile -Encoding UTF8
Write-Host "[OK] .env atualizado (chaves NAO commitadas)" -ForegroundColor Green

$env:PYTHONPATH = $PSScriptRoot
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "Testando conexao..."
& $py scripts/test_binance_testnet.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "Iniciando treino aprendiz (1 ciclo)..."
    & $py scripts/binance_apprentice_training.py --once
}
