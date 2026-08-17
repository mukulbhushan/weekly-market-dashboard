@echo off
title Executive Market Dashboard - Streamlit Web App
echo ========================================================
echo Launching Executive Weekly Market Dashboard in Streamlit...
echo ========================================================
cd /d "%~dp0"
streamlit run app.py
pause
