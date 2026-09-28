<#
.SYNOPSIS
    Automated Semantic Release & Tagging Script for CodePilot AI.
.DESCRIPTION
    Runs quality gates (linting + tests), calculates next semantic version,
    updates pyproject.toml, app/core/config.py, updates CHANGELOG.md,
    and displays Git commands to tag the release.
.PARAMETER Bump
    Semantic version bump type: 'patch' (default), 'minor', or 'major'.
.PARAMETER CustomVersion
    Explicitly specify version override (e.g. '1.0.0').
.PARAMETER SkipTests
    Bypass pre-release automated test gate.
.PARAMETER DryRun
    Simulate version bump and changelog generation without committing changes.
.EXAMPLE
    .\scripts\release.ps1 -Bump patch
    .\scripts\release.ps1 -Bump minor
    .\scripts\release.ps1 -CustomVersion "1.0.0"
#>

param (
    [ValidateSet("patch", "minor", "major")]
    [string]$Bump = "patch",
    [string]$CustomVersion = "",
    [switch]$SkipTests,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
if (Test-Path ".\venv\Scripts") { $env:PATH = "$PWD\venv\Scripts;$env:PATH" }

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CodePilot AI - Semantic Release Automation (Phase 13)" -ForegroundColor Cyan
Write-Host " Bump Mode: $Bump | Dry Run: $DryRun" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Run Quality Gates (Linting & Tests)
if (-not $SkipTests) {
    Write-Host "`n[Step 1/5] Running pre-release verification tests..." -ForegroundColor Green
    pytest tests/unit -v --tb=short
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Release aborted: Unit tests failed."
        exit 1
    }

    Write-Host "`n[Step 2/5] Running pre-release code style checks..." -ForegroundColor Green
    ruff check app
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Release aborted: Ruff found linting issues."
        exit 1
    }
} else {
    Write-Warning "Skipping pre-release test gates (-SkipTests specified)."
}

# 2. Extract Current Version from app/core/config.py
Write-Host "`n[Step 3/5] Calculating new semantic version..." -ForegroundColor Green
$ConfigFile = "app\core\config.py"
$ConfigContent = Get-Content $ConfigFile -Raw
$Pattern = 'APP_VERSION:\s*str\s*=\s*Field\(\s*default="([0-9]+\.[0-9]+\.[0-9]+)"'
if ($ConfigContent -match $Pattern) {
    $CurrentVersion = $Matches[1]
} else {
    $CurrentVersion = "0.1.0"
}
Write-Host " Current Version: $CurrentVersion" -ForegroundColor Yellow

# Calculate New Version
if ($CustomVersion -ne "") {
    $NewVersion = $CustomVersion
} else {
    $parts = $CurrentVersion.Split(".")
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    $patch = [int]$parts[2]

    switch ($Bump) {
        "major" { $major++; $minor = 0; $patch = 0 }
        "minor" { $minor++; $patch = 0 }
        "patch" { $patch++ }
    }
    $NewVersion = "$major.$minor.$patch"
}
Write-Host " Target Version:  $NewVersion" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n[DRY RUN] Would update version from $CurrentVersion to $NewVersion and tag 'v$NewVersion'." -ForegroundColor Cyan
    exit 0
}

# 3. Update Version in Source Files
Write-Host "`n[Step 4/5] Updating version in configuration files..." -ForegroundColor Green

# Update app/core/config.py
$ConfigTarget = 'APP_VERSION:\s*str\s*=\s*Field\(\s*default="[0-9]+\.[0-9]+\.[0-9]+"'
$ConfigRepl = 'APP_VERSION: str = Field(' + "`n" + '        default="' + $NewVersion + '"'
$UpdatedConfig = [regex]::Replace($ConfigContent, $ConfigTarget, $ConfigRepl)
Set-Content -Path $ConfigFile -Value $UpdatedConfig -NoNewline
Write-Host " [OK] Updated $ConfigFile" -ForegroundColor Green

# Update pyproject.toml
if (Test-Path "pyproject.toml") {
    $PyProjectContent = Get-Content "pyproject.toml" -Raw
    $PyTarget = 'version\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+"'
    $PyRepl = 'version = "' + $NewVersion + '"'
    $UpdatedPyProject = [regex]::Replace($PyProjectContent, $PyTarget, $PyRepl)
    Set-Content -Path "pyproject.toml" -Value $UpdatedPyProject -NoNewline
    Write-Host " [OK] Updated pyproject.toml" -ForegroundColor Green
}

# 4. Append to CHANGELOG.md
Write-Host "`n[Step 5/5] Updating CHANGELOG.md..." -ForegroundColor Green
$DateStamp = (Get-Date).ToString("yyyy-MM-dd")
$ChangelogHeader = "`n## [" + $NewVersion + "] - " + $DateStamp + "`n`n### Added`n- Production release version " + $NewVersion + ".`n- Automated GitHub Actions CI/CD workflows and DevOps tooling.`n"

if (Test-Path "CHANGELOG.md") {
    $ChangelogContent = Get-Content "CHANGELOG.md" -Raw
    if ($ChangelogContent -match "<!-- NEXT_VERSION_HEADER -->") {
        $UpdatedChangelog = $ChangelogContent -replace "<!-- NEXT_VERSION_HEADER -->", ("<!-- NEXT_VERSION_HEADER -->" + $ChangelogHeader)
        Set-Content -Path "CHANGELOG.md" -Value $UpdatedChangelog -NoNewline
    } else {
        Set-Content -Path "CHANGELOG.md" -Value ($ChangelogHeader + "`n" + $ChangelogContent) -NoNewline
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Release v$NewVersion prepared successfully!" -ForegroundColor Green
Write-Host " Git commands to publish:" -ForegroundColor Yellow
Write-Host "   git add -A" -ForegroundColor White
Write-Host "   git commit -m 'chore(release): bump version to v$NewVersion'" -ForegroundColor White
Write-Host "   git tag -a 'v$NewVersion' -m 'Release v$NewVersion'" -ForegroundColor White
Write-Host "   git push origin main --tags" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
