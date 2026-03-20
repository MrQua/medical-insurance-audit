$ErrorActionPreference = "Stop"

$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ComposeFile = "docker-compose.prod.yml"
$EnvFile = ".env.prod"

Set-Location $AppDir

Write-Host "==> checking docker daemon"
$dockerVersion = docker version 2>$null
if ($LASTEXITCODE -ne 0) {
  throw "Docker daemon unavailable. Please start Docker Desktop first."
}

Write-Host "==> build and start containers"
docker compose -f $ComposeFile --env-file $EnvFile up -d --build

Write-Host "==> run database migrations"
docker compose -f $ComposeFile --env-file $EnvFile exec -T backend alembic upgrade head

Write-Host "==> show service status"
docker compose -f $ComposeFile --env-file $EnvFile ps

Write-Host "==> deployment finished"
