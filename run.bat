@echo off
echo ==========================================
echo Movie Recommender System - Starting...
echo ==========================================

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run Streamlit app
echo Starting Streamlit application...
streamlit run app.py

pause
