<#
.SYNOPSIS
    Automated test runner and quality assurance script for Windows PowerShell.
.DESCRIPTION
    Runs unit tests, integration tests, security audits, performance benchmarks, and generates coverage reports.
.PARAMETER Target
    Specify test scope: 'all' (default), 'unit', 'integration', 'security', 'performance', or 'coverage'.
.EXAMPLE
    .\scripts\run_tests.ps1 -Target unit
    .\scripts\run_tests.ps1 -Target coverage
#>

param (
    [ValidateSet("all", "unit", "integration", "security", "performance", "coverage")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CodePilot AI - Phase 11 Automated Testing Infrastructure" -ForegroundColor Cyan
Write-Host " Target Mode: $Target" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

switch ($Target) {
    "unit" {
        Write-Host "Running Isolated Unit Tests..." -ForegroundColor Green
        pytest tests/unit -v -m unit
    }
    "integration" {
        Write-Host "Running End-to-End API Integration Tests..." -ForegroundColor Green
        pytest tests/integration -v -m integration
    }
    "security" {
        Write-Host "Running Security, Rate Limiting, and Exploit Rejection Tests..." -ForegroundColor Green
        pytest tests/security -v -m security
    }
    "performance" {
        Write-Host "Running Latency and Throughput Benchmarks..." -ForegroundColor Green
        pytest tests/performance -v -m performance
    }
    "coverage" {
        Write-Host "Running Full Test Suite with HTML Coverage Report..." -ForegroundColor Green
        pytest --cov=app --cov-report=term-missing --cov-report=html:coverage_html --cov-report=xml:coverage.xml
        Write-Host "Coverage report saved to: coverage_html/index.html" -ForegroundColor Cyan
    }
    "all" {
        Write-Host "Executing Complete CodePilot AI Test Suite..." -ForegroundColor Green
        pytest -v
    }
}

Write-Host ""
Write-Host "All tests completed successfully!" -ForegroundColor Green
