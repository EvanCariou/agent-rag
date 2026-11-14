@echo off
cd /d "%~dp0"
start "" python interface.py
timeout /t 3
start http://127.0.0.1:7860
