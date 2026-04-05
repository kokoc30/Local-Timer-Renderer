<#
.SYNOPSIS
    Local Timer Renderer Startup Launcher (Task 8)

.DESCRIPTION
    Simplifies local app startup.
    - Resolves project environment
    - Starts backend server
    - Waits for readiness
    - Automatically opens browser

.PARAMETERS
    NoBrowser - Set to true to disable automatic browser opening
    Port      - Port to run on (default 8001)
    AppHost   - Host to run on (default 127.0.0.1)

.EXAMPLE
    .\start.ps1
#>

param (
    [switch]$NoBrowser = $false,
    [int]$Port = 8001,
    [string]$AppHost = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

Write-Host "`n--- Local Timer Renderer Launcher (Task 8) ---" -ForegroundColor Cyan

# 1. Resolve Project Root and Environment
$ProjectRoot = Get-Item $PSScriptRoot
$PythonPath = Join-Path $ProjectRoot.FullName ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonPath)) {
    Write-Host "Virtual environment not found at .venv\Scripts\python.exe" -ForegroundColor Yellow
    Write-Host "Searching for 'python' in PATH..." -ForegroundColor Gray
    $PythonPath = "python"
} else {
    Write-Host "Using virtual environment: $PythonPath" -ForegroundColor Gray
}

# 2. Port Discovery: Find a usable port
$TargetPort = $Port
$IsExplicitPort = $PSBoundParameters.ContainsKey('Port')
$FinalPort = $null
$AlreadyRunning = $false
$ExpectedAppName = "Local Timer Renderer"

Write-Host "Resolving target port..." -ForegroundColor Gray

# Scan loop: If explicit port, only check once. If default, scan 10 ports.
$MaxScan = if ($IsExplicitPort) { 1 } else { 10 }

for ($i = 0; $i -lt $MaxScan; $i++) {
    $CurrentPort = $TargetPort + $i
    $CurrentBaseUrl = "http://$($AppHost):$($CurrentPort)"
    $CurrentHealthUrl = "$($CurrentBaseUrl)/api/system/status"
    
    # A. Check if OUR app is already running here
    try {
        $Response = Invoke-RestMethod -Uri $CurrentHealthUrl -Method Get -ErrorAction SilentlyContinue -TimeoutSec 2
        if ($Response -and $Response.ok -eq $true -and $Response.app_name -eq $ExpectedAppName) {
            $FinalPort = $CurrentPort
            $AlreadyRunning = $true
            Write-Host "Local Timer Renderer is already running at $CurrentBaseUrl" -ForegroundColor Green
            break
        }
    } catch { }

    # B. If not running, check if the TCP port is free
    $PortCheck = Get-NetTCPConnection -LocalPort $CurrentPort -ErrorAction SilentlyContinue
    if (-not $PortCheck) {
        $FinalPort = $CurrentPort
        if ($i -gt 0) {
            Write-Host "Default port $TargetPort is occupied. Automatically falling back to $FinalPort." -ForegroundColor Yellow
        }
        break
    } else {
        if ($IsExplicitPort) {
            Write-Host "Error: Explicitly requested port $TargetPort is already in use by another process." -ForegroundColor Red
            Write-Host "Please free the port or choose a different one." -ForegroundColor Gray
            exit 1
        }
        Write-Host "Port $CurrentPort is occupied by another process, skipping..." -ForegroundColor Gray
    }
}

if (-not $FinalPort) {
    Write-Host "Error: Could not find a free port in the range $TargetPort - $($TargetPort + $MaxScan - 1)." -ForegroundColor Red
    exit 1
}

$BaseUrl = "http://$($AppHost):$($FinalPort)"
$HealthUrl = "$($BaseUrl)/api/system/status"

# 3. Start Backend Process (if not already running)
$ServerProcess = $null
if (-not $AlreadyRunning) {
    Write-Host "Starting Uvicorn backend on port $FinalPort..." -ForegroundColor Cyan
    # We use Start-Process with -NoNewWindow so logs stay in the same terminal
    $ServerProcess = Start-Process -FilePath $PythonPath -ArgumentList "-m uvicorn app.main:app --host $AppHost --port $FinalPort" -PassThru -NoNewWindow
    
    # 4. Wait for Readiness
    $MaxAttempts = 15
    $Attempt = 0
    $IsReady = $false
    
    Write-Host "Waiting for app readiness at $HealthUrl..." -ForegroundColor Gray
    
    while ($Attempt -lt $MaxAttempts -and -not $IsReady) {
        try {
            $Response = Invoke-RestMethod -Uri $HealthUrl -Method Get -ErrorAction SilentlyContinue
            if ($Response.ok -eq $true) {
                $IsReady = $true
            }
        }
        catch {
            # Keep waiting
        }
        
        if (-not $IsReady) {
            $Attempt++
            Start-Sleep -Seconds 1
        }
    }
    
    if (-not $IsReady) {
        Write-Host "Error: App failed to become ready on port $FinalPort after $($MaxAttempts) seconds." -ForegroundColor Red
        exit 1
    }
    Write-Host "App is ready!" -ForegroundColor Green
}

# 5. Handle Browser and Wait
Write-Host "URL: $BaseUrl" -ForegroundColor Cyan

if (-not $NoBrowser) {
    Write-Host "Opening browser..." -ForegroundColor Gray
    Start-Process $BaseUrl
}

if ($AlreadyRunning) {
    Write-Host "`nLauncher complete. App continues running in its original process." -ForegroundColor Gray
    exit 0
}

Write-Host "`nServer running. Press Ctrl+C to stop.`n" -ForegroundColor Gray

# Keep script alive to catch logs or wait for termination
try {
    while ($true) {
        if ($ServerProcess.HasExited) {
            Write-Host "Server process has stopped." -ForegroundColor Yellow
            break
        }
        Start-Sleep -Seconds 2
    }
}
finally {
    # Cleanup: Make sure to stop the server process if this script is interrupted
    if ($ServerProcess -and -not $ServerProcess.HasExited) {
        Write-Host "`nStopping server process..." -ForegroundColor Gray
        Stop-Process -Id $ServerProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
