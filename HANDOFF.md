# HANDOFF.md -- FamilyForecast.AI

## DAILY STARTUP — Do This Every Morning

### CRITICAL RULES
- ALWAYS use CMD (not PowerShell) on backup laptop
- ALWAYS launch /remote-control from INSIDE Claude Code
- NEVER use `claude remote-control` directly from terminal — it FAILS on Windows with nvm

### Terminal 1 — Start the app
Open CMD and type:
```
cd C:\DEV\family_retirement_no_OCR
git pull
.\start_familyforecast.bat
```
Verify app is running at: http://localhost:8502
Verify Flask is running at: http://localhost:5000/health

### Terminal 2 — Start Remote Control
Open a NEW CMD window and type:
```
cd C:\DEV\family_retirement_no_OCR
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
- Project folder: `C:\DEV\family_retirement_no_OCR`
- Startup file: `start_familyforecast.bat`

---

## SECTION 1 -- RECENT PROGRESS

---

### April 7, 2026 — Full Two-PC Sync + QA Pass + Email Routing Rebuilt

**ONE LINE:** Full two-PC sync completed via GitHub, FF SUPPORTING FILES repo created, FamilyForecast.AI passed complete QA on desktop and mobile, Roth Calculator age crash fixed, Cloudflare email routing rebuilt and tested, all three previously disputed items confirmed done.

**What was decided:**
- Folder structure standardized on both PCs: `family_retirement_no_OCR` moved directly under `C:\DEV\` — no more `retirement-simulator` wrapper folder
- `retirement-simulator` renamed to **FF SUPPORTING FILES** on both PCs
- FF SUPPORTING FILES gets its own private GitHub repo (`sergecastro/ff-supporting-files`) — best long-term sync solution, both PCs now pulling/pushing from same repo
- Switched from ImprovMX to **Cloudflare Email Routing** — ImprovMX account inaccessible, Cloudflare simpler, already in use, tested and working
- IUL-FF.AI stays down intentionally — Lovable set to private until Reina partnership terms confirmed
- All features free until May 15 — `FEATURE_GATING_ENABLED=false` confirmed correct, matches public LinkedIn announcement
- Stripe webhook confirmed live — HTTP 400 on invalid payload = correct behavior, route exists and validates signatures

**What was built or changed:**

| Item | Detail |
|------|--------|
| `pages/roth_calculator.py` | `max_value` raised 72→99 on lines 110 and 266. Commit c4679b1 pushed to master. |
| `.gitignore` in family_retirement_no_OCR | `start_familyforecast.bat` added — Anthropic API key protected, removed from git history |
| GitHub repo `ff-supporting-files` | New private repo created. 152 files from MAIN + BACKUP's `.claude` and `lovable_backup_2026-04-03` — two-way sync completed |
| Cloudflare Email Routing | Replaced ImprovMX. 3 forwarding rules active and tested: `support@`, `privacy@`, `legal@` → `serge@emiramed.com`. Confirmed delivery in 30 seconds |

**Confirmed DONE — previously disputed:**

| Item | Confirmed | Evidence |
|------|-----------|----------|
| BETA badge removed | Done March 2 | Commit b4e92a9. Line 825 `app.py` = "Founding Member Preview." `beta_agreement` in code = internal session variable, never user-visible |
| Medicare data updated 2025→2026 | Done April 3 | Commit bb94ed5. Part D, MSP, Extra Help all updated. Minor "2025 estimates" label on state premiums = non-blocking |
| Stripe webhook live on Render | Confirmed today | HTTP 400 on dummy payload = correct. Route exists, validates Stripe signatures, rejects invalid requests |

**Full QA Results — today:**

| Test | Result |
|------|--------|
| Site loads clean — no BETA badge | PASS |
| Quick Mode — all fields, Run Simulation, AI ? buttons | PASS |
| Roth Calculator age crash (age >72) | FIXED — max now 99 |
| Feature gating — all free until May 15 | PASS by design |
| Email registration + vault save | PASS |
| Return user / email login + data restore | PASS |
| Mobile QA — full including return user on iPhone | PASS |
| Email forwarding — support@, privacy@, legal@ | FIXED + TESTED |
| Stripe webhook live | CONFIRMED |

**Commits:** c4679b1, 507f580
**Branch:** master

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

### March 7, 2026 — Value-First Gating Complete

- Stripe webhook committed (20cd498) + SUPABASE_SERVICE_KEY added to Render
- Feature gating moved from top-level app.py to inside each premium feature
- Upgrade wall completely redesigned (dark theme, founding member banner, pricing cards)
- All 5 premium features gated at last action button (value-first philosophy)

**Commits:** f881344, 1e22559, 645645f, 6b4c8c0, fa15073, 427a6f6, 20cd498

---

## SECTION 2 -- ARCHITECTURE

**Folder structure (standardized April 7, 2026):**
- `C:\DEV\family_retirement_no_OCR` — Main project (Streamlit app, this repo)
- `C:\DEV\FF SUPPORTING FILES` — Supporting files, `.claude` config, Lovable backups (separate private repo: `sergecastro/ff-supporting-files`)

**Three domains:**
- `familyforecast.ai` — Landing page (Lovable)
- `intake.familyforecast.ai` — INTAKE questionnaire (Lovable, same project)
- `app.familyforecast.ai` — Analysis engine (Streamlit on Render)

**Email routing:** Cloudflare Email Routing (replaced ImprovMX April 7)
- `support@familyforecast.ai` → `serge@emiramed.com`
- `privacy@familyforecast.ai` → `serge@emiramed.com`
- `legal@familyforecast.ai` → `serge@emiramed.com`

**IUL-FF.AI:** Down intentionally (Lovable set to private). Patent No. 64/031,074 filed April 6, 2026. Non-provisional due April 6, 2027.

---

## SECTION 3 -- GIT COMMITS
Managed automatically by ClaudeManager.

---

## OPEN ITEMS — Honest and Verified

| # | Item | Priority | Notes |
|---|------|----------|-------|
| 1 | Stripe live mode — bank account verification in Stripe dashboard | CRITICAL | Must before May 15. Cannot accept real payments until complete |
| 2 | `FEATURE_GATING_ENABLED=true` on Render | CRITICAL | Set on May 14. One env var change — do day before launch |
| 3 | Stripe live end-to-end test with real card | CRITICAL | After bank account connected. Test after switching to live keys |
| 4 | Sankey chart API — shows zero data points when ? clicked | MEDIUM | Needs audit of chart API connections |
| 5 | Part D state premiums label — still says "2025 estimates" | MINOR | Non-blocking, cosmetic |
| 6 | Lovable debug console.logs cleanup in QuickReview.tsx | MEDIUM | Do after all testing confirmed complete |
| 7 | IUL-FF.AI — reopen when Reina partnership terms confirmed | PENDING | All IUL docs must reference patent No. 64/031,074 |
| 8 | Seagate backup | CRITICAL | Overdue — both PCs perfectly synced right now |

---

## PROJECT ROADMAP

- [x] Both PCs fully synced via GitHub (Apr 7)
- [x] FF SUPPORTING FILES private repo created (Apr 7)
- [x] Email forwarding rebuilt on Cloudflare (Apr 7)
- [x] Roth Calculator age crash fixed (Apr 7)
- [x] Full QA passed — desktop + mobile (Apr 7)
- [x] BETA badge removed (Mar 2)
- [x] Medicare data updated to 2026 (Apr 3)
- [x] Landing page overhaul — Curtis feedback (Apr 3)
- [x] Email signup bug fixed (Mar 2)
- [x] Stripe webhook live on Render (Mar 7+)
- [x] IUL-FF provisional patent filed (Apr 6) — Patent No. 64/031,074, non-provisional due Apr 6, 2027
- [ ] **Stripe bank account verification → live mode** ← START HERE TOMORROW
- [ ] `FEATURE_GATING_ENABLED=true` (May 14)
- [ ] Stripe live end-to-end test
- [ ] May 15 paid launch
- [ ] Post-launch: Plaid integration
- [ ] IUL-FF V2 + advisor licensing (after Reina confirmed)

---

## MARKETING NOTE
LinkedIn "all free until May 15" post live and getting engagement (Alex Sidorenko comment responded to). Email forwarding now working — `support@familyforecast.ai` reaches `serge@emiramed.com` instantly. Founding Member messaging active across landing page and sidebar.

## EXACT NEXT STEP TOMORROW
Start here: Stripe bank account verification in Stripe dashboard → complete business verification → connect bank account → switch to live keys on Render → test one real transaction → confirm live mode working. **This is the last major pre-launch blocker.**

---
*Reminder: Seagate backup before you close anything. Both PCs are perfectly synced. Best possible moment.*
