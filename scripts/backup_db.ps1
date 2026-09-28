<#
.SYNOPSIS
    PowerShell Database Backup Script for CodePilot AI (Windows / Docker Desktop).
.DESCRIPTION
    Creates a timestamped, compressed backup of the PostgreSQL database running
    in Docker (or locally) and saves it to the backups/ directory.
.PARAMETER TargetContainer
    The name of the PostgreSQL container (default: 'codepilot_postgres').
.PARAMETER RetentionDays
    Number of days to keep backups (default: 7).
.EXAMPLE
    .\scripts\backup_db.ps1
    .\scripts\backup_db.ps1 -RetentionDays 14
#>

param (
    [string]$TargetContainer = "codepilot_postgres",
    [int]$RetentionDays = 7,
    [string]$Database = "codepilot_db",
    [string]$User = "postgres"
)

$ErrorActionPreference = "Stop"
$BackupDir = Join-Path $PSScriptRoot "..\backups"

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFileName = "codepilot_${Database}_${Timestamp}.sql"
$BackupFilePath = Join-Path $BackupDir $BackupFileName

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CodePilot AI — Database Backup (Windows / Docker)" -ForegroundColor Cyan
Write-Host " Container: $TargetContainer | DB: $Database" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# Check if Docker container is running
$ContainerRunning = docker ps --filter "name=$TargetContainer" --filter "status=running" --format "{{.Names}}" 2>$null
if (-not $ContainerRunning) {
    Write-Warning "Container '$TargetContainer' is not running. Attempting local pg_dump..."
    try {
        & pg_dump -h localhost -p 5432 -U $User -d $Database -f $BackupFilePath
    } catch {
        Write-Error "Failed to backup database. Ensure container '$TargetContainer' is running or PostgreSQL is installed locally."
        exit 1
    }
} else {
    Write-Host "[BACKUP] Dumping database from container '$TargetContainer'..." -ForegroundColor Cyan
    docker exec -t $TargetContainer pg_dump -U $User -d $Database > $BackupFilePath
}

if (Test-Path $BackupFilePath) {
    $FileSize = (Get-Item $BackupFilePath).Length / 1MB
    Write-Host "[OK] Backup created successfully: $BackupFileName ($([Math]::Round($FileSize, 2)) MB)" -ForegroundColor Green

    # Rotate old backups
    Write-Host "[BACKUP] Rotating backups older than $RetentionDays days..." -ForegroundColor Gray
    $CutoffDate = (Get-Date).AddDays(-$RetentionDays)
    Get-ChildItem -Path $BackupDir -Filter "codepilot_*.sql" | Where-Object { $_.LastWriteTime -lt $CutoffDate } | ForEach-Object {
        Write-Host "  Removing expired backup: $($_.Name)" -ForegroundColor DarkGray
        Remove-Item $_.FullName -Force
    }
} else {
    Write-Error "Backup file was not created!"
    exit 1
}
