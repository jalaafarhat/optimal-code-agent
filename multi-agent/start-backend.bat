@echo off
cd /d "%~dp0"
call ..\.venv\Scripts\activate.bat
echo Starting FinAgent backend on http://localhost:8000
uvicorn server:app --reload --host 127.0.0.1 --port 8000
