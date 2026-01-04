#!/bin/bash
# VibeCheck Startup Script for Linux/Mac
# This script starts both the backend and frontend

echo "===================================="
echo "   VibeCheck AI - Starting Up"
echo "===================================="
echo

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "[WARNING] No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "[INFO] Please edit .env with your credentials before continuing."
    read -p "Press Enter to continue..."
fi

# Start backend in background
echo "[1/2] Starting Backend API..."
cd backend && python api.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "[2/2] Starting Frontend UI..."
cd frontend-react && npm run dev &
FRONTEND_PID=$!
cd ..

echo
echo "===================================="
echo "   VibeCheck AI is Running!"
echo "===================================="
echo
echo "Backend API: http://localhost:8000"
echo "API Docs:    http://localhost:8000/docs"
echo "Frontend:    http://localhost:5173"
echo
echo "Press Ctrl+C to stop both servers"
echo

# Open browser (works on Mac and Linux with xdg-open)
if command -v open &> /dev/null; then
    open http://localhost:5173
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173
fi

# Wait for Ctrl+C and cleanup
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
