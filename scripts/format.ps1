<#
.SYNOPSIS
    Automated Code Formatting Script for CodePilot AI.
.DESCRIPTION
    Applies consistent formatting across the codebase using Black, isort, and Ruff fix.
.EXAMPLE
    .\scripts\format.ps1
#>

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
if (Test-Path ".\venv\Scripts") { $env:PATH = "$PWD\venv\Scripts;$env:PATH" }

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CodePilot AI - Automated Code Formatter (Phase 13)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. isort - Organize and standardise imports
Write-Host "[1/3] Sorting imports with isort..." -ForegroundColor Yellow
try {
    isort app tests
    Write-Host " [OK] Import sorting completed." -ForegroundColor Green
} catch {
    Write-Warning "isort encountered an issue: $_"
}

# 2. Black - Format code to 88-character standard
Write-Host "[2/3] Formatting source code with Black..." -ForegroundColor Yellow
try {
    black app tests
    Write-Host " [OK] Black formatting completed." -ForegroundColor Green
} catch {
    Write-Warning "Black encountered an issue: $_"
}

# 3. Ruff - Fast linter autofix for safe rules
Write-Host "[3/3] Applying safe autofixes with Ruff..." -ForegroundColor Yellow
try {
    ruff check app tests --fix
    Write-Host " [OK] Ruff autofixes completed." -ForegroundColor Green
} catch {
    Write-Warning "Ruff encountered an issue: $_"
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Code formatting completed successfully!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
