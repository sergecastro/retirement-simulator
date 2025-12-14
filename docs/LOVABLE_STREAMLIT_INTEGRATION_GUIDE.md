# Lovable + Streamlit Integration Guide
## Family Forecast Architecture Documentation
**Created:** December 13, 2025
**Author:** Claude Code
**Purpose:** Complete reference for how Lovable apps integrate with Streamlit backend

---

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [The Three Apps](#2-the-three-apps)
3. [User Flows](#3-user-flows)
4. [URL Parameter System](#4-url-parameter-system)
5. [Navigation Redirects](#5-navigation-redirects)
6. [Data Sharing Strategy](#6-data-sharing-strategy)
7. [File Reference](#7-file-reference)
8. [Future: Adding Lovable Analysis](#8-future-adding-lovable-analysis)
9. [Debugging Tips](#9-debugging-tips)
10. [Common Pitfalls](#10-common-pitfalls)

---

## 1. Architecture Overview

Family Forecast uses a **hybrid architecture** with two frontend technologies:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LOVABLE (React/TypeScript)                       │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────┐ │
│  │   LANDING PAGE          │    │   INTAKE                            │ │
│  │   familyforecast.ai     │───▶│   intake.familyforecast.ai/intake   │ │
│  │                         │    │                                     │ │
│  │   - Marketing           │    │   - 6 pages of data collection      │ │
│  │   - "Open the App"      │    │   - Saves to Supabase               │ │
│  │   - Testimonials        │    │   - "Continue to Analysis" button   │ │
│  └─────────────────────────┘    └──────────────────┬──────────────────┘ │
└────────────────────────────────────────────────────┼────────────────────┘
                                                     │
                                                     ▼ ?mode=Analysis
┌─────────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT (Python)                               │
│                         app.familyforecast.ai                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │   Analysis   │ │  Healthcare  │ │  Scenarios   │ │   History    │   │
│  │              │ │              │ │              │ │              │   │
│  │  Monte Carlo │ │  Medicare    │ │  What-if     │ │  Tracking    │   │
│  │  Simulation  │ │  IRMAA       │ │  Comparison  │ │  Over time   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│                                                                          │
│  + Social Security module (social_security)                              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

1. **Lovable excels at**: Beautiful UI, forms, mobile-responsive design, fast iteration
2. **Streamlit excels at**: Data visualization, Monte Carlo simulations, complex calculations
3. **Result**: Best of both worlds - gorgeous INTAKE, powerful Analysis

---

## 2. The Three Apps

### 2.1 Landing Page (Lovable)
- **URL:** `https://familyforecast.ai`
- **Hosted on:** Lovable.dev
- **Purpose:** Marketing, first impression, call-to-action
- **Key button:** "Open the App" → redirects to INTAKE

### 2.2 INTAKE (Lovable)
- **URL:** `https://intake.familyforecast.ai/intake`
- **Hosted on:** Lovable.dev (separate project from landing page)
- **Purpose:** Collect user financial data across 6 pages
- **Data storage:** Supabase (encrypted)
- **Key button:** "Continue to Analysis" → redirects to Streamlit with `?mode=Analysis`

### 2.3 Streamlit App
- **URL:** `https://app.familyforecast.ai`
- **Hosted on:** Streamlit Cloud (or your server)
- **Purpose:** Analysis, Healthcare, Scenarios, Social Security, History
- **Data storage:**
  - Session state (runtime)
  - localStorage (browser persistence)
  - Supabase (cloud backup)

---

## 3. User Flows

### 3.1 New User Flow (Primary Path)
```
1. User visits familyforecast.ai (Landing)
2. Clicks "Open the App"
3. → Redirected to intake.familyforecast.ai/intake (Lovable INTAKE)
4. Completes 6 pages of data entry
5. Clicks "Continue to Analysis"
6. → Redirected to app.familyforecast.ai?mode=Analysis (Streamlit)
7. Streamlit loads data from Supabase, runs simulation
8. User sees results in Analysis mode
```

### 3.2 Returning User with Cloud Backup
```
1. User visits app.familyforecast.ai directly
2. Streamlit reads ff_vault_id or ff_user_email from localStorage
3. Shows "Welcome back! Restore My Plan?" prompt
4. User clicks "Restore My Plan"
5. Enters password, data decrypted from Supabase
6. → Goes directly to Analysis (data already exists)
```

### 3.3 New User Creating Account at Welcome Page
```
1. User visits app.familyforecast.ai directly
2. Sees welcome page with signup options
3. Clicks "Create Free Account" or "Try Anonymous"
4. Fills form, account/vault created in Supabase
5. → Redirected to intake.familyforecast.ai/intake (Lovable INTAKE)
6. Completes INTAKE, continues to Analysis
```

### 3.4 Navigation from Streamlit back to INTAKE
```
1. User is in Analysis/Healthcare/Scenarios
2. Clicks "My Information" in hamburger menu or sidebar
3. → Redirected to intake.familyforecast.ai/intake (Lovable INTAKE)
```

---

## 4. URL Parameter System

### 4.1 The ?mode= Parameter

Streamlit accepts a `mode` query parameter for direct navigation from external apps:

**Valid modes:**
- `?mode=Analysis` - Monte Carlo simulation results
- `?mode=Healthcare` - Medicare/IRMAA calculations
- `?mode=scenario_studio` - What-if scenarios
- `?mode=social_security` - SS optimization
- `?mode=historical_tracking` - History over time
- `?mode=INTAKE` - (Legacy, now redirects to Lovable)

**Implementation in app.py (lines 345-356):**
```python
# MODE SHORTCUT - Direct navigation from external apps (Lovable)
mode_param = st.query_params.get("mode")
if mode_param and mode_param in ["INTAKE", "Analysis", "Healthcare", "scenario_studio", "social_security", "historical_tracking"]:
    st.session_state.mode_selected = True
    st.session_state.current_mode = mode_param
    st.session_state["beta_agreement"] = True
    st.query_params.clear()  # Clean URL after processing
    st.rerun()
```

### 4.2 Why Clear Query Params?

`st.query_params.clear()` is called to:
1. Clean up the URL (looks better)
2. Prevent re-triggering on page refresh
3. Allow normal navigation afterward

### 4.3 Future: Passing Data via URL

For Lovable Analysis, consider:
```
?mode=Analysis&scenario_id=abc123
```

Then Streamlit/Lovable can fetch that specific scenario from Supabase.

---

## 5. Navigation Redirects

### 5.1 The Redirect Pattern

All INTAKE redirects use this pattern:
```python
st.markdown(
    '<meta http-equiv="refresh" content="0;url=https://intake.familyforecast.ai/intake">',
    unsafe_allow_html=True
)
st.stop()
```

**Key points:**
- `content="0"` = instant redirect
- `content="1"` = 1 second delay (used after success messages)
- `st.stop()` = CRITICAL - prevents further Streamlit execution

### 5.2 All Redirect Locations (as of Dec 13, 2025)

| File | Function/Location | Redirect To |
|------|-------------------|-------------|
| `ui/components/top_navigation.py` | Hamburger menu "My Information" | Lovable INTAKE |
| `app.py` (line ~545) | Analysis sidebar radio "My Information" | Lovable INTAKE |
| `app.py` (line ~915) | Healthcare sidebar radio "My Information" | Lovable INTAKE |
| `ui/results_page.py` (line ~291) | "Go to INTAKE" button (demo mode) | Lovable INTAKE |
| `ui/scenario_studio_page.py` (line ~314) | "Go to INTAKE" button | Lovable INTAKE |
| `ui/scenario_studio_page.py` (line ~329) | "Go to INTAKE" button | Lovable INTAKE |
| `ui/welcome.py` (line ~269) | Account signup success | Lovable INTAKE |
| `ui/welcome.py` (line ~345) | Vault signup success | Lovable INTAKE |

### 5.3 Locations NOT Redirected (Intentionally)

| File | Location | Why Not Redirected |
|------|----------|-------------------|
| `ui/welcome.py` | "Continue My Plan" button | Legacy localStorage users (currently non-existent, marketing paused) |
| `ui/cloud_backup_modal.py` | After backup signup | User already completed INTAKE, goes to Analysis |
| `ui/welcome.py` | Restore form success | User has data, goes to Analysis |

---

## 6. Data Sharing Strategy

### 6.1 The localStorage Problem

**Critical limitation:** localStorage is origin-specific.
- `intake.familyforecast.ai` has its OWN localStorage
- `app.familyforecast.ai` has its OWN localStorage
- They CANNOT share localStorage directly!

### 6.2 Solution: Supabase as Bridge

```
┌──────────────────┐         ┌──────────────┐         ┌──────────────────┐
│  Lovable INTAKE  │──save──▶│   SUPABASE   │◀──load──│  Streamlit App   │
│                  │         │              │         │                  │
│  intake.ff.ai    │         │  - Encrypted │         │  app.ff.ai       │
│                  │         │  - user_data │         │                  │
└──────────────────┘         │  - vaults    │         └──────────────────┘
                             └──────────────┘
```

### 6.3 Data Flow Details

**Lovable INTAKE saves to Supabase:**
- User completes INTAKE pages
- Data encrypted with AES-256-GCM (user's password as key)
- Saved to Supabase `user_data` or `anonymous_vaults` table
- User gets `user_email` or `vault_id` identifier

**Streamlit loads from Supabase:**
- Reads `ff_user_email` or `ff_vault_id` from localStorage
- Prompts for password (if not in session)
- Fetches encrypted blob from Supabase
- Decrypts with password
- Loads into `st.session_state.intake_data`

### 6.4 Key Session State Variables

```python
# User identification
st.session_state.user_email      # Email for account users
st.session_state.vault_id        # Vault ID for anonymous users
st.session_state.cloud_password  # Decryption key (session only, never stored)

# Data
st.session_state.intake_data     # Dict with all INTAKE fields

# Navigation
st.session_state.current_mode    # "Analysis", "Healthcare", etc.
st.session_state.mode_selected   # True when user has chosen a mode
st.session_state.beta_agreement  # True when user accepted terms
```

### 6.5 localStorage Keys (Streamlit side)

```javascript
ff_user_email    // User's email (account users)
ff_vault_id      // Vault ID (anonymous users)
ff_intake_data   // Encrypted intake data (legacy, being phased out)
ff_last_visit    // Timestamp of last visit
ff_user_name     // User's name (for "Welcome back" message)
```

---

## 7. File Reference

### 7.1 Core Navigation Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit app, mode routing, URL param handling |
| `ui/components/top_navigation.py` | Hamburger menu component |
| `ui/welcome.py` | Welcome page, signup forms, returning user detection |
| `ui/cloud_backup_modal.py` | Backup signup modal (shown after INTAKE) |

### 7.2 Module Pages

| File | Module |
|------|--------|
| `ui/results_page.py` | Analysis (Monte Carlo results) |
| `ui/healthcare_page.py` | Healthcare/Medicare |
| `ui/scenario_studio_page.py` | Scenarios (what-if) |
| `ui/social_security_page.py` | Social Security |
| `ui/historical_tracking.py` | History |

### 7.3 Data/Sync Files

| File | Purpose |
|------|---------|
| `utils/supabase_sync.py` | All Supabase operations (save, load, encrypt, decrypt) |
| `utils/safe_local_storage.py` | Safe localStorage read (with polling) |
| `utils/cookie_helper.py` | Returning user detection |
| `simulation/simulation_core.py` | Monte Carlo simulation engine |

---

## 8. Future: Adding Lovable Analysis

When you rebuild Analysis in Lovable, here's what to consider:

### 8.1 Option A: Full Lovable (Recommended for Display)

**For display-only results:**
```
Lovable INTAKE → Supabase → Streamlit (runs simulation, saves results) → Supabase → Lovable Analysis (displays)
```

**Pros:** Beautiful charts, responsive design
**Cons:** Need to run simulation somewhere (Streamlit API? Cloud function?)

### 8.2 Option B: Hybrid (Keep Streamlit for Calculation)

**For interactive scenarios:**
```
Lovable INTAKE → Supabase → Streamlit Analysis (calculate + display)
```

Then later add Lovable display layer that fetches pre-calculated results.

### 8.3 Key Considerations

1. **Simulation Engine:**
   - `simulation/simulation_core.py` runs 1000+ Monte Carlo iterations
   - CPU-intensive, takes 2-5 seconds
   - Options: Keep in Streamlit, move to Supabase Edge Function, or Python API

2. **Chart Libraries:**
   - Streamlit uses Plotly (via `st.plotly_chart`)
   - Lovable can use Recharts, Chart.js, or Plotly.js
   - Consider: Can you replicate the charts?

3. **Session Data:**
   - Streamlit stores scenario results in `st.session_state`
   - For Lovable: Store results in Supabase, fetch by scenario_id

4. **Real-time Updates:**
   - Streamlit: Slider changes → instant recalculation
   - Lovable: Would need API call for each change (latency concern)

### 8.4 Migration Path

1. **Phase 1 (Current):** Lovable INTAKE + Streamlit Analysis ✅
2. **Phase 2:** Add Lovable display for static results (view-only)
3. **Phase 3:** Move simulation to API endpoint
4. **Phase 4:** Full Lovable Analysis with real-time updates

### 8.5 URL Patterns for Lovable Analysis

```
# View specific scenario
https://analysis.familyforecast.ai/results?scenario_id=abc123

# View user's scenarios
https://analysis.familyforecast.ai/scenarios?user_id=xyz

# Direct from INTAKE
https://analysis.familyforecast.ai/results?intake_id=xxx&run_simulation=true
```

---

## 9. Debugging Tips

### 9.1 Check Which App You're On

```
familyforecast.ai        → Lovable Landing (check Lovable dashboard)
intake.familyforecast.ai → Lovable INTAKE (check Lovable dashboard)
app.familyforecast.ai    → Streamlit (check Streamlit Cloud logs)
```

### 9.2 Streamlit Debug Prints

The codebase has debug prints (search for `print(` or `🔥` or `🔐`):
```python
print(f"🔥 WELCOME REGISTRATION: user_email SET TO: {st.session_state.user_email}")
print(f"🔐 RESTORE MODAL: SET cloud_password (len={len(password)})")
```

View these in Streamlit Cloud logs or local terminal.

### 9.3 Common Issues

**"Redirect not working"**
- Check: Is `st.stop()` called after the meta refresh?
- Check: Is the URL correct? (https, correct subdomain)

**"Data not loading in Streamlit"**
- Check: Is `ff_vault_id` or `ff_user_email` in localStorage?
- Check: Is the password correct?
- Check: Supabase connection (check `utils/supabase_sync.py`)

**"User stuck in wrong mode"**
- Check: `st.session_state.current_mode` value
- Check: `st.session_state.mode_selected` is True

### 9.4 Lovable → Streamlit Data Flow Debug

1. In Lovable INTAKE, after save, log the user_id/vault_id
2. Check Supabase dashboard for the record
3. In Streamlit, check if localStorage has the credentials
4. Check if `load_from_supabase()` is being called
5. Check if `st.session_state.intake_data` is populated

---

## 10. Common Pitfalls

### 10.1 localStorage Across Subdomains

**WRONG assumption:** "They share localStorage"
**REALITY:** Each subdomain has isolated localStorage

**Solution:** Use Supabase as the data bridge.

### 10.2 Forgetting st.stop()

**WRONG:**
```python
st.markdown('<meta http-equiv="refresh" content="0;url=...">', unsafe_allow_html=True)
# Streamlit continues executing, causes issues
```

**RIGHT:**
```python
st.markdown('<meta http-equiv="refresh" content="0;url=...">', unsafe_allow_html=True)
st.stop()  # CRITICAL!
```

### 10.3 Query Params Not Clearing

If you don't clear query params:
```python
st.query_params.clear()
```
The mode will re-trigger on every rerun, causing navigation loops.

### 10.4 Hardcoded URLs

**Current hardcoded URLs:**
- `https://intake.familyforecast.ai/intake` (8+ locations)
- `https://app.familyforecast.ai` (in Lovable apps)

**Suggestion for future:** Create a config file:
```python
# config/urls.py
LOVABLE_INTAKE_URL = "https://intake.familyforecast.ai/intake"
STREAMLIT_APP_URL = "https://app.familyforecast.ai"
```

### 10.5 Mobile Sidebar Hidden

The sidebar is hidden on mobile (see `MOBILE_SIDEBAR_CSS` in app.py).
Users navigate via hamburger menu (`top_navigation.py`) on mobile.

### 10.6 The "or" vs "and" Bug (Dec 5, 2025)

In `safe_local_storage.py`, there was a bug:
```python
# WRONG: Required BOTH email AND vault
if ff_user_email == 0 or ff_vault_id == 0:

# RIGHT: Wait only if BOTH are still pending
if ff_user_email == 0 and ff_vault_id == 0:
```

Lesson: Users may have email OR vault, not both.

---

## Appendix A: Git Commits Reference

Key commits for this integration:

```
8c73d47 FIX: Redirect signup forms to Lovable INTAKE instead of Streamlit
e7b3e44 FEATURE: Redirect 'My Information' navigation to Lovable INTAKE
fc1a524 FEATURE: Add ?mode= URL parameter for external app navigation
```

---

## Appendix B: Supabase Tables

```sql
-- User accounts (email signup)
user_data (
    id,
    email,
    encrypted_data,  -- AES-256-GCM encrypted JSON
    created_at,
    updated_at
)

-- Anonymous vaults
anonymous_vaults (
    vault_id,        -- Format: FF-XXXX-XXXX
    encrypted_data,  -- AES-256-GCM encrypted JSON
    created_at,
    expires_at,      -- 30 days from creation
    scenario_count   -- Max 3 for anonymous
)
```

---

## Appendix C: Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    QUICK REFERENCE                          │
├─────────────────────────────────────────────────────────────┤
│ Landing Page:     familyforecast.ai                         │
│ INTAKE (Lovable): intake.familyforecast.ai/intake           │
│ App (Streamlit):  app.familyforecast.ai                     │
├─────────────────────────────────────────────────────────────┤
│ URL Param:        ?mode=Analysis (or Healthcare, etc.)      │
│ Data Bridge:      Supabase (encrypted)                      │
│ Auth:             ff_user_email OR ff_vault_id              │
├─────────────────────────────────────────────────────────────┤
│ Redirect Pattern:                                           │
│   st.markdown('<meta http-equiv="refresh" ...>')            │
│   st.stop()  # DON'T FORGET!                                │
├─────────────────────────────────────────────────────────────┤
│ Key Files:                                                  │
│   app.py                 - Main routing                     │
│   ui/welcome.py          - Signup forms                     │
│   top_navigation.py      - Hamburger menu                   │
│   utils/supabase_sync.py - Data sync                        │
└─────────────────────────────────────────────────────────────┘
```

---

**Document maintained by:** Development Team
**Last updated:** December 13, 2025
**Next review:** When adding Lovable Analysis module
