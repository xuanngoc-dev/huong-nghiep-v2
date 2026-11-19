[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Start', 'Stop')]
    [string]$Action,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root 'backend'
$frontend = Join-Path $root 'frontend'
$logDir = Join-Path $backend 'logs\dev'
$statePath = Join-Path $logDir 'processes.json'
$backendUrl = 'http://127.0.0.1:3060'
$frontendUrl = 'http://localhost:5173'
$proxyHealthUrl = 'http://127.0.0.1:5173/api/v1/health'

function Get-ProjectProcess($entry) {
    $process = Get-Process -Id $entry.Id -ErrorAction SilentlyContinue
    if ($process -and -not $process.HasExited -and
        [string]$process.StartTime.ToUniversalTime().Ticks -eq $entry.StartTicks) {
        $process
    }
}

function Stop-ProjectProcesses($entries) {
    $failed = @()
    foreach ($entry in $entries) {
        $process = Get-ProjectProcess $entry
        if (-not $process) {
            continue
        }
        try {
            if ($PSVersionTable.PSEdition -eq 'Core') {
                $process.Kill($true)
                $process.WaitForExit(5000) | Out-Null
            }
            else {
                Start-Process -FilePath "$env:SystemRoot\System32\taskkill.exe" `
                    -ArgumentList @('/PID', $entry.Id, '/T', '/F') -WindowStyle Hidden -Wait
            }
        }
        catch {
            Write-Warning $_.Exception.Message
        }
        if (Get-ProjectProcess $entry) {
            $failed += "$($entry.Name) (PID $($entry.Id))"
        }
    }
    if ($failed.Count) {
        throw "Khong dung duoc $($failed -join ', ')."
    }
}

function Test-ProjectReady {
    try {
        $backendHealth = Invoke-RestMethod -Uri "$backendUrl/api/v1/health" -UseBasicParsing -TimeoutSec 2
        if ($backendHealth.status -ne 'ok') {
            return $false
        }
        $health = Invoke-RestMethod -Uri $proxyHealthUrl -UseBasicParsing -TimeoutSec 2
        return $health.status -eq 'ok'
    }
    catch {
        return $false
    }
}

function Open-Project {
    Write-Host "Frontend: $frontendUrl"
    Write-Host "Swagger:  $backendUrl/docs"
    if (-not $NoBrowser) {
        try {
            Start-Process $frontendUrl
        }
        catch {
            Write-Warning "Mo $frontendUrl tren trinh duyet."
        }
    }
}

# Khoa theo workspace de hai lan bam khong khoi dong hoac dung cung luc.
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$lockPath = Join-Path $logDir 'launcher.lock'
try {
    $lock = [System.IO.File]::Open($lockPath, 'OpenOrCreate', 'ReadWrite', 'None')
}
catch [System.IO.IOException] {
    throw 'Trinh khoi dong dang xu ly mot lenh khac. Hay thu lai sau.'
}

try {
    $tracked = @()
    if (Test-Path -LiteralPath $statePath) {
        $saved = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
        $tracked = @($saved)
    }
    $running = @($tracked | Where-Object { Get-ProjectProcess $_ })

    if ($Action -eq 'Stop') {
        Stop-ProjectProcesses $running
        if (Test-Path -LiteralPath $statePath) {
            Remove-Item -LiteralPath $statePath
        }
        Write-Host 'Da dung cac dich vu khoi dong bang start-dev.bat.'
        return
    }

    if ($running.Count -eq 2 -and (Test-ProjectReady)) {
        Open-Project
        return
    }
    Stop-ProjectProcesses $running
    if (Test-Path -LiteralPath $statePath) {
        Remove-Item -LiteralPath $statePath
    }

    $tcp = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties()
    $busyPorts = @($tcp.GetActiveTcpListeners() | Where-Object Port -in 3060, 5173)
    if ($busyPorts.Count) {
        $ports = ($busyPorts.Port | Sort-Object -Unique) -join ', '
        throw "Cong $ports dang duoc tien trinh khac su dung. Hay dong tien trinh do roi chay lai."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $backend '.env') -PathType Leaf)) {
        throw 'Thieu backend/.env. Kiem tra ten file cau hinh backend.'
    }
    if (-not (Test-Path -LiteralPath (Join-Path $frontend 'node_modules\vite\bin\vite.js') -PathType Leaf)) {
        throw 'Thieu Vite. Chay npm.cmd ci trong thu muc frontend roi thu lai.'
    }

    $python = Join-Path $backend '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        $python = (Get-Command python.exe -CommandType Application | Select-Object -First 1).Source
    }
    $node = (Get-Command node.exe -CommandType Application | Select-Object -First 1).Source
    $env:API_PUBLIC_URL = $backendUrl
    $env:VITE_API_BASE_URL = '/api/v1'
    $env:DEV_API_TARGET = $backendUrl

    $services = @(
        @{
            Name = 'backend'
            File = $python
            Directory = $backend
            Arguments = @('-m', 'uvicorn', 'app.main:app', '--env-file', '.env', '--reload', '--host', '127.0.0.1', '--port', '3060')
        },
        @{
            Name = 'frontend'
            File = $node
            Directory = $frontend
            Arguments = @('node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '5173', '--strictPort')
        }
    )

    $started = @()
    try {
        foreach ($service in $services) {
            $process = Start-Process -FilePath $service.File -ArgumentList $service.Arguments `
                -WorkingDirectory $service.Directory -WindowStyle Hidden -PassThru `
                -RedirectStandardOutput (Join-Path $logDir "$($service.Name).out.log") `
                -RedirectStandardError (Join-Path $logDir "$($service.Name).err.log")
            $started += [pscustomobject]@{
                Name = $service.Name
                Id = $process.Id
                StartTicks = [string]$process.StartTime.ToUniversalTime().Ticks
            }
            ConvertTo-Json -InputObject $started | Set-Content -LiteralPath $statePath -Encoding UTF8
        }

        Write-Host "Dang doi backend va frontend. Log: $logDir"
        $deadline = [DateTime]::UtcNow.AddSeconds(45)
        do {
            foreach ($entry in $started) {
                if (-not (Get-ProjectProcess $entry)) {
                    throw "$($entry.Name) da thoat. Xem log trong $logDir."
                }
            }
            if (Test-ProjectReady) {
                Open-Project
                return
            }
            Start-Sleep -Milliseconds 300
        } while ([DateTime]::UtcNow -lt $deadline)
        throw "Het thoi gian cho dich vu. Xem log trong $logDir."
    }
    catch {
        $startupError = $_
        try {
            Stop-ProjectProcesses $started
            if (Test-Path -LiteralPath $statePath) {
                Remove-Item -LiteralPath $statePath
            }
        }
        catch {
            Write-Warning $_.Exception.Message
        }
        throw $startupError
    }
}
finally {
    $lock.Dispose()
}
