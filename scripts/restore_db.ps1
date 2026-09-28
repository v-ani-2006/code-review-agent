<#
.SYNOPSIS
    PowerShell Database Restore Script for CodePilot AI (Windows / Docker Desktop).
.DESCRIPTION
    Restores the PostgreSQL database from a specified (or the latest) .sql file.
.PARAMETER BackupFile
    Path to the backup file. If not provided, the latest backup in backups/ is used.
.PARAMETER Force
    Skip confirmation prompt.
.EXAMPLE
    .\scripts\restore_db.ps1
    .\scripts\restore_db.ps1 -BackupFile .\backups\codepilot_codepilot_db_20260928_120000.sql -Force
#>

param (
    [string]$BackupFile = "",
    [switch]$Force,
    [string]$TargetContainer = "codepilot_postgres",
    [string]$Database = "codepilot_db",
    [string]$User = "postgres"
)

$ErrorActionPreference = "Stop"
$BackupDir = Join-Path $PSScriptRoot "..\backups"

# Resolve backup file
if ([string]::IsNullOrWhiteSpace($BackupFile)) {
    $Latest = Get-ChildItem -Path $BackupDir -Filter "codepilot_*.sql*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $Latest) {
        Write-Error "No backup files found in $BackupDir"
        exit 1
    }
    $BackupFile = $Latest.FullName
} elseif (-not (Test-Path $BackupFile)) {
    Write-Error "Specified backup file not found: $BackupFile"
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CodePilot AI — Database Restore (Windows / Docker)" -ForegroundColor Cyan
Write-Host " Backup File: $BackupFile" -ForegroundColor Yellow
Write-Host " Target Container: $TargetContainer | DB: $Database" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

if (-not $Force) {
    Write-Warning "This will DROP and RECREATE database '$Database'. ALL EXISTING DATA WILL BE LOST!"
    $Confirmation = Read-Host "Type 'yes' to proceed"
    if ($Confirmation -ne "yes") {
        Write-Host "Restore cancelled by user." -ForegroundColor Gray
        exit 0
    }
}

# Check if Docker container is running
$ContainerRunning = docker ps --filter "name=$TargetContainer" --filter "status=running" --format "{{.Names}}" 2>$null

if ($ContainerRunning) {
    Write-Host "[RESTORE] Recreating database in container '$TargetContainer'..." -ForegroundColor Cyan
    docker exec -t $TargetContainer psql -U $User -d postgres -c "DROP DATABASE IF EXISTS `"$Database`";"
    docker exec -t $TargetContainer psql -U $User -d postgres -c "CREATE DATABASE `"$Database`" OWNER `"$User`";"

    Write-Host "[RESTORE] Restoring database contents..." -ForegroundColor Cyan
    Get-Content $BackupFile | docker exec -i $TargetContainer psql -U $User -d $Database
} else {
    Write-Host "[RESTORE] Running local psql..." -ForegroundColor Cyan
    & psql -h localhost -p 5432 -U $User -d postgres -c "DROP DATABASE IF EXISTS `"$Database`";"
    & psql -h localhost -p 5432 -U $User -d postgres -c "CREATE DATABASE `"$Database`" OWNER `"$User`";"
    & psql -h localhost -p 5432 -U $User -d $Database -f $BackupFile
}

Write-Host "[OK] Database restored successfully from: $BackupFile" -ForegroundColor Green
