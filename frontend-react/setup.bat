@echo off
REM VibeCheck React Frontend - Windows Setup Script

echo ====================================
echo   VibeCheck React Frontend Setup
echo ====================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Setup complete!
echo.
echo ====================================
echo   Ready to start development!
echo ====================================
echo.
echo Run: npm run dev
echo.
echo The app will open at http://localhost:3000
echo Make sure the backend is running at http://localhost:8000
echo.
pause
