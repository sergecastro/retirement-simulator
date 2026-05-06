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

### May 6, 2026 — Stripe Payment Redirect Handler + Expander Audit

**ONE LINE:** Code Fix 2 from the April 28 punch-list landed on master — `app.py` now handles `?upgrade=success` (green banner + balloons) and `?upgrade=cancelled` (info banner) Stripe redirects; Code Fix 4 (nested-expander mobile bug) cleared `utils/stripe_utils.py` as a suspect via read-only audit, leaving the triggering page TBD by Serge.

**What was decided / done — Streamlit side:**

| Item | Detail |
|------|--------|
| Fix 2 — payment redirect handler | New 14-line block in `app.py:550-563` (between the `?mode=` handler at lines 542-548 and the analytics injection). Reads `st.query_params.get("upgrade")`. On `success` → `st.success("✅ Payment confirmed — welcome to FamilyForecast Premium!")` + `st.balloons()` + `st.query_params.clear()`. On `cancelled` → `st.info("ℹ️ Payment cancelled — no charges made. You can upgrade anytime.")` + `st.query_params.clear()`. No `st.rerun()` after clear — banner needs to render on this pass. |
| Fix 4 — expander audit | Read-only verification ruled out `utils/stripe_utils.py` as the source of the "Expanders may not be nested" mobile error. Both expanders inside `show_upgrade_wall()` (`stripe_utils.py:159, 253`) sit inside `col2` from `st.columns([1, 3, 1])` — columns are not expanders. All 7 call-sites of `show_upgrade_wall()` (5 in `app.py`, 2 in `healthcare/healthcare_main.py`) are top-level or inside columns, never inside an `st.expander`. The mobile bug originates elsewhere — triggering page TBD by Serge at next session start. |
| Local QA | All 4 manual tests passed at localhost:8502: bare URL clean (no banner), `?upgrade=success` shows green banner + balloons, `?upgrade=cancelled` shows info banner, banners do not persist on next navigation. |
| Process | Worked on branch `feature/payment-handler-2026-05-06` with safety tag `before-payment-handler-2026-05-06`. Merged with `--no-ff` after Serge approval, pushed to `origin/master`. Local feature branch deleted post-merge; remote retains for history. |

**Commits:**
- `1ebf1f0a` — Add Stripe ?upgrade=success/cancelled handler with balloons (feature branch)
- `e933d260` — Merge: Stripe payment redirect handler with balloons (current master HEAD)

**Branch:** `master`, clean, in sync with `origin`.

**Open items — punch-list status (carry-over from April 28):**

1. 🔴 IUL-FF Stripe wiring — still pending
2. 🟡 Code Fix 1 (upgrade wall contrast): `!important` is in place at `utils/stripe_utils.py:124, 127, 146, 147, 150, 197, 221` (commits `c6df7c71`, `5d2bc74a` from April 27). April 28 handoff flagged this as still visually inadequate — Serge to re-verify after Render redeploys today's merge.
3. ✅ Code Fix 2 (`?upgrade=success/cancelled`) — DONE today, on master.
4. 🔴 Code Fix 3 / Fix 4 (nested-expander mobile bug): triggering page still TBD by Serge; `stripe_utils.py` ruled out today.
5. 🔴 Lovable Fix: `console.log` cleanup in `QuickReview.tsx`.
6. 🟡 Serge testing: Render auto-deploy verification of today's merge, return user paths 2-5, mobile full QA, UX design review.

**Reminders:**
- `FEATURE_GATING_ENABLED = false` — keep until May 14.
- 9 days to launch (May 15, 2026).
- Safety tag from today: `before-payment-handler-2026-05-06`.

**Anomaly:** Local Streamlit was launched via Bash with the full executable path `C:\Users\serge\AppData\Local\Programs\Python\Python312\Scripts\streamlit.exe` — neither `streamlit` nor `python` is on Git Bash's PATH on this machine. PowerShell tool also failed today with a `System.Management.Automation.Runspaces.InitialSessionState` initializer error. Pinned both facts to memory (`reference_python_path.md`) so future Claude sessions can launch the app without rediscovering this. End-of-session TaskStop on `b12135nf5` returned "No task found" — task had already been stopped at merge time, no orphan process.

---

### April 28, 2026 — Stripe Live + Email Handoff Fixed + RLS Unblocked

**ONE LINE:** Stripe is fully live (Synaptal Technologies entity, live products + webhook + Founding Member coupon all wired and confirmed end-to-end), the Lovable→Streamlit email handoff bug that was blocking the upgrade wall is fixed, Supabase RLS rejection on `user_vaults` INSERT is unblocked, and the open punch-list before May 15 launch is down to four targeted Code fixes plus IUL-FF Stripe wiring tomorrow.

