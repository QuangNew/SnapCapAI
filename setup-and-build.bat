@echo off
REM ============================================================
REM SnapCapAI - Auto Setup and Build to EXE
REM Updated: December 2025
REM ============================================================

echo.
echo ============================================================
echo   SnapCapAI - Setup and Build to EXE
echo ============================================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found!
        echo Please install Python 3.10+ from https://python.org
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py
)
%PYTHON_CMD% --version
echo [OK] Python found!
echo.

REM Upgrade pip
echo [2/5] Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip
echo.

REM Install requirements
echo [3/5] Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo [OK] Dependencies installed!
echo.

REM Verify core modules
echo [4/5] Verifying installation...
%PYTHON_CMD% -c "import customtkinter; import PIL; import google.generativeai; print('[OK] Core modules verified')"
if errorlevel 1 (
    echo [ERROR] Module verification failed!
    pause
    exit /b 1
)
echo.

REM Build executable
echo [5/5] Building executable...
echo.

REM Clean old builds
if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1

REM Run PyInstaller
%PYTHON_CMD% -m PyInstaller SnapCapAI.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   BUILD COMPLETED!
echo ============================================================
echo.
echo   Output: dist\SnapCapAI.exe
echo.
echo   NOTE: Run as Administrator for full Stealth Mode
echo.

set /p OPEN="Open dist folder? (Y/N): "
if /i "%OPEN%"=="Y" start explorer dist

pause
