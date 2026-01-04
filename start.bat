@echo off
REM VibeCheck Startup Script for Windows
REM This script starts both the backend and frontend

echo ====================================
echo    VibeCheck AI - Starting Up
echo ====================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] No .env file found. Copying from .env.example...
    copy .env.example .env
    echo [INFO] Please edit .env with your credentials before continuing.
    pause
)

echo [1/2] Starting Backend API...
start "VibeCheck Backend" cmd /k "cd backend && python api.py"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend UI...
start "VibeCheck Frontend" cmd /k "cd frontend && streamlit run app.py"

echo.
echo ====================================
echo    VibeCheck AI is Running!
echo ====================================
echo.
echo Backend API: http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo Frontend:    http://localhost:8501
echo.
echo Press any key to open the app in your browser...
pause > nul

start http://localhost:8501
