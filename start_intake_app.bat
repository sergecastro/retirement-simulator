@echo off
echo.
echo ========================================
echo   INTAKE QUESTIONNAIRE APP
echo ========================================
echo.
echo Starting on port 8503...
echo URL will open automatically in browser
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.
streamlit run intake_app.py --server.port 8503
pause