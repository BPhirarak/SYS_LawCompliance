@echo off
echo Starting Thai Law Compliance System...
echo.

echo [0/2] Checking Python dependencies...
pip install -r "%~dp0backend\requirements.txt" --quiet
echo Dependencies OK.
echo.

echo [1/2] Starting Backend (FastAPI on port 8000)...
start "Thai Law Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --reload --port 8000"
timeout /t 2 /nobreak > nul

echo [2/2] Opening browser...
start http://localhost:8000
echo.
echo System started!
echo    App: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
pause
