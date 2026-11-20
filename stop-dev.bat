@echo off
setlocal
set "shell=powershell.exe"
where.exe pwsh.exe >nul 2>&1 && set "shell=pwsh.exe"
"%shell%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\dev-windows.ps1" -Action Stop
if errorlevel 1 (
    pause
    exit /b 1
)
exit /b 0
