@echo off
REM LifeLens AI — Setup (Windows)
cd /d "%~dp0..\backend"
echo Setting up LifeLens AI...
python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo Setup complete! Now run: scripts\run.bat
pause
