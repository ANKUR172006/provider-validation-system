@echo off
echo ===============================
echo   Starting Backend (FastAPI)
echo ===============================

REM Move into backend folder
cd /d "%~dp0backend"

REM Step 1: Check if venv exists
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Step 2: Activate venv
echo Activating virtual environment...
call venv\Scripts\activate

REM Step 3: Install requirements
IF EXIST "requirements.txt" (
    echo Installing required packages...
    pip install --upgrade pip
    pip install -r requirements.txt
) ELSE (
    echo ERROR: requirements.txt not found!
    pause
    exit /b
)

REM Step 4: Run FastAPI server
echo Running FastAPI backend...
uvicorn main:app --reload --port 8000

pause
