@echo off
title RoboPilot - Saleh Aldwais - SIMULATION
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" server.py --bind 0.0.0.0
) else if exist "..\.venv\Scripts\python.exe" (
  "..\.venv\Scripts\python.exe" server.py --bind 0.0.0.0
) else (
  py -3 server.py --bind 0.0.0.0
)
pause
