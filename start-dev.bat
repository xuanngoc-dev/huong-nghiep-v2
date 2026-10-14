@echo off
setlocal
cd /d "%~dp0"
title Khoi dong Du an Dinh Huong Nghe

echo ========================================================
echo       DANG KHOI DONG HE THONG (BACKEND + FRONTEND)
echo ========================================================
echo.

:: 1. Mo cua so Backend (FastAPI - Port 3060)
echo [*] Khoi dong Backend (Port 3060)...
start "Backend - FastAPI" powershell -NoExit -ExecutionPolicy Bypass -Command "Set-Location '%~dp0backend'; if (Test-Path '.venv\Scripts\python.exe') { & '.venv\Scripts\python.exe' -m uvicorn app.main:app --reload --port 3060 } else { python -m uvicorn app.main:app --reload --port 3060 }"

:: 2. Mo cua so Frontend (Vite - Port 5173)
echo [*] Khoi dong Frontend (Port 5173)...
start "Frontend - Vite" powershell -NoExit -ExecutionPolicy Bypass -Command "Set-Location '%~dp0frontend'; npm run dev"

echo.
echo ========================================================
echo   Backend Swagger: http://127.0.0.1:3060/docs
echo   Frontend Web:    http://localhost:5173
echo ========================================================
echo.

:: Cho 3 giay de server khoi dong roi tu dong mo trinh duyet
ping 127.0.0.1 -n 4 >nul
start http://localhost:5173

exit
