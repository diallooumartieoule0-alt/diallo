Param(
    [switch]$NoCleanup
)

$ErrorActionPreference = 'Stop'

Write-Host "[test_docker] Checking Docker CLI..."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker CLI not found. Install Docker Desktop and ensure 'docker' is on PATH."
    exit 1
}

$Image = 'local/diallo:latest'
$Container = "test_diallo_$([System.Guid]::NewGuid().ToString('N').Substring(0,8))"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ModelHostPath = Join-Path $ScriptDir 'models'

if (-not (Test-Path $ModelHostPath)) {
    Write-Warning "models directory not found at: $ModelHostPath. The container may not find a serialized model."
}

Write-Host "[test_docker] Building Docker image: $Image"
docker build -t $Image .

Write-Host "[test_docker] Running container: $Container (detached, no network to avoid external calls)"
$volumeArg = ''
if (Test-Path $ModelHostPath) { $volumeArg = "--mount type=bind,source=`"$ModelHostPath`",target=/app/models" }

# Use a dummy token and no network to avoid external Telegram connections during the smoke test
$runCmd = "docker run --name $Container -e TELEGRAM_TOKEN='DUMMY_TOKEN' -e TELEGRAM_MODEL_PATH='/app/models/poisson_baseline.joblib' $volumeArg --network none -d $Image"
Write-Host "[test_docker] Command: $runCmd"
Invoke-Expression $runCmd

Write-Host "[test_docker] Waiting for container to initialize..."
Start-Sleep -Seconds 6

Write-Host "[test_docker] Fetching logs (last 200 lines)..."
docker logs --tail 200 $Container

if (-not $NoCleanup) {
    Write-Host "[test_docker] Cleaning up container..."
    docker rm -f $Container | Out-Null
    Write-Host "[test_docker] Container removed."
} else {
    Write-Host "[test_docker] Leaving container running (NoCleanup). Container name: $Container"
}

Write-Host "[test_docker] Done."
