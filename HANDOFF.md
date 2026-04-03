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

---

### April 3, 2026 — Landing Page Overhaul + Bug Fixes

**Summary:** Complete landing page rewrite responding to board
member Curtis Cluff's feedback. Competitive research on Empower,
Boldin, Betterment. All content updated in Lovable (hero, banner,
FAQ, security, screenshots, CTA, trust strip). Code changes:
Privacy/Terms sidebar links, BETA text removal, email signup
cloud_password bug fix, Medicare data updated to 2026 (6 files,
16 edits). Feature gating set to false on Render. Email signup
→ restore flow tested and working.

**Commits:** d364eee, 881fea2, bb94ed5
**Branch:** master (3 feature branches merged and deleted)
**Landing page:** familyforecast.ai fully updated and live
**Next:** Stripe wiring + return user path testing (paths 2-5)

---

<!-- Updated automatically by ClaudeManager from GitHub Gist -->

### Session Summary -- 2026-03-15
Fixed the Gist multi-project merge. Each project now updates only its own section.

---

<!-- Updated automatically by ClaudeManager from GitHub Gist -->

---

### Session Summary -- 2026-03-15
TEST A — FamilyForecast section only.

---

<!-- Updated automatically by ClaudeManager from GitHub Gist -->

---

---

### Session Summary -- 2026-03-15
LIVE TEST — Serge ran this himself.
FamilyForecast working correctly.

---

<!-- Updated automatically by ClaudeManager from GitHub Gist -->

---

---

---

### Session Summary -- 2026-03-15
TEST — FamilyForecast only.

---

<!-- Updated automatically by ClaudeManager from GitHub Gist -->

---

---

---

## SECTION 2 -- ARCHITECTURE
No architecture info recorded yet.

## SECTION 3 -- GIT COMMITS
Managed automatically by ClaudeManager.

---
## Session: March 7, 2026 — Value-First Gating Complete

### Recent Progress
- Stripe webhook committed (20cd498) + SUPABASE_SERVICE_KEY added to Render
- Feature gating moved from top-level app.py to inside each premium feature
- Upgrade wall completely redesigned (dark theme, founding member banner, pricing cards)
- All 5 premium features gated at last action button (value-first philosophy)

### Files Changed
- app.py — removed top-level gate, sets session_state["gating_enabled"]
- utils/stripe_utils.py — beautiful upgrade wall redesign
- healthcare/healthcare_main.py — gate at IRMAA + Medigap buttons
- pages/roth_calculator.py — gate at Save Strategy button
- ui/scenario_studio_page.py — gate at Run Scenario submit
- pages/social_security_optimizer.py — gate at Create SS Scenario button
- ui/historical_tracking_page.py — gate at render() entry

### Git Commits (master)
f881344 Value-first gating: Remove top-level gate + redesign upgrade wall
1e22559 Value-first gating: Historical Tracking
645645f Value-first gating: SS Optimizer button
6b4c8c0 Value-first gating: Scenario Studio button
fa15073 Value-first gating: Roth Calculator button
427a6f6 Value-first gating: Healthcare buttons
20cd498 Add Stripe webhook endpoint to Flask API

### Remaining Before April 15
- [ ] Test upgrade wall end-to-end with test payment (4242 4242 4242 4242)
- [ ] Privacy Policy page (Lovable)
- [ ] Terms of Service page (Lovable)
- [ ] UX Design Review session (4 questions)
- [ ] Stripe sandbox → live mode (bank account needed)
- [ ] Email registered users — Early Bird offer
