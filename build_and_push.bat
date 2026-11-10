@echo off
setlocal

rem Cach dung: build_and_push.bat [tag]   (mac dinh tag = latest)
set "REGISTRY=103.226.249.128:8142/huongnghiep"
set "TAG=%~1"
if "%TAG%"=="" set "TAG=latest"

set "ROOT=%~dp0"

echo ===== [1/4] Build image backend =====
cd /d "%ROOT%backend" || goto :error
rem Build context la thu muc goc du an (Dockerfile can copy data_dh_json)
docker build -f Dockerfile -t huongnghiep-backend:%TAG% .. || goto :error

echo ===== [2/4] Build frontend (npm run build) =====
cd /d "%ROOT%frontend" || goto :error
call npm run build || goto :error

echo ===== [3/4] Build image frontend =====
docker build -t huongnghiep-frontend:%TAG% . || goto :error

echo ===== [4/4] Tag va push image len %REGISTRY% =====
docker tag huongnghiep-backend:%TAG% %REGISTRY%/huongnghiep-backend:%TAG% || goto :error
docker tag huongnghiep-frontend:%TAG% %REGISTRY%/huongnghiep-frontend:%TAG% || goto :error
docker push %REGISTRY%/huongnghiep-backend:%TAG% || goto :error
docker push %REGISTRY%/huongnghiep-frontend:%TAG% || goto :error

cd /d "%ROOT%"
echo.
echo ===== HOAN THANH =====
echo   %REGISTRY%/huongnghiep-backend:%TAG%
echo   %REGISTRY%/huongnghiep-frontend:%TAG%
endlocal
exit /b 0

:error
echo.
echo ***** LOI: buoc tren that bai (exit code %ERRORLEVEL%) *****
cd /d "%ROOT%"
endlocal
exit /b 1
