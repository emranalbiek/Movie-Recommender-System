@echo off
echo ==========================================
echo Movie Recommender System - Setup
echo ==========================================

REM Create virtual environment
echo Creating virtual environment...
python -m venv recommender-system

REM Activate virtual environment
echo Activating virtual environment...
call recommender-system\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist "artifacts" mkdir artifacts
if not exist "data" mkdir data

rem Save the artifacts for running the application
echo Saving artifacts...
python main.py

echo ==========================================
echo Setup completed successfully!
echo Run 'run.bat' to start the application
echo ==========================================
pause
