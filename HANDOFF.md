# HANDOFF.md -- FamilyForecast.AI

## 🚀 DAILY STARTUP — Do This Every Morning

### ⚠️ CRITICAL RULES
- ALWAYS use CMD (not PowerShell) on backup laptop
- ALWAYS launch /remote-control from INSIDE Claude Code
- NEVER use `claude remote-control` directly from terminal — it FAILS on Windows with nvm

### Terminal 1 — Start the app
Open CMD and type:
```
cd C:\DEV\retirement-simulator\family_retirement_no_OCR
git pull
.\start_familyforecast.bat
```
Verify app is running at: http://localhost:8502
Verify Flask is running at: http://localhost:5000/health

### Terminal 2 — Start Remote Control
Open a NEW CMD window and type:
```
cd C:\DEV\retirement-simulator\family_retirement_no_OCR
claude
```
Wait for Claude Code to fully open, then type: `/remote-control`
Copy the session URL shown (format: `https://claude.ai/code/session_XXXXX`)

### Main Laptop — Connect
Open browser and paste the session URL from backup laptop.

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `/remote-control` hangs forever | You're in PowerShell — switch to CMD |
| `bad option: --sdk-url` error | You used `claude remote-control` in terminal — use CMD + claude + /rc instead |
| Logo error on startup | Streamlit launched from wrong folder — use start_familyforecast.bat |
| Port 8502 already in use | Run: `taskkill /f /im py.exe` then restart |
| `git pull` fails with HANDOFF.md conflict | Run: `git checkout -- HANDOFF.md` then `git pull` |
| Remote Control times out after inactivity | Restart: open CMD, cd to project, claude, /remote-control |

### Quick Reference
- App URL: http://localhost:8502
- Flask API: http://localhost:5000/health
- Project folder: `C:\DEV\retirement-simulator\family_retirement_no_OCR`
- Startup file: `start_familyforecast.bat`

---

## SECTION 1 -- RECENT PROGRESS
<!-- Updated automatically by ClaudeManager from GitHub Gist -->

### Session Summary — 2026-03-02
**Session:** Return User QA + 24 Bug Fixes + Production Verified

#### ✅ COMPLETED TODAY
- Fixed 12 bugs across all 5 return user paths
- start_familyforecast.bat fixed for both laptops
- Production app confirmed perfect on desktop and iPhone
- Income display confirmed working correctly (Feb 13 fix)
- Local CSS icon issue confirmed NOT a production bug
- REMOTE_CONTROL_STARTUP.md created

#### 🔧 OPEN ITEMS
- Sankey chart not connected to explanation API
- Supabase SMTP → Resend for email confirmation
- Remove BETA DEMO badge before launch
- Stripe integration — after all testing complete

#### 📋 FOR MARKETING AGENT
- LinkedIn post opportunity: "24 bugs fixed in one session — production verified on desktop + iPhone"
- Educational angle: rigorous QA matters before launch

#### ▶️ START NEXT SESSION
"Connect Sankey and other charts to explanation API, then tackle Supabase SMTP Resend connection."

---

### Session Summary — 2026-03-01
**Session:** Full QA + 6 Simulation Bugs Fixed + Both Laptops Synced

#### ✅ COMPLETED TODAY
- Fixed 6 critical simulation_core.py bugs:
  1. College costs were double-counted
  2. Liabilities never decreased (now 5%/yr paydown)
  3. Income ratios hardcoded (now uses real intake data)
  4. tax_rate parameter undocumented (now flagged)
  5. Other assets never appreciated (now 2%/yr)
  6. RMD table wrong for ages 100+ (extended to age 120)
- Re-enabled IRMAA analysis (was hardcoded False)
- Fixed nested expanders bug — AI Advisor works on all devices
- Replaced Seagate sync with GitHub workflow (git pull/push)
- Both laptops 100% identical and in sync
- ClaudeManager fully working on backup laptop
- GitHub Gist token configured on backup laptop
- Supabase connection confirmed working on backup laptop
- start_familyforecast.bat updated with git pull reminder
- All fixes committed and pushed to GitHub master

#### 🔧 OPEN ITEMS
- Supabase SMTP: connect Resend API for email confirmation
- Sidebar interconnect on mobile needs recheck
- Full manual QA (clicking every button) still pending
- LinkedIn post: write about today's QA + 6 bugs fixed

#### 📋 FOR MARKETING AGENT
- Strong LinkedIn post opportunity: "Found and fixed 6 simulation bugs via AI-powered Remote Control QA session"
- Educational angle: accuracy matters in retirement planning

#### ▶️ START NEXT SESSION
"Connect Resend API to Supabase for email confirmation, then complete full manual QA of all FamilyForecast features."

---

## SECTION 2 -- ARCHITECTURE
No architecture info recorded yet.

## SECTION 3 -- GIT COMMITS
Managed automatically by ClaudeManager.
