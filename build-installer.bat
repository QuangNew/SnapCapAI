@echo off
REM ============================================================
REM SnapCapAI - Build Installer Script
REM Version: 2.0
REM Created: January 2026
REM ============================================================

echo.
echo ============================================================
echo   SnapCapAI - Build Installer
echo   Version 2.0
echo ============================================================
echo.

REM Step 1: Clean old builds
echo [1/4] Cleaning old builds...
if exist build (
    echo    - Removing build folder...
    rmdir /s /q build
)
if exist dist (
    echo    - Removing dist folder...
    rmdir /s /q dist
)
if exist Output (
    echo    - Removing Output folder...
    rmdir /s /q Output
)
echo    [OK] Old builds cleaned
echo.

REM Step 2: Build executable with PyInstaller
echo [2/4] Building executable with PyInstaller...
echo    This may take a few minutes...
echo.
py -m PyInstaller SnapCapAI.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)
echo.
echo    [OK] Executable built successfully
echo.

REM Step 3: Verify exe exists
echo [3/4] Verifying executable...
if not exist "dist\SnapCapAI.exe" (
    echo    [ERROR] SnapCapAI.exe not found in dist folder!
    echo    The build may have failed silently.
    pause
    exit /b 1
)

REM Get file size
for %%A in ("dist\SnapCapAI.exe") do (
    echo    [OK] Found: SnapCapAI.exe ^(%%~zA bytes^)
)
echo.

REM Step 4: Check for Inno Setup and compile installer
echo [4/4] Compiling installer with Inno Setup...
echo.

REM Try common Inno Setup installation paths
set "INNO_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set "INNO_PATH=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
)

if not defined INNO_PATH (
    echo    [WARNING] Inno Setup not found!
    echo.
    echo    Please install Inno Setup 6 from:
    echo    https://jrsoftware.org/isdl.php
    echo.
    echo    After installation, run this script again.
    echo.
    echo    Note: The executable was built successfully at:
    echo          dist\SnapCapAI.exe
    echo.
    pause
    exit /b 1
)

echo    Using: %INNO_PATH%
echo.
"%INNO_PATH%" SnapCapAI-installer.iss
if errorlevel 1 (
    echo.
    echo [ERROR] Inno Setup compilation failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo ============================================================
echo.
echo   Executable: dist\SnapCapAI.exe
echo   Installer:  Output\SnapCapAI-Setup.exe
echo.
echo   You can now distribute SnapCapAI-Setup.exe to users.
echo.
echo ============================================================
echo.

REM Open Output folder
set /p OPEN="Open Output folder? (Y/N): "
if /i "%OPEN%"=="Y" (
    if exist "Output\SnapCapAI-Setup.exe" (
        start explorer /select,"Output\SnapCapAI-Setup.exe"
    ) else (
        start explorer Output
    )
)

pause
