@echo off
echo.
echo ========================================
echo   IPL Cricket Analytics Dashboard
echo ========================================
echo.
echo Starting dashboard...
echo.
echo Dashboard will open in your browser automatically.
echo Press Ctrl+C to stop the dashboard.
echo.

cd /d %~dp0\..
streamlit run dashboard\app.py

pause
