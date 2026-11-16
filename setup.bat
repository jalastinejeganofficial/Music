@echo off
setlocal
title Music Desktop - Package Manager & Setup

echo =======================================================
echo    Music Desktop - Automatic Package Manager
echo =======================================================
echo.
echo Installing Music Desktop App...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0packaging\windows\install.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] An error occurred during installation.
    pause
)
