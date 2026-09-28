<#
.SYNOPSIS
    Convenience wrapper for Docker operations on Windows / Docker Desktop.
.DESCRIPTION
    Provides simple subcommands for building, starting, stopping, inspecting,
    migrating, and testing the CodePilot AI containerized environment.
.PARAMETER Action
    Command to run: 'up', 'down', 'build', 'restart', 'logs', 'migrate', 'test', 'health', 'ps'.
.PARAMETER Prod
    Use docker-compose.prod.yml instead of development docker-compose.yml.
.EXAMPLE
    .\scripts\docker_manage.ps1 -Action up
    .\scripts\docker_manage.ps1 -Action build
    .\scripts\docker_manage.ps1 -Action logs
    .\scripts\docker_manage.ps1 -Action migrate
    .\scripts\docker_manage.ps1 -Action test
    .\scripts\docker_manage.ps1 -Action up -Prod
#>

param (
    [ValidateSet("up", "down", "build", "restart", "logs", "migrate", "test", "health", "ps")]
    [string]$Action = "up",
    [switch]$Prod
)

$ErrorActionPreference = "Stop"
$ComposeFile = if ($Prod) { "docker-compose.prod.yml" } else { "docker-compose.yml" }
$Mode = if ($Prod) { "Production" } else { "Development" }

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CodePilot AI — Docker Orchestrator ($Mode)" -ForegroundColor Cyan
Write-Host " Compose File: $ComposeFile | Action: $Action" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

switch ($Action) {
    "up" {
        Write-Host "Starting containers..." -ForegroundColor Green
        docker compose -f $ComposeFile up -d
        docker compose -f $ComposeFile ps
    }
    "build" {
        Write-Host "Building and starting containers..." -ForegroundColor Green
        docker compose -f $ComposeFile up --build -d
        docker compose -f $ComposeFile ps
    }
    "down" {
        Write-Host "Stopping and removing containers..." -ForegroundColor Yellow
        docker compose -f $ComposeFile down
    }
    "restart" {
        Write-Host "Restarting containers..." -ForegroundColor Yellow
        docker compose -f $ComposeFile restart
    }
    "logs" {
        Write-Host "Tailing backend logs (Ctrl+C to exit)..." -ForegroundColor Cyan
        docker compose -f $ComposeFile logs -f backend
    }
    "migrate" {
        Write-Host "Applying database migrations inside backend container..." -ForegroundColor Cyan
        docker compose -f $ComposeFile exec backend alembic upgrade head
    }
    "test" {
        Write-Host "Running pytest inside backend container..." -ForegroundColor Cyan
        docker compose -f $ComposeFile exec backend pytest
    }
    "health" {
        Write-Host "Checking service health..." -ForegroundColor Cyan
        docker compose -f $ComposeFile ps
        try {
            $resp = Invoke-RestMethod -Uri "http://localhost/health" -Method Get -TimeoutSec 5
            Write-Host "Nginx /health HTTP response:" -ForegroundColor Green
            $resp | Format-List
        } catch {
            Write-Warning "Could not reach http://localhost/health via Nginx: $_"
            try {
                $resp2 = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
                Write-Host "Direct backend /health HTTP response:" -ForegroundColor Green
                $resp2 | Format-List
            } catch {
                Write-Error "Backend is not responding on port 8000 either: $_"
            }
        }
    }
    "ps" {
        docker compose -f $ComposeFile ps
    }
}
