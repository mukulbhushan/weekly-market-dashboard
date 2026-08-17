@echo off
title Update Weekly Report Spreadsheet & HTML Dashboard
echo ========================================================
echo Running Market Data Update Script...
echo Updating Excel Workbook & HTML Dashboard...
echo ========================================================
cd /d "%~dp0"
python update_spreadsheet.py
echo.
echo ========================================================
echo Process Finished!
echo Both 'WEEKLY REPORT SPREADSHEET.xlsx' and 
echo 'weekly-market-dashboard.html' have been updated.
echo ========================================================
pause
