@echo off
REM ============================================================
REM SnapCapAI - Auto Setup and Build to EXE
REM By QuangNew
REM ============================================================

echo.
echo ============================================================
echo   SnapCapAI - Setup and Build to EXE
echo   By QuangNew
echo ============================================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found!
        echo Please install Python 3.12+ from https://python.org
        echo Make sure to check "Add Python to PATH" during installation
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

REM Check pip
echo [2/5] Checking and upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip
echo [OK] pip upgraded!
echo.

REM Install requirements
echo [3/5] Installing dependencies from requirements.txt...
echo This may take 5-10 minutes...
echo.
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo.
echo [OK] All dependencies installed!
echo.

REM Verify installation
echo [4/5] Verifying installation...
%PYTHON_CMD% -c "import customtkinter; import PIL; import pynput; import google.generativeai; print('[OK] Core modules verified')"
if errorlevel 1 (
    echo [ERROR] Some modules failed to import!
    pause
    exit /b 1
)
echo.

REM Build executable with PyInstaller
echo [5/5] Building executable with PyInstaller...
echo This will take 5-10 minutes...
echo.

REM Clean old builds
echo Cleaning old builds...
if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1
echo.

REM Run PyInstaller
%PYTHON_CMD% -m PyInstaller CapSnapAI.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo ============================================================
echo.

REM Check exe file
if exist "dist\CapSnapAI.exe" (
    echo Executable created: dist\CapSnapAI.exe
    for %%A in ("dist\CapSnapAI.exe") do (
        set "SIZE=%%~zA"
    )
    if defined SIZE (
        set /a SIZE_MB=SIZE / 1048576
        if !SIZE_MB! equ 0 set /a SIZE_MB=1
        echo Size: !SIZE_MB! MB
    )
) else (
    echo [WARNING] Exe file not found in expected location
)

echo.
echo You can now:
echo   1. Test: cd dist ^&^& CapSnapAI.exe
echo   2. Distribute: Copy dist\CapSnapAI.exe to other machines
echo.
echo ============================================================
echo.

REM Ask to open dist folder
set /p OPEN_FOLDER="Open dist folder? (Y/N): "
if /i "%OPEN_FOLDER%"=="Y" (
    start explorer dist
)

pause
