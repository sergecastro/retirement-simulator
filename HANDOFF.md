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

### Session Summary -- 2026-02-27
### Session Summary — 2026-02-26
*No direct development work today — marketing infrastructure built*

**FOR YOUR MORNING RECAP:**

What changed: No code changes to the app itself today. Focus was entirely on marketing automation.
What was completed: LinkedIn content pipeline live — first post scheduled and confirmed in Buffer for today 2:40 PM
What is still in progress: App development continues as normal next session
Next TODO: Resume Phase II development next FamilyForecast session

**FOR MARKETING AGENT:**
- New/changed worth posting: NO new features today
- Post already sent today — skip next Wednesday for FamilyForecast, use Synaptal slot


## SECTION 2 -- ARCHITECTURE
No architecture info recorded yet.

## SECTION 3 -- GIT COMMITS
Managed automatically by ClaudeManager.
