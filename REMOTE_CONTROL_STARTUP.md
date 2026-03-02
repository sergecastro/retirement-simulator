# 🚀 Remote Control Startup Protocol
## Updated: 2026-03-02

---

## ⚠️ CRITICAL RULES
- ALWAYS use CMD (not PowerShell) on backup laptop
- ALWAYS launch /remote-control from INSIDE Claude Code
- NEVER use `claude remote-control` directly from terminal — it FAILS on Windows with nvm

---

## BACKUP LAPTOP — Do this EVERY morning (in order)

### Terminal 1 — Start the app
Open CMD and type:
cd C:\DEV\retirement-simulator\family_retirement_no_OCR
git pull
.\start_familyforecast.bat
Verify app is running at: http://localhost:8502
Verify Flask is running at: http://localhost:5000/health

### Terminal 2 — Start Remote Control
Open a NEW CMD window and type:
cd C:\DEV\retirement-simulator\family_retirement_no_OCR
claude
Wait for Claude Code to fully open, then type:
/remote-control
Copy the session URL shown (format: https://claude.ai/code/session_XXXXX)

---

## MAIN LAPTOP — Connect to Remote Control
Open browser and paste the session URL from backup laptop.
You can now control backup laptop from main laptop!

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| `/remote-control` hangs forever | You're in PowerShell — switch to CMD |
| `bad option: --sdk-url` error | You used `claude remote-control` in terminal — use CMD + claude + /rc instead |
| Logo error on startup | Streamlit launched from wrong folder — use start_familyforecast.bat |
| Port 8502 already in use | Run: `taskkill /f /im py.exe` then restart |
| `git pull` fails with HANDOFF.md conflict | Run: `git checkout -- HANDOFF.md` then `git pull` |
| Remote Control times out after inactivity | Restart: open CMD, cd to project, claude, /remote-control |

---

## QUICK REFERENCE
- App URL: http://localhost:8502
- Flask API: http://localhost:5000/health
- Project folder: C:\DEV\retirement-simulator\family_retirement_no_OCR
- GitHub: https://github.com/sergecastro/retirement-simulator
- Startup file: start_familyforecast.bat

---

## SESSION END CHECKLIST
1. git add . && git commit -m "description" && git push
2. Update HANDOFF.md Section 1
3. Confirm both laptops in sync
