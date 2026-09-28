<#
.SYNOPSIS
    Automated Code Quality & Linter Verification Script for Windows PowerShell.
.DESCRIPTION
    Runs Ruff, Black (check-only), isort (check-only), MyPy, and Bandit security scans.
.PARAMETER Strict
    Treat warnings as fatal errors.
.EXAMPLE
    .\scripts\lint.ps1
    .\scripts\lint.ps1 -Strict
#>

param (
    [switch]$Strict
)

$ErrorActionPreference = "Continue"
$env:PYTHONPATH = "."
if (Test-Path ".\venv\Scripts") { $env:PATH = "$PWD\venv\Scripts;$env:PATH" }
$Failures = 0

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CodePilot AI - Code Quality & Linting Verification" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Ruff Linter
Write-Host "`n[1/5] Running Ruff Linter..." -ForegroundColor Yellow
ruff check .
if ($LASTEXITCODE -ne 0) {
    Write-Host " [FAIL] Ruff identified linting issues." -ForegroundColor Red
    $Failures++
} else {
    Write-Host " [PASS] Ruff linting clean." -ForegroundColor Green
}

# 2. Black Code Formatting Check
Write-Host "`n[2/5] Checking Black Code Formatting..." -ForegroundColor Yellow
black --check --diff .
if ($LASTEXITCODE -ne 0) {
    Write-Host " [FAIL] Black formatting issues detected. Run .\scripts\format.ps1 to fix." -ForegroundColor Red
    $Failures++
} else {
    Write-Host " [PASS] Black code style conforms to standard." -ForegroundColor Green
}

# 3. isort Import Order Check
Write-Host "`n[3/5] Checking isort Import Order..." -ForegroundColor Yellow
isort --check-only --diff .
if ($LASTEXITCODE -ne 0) {
    Write-Host " [FAIL] Import sorting discrepancies detected. Run .\scripts\format.ps1 to fix." -ForegroundColor Red
    $Failures++
} else {
    Write-Host " [PASS] Import sorting conforms to standard." -ForegroundColor Green
}

# 4. MyPy Static Type Analysis
Write-Host "`n[4/5] Running MyPy Static Type Analysis..." -ForegroundColor Yellow
mypy app --config-file=mypy.ini
if ($LASTEXITCODE -ne 0) {
    Write-Host " [FAIL] MyPy reported static type mismatches." -ForegroundColor Red
    $Failures++
} else {
    Write-Host " [PASS] MyPy static typing verified." -ForegroundColor Green
}

# 5. Bandit AST Security Scanner
Write-Host "`n[5/5] Running Bandit AST Security Audit..." -ForegroundColor Yellow
bandit -c .bandit -r app -ll
if ($LASTEXITCODE -ne 0) {
    Write-Host " [FAIL] Bandit detected security issues in application source." -ForegroundColor Red
    $Failures++
} else {
    Write-Host " [PASS] Bandit security scan passed." -ForegroundColor Green
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
if ($Failures -gt 0) {
    Write-Host " Quality check finished with $Failures failure(s)." -ForegroundColor Red
    if ($Strict) {
        exit 1
    }
} else {
    Write-Host " All 5 code quality and security gates passed!" -ForegroundColor Green
}
Write-Host "==========================================================" -ForegroundColor Cyan