**Full archived report:** `docs/HANDOFF_REPORT_2026-04-28.md`

**What was decided / done — Lovable side:**

| Item | Detail |
|------|--------|
| Email handoff bug | 3 Lovable files updated to append `&email=XXX` to redirect URL: `QuickReview.tsx` (lines 217 + 279) and `IntakeReview.tsx` (line 174). `ff_user_email` confirmed written in `BackupPrompt.tsx:156` before `handleGoToAnalysis` runs. URL now correctly carries `?session=TEMP-XXXX&then=Analysis&email=...`. Override of "Never modify handleGoToAnalysis" Core memory rule was deliberate and verified safe (string concat only, no logic). |
| BETA banner | Removed from `IntakeWelcome.tsx`. Onboarding now clean. |

**What was decided / done — Streamlit side:**

| Item | Detail |
|------|--------|
| Investigation only | No commits to this repo today. Working tree clean at `5d2bc74`. All four launch-blocker issues investigated read-only and root-caused. |
| Silent payment failure | Diagnosed: `app.py` has zero handler for `?upgrade=success` / `?upgrade=cancelled` despite `utils/stripe_utils.py:84-85` redirecting users there after Stripe checkout. Fix lands in `app.py` lines 410-500 next session. |
| Privacy/Terms footer | Confirmed already present at `ui/navigation.py:227` (sidebar) and `config/settings.py:262` (bottom). No fix needed — possibly only restyling for visibility. |
| Sidebar BETA badge | `show_sidebar_footer` (`ui/navigation.py:161`) shows "✅ Full Access" / "👤 Demo Access" — no literal "BETA" text in the active code path. |
| Nested expander mobile bug | ~60 expander sites mapped repo-wide. Cannot pinpoint via grep alone (Streamlit nests via cross-function calls). Serge to identify triggering page at session start. Likely candidates: `ai_advisor.py` (lines 460/515/523), Healthcare Hub, or Results page after Run Simulation. |
| Stale duplicates flagged | 9 stale files identified (`LOVABLE_HANDOFF/` folder, `* - Copy.py`, `* BEFORE GEMINI.py`). Cleanup deferred to post-launch. |

**What was decided / done — Supabase + Stripe + Infra:**

| Item | Detail |
|------|--------|
| Supabase RLS unblocked | "Confirm email" toggled **OFF** in Supabase Auth. Prior failure: `auth.sign_up()` returned a user but `auth.uid()` was null at INSERT time, causing RLS rejection on `user_vaults`. Now resolved without code change. |
| Supabase clean slate | All test auth users + rows in `user_vaults`, `anonymous_vaults`, `subscriptions` deleted. Ready for real users. (Re-clean before May 15 once final QA is done.) |
| Stripe LIVE | Synaptal Technologies entity. Annual `price_1TQvPB7iOvTHoIoEUh5rW0es` ($49/yr), Monthly `price_1TQvSV7iOvTHoIoECVxkMW3g` ($5/mo). Founding Member coupon `POKg7YZp` — 20% off, 500 redemptions, expires Jul 14. All 4 Stripe env vars on BOTH Render services. Live webhook at `https://forcash-api.onrender.com/webhook` — 5 events. |
| Stripe end-to-end confirmed | Checkout opens, coupon auto-applies ($49 → $39.20), test card declines correctly in live mode. Real payments will work. |
| IVC monitor | UptimeRobot added for `https://ivc-retirement-api.onrender.com/health` — every 5 min, currently UP. (IVC `/health` endpoint needs `methods=['GET','HEAD']` fix next session.) |

**Open items — priority order (full detail in archived report):**

1. 🔴 IUL-FF Stripe wiring — tomorrow's first task, same May 15 launch
2. 🔴 Code Fix 1: Upgrade wall text contrast still broken (`!important` insufficient — try global CSS via `[data-testid="stMarkdownContainer"]`)
3. 🔴 Code Fix 2: Add `?upgrade=success` / `?upgrade=cancelled` handlers in `app.py:410-500`
4. 🔴 Code Fix 3: Nested expander mobile bug (page TBD by Serge)
5. 🔴 Lovable Fix: `console.log` cleanup in `QuickReview.tsx`
6. 🟡 Serge testing: return user paths 2-5, mobile full QA, UX design review

**Reminders:**
- `FEATURE_GATING_ENABLED = false` — keep until May 14
- Anthropic API was down today — some Code work deferred
- 17 days to launch (May 15, 2026)

**Commits:** None today on Streamlit. Last commit on master remains `5d2bc74` (Apr 27).
**Branch:** `master`, clean, in sync with `origin`.

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
