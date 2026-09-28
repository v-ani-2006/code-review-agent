<#
.SYNOPSIS
    Automated Test Runner & Code Coverage Reporter for CodePilot AI.
.DESCRIPTION
    Executes unit tests, integration tests, security audits, and generates terminal, HTML, and XML coverage reports.
.PARAMETER Target
    Test scope: 'all' (default), 'unit', 'integration', 'security', 'performance', or 'coverage'.
.PARAMETER MinCoverage
    Minimum percentage threshold for coverage failure (default: 40).
.EXAMPLE
    .\scripts\test.ps1
    .\scripts\test.ps1 -Target unit
    .\scripts\test.ps1 -Target coverage
#>

param (
    [ValidateSet("all", "unit", "integration", "security", "performance", "coverage")]
    [string]$Target = "all",
    [int]$MinCoverage = 40
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
if (Test-Path ".\venv\Scripts") { $env:PATH = "$PWD\venv\Scripts;$env:PATH" }

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CodePilot AI - Automated Test Suite (Phase 13)" -ForegroundColor Cyan
Write-Host " Target Mode: $Target | Minimum Coverage: $MinCoverage%" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

switch ($Target) {
    "unit" {
        Write-Host "Executing Isolated Unit Tests..." -ForegroundColor Green
        pytest tests/unit -v -m unit
    }
    "integration" {
        Write-Host "Executing End-to-End API Integration Tests..." -ForegroundColor Green
        pytest tests/integration -v -m integration
    }
    "security" {
        Write-Host "Executing Security, Rate Limiting & Exploit Tests..." -ForegroundColor Green
        pytest tests/security -v -m security
    }
    "performance" {
        Write-Host "Executing Performance & Latency Benchmarks..." -ForegroundColor Green
        pytest tests/performance -v -m performance
    }
    "coverage" {
        Write-Host "Running Complete Test Suite with Comprehensive Coverage..." -ForegroundColor Green
        pytest --cov=app `
               --cov-report=term-missing `
               --cov-report=html:coverage_html `
               --cov-report=xml:coverage.xml `
               --cov-fail-under=$MinCoverage

        Write-Host "`n Coverage reports generated:" -ForegroundColor Cyan
        Write-Host "  - HTML: coverage_html\index.html" -ForegroundColor Cyan
        Write-Host "  - XML:  coverage.xml" -ForegroundColor Cyan
    }
    "all" {
        Write-Host "Executing Complete CodePilot AI Test Suite..." -ForegroundColor Green
        pytest -v
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Test execution completed successfully!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
