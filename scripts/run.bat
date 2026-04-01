@echo off
REM LifeLens AI — Start Server (Windows)
cd /d "%~dp0..\backend"
if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
if not exist database\__init__.py echo. > database\__init__.py
if not exist models\__init__.py echo. > models\__init__.py
if not exist routes\__init__.py echo. > routes\__init__.py
if not exist utils\__init__.py echo. > utils\__init__.py
if not exist ml_models\nul mkdir ml_models
echo Starting LifeLens AI on http://localhost:8000
echo API Docs: http://localhost:8000/api/docs
python main.py
pause
