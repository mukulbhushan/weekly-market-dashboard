@echo off
title Export Executive Weekly Market Dashboard PDF (A4 Edition)
echo ========================================================
echo Exporting 2-Page Executive Market Dashboard PDF (A4 Edition)
echo Using Aptos Typography and Enhanced Visual Hierarchy...
echo ========================================================
cd /d "%~dp0"
python generate_shareable_pdf.py
echo.
echo ========================================================
echo PDF Generation Complete!
echo The shareable executive PDF is ready in this folder.
echo ========================================================
pause
