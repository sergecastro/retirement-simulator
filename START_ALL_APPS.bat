@echo off
echo.
echo ============================================================
echo   RETIREMENT SIMULATOR - COMPLETE SYSTEM STARTUP
echo ============================================================
echo.
echo This will start 3 windows:
echo   1. Flask API Server (port 8502)
echo   2. Main Simulator (port 8501)
echo   3. Intake App (port 8503)
echo.
echo ⚠️  Keep all windows OPEN while using the apps
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul
echo.
echo ============================================================

echo [1/3] Starting Flask API Server...
start "Flask API Server" cmd /k start_flask_server.bat

echo Waiting for Flask to initialize...
timeout /t 3 /nobreak >nul

echo [2/3] Starting Main App...
start "Main Simulator" cmd /k start_main_app.bat

timeout /t 2 /nobreak >nul

echo [3/3] Starting Intake App...
start "Intake App" cmd /k start_intake_app.bat

echo.
echo ============================================================
echo ✅ All apps starting!
echo.
echo You should see 3 command windows and 2 browser tabs
echo Close this window anytime - the apps will keep running
echo ============================================================
echo.
pause