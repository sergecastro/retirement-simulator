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
<!-- Updated automatically by ClaudeManager from GitHub Gist -->

## June 18–20 2026 — Tracks N–Q + Lovable fixes
- **Track N** (`db708d09`): CC banner gated — only shows after simulation runs, moved to bottom of results.
- **Track O** (`c40db0f2`): Plausible top-window injection in `app.py` — Streamlit pageviews now track `app.familyforecast.ai` (were lost inside `st.components.v1.html`'s iframe).
- **Track P** (`1a71e983`): `/cc/summary` `taxOpportunities` adds real fields — `iraBalance`, `rothBalance`, `four01kBalance`, `taxableInvestments`, `grossAnnualIncome`, `rothConvertMax` (no proxies; balances populate after a fresh Analysis run; `capitalGainsRoom`/`estimatedTaxableIncome` intentionally omitted as un-computable).
- **Track Q** (`3caf8672`): premium gate added to the internal Streamlit Command Center (matches the other gated modes; dormant until `FEATURE_GATING_ENABLED=true`).
- **Lovable shipped:** My Plan tab now first; Return-to-Analysis 404 fixed (carries `session_id`); AI chat confirmed conversational (backend `/cc/chat` round-trips history).
- **Still Lovable-side:** Tax tab must consume Track P fields + show `rothConversionMessage` (not $0); Full-Mode "Open Command Center" button (no Streamlit button exists in the intake flow — Lovable-only); premium gate on `familyforecast.ai/command-center`; Plausible `<head>` tag on the Lovable site; renders for `homeEquity` / `irmaaWatch` / `collegePlanning` / Monthly Expenses $0.

### Session Summary -- 2026-06-17

**🎯 DATA-INTEGRITY DAY — first clean Command Center: assets correct for the first time ($1,400K IRA + $200K Roth + $1,500K Taxable = $3,100K), Oren tested live for hours**

Massive correctness pass after Oren (first real user) surfaced wrong numbers. Backend Tracks A–G (`master` + `feature/command-center`), Lovable shipped the matching frontend fixes, and 15 Supabase records were patched. The product went from completely wrong (invisible Roth, doubled IRA, $0 income) to showing Oren's real picture: $3.1M total, 100% Monte Carlo, Green Zone.

**Decisions:** fix for ALL users (not just Oren); SS claiming age = mandatory/blank/hard-blocked (never pre-filled); Roth + IRMAA + income-gap all age-conditional; IRA fields fully separate; iraAccounts handled by priority logic, not summing.

**Backend (Code) — Tracks A–G on master:**
- **A** (`6eeab1d2`) `command_center_ai.py`: +4 income sources; `_get` no longer treats $0 as missing; real 0% MC shows "0%".
- **B** (`cf6835ba`) transform: `input_partner_age` from `partnerBirthYear`.
- **C** (`4c13021b`) + **hotfix** (`ec58c36f`): **recovered Roth** (`assets.rothIra` was never mapped — Oren's $200K invisible); IRA uses **priority** logic (`traditionalIra` if >0 else `iraAccounts`) to avoid double-count; `input_partner_retirement_age` mapped.
- **D** (`26b4b243`) session-aware `/cc/chat` + `_collect_intake_snapshot()` into `raw_results.intake`.
- **E** (`98629045`) CC screens: 4 wrong keys fixed; IRA line sums IRA+401k; age-aware Roth.
- **F** (`de6e53ae`) `/cc/summary` age-conditional Roth (`rothConversionStatus`/`Message`, `bracketRoom:0` for workers).
- **G** (`7dbf01ac`) IRMAA age-gate (under 63 → `not_yet_relevant`).
- **I** (`dc5cf15c`) Annual labels ×12 in `ai_advisor.py` + `scenario_comparison_enhanced.py` (were showing monthly under "Annual"); historical-snapshot save fixed (7 wrong session keys → real `input_*`, was saving all $0); **Roth added to `liquid_assets`** in `financial_inputs.py` (was excluded → raises safe-spending + net worth). *(Track H — income-gap temporal framing — deferred, not built.)*
- **J** (`42eff427`) home equity: `mortgage_balance` added to the intake snapshot; `/cc/summary` returns a `homeEquity` block `{homeValue, mortgage, equity}` when `homeValue > 0`.
- **K** (`eafa7184`) SS claiming age mapped: `profile.socialSecurityAge` → `input_social_security_age` (no default — Lovable hard-blocks until entered). *(Lovable confirmed the key is `profile.socialSecurityAge`.)*
- **L** (`f443c585`) college planning: snapshot now carries `children_list` + `five29_plan_balance`; `/cc/summary` returns `collegePlanning[]` per child `{name, startYear, estimatedCost, current529, gap}` (cost map: Public In-State $120K / Out-of-State $180K / Private $280K). Note: 529 shown per-child (shared 529 not split — don't sum gaps naively).
- **M** (`2b45f4c7`) SS timing gate: `simulation_core.py` pays SS only from `user_age >= input_social_security_age` (was paying from year 1). Timing only — benefit-amount actuarial adjustment still deferred. Existing results need a re-run.

**Lovable — published today:** SS claiming age (mandatory, blank, 62–70, red border, hard-block on Continue); Roth 401k field added; Traditional vs Roth IRA fields **separated (binding fix — no longer copies Roth into iraAccounts)**; `retirementAgePartner` saved; **`session_id` passed in `/cc/chat`**; `rothConversionStatus/Message` rendered (Roth rec hidden when `window_not_open`). *(The 3 queued Lovable instructions are now LIVE.)*

**Supabase — direct patch:** 15 records (Oren + OC-2026) had `iraAccounts.currentValue` set to **0**, removing the $200K duplicate. (Root cause was the Lovable form binding, now fixed — confirm with one fresh run.)

**🔴 CRITICAL OPEN (first tomorrow):**
- **Monthly Expenses / Gap show $0** in Command Center My Plan despite **$10,500** in Supabase. Assets are correct but the income section reads $0/$0/$0. → Investigate `monthly_expenses` / `guaranteed_income` flow from the freshest `analysis_results` row to the display.
- **Tax bracket inconsistency:** Tax tab shows 24% but My Plan shows 32% — reconcile.
- **Mobile (iPhone Safari) display issues** — batch fixes once Serge shares flight screenshots.

**Open / deferred (carry forward — see also memory `project_command_center_next_steps`):**
- ✅ **SS engine timing gap — FIXED (Track M, `2b45f4c7`):** engine now pays SS only from `user_age >= input_social_security_age`. *Still deferred:* adjusting the benefit **amount** for early/late claiming (actuarial) — timing only so far.
- **Track H** — income-gap temporal framing for pre-retirees (label "Guaranteed *retirement* income"; frame gap as future, not current shortfall). Deferred.
- **Option B IRMAA** — richer MAGI incl. taxable withdrawals (engine change). Deferred.
- `customSources` income mapping (Lovable `income.customSources` never mapped — custom income lost).
- `annuities` + `lifeInsuranceCashValue` assets — present in Lovable, never mapped.
- Verify `input_partner_retirement_age` consumer (mapped, but does anything read it?).
- **Premium gate** on the Command Center route (currently free to all).
- "Open Command Center" button missing after Full Mode save (only after Quick Mode).
- **`feature/merged-app` is 338 commits behind master** — decide: reconcile, retire, or canonical. (All session work synced to `feature/command-center`.)
- **Lovable renders pending:** Monthly Expenses $0 (read `monthlyCommand.monthlyExpenses`); `homeEquity` block; `irmaaWatch` `not_yet_relevant` shape; `collegePlanning[]` cards (note shared-529 — don't sum gaps naively).
- Confirm Lovable form fix with one fresh run (iraAccounts no longer duplicates Roth).

**Not ready for new users until the Monthly Expenses $0 issue is fixed.**

### Session Summary -- 2026-06-16

**🎯 COMMAND CENTER IS LIVE ON REAL DATA, MERGED TO PRODUCTION, + a major engine bug fixed and a one-link-to-any-phone share path shipped**

Big day. The Lovable Command Center went from showing **fabricated "proxy" numbers** to showing **real, engine-computed results** for a real user (Oren), end-to-end — then we fixed a serious math bug that had been silently inflating every plan, and made the whole thing shareable by a single link.

**1. Killed the fake numbers; wired real data (`3a044126`).** `/cc/summary` now reads genuine engine outputs from the new Supabase `analysis_results` table and returns `requiresAnalysis: true` when no real Analysis exists — never invented figures.

**2. Found & fixed the root-cause wiring bug (`89b7e779`).** A direct Supabase query proved **Lovable's intake payload has no `id` field**, so the Streamlit write (`save_analysis_results`) had **never fired** — proxies had masked it. Switched the linking key to the frictionless **`session_id` (`TEMP-XXX`)** shared by both sides, with `.strip().upper()` normalization so case can't break the match.

**3. Merged Command Center to production (`b57a3352`)** and made the Analysis page show **one** CTA → the Lovable Command Center (`familyforecast.ai/command-center`), removing the duplicate internal-Streamlit button (`0f0f311d`).

**4. Populated ALL Command Center fields from real outputs (`ea9b1da4`, `91e06d0b`).** Five computed — `safe_monthly_spending` (labeled 4% guideline + caveat note), `tax_bracket`, `bracket_room`, `irmaa_margin`, `rmd_at_73` (derived from the user's projected income using the engine's own 2025 bracket tables / per-year RMD). Three intake values for the report — `monthly_expenses`, `guaranteed_income`, `total_assets`.

**5. MAJOR engine bug fixed (`bcb99c89`): monthly→annual mismatch.** Income was annualized (×12) but **expenses were not**, in BOTH `simulation_core.py` and `monte_carlo.py` — so plans counted only ~1 month of expenses against a full year of income, **inflating success rates dramatically**. Now both engines annualize consistently; `emergency_months` left intact. Expect success rates to drop to honest levels going forward.

**6. AI explanation quality (`b055d487`, `d76f9245`).** Chart explanations now inject **retirement-year context** ("user is age X, retires in year Z; projections start today, not at retirement") so the AI stops calling the current year "your first retirement year." Fixed **7 wrong `session_state` key names** in `command_center_ai.py` (it was feeding the AI $0s). Added **Social Security claiming guidance** to `/cc/chat` (tie advice to the user's real numbers: need, break-even, Roth window, IRMAA).

**7. One-link-to-any-phone (`dba4e90f` docs).** Lovable shipped `?session=` → `localStorage` on the Command Center, so opening `familyforecast.ai/command-center?session=TEMP-XXXX` loads that person's saved results on **any device**. Verified end-to-end for Oren. Instruction recorded in `docs/LOVABLE_command_center_session_link.md`.

**8. First real user profile (Oren, "OC-2026", age 49).** Built on cell phone, ran real Analysis. Caught & patched a data bug where Birth Year defaulted to 1949 (showed age 77). Full profile + results backed up locally at `intake_templates/oren_OC-2026.json` (uncommitted by request); his session link extended through 2026-06-24.

**Still open / next session:**
- **Session-aware `/cc/chat`** — the "Ask the AI Advisor" chat still builds context from the posted intake, so a user arriving via link has no chat context ("coming online"). Make `/cc/chat` accept `session_id` and load context from `analysis_results` (same pattern as `/cc/summary`); Lovable passes the id.
- **Profile editing over time** (load existing → edit → re-run) and **session recording + change advice** (keep run history, diff between runs, AI explains — the "What Changed" tab).
- **Premium gate** on the Command Center route is still missing (currently open to all users).
- Sanity-check Monte Carlo `mc_success` (shows 100 on a ~$5M plan); Roth not yet captured in Lovable intake; `retirementAgeUser` arrived null (defaults to 65).

### Session Summary -- 2026-06-15

**🎯 RETIREMENT COMMAND CENTER — built end-to-end + all AI brought back online**

Major feature night. Built the **Command Center**, a premium, decision-first experience for subscribers, and fixed a silent production-wide AI outage discovered along the way.

**What was built (new Streamlit module, isolated on `feature/command-center`):**
- `ui/command_center.py` — entry point, INTAKE gate, sidebar nav, shared helpers, navy/gold CSS
- `ui/command_center_screens.py` — the screen functions
- `ui/command_center_ai.py` — per-screen AI advisor (builds context from the user's intake, calls Claude directly)
- **10 screens:** Monthly Command, Income Recipe, Guardrail Zone, Tax Opportunities, Social Security, RMD Forecast, IRMAA Watch, What Changed, Next Best Action, and **🟢 My Action Plan** (Green Summary — hero status bar, master action table, income/asset snapshots, plain-English summary).
- **AI on every tab:** each screen has a "Quick questions" + chat panel powered by the Anthropic SDK, pre-loaded with the user's full retirement data as context. Quick-question buttons now answer immediately (fixed a focus-steal bug).
- Reachable via a new **🎯 Command Center** card on the welcome screen and the sidebar **Quick Mode Switch** (added to all 3 views).

**Critical bug fixed (was breaking production silently):** every AI feature referenced a **dead model id** `claude-sonnet-4-20250514` (404 not-found). The "?" chart explanations *and* the Analysis AI Advisor were failing. Updated **all** references across `ai_advisor.py`, `explain_api_server.py`, and `explain_visual_handler.py` to **`claude-sonnet-4-6`**. Verified with a live API call.

**New Flask API for the Lovable Command Center** (`explain_api_server.py`, deployed to production via `master`):
- `POST /cc/summary` — receives intake JSON from Lovable, returns calculations for all screens in one call (safe spending, guardrail zone, tax/Roth room, IRMAA margin, RMD forecast, SS claiming comparison, withdrawal order, prioritized action plan).
- `POST /cc/chat` — context-aware AI chat endpoint.
- **CORS hardened:** baked all production + Lovable origins into the default (`app/root/www/intake familyforecast.ai`, `familyforecast.lovable.app`, `forcash.onrender.com`) so it works even if the env var is missing.

**Deployment:** model fix + CORS + `/cc/*` endpoints cherry-picked to **`master`** (live for Render `forcash-api`). Command Center UI stays on `feature/command-center` (not yet exposed to production users — still placeholder data on several screens). Local dev validated on Streamlit `:8502` + Flask `:5000`.

**Still open / next:** wire real Analysis-engine data into the Streamlit Command Center screens (several still show preview tables); confirm Render `forcash-api` auto-deployed `b3bf9720` and production `/cc/summary` returns live data; add the premium gate to the Command Center route before exposing it; decide whether the Streamlit Command Center or the Lovable+Flask version is the canonical product (currently both exist).

### Session Summary -- 2026-06-13
📋 PRE-TRAVEL HANDOFF REPORT — Friday, June 12, 2026
"4-Week Pause Anchor Document — Complete State of the Project"
Prepared by Claude.ai for Serge Castro — Synaptal Technologies, Inc.

This is your single source of truth when you return from your trip.

1. ONE LINE SUMMARY
FamilyForecast.AI launched May 15, 2026 with Stripe live, feature gating built and confirmed, payment handler with balloons shipped, Lovable intake clean — and now sits in early post-launch state with a defined list of 12 outstanding items to address when you return, ranging from Supabase SMTP email setup (currently broken) to Sankey chart API audit to UX design review.

2. WHAT WE DECIDED TODAY (AND IN RECENT SESSIONS)
Decision 1 — Pause all development for 4-week trip.

You are leaving next week. No code changes should happen during travel. The product is live and revenue-capable. Nothing is broken badly enough to require emergency action.
Decision 2 — This document replaces the HANDOFF.md as your re-entry anchor.

When you return, read this document first. Then read HANDOFF.md on GitHub. Then ask Claude Code to run git log --oneline -10 to confirm no drift.
Decision 3 — Feature gating stays at FEATURE_GATING_ENABLED=false during your absence.

Do NOT flip this to true while you are traveling. You cannot monitor properly. The plan was to flip it on May 14 pre-launch — confirm with Code whether this was done. If not, it stays false until you return and run a full regression.
Decision 4 — IUL-FF remains a completely separate project.

All IUL documents reference patent No. 64/031,074. Never mix IUL work with FamilyForecast sessions. Reina partnership discussion is on hold until after travel.

3. WHAT WAS BUILT OR CHANGED (Complete Feature Inventory)
✅ FULLY BUILT AND DEPLOYED (production at app.familyforecast.ai)
FeatureLinesStatusINTAKE (8-page questionnaire, Quick + Full Mode)~2,000✅ LiveAnalysis Mode (Monte Carlo simulation)~3,000✅ LiveHealthcare Hub (IRMAA calculator + Medigap)~3,545✅ LiveScenario Studio (comparison tool)~1,200✅ LiveSocial Security Optimizer~1,674✅ LiveRoth Conversion Calculator~905✅ LivePrivacy/Encryption (AES-256 client-side)~600✅ LiveAI Explanations (unique competitive moat)~600✅ LiveStripe checkout + subscription + webhook~263✅ LiveFeature gating (5 premium features)in app.py✅ BuiltStripe redirect handler (?upgrade=success)in app.py✅ LiveLovable landing page + INTAKE (one merged project)React/TypeScript✅ Live5 return user paths (vault, email, pending, localStorage, .ffb)in app.py✅ Built
Total codebase: 19,500+ lines of production Python + React
✅ CONFIRMED WORKING (as of last session May 6, 2026)

Stripe live mode with Founding Member coupon POKg7YZp (20% off forever)
Annual price $49/yr (price_1TQvPB7iOvTHoIoEUh5rW0es) confirmed
Monthly price $5/mo (price_1TQvSV7iOvTHoIoECVxkMW3g) confirmed
Webhook firing 5 events to https://forcash-api.onrender.com/webhook
Payment confirmation shows st.balloons() + ✅ emoji banner on success
Mobile nested expanders bug: confirmed resolved on clean iPhone (May 6)
Lovable console.log cleanup: 13 debug statements removed from QuickReview.tsx + IntakeReview.tsx
iPhone bookmark issue: resolved — full instructions in memory


4. PROBLEMS WE HIT & HOW WE SOLVED THEM (Session History)
Problem 1 — Two months of illness (Dec 2025 – Feb 2026)

After the November 2025 build sprint, Serge was ill. Development paused. When resuming in February, the frictionless new-user flow from INTAKE → Analysis was broken.

Solved: Feb 12 marathon session (10+ bugs fixed). Quick Mode end-to-end confirmed working. 4 commits, 25+ field names corrected.
Problem 2 — Stripe setup blocked by bank verification

Could not switch from sandbox to live mode until Stripe business verification (2–7 days).

Solved: Synaptal Technologies, Inc. Chase Business Complete Checking account 2909225007 connected. Stripe live mode confirmed working as of April 28.
Problem 3 — Upgrade wall contrast (accessibility)

Upgrade wall text was illegible at low contrast.

Solved: Added !important to CSS rules. AAA-level contrast confirmed. Shipped commit 5d2bc74a.
Problem 4 — Main iPhone not showing Lovable landing

iPhone was loading app.familyforecast.ai directly via a saved bookmark, bypassing the marketing site.

Solved: Close all tabs → delete favorite → clear bookmarks → clear history → retype clean URL. Both phones now identical.
Problem 5 — Supabase email confirmation broken

sign_up() was throwing "Error sending confirmation email." RLS INSERT rejection.

Solved (partial): Toggled off email confirmation in Supabase as temporary workaround. Resend API key re_g6S4RTuB_9W3VH7x8y5AggRR9RPByGb1T is in .env but NOT yet connected to Supabase SMTP. This is still open — see Section 5.

5. OPEN QUESTIONS — NOT YET RESOLVED
These are your first-week-back priority list, in order of importance:
🔴 CRITICAL — Do First
1. Supabase SMTP / Resend connection

Email confirmation currently returns error. Resend API key exists but not wired to Supabase.

What to do: Supabase Dashboard → Authentication → Email → SMTP Settings → enter Resend credentials → re-enable "Confirm email" → test round-trip.

Risk: Without this, new email registrations cannot confirm their accounts.
2. Confirm FEATURE_GATING_ENABLED status on Render

Was this flipped to true on May 14 as planned? If yes, confirm all 5 gated features work correctly with live Stripe. If no, plan this as first Code session.

Risk: Healthcare Hub, Scenario Studio, SS Optimizer, Roth Calculator, AI Advisor may be freely accessible to all users without payment.
3. Feature gating redirect bug (Healthcare Hub)

When FEATURE_GATING_ENABLED=true, clicking Healthcare Hub redirects to the welcome screen instead of showing the upgrade wall.

What to investigate: show_upgrade_wall() function and app.py lines 925–970.

Risk: This breaks the upgrade path — no wall means no paid conversions.
🟡 IMPORTANT — Do Second
4. Return user paths 2–5 testing

Path 1 (email login) was confirmed working April 28. Paths 2–5 were never fully tested:

Path 2: Anonymous vault → load_anonymous_vault() → Supabase anonymous_vaults
Path 3: Frictionless pending intake → load_pending_intake() → pending_intake table (24hr, no password)
Path 4: Browser localStorage → load_snapshot()
Path 5: File import from .ffb file

These require your hands-on testing, not Code. Start with Path 2 (anonymous vault on clean iPhone Safari).

5. Banner display duration too brief

The ?upgrade=success banner auto-dismisses too quickly. Streamlit default.

Three options to evaluate: (a) custom HTML banner with CSS animation, (b) time.sleep(5), (c) session_state persistent banner.

Affects app.py lines 555–562.
6. UX Design Review (4 questions, requires dedicated session)

New visitor experience post-launch — what do they see first?
Vault creation = 30-day free premium trial — how/where communicated?
Returning email user flow — smooth end-to-end on mobile?
When/where to show the registration offer?

Prerequisite: Webhook confirmed working first.

7. Full A-to-Z iPhone Safari regression

Was the May 14 pre-launch regression completed? If not, schedule as first mobile test session.

Procedure: Settings → Safari → Clear History and Website Data → open familyforecast.ai → complete Quick Mode as new user → run simulation → verify all sections → test email registration.
🟢 NON-BLOCKING — Backlog
8. Sankey chart "zero data points"

When ? button clicked on Sankey chart, shows zero data. Some chart API connections may not be wired. Audit all chart API connections. Non-blocking at launch.
9. Income numbers showing for vault users

Analysis intake screen shows actual income numbers (e.g., $55,555) instead of expected totals for vault users. Investigate display logic in Code. Non-blocking.
10. Upgrade wall banner copy

Remove "$1/month intro" language. Replace with Founding Member coupon POKg7YZp messaging.
11. Privacy Policy / Terms of Service

Add privacy@ and legal@familyforecast.ai addresses in Lovable
Add Privacy/Terms footer links in Streamlit app

Both email addresses route to serge@emiramed.com via Cloudflare.

12. Post-launch: Should app.familyforecast.ai redirect first-time visitors to the marketing landing?

Raised by the iPhone bookmark issue. Users with saved bookmarks bypass the marketing site entirely. Decision to make after reviewing real user behavior data in Plausible.

6. MARKETING NOTE
YES — There is real marketing work waiting when you return.
LinkedIn Buffer queue status: Posts from the April 15 Batch 1 were loaded. Batch 2 posts were scheduled for April 30. Verify Buffer queue is still active — it may have exhausted.
IUL-FF marketing: Entirely separate. Reina partnership discussion pending. Do not mix with FamilyForecast marketing activities.
Suggested first post-return LinkedIn angle: "We launched. Here's what 4 weeks of real users showed us that we didn't expect." (Post-travel, post-data reflection post.)

7. EXACT NEXT STEP WHEN YOU RETURN
Start here — first morning back:

Read this document top to bottom (you're doing it)
Ask Claude Code: git log --oneline -10 — confirm no changes during travel
Check Render dashboard — is the app running? Check forcash and forcash-api uptime
Check Sentry — any errors accumulating?
Check Plausible — any real visitors / signups since launch?
First Code session: Wire Supabase SMTP → Resend API → re-enable email confirmation
First mobile session: Full A-to-Z iPhone regression (if not done May 14)
First product session: Test return user Paths 2–5

Do NOT flip FEATURE_GATING_ENABLED=true until after Path 2–5 testing and UX review.

8. PROJECT ROADMAP — NEXT DEFINED STEPS
✅ INTAKE + Analysis + Healthcare Hub + Scenario Studio — COMPLETE
✅ SS Optimizer + Roth Calculator + AI Explanations — COMPLETE  
✅ AES-256 encryption + 5 return user paths — COMPLETE
✅ Lovable landing page + INTAKE merged project — COMPLETE
✅ Stripe live mode confirmed (Apr 28)
✅ Founding Member coupon POKg7YZp working at $39.20 (Apr 28)
✅ Webhook firing 5 events on live (Apr 28)
✅ Upgrade wall contrast fix shipped (Apr 27)
✅ Stripe ?upgrade=success/cancelled handler with balloons (May 6)
✅ Mobile nested expanders bug closed (May 6)
✅ Lovable console.log cleanup (May 6)
✅ iPhone bookmark issue resolved (May 6)
✅ LAUNCH: May 15, 2026

👉 [FIRST WEEK BACK] Wire Supabase SMTP to Resend API
👉 [FIRST WEEK BACK] Confirm FEATURE_GATING_ENABLED status
👉 [FIRST WEEK BACK] Fix Healthcare Hub gating redirect bug
👉 [FIRST WEEK BACK] Test return user paths 2–5
👉 [FIRST WEEK BACK] Full iPhone A-to-Z regression if not done
👉 [SECOND WEEK BACK] UX Design Review (4 questions)
👉 [SECOND WEEK BACK] Banner duration improvement
👉 [SECOND WEEK BACK] Upgrade wall banner copy (remove $1/month)

○ Sankey chart API audit
○ Income display logic for vault users
○ Privacy/Terms footer links in Streamlit
○ app.familyforecast.ai → landing page redirect question
○ "BETA DEMO" badge removal from sidebar (if still present)
○ LinkedIn Batch 2 posts (verify Buffer queue)

POST-LAUNCH MAJOR FEATURES (months 2–6):
○ Plaid integration (12–15 hours) — auto-fill from banks
○ PDF Reports (8–10 hours) — export functionality  
○ Historical tracking (10–13 hours) — year-over-year snapshots
○ LTC Planner
○ Tax Optimization Dashboard

POST-LAUNCH ADVANCED (months 7–12):
○ White-label for advisors portal
○ Advanced estate planning module
○ Community features

IUL-FF (SEPARATE PROJECT — never mix):
○ V1: Stable, patent filed (App No. 64/031,074, filed Apr 6, 2026)
○ Non-provisional due: April 6, 2027 — do NOT miss this
○ V2 roadmap: Tax Bucket Visualizer, Market History Stress Test, 
  One-Click Spouse PDF
○ Reina partnership discussion: pending after travel
○ Stripe wiring for IUL-FF: pending

KEY INFRASTRUCTURE REFERENCE (when you need to find things fast)
SystemURL / LocationStatusStreamlit appapp.familyforecast.ai → Render "forcash"✅ LiveFlask APIforcash-api.onrender.com → Render "forcash-api"✅ LiveMarketing landingfamilyforecast.ai → Lovable✅ LiveLocal codeC:\DEV\family_retirement_no_OCR✅ GitGitHubsergecastro/retirement-simulator✅ SyncedSupabaseebhzvauommuhqlcswdil.supabase.co✅ RunningStripe liveAnnual price_1TQvPB7..., Monthly price_1TQvSV7...✅ LiveFounding Member couponPOKg7YZp — 20% off forever✅ ActiveWebhookforcash-api.onrender.com/webhook✅ FiringResend keyre_g6S4RTuB_9W3VH7x8y5AggRR9RPByGb1T✅ In .envPlausibleAnalytics✅ RunningSentryError tracking✅ RunningUptimeRobotUptime monitoring✅ ActiveBufferLinkedIn queue⚠️ Verify active

--- NOTEBOOKLM CONTEXT UPDATE ---

Project: FamilyForecast.AI

Date: June 12, 2026

Status snapshot: Product launched May 15, 2026 — Stripe live, feature gating built, payment handler with balloons shipped, 19,500+ lines of production code across Streamlit + React/Lovable; entering 4-week travel pause with 12 defined post-return items.

Key decisions made today:

Created comprehensive pre-travel anchor handoff document
Confirmed FEATURE_GATING_ENABLED should remain false during travel
Confirmed IUL-FF isolation protocol remains in effect
Prioritized Supabase SMTP wiring as first-week-back critical item

Critical next steps:
Wire Supabase SMTP to Resend API (email confirmation broken)
Confirm and test FEATURE_GATING_ENABLED=true (may not have been flipped May 14)
Fix Healthcare Hub gating redirect bug (routes to welcome screen instead of upgrade wall)
Test return user paths 2–5 on clean iPhone
Full A-to-Z iPhone Safari regression
UX Design Review session (4 questions)

Open risks or blockers:
Email confirmation non-functional until Resend is wired to Supabase SMTP
Feature gating status unknown — may be false, meaning premium features are free to all
Healthcare Hub upgrade wall redirect bug breaks the paid conversion path
Return user paths 2–5 untested — risk of broken flows for real users
IUL-FF non-provisional patent due April 6, 2027 — calendar it now

--- END NOTEBOOKLM CONTEXT ---


Have a wonderful trip, Serge. The product is live. The code is stable. Everything is waiting exactly where you left it. 🌎You said: thank you!thank you!Jun 12Claude responded: You're welcome!You're welcome! Have a great trip. Everything will be here when you get back. 🌍

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

**Command Center (built June 15; real-data wiring + production merge June 16, 2026):**
- Streamlit module **now on `master`** (merged `b57a3352`): `ui/command_center.py`, `ui/command_center_screens.py`, `ui/command_center_ai.py`. Routed in `app.py` as `current_mode == "command_center"`. The Analysis page links out to the **Lovable** Command Center via one gold HTML link (the duplicate internal-Streamlit button was removed — single CTA).
- **Canonical UI = Lovable** at `familyforecast.ai/command-center`. Flask API (on `master`, live via Render `forcash-api`): `POST /cc/summary` and `POST /cc/chat` in `explain_api_server.py`.
- **Real-data flow (no proxies):** Streamlit writes genuine Analysis-engine outputs to Supabase **`analysis_results`** via `save_analysis_results()` (`utils/supabase_sync.py`) after a real Analysis (`ui/results_page.py`). `/cc/summary` reads that table and returns `requiresAnalysis: true` when no row exists — NEVER fabricates numbers.
  - **`analysis_results` columns (all live):** `intake_id` (linking key), `monte_carlo_success_rate`, `final_savings`, `safe_monthly_spending` (labeled 4% guideline; caveat in `raw_results.safe_spending_method`, surfaced as `safeSpendingNote`), `tax_bracket`, `bracket_room`, `irmaa_margin`, `rmd_at_73` (derived from projected income + engine 2025 bracket tables / per-year RMD), `monthly_expenses`, `guaranteed_income`, `total_assets` (intake values), `raw_results` (jsonb), timestamps. RLS = service role only; both sides use `SUPABASE_SERVICE_KEY` (set on both Render services).
  - **Linking key = frictionless `session_id` (`TEMP-XXX`)** (Lovable payload has no `id`). Write & read both `.strip().upper()`.
  - **Share path:** Lovable seeds `ff_session_id` from `?session=` in the URL (`docs/LOVABLE_command_center_session_link.md`), so `familyforecast.ai/command-center?session=TEMP-XXXX` opens a saved Command Center on **any device**. `analysis_results` has no TTL, so links keep working after the 24h `pending_intake` record expires.
- **Engine money convention:** intake values are **MONTHLY**; `simulation_core.py` and `monte_carlo.py` annualize (×12) internally (fixed June 16 — expenses were previously not annualized, inflating success rates). `base_total_*` stay monthly for `emergency_months`.
- **`/cc/chat` is session-aware (Track D):** `save_analysis_results` snapshots the user's intake into `raw_results.intake`; `/cc/chat` accepts `session_id` and, when the posted intake is thin (link arrival), loads intake + computed results from `analysis_results`. Needs Lovable to pass `session_id` in the `/cc/chat` body.
- **Age-aware guidance (Tracks F/G):** `/cc/summary` returns `taxOpportunities.rothConversionStatus`/`rothConversionMessage` (suppresses misleading "Roth room" for working users) and `irmaaWatch.{status,message,safetyMargin}` (gated `not_yet_relevant` under age 63). Lovable renders these shapes as of 2026-06-17 (session_id pass-through + Roth status/message live; SS claiming age now a mandatory intake field).
- **All AI uses model `claude-sonnet-4-6`** (`ai_advisor.py`, `explain_api_server.py`, `explain_visual_handler.py`).
- Local dev requires BOTH servers: Streamlit `:8502` (`start_familyforecast.bat`) and Flask `:5000` (`python explain_api_server.py`).

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
