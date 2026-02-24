# Family Forecast — Project Context for Claude Code
*Last Updated: February 22, 2026*

---

## What This Is
Retirement planning SaaS (privacy-first, AES-256 encrypted) targeting pre-retirees 55-64.

**Three domains:**
- `familyforecast.ai` — Landing page (Lovable)
- `intake.familyforecast.ai` — INTAKE questionnaire (Lovable, same project as landing)
- `app.familyforecast.ai` — Analysis engine (Streamlit on Render)

---

## Architecture
- **Frontend:** Lovable (React) — Landing page + INTAKE merged into ONE Lovable project
- **Backend:** Streamlit Python app (~20 modules, ~19,500 lines)
- **Database:** External Supabase `ebhzvauommuhqlcswdil`
  - `pending_intake` table — anonymous vault transfers
  - `user_vaults` table — encrypted user data (email accounts)
  - `anonymous_vaults` table — anonymous vault storage
- **Encryption:** AES-256-GCM, PBKDF2 600K iterations, client-side only
- **Email:** Resend SMTP via `noreply@familyforecast.ai` (verified Feb 22 2026)
- **Hosting:** Render (Streamlit), Cloudflare (DNS), Lovable (React)

---

## Data Flow
```
User fills INTAKE (Lovable)
  → Encrypted in browser (AES-256)
  → Saved to Supabase user_vaults OR anonymous_vaults
  → Streamlit reads via URL param ?restore=cloud&vault_id=XXX
  → Decrypts → loads into session state → Analysis runs
```

---

## Key Files
| File | Purpose |
|------|---------|
| `app.py` | Main routing, URL params, session handler (lines 357-399) |
| `utils/supabase_sync.py` | `transform_lovable_to_streamlit()`, `load_pending_intake()` |
| `utils/encryption.py` | AES-256-GCM — DO NOT TOUCH |
| `utils/snapshot_manager.py` | localStorage + disk cache — handle carefully |
| `ui/intake_integrated.py` | INTAKE pages Quick/Full Mode |
| `ui/scenario_studio_page.py` | Scenario Studio (4th card) |
| `pages/social_security_optimizer.py` | SS Optimizer |
| `healthcare/medicare_irmaa_calculator.py` | IRMAA calculator (2026 CMS data) |
| `healthcare/medicare_data.py` | All Medicare data (updated to 2026) |

---

## Current Status — February 22, 2026

### ✅ FULLY WORKING
- Quick Mode end-to-end (desktop + mobile iPhone Safari)
- Full Mode end-to-end (desktop)
- Anonymous vault flow
- Email account creation + confirmation (Resend SMTP live)
- Data restore with password → Analysis loads correctly
- Anthropic AI API explanations (all modules)
- Medicare/IRMAA data updated to 2026 CMS rates
- All 6 modules deployed: INTAKE, Analysis, Healthcare Hub, Scenario Studio, SS Optimizer, History

### ⚠️ KNOWN BUGS (in progress)
- **Scenario Studio salary label:** `scenario_studio_page.py:535` shows monthly value under "Annual" label when `template_adjustments['salary_wages']` is pre-populated. Fix: ensure value is ×12 before display OR change label to Monthly.

### 📋 PENDING (next sessions)
- Scenario Studio salary label fix (in progress today)
- Debug console.log cleanup in Lovable (QuickReview.tsx)
- Landing page "Create Free Account" button full wiring
- Supabase test records cleanup
- Medicare Part D cost structure, Medicare Savings Programs, Extra Help → update to 2026 values in `healthcare/` folder
- Stripe payment integration
- Full Mode mobile test
- AI Enhancement: upgrade to full family financial analyst (conversational, context-aware)

---

## Critical Rules — NEVER BREAK THESE

1. **COMMIT before every change:**
   ```bash
   git add -A && git commit -m "Before [description] - [date]"
   ```
2. **SHOW git diff BEFORE committing** — wait for Serge approval
3. **NO truncation ever** — full files only
4. **One tiny step at a time** — one file, one function per change
5. **INVESTIGATE before modifying** — read first, report, then implement
6. **NEVER touch `utils/encryption.py`** without explicit approval
7. **Max 500 lines per file**
8. **"For Educational Purposes" disclaimer required**
9. **NEVER store API keys in claude.md or any committed file** — All API keys, secrets, and credentials must go in `.env` files ONLY. `.env` must always be in `.gitignore`. No exceptions.

---

## Mandatory Workflow
```
1. git commit (backup)
2. Investigate / read files
3. Show proposed change to Serge
4. Wait for "APPROVED"
5. Implement with str_replace (surgical edits)
6. Show git diff
7. Wait for Serge approval
8. Commit + push
```

---

## Testing Procedure
- Desktop: Chrome incognito
- Mobile: iPhone Safari (clear cache: Settings → Safari → Clear History and Website Data)
- Always test BOTH anonymous vault AND email registration flows
- Clean Supabase test records before new test runs

---

## Key Credentials (for reference)
- Supabase URL: `https://ebhzvauommuhqlcswdil.supabase.co`
- Resend API key / SMTP password: `REMOVED_SEE_ENV_FILE`
- SMTP host: `smtp.resend.com` / port: `465` / username: `resend`
- Sender: `noreply@familyforecast.ai`

---

## Local Dev Shortcuts
- Backup entry when cache has data: `http://localhost:8502/?restore=cloud`
- Check line counts: `wc -l filename.py`
- Find functions: `grep -n "def " filename.py | head -20`
- Find field references: `grep -rn "field_name" . --include="*.py"`

## 🤖 END OF SESSION — MANDATORY
At the end of every session, before closing, you MUST update the file `HANDOFF.md` 
in this same folder. Use the following structure:

- Update PROJECT ARCHITECTURE if anything changed (new files, agents, URLs, services)
- Write a LAST SESSION SUMMARY of what was done today
- Add any SIGNIFICANT CHANGES that changed direction
- Add a new PROGRESS MILESTONE with today's date and what was achieved
- Update STATUS (🟢 Active / 🟡 Paused / 🔴 Blocked)

Do this automatically. Do not ask for permission. Do not wait to be reminded.