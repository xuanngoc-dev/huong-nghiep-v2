@echo off
setlocal
cd /d "%~dp0"
title Dung du an Dinh Huong Nghe

echo ========================================================
echo       DANG DUNG DICH VU (PORT 3060 VA 5173)...
echo ========================================================
echo.

powershell -NoExit -ExecutionPolicy Bypass -Command "Get-NetTCPConnection -LocalPort 3060,5173 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }; Write-Host '[*] Da dung cac tien trinh tren port 3060 va 5173 thanh cong!' -ForegroundColor Green; Start-Sleep -Seconds 2; exit"

exit
