@echo off
echo Starting Thai Law Compliance System...
echo.
echo [1/2] Starting Backend (FastAPI on port 8000)...
start "Thai Law Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --reload --port 8000"
timeout /t 2 /nobreak > nul
echo [2/2] Starting Frontend (Vite on port 5173)...
start "Thai Law Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
echo.
echo ✅ System started!
echo    Frontend: http://localhost:5173
echo    Backend API: http://localhost:8000/docs
echo.
pause
