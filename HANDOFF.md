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

### Session Summary -- 2026-03-14
## SECTION 1 — Session Summary
Date: 2026-03-11 | Project: ALL PROJECTS

### WHAT HAPPENED TODAY

**Vettario — Built from scratch:**
- Created "Vettario Dev Sessions" Claude Project with full system prompt
- Vettario defined: B2B matching platform — manufacturers/suppliers of 
  aesthetic & medical equipment ↔ distributors (USA + worldwide)
- Same Relational DNA matching engine as Synaptal, different market
- GitHub repo created: github.com/sergecastro/vettario (private)
- Local folder created: C:\DEV\VETTARIO
- HANDOFF.md, CLAUDE.md, .gitignore all created and pushed to GitHub

**ClaudeManager — Major upgrades:**
- config.json updated: Vettario added as 4th monitored project
- GIST_TOKEN added to all 4 project .env files (was missing in 3)
- New GitHub token generated and deployed to all 4 projects
- push_handoff.py + push_handoff.bat built and tested on Desktop
- Gist push confirmed working ✅

**Architecture clarified:**
- Synaptal = AI companies ↔ job seekers
- Vettario = manufacturers ↔ distributors (aesthetic/medical equipment)
- Shared matching engine concept — separate codebases
- All 4 projects now fully monitored by ClaudeManager

### WHAT IS NEXT
- Tonight: first full automatic run across all 4 projects
- Tomorrow morning: verify START_HERE.html shows all 4 cards cleanly
- Next session: fix ClaudeManager morning report quality (messy history issue)
- Future: start Vettario dimension questionnaire and matching engine

### FOR MARKETING AGENT
- Vettario launched as new project today — early reveal phase
- Can reference Vettario name and B2B distribution matching concept
- Synaptal focus: AI talent matching thought leadership continues

---

<!-- Updated automatically by ClaudeManager from GitHub Gist -->

---

### Session Summary — 2026-03-13
**Session:** LinkedIn Campaign + OG Image + Marketing Assets

**ONE LINE:** Pure marketing day — 11 LinkedIn visuals created, 2 carousel PDFs built, og:image fixed, Post Inspector 100% clean, and 2 weeks of LinkedIn content fully prepared.

**WHAT WE DECIDED:**
- **og:image strategy** — confirmed `og-image.png` hosted at `familyforecast.ai/og-image.png`, added all 4 OG meta tags to Lovable `index.html`, extended description to 124 characters. LinkedIn Post Inspector now 100% clean — no warnings.
- **Carousel = PDF not images** — LinkedIn groups images as 2+3 thumbnails. Only PDF uploads render as true swipeable carousels. Both carousels built as PDFs.
- **Post 9 revised** — "Tomorrow" → "On April 15th" and "You have ONE day" → "Still totally free for only a few days" — works for any posting date.
- **Post 10 revised** — "today only" removed, replaced with "Founding Member pricing — still available."
- **LinkedIn group sharing strategy** — post on personal feed first (public), then Share → Send into each group one by one with short personal intro.

**WHAT WAS BUILT:**
- All 10 LinkedIn post PNGs rebuilt/refined (1080×1350px, 300 DPI): `post1` through `post10`
- `FamilyForecast_Carousel_A.pdf` — posts 1–5
- `FamilyForecast_Carousel_B.pdf` — posts 6–10
- Lovable `index.html` updated with og:image + og:description meta tags

**OPEN QUESTIONS:**
- Stripe Sandbox → Live mode — still needs bank account verification before April 15
- `FEATURE_GATING_ENABLED` still `false` in Render — must flip to `true` on April 13th
- Lovable debug console.logs still in `QuickReview.tsx`
- Medicare 2025 → 2026 values not updated in `healthcare/` folder
- Sankey chart API still shows "zero data points"
- Quick Mode with partner — not retested since fix
- Mobile full QA — never fully completed on iPhone Safari

**FOR MARKETING AGENT:**
- YES — Entire session was marketing. 10 post visuals + 2 carousel PDFs + post texts ready.
- **Post 1 should go out tomorrow — March 14th.**

**NEXT STEP:**
- DEV: Return user flow testing (vault login, email login, all edge cases)
- MARKETING: Post `post1_announcement.png` on LinkedIn with Post 1 copy

---

---

### Session Summary — 2026-03-10
**Session:** Stripe Gating + Webhook Verified + Privacy/Terms Pages + Footer Links

#### COMPLETED TODAY
- **Stripe feature gating:** added gating blocks to all 5 premium features in `app.py` router (Healthcare, Scenario Studio, Historical Tracking, SS Optimizer, Roth Calculator) — controlled by `FEATURE_GATING_ENABLED` env var, defaults to `false` (everything free until April 15)
- **Stripe webhook verified live:** `https://forcash-api.onrender.com/webhook` returns 400 "Invalid signature" (correct — signature verification working). Webhook code already existed in `explain_api_server.py`, confirmed deployed on Render
- **All Render env vars confirmed:** `STRIPE_WEBHOOK_SECRET`, `SUPABASE_SERVICE_KEY`, `SUPABASE_URL` on forcash-api service
- **Privacy Policy page** built in Lovable — live at `familyforecast.ai/privacy`
- **Terms of Service page** built in Lovable — live at `familyforecast.ai/terms`
- **Privacy/Terms footer links** added to Streamlit app footer (`config/settings.py`)
- **ImprovMX email forwarding** active for `support@`, `privacy@`, `legal@familyforecast.ai`
- **Outbound confirmation email** verified working via Resend SMTP

#### PENDING (before April 15 launch)
- Mobile full QA pass (iPhone Safari + Android)
- Lovable email address audit (`support@`, `privacy@`, `legal@`)
- Verify Streamlit footer Privacy/Terms links render correctly after deploy
- **April 13:** flip `FEATURE_GATING_ENABLED=true` on Render and test all 5 gates
- Stripe end-to-end payment test (test card → webhook → Supabase subscription → premium unlock)

#### KEY FILES CHANGED
- `app.py` — 5 gating blocks added (lines 945-988)
- `config/settings.py` — Privacy/Terms links in footer
- `ui/welcome.py` — BETA banner removed (from Mar 9 session)

#### KEY COMMITS
- `bf14b16` — Privacy/Terms footer links
- `1e4c8dc` — Feature gating blocks (5 premium features)
- `ca5888a` — BETA banner + checkbox removal

#### FOR MARKETING AGENT
- Privacy Policy and Terms of Service now live — update any "coming soon" references
- Stripe integration complete — payment infrastructure ready for April 15 launch

---

---

### Session Summary — 2026-03-09
**Session:** Quick Estimate Feature Launch + Landing Page Redesign + BETA Removal

#### COMPLETED TODAY
- **Quick Estimate feature:** built and launched — frictionless entry with 8 client-side calculations
- **Landing page redesign (Lovable):** scrolling ticker countdown banner, TrustBanner, InvitationSection ("Complete access. Zero friction. Right now."), hero CTA updated
- **BETA removal:** removed yellow BETA banner from `ui/welcome.py` and `beta_agreement` checkbox gate from `app.py` (commit `ca5888a`)
- **Mobile fixes:** hero text overflow, CTA button wrap, phone mockup, wrong disclaimer bar removed
- **All confirmed working** on iPhone Safari and Android

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
