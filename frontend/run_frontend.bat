@echo off
cd /d "%~dp0\frontend"
echo Starting Frontend...
call npm install
npm run dev
pause
