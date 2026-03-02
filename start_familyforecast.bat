@echo off
echo ============================================
echo  REMINDER: Run git pull before starting!
echo  cd C:\DEV\retirement-simulator\family_retirement_no_OCR
echo  git pull
echo ============================================
echo Starting FamilyForecast.AI...
start "Flask API" py -3.11 explain_api_server.py
timeout /t 3 /nobreak
start "Streamlit App" cmd /k "cd /d C:\DEV\retirement-simulator\family_retirement_no_OCR && py -3.11 -m streamlit run app.py"echo Both servers started! Opening browser in a few seconds...
