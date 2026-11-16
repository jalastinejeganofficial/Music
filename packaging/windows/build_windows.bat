@echo off
REM Windows Executable Build Script
REM Generates native standalone Music.exe using PyInstaller

echo ========================================================
echo           Building Music Desktop App for Windows
echo ========================================================

REM 1. Ensure Python dependencies are installed
echo [1/3] Checking dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller pywebview

REM 2. Run PyInstaller
echo [2/3] Building standalone Windows executable...
pyinstaller --noconfirm --clean Music.spec

REM 3. Package output into a zip file for distribution
echo [3/3] Creating portable distribution zip...
python packaging\windows\create_portable_zip.py

echo ========================================================
echo   Build Successful!
echo   Executable: dist\Music\Music.exe
echo   Zip Package: dist\Music-Windows-x64.zip
echo ========================================================
pause
