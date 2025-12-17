# Lovable + Streamlit Integration Guide
## Family Forecast Architecture Documentation
**Created:** December 13, 2025
**Last Updated:** December 16, 2025
**Author:** Claude Code
**Purpose:** Complete reference for how Lovable apps integrate with Streamlit backend

> **IMPORTANT UPDATE (Dec 16, 2025):** Landing Page and INTAKE are now merged into a single Lovable project. The architecture diagrams below reflect this change.

---

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [The Two Apps](#2-the-two-apps) *(Updated: merged Lovable project)*
3. [User Flows](#3-user-flows)
4. [Encryption Parameters](#4-encryption-parameters) *(NEW)*
5. [URL Parameter System](#5-url-parameter-system)
6. [Data Transformer](#6-data-transformer) *(NEW)*
7. [Navigation Redirects](#7-navigation-redirects)
8. [Data Sharing Strategy](#8-data-sharing-strategy)
9. [File Reference](#9-file-reference)
10. [Future: Adding Lovable Analysis](#10-future-adding-lovable-analysis)
11. [Debugging Tips](#11-debugging-tips)
12. [Common Pitfalls](#12-common-pitfalls)

---

## 1. Architecture Overview

Family Forecast uses a **hybrid architecture** with two apps:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   LOVABLE (React/TypeScript) - MERGED PROJECT            │
│                   familyforecast.ai / intake.familyforecast.ai           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │   LANDING PAGE (/)              INTAKE (/intake)                    │ │
│  │   - Marketing                   - 6 pages of data collection        │ │
│  │   - "Open the App" button       - Password dialog on submit         │ │
│  │   - Returning user detection    - Client-side encryption            │ │
│  │   - Two buttons for returning:  - Saves encrypted data to Supabase  │ │
│  │     • "Go to Analysis"          - Redirects to Streamlit            │ │
│  │     • "Update My Info"                                              │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
              ?mode=Analysis  ?restore=cloud   /intake
              (new users)     &vault_id=XXX    (update info)
                              (returning)
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT (Python)                               │
│                         app.familyforecast.ai                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │   Analysis   │ │  Healthcare  │ │  Scenarios   │ │   History    │   │
│  │   (READ-ONLY │ │              │ │              │ │              │   │
│  │    inputs)   │ │  Medicare    │ │  What-if     │ │  Tracking    │   │
│  │  Monte Carlo │ │  IRMAA       │ │  Comparison  │ │  Over time   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│                                                                          │
│  + Social Security module (social_security)                              │
│  NOTE: All input fields in Analysis are DISABLED (disabled=True)         │
│        Users must go to Lovable INTAKE to edit data                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

1. **Lovable excels at**: Beautiful UI, forms, mobile-responsive design, fast iteration
2. **Streamlit excels at**: Data visualization, Monte Carlo simulations, complex calculations
3. **Result**: Best of both worlds - gorgeous INTAKE, powerful Analysis

### Key Architectural Decisions (Dec 16, 2025)

1. **Merged Lovable Project**: Landing Page + INTAKE are now ONE Lovable project
2. **No Lovable Decryption**: INTAKE cannot decrypt data (avoids double password prompt)
3. **Streamlit Read-Only**: Analysis input fields are disabled - edit only in INTAKE
4. **Data Transformer**: Streamlit transforms Lovable's nested format to flat format

---

## 2. The Two Apps

> **Note:** Previously "The Three Apps" - Landing and INTAKE merged Dec 16, 2025

### 2.1 Lovable (Landing + INTAKE) - MERGED
- **URLs:**
  - `https://familyforecast.ai` (Landing Page)
  - `https://intake.familyforecast.ai/intake` (INTAKE form)
- **Hosted on:** Lovable.dev (single project)
- **Purpose:** Marketing, user registration, data collection
- **Key features:**
  - Returning user detection via `ff_vault_id` or `ff_user_email` in localStorage
  - Two buttons for returning users: "Go to Analysis" and "Update My Info"
  - Client-side AES-256-GCM encryption before saving to Supabase

### 2.2 Streamlit App
- **URL:** `https://app.familyforecast.ai`
- **Hosted on:** Streamlit Cloud
- **Purpose:** Analysis, Healthcare, Scenarios, Social Security, History
- **Data storage:**
  - Session state (runtime)
  - localStorage (browser persistence)
  - Supabase (cloud backup)
- **Key features:**
  - Data transformer: converts Lovable format to Streamlit format
  - All INTAKE input fields are `disabled=True` (read-only)
  - Password prompt via restore modal for returning users

---

## 3. User Flows

### 3.1 New User Flow (Primary Path)
```
1. User visits familyforecast.ai (Landing)
2. Clicks "Open the App"
3. → Goes to /intake route (same Lovable project)
4. Completes 6 pages of data entry
5. Clicks "Continue to Analysis" → Password dialog appears
6. Enters password → Data encrypted client-side
7. → Redirected to app.familyforecast.ai?mode=Analysis&vault_id=XXX
8. Streamlit prompts for password, decrypts, transforms data
9. User sees results in Analysis mode
```

### 3.2 Returning User - Go to Analysis (Primary)
```
1. User visits familyforecast.ai (Landing)
2. Lovable detects returning user (ff_vault_id in localStorage)
3. Shows "Welcome back!" with two buttons
4. User clicks "Go to Analysis"
5. → Opens app.familyforecast.ai?restore=cloud&vault_id=XXX
6. Streamlit shows password prompt (restore modal)
7. User enters password, data decrypted from Supabase
8. → Goes directly to Analysis
```

### 3.3 Returning User - Update Info (Re-enter Data)
```
1. User visits familyforecast.ai (Landing)
2. Lovable detects returning user
3. Shows "Welcome back!" with two buttons
4. User clicks "Update My Info" (sees warning about re-entering data)
5. → Goes to /intake (EMPTY form - no decryption capability)
6. User re-enters all data
7. → Same as new user flow from step 5
```

**Note:** Update flow requires re-entering ALL data because:
- Lovable has NO decryption capability
- This avoids a double password prompt (once in Lovable, once in Streamlit)
- This is acceptable because data updates are rare

### 3.4 Navigation from Streamlit back to INTAKE
```
1. User is in Analysis/Healthcare/Scenarios
2. Clicks "My Information" in hamburger menu or sidebar
3. → Redirected to intake.familyforecast.ai/intake (Lovable INTAKE)
```

**Warning:** This sends user to empty INTAKE form (no data pre-filled)

---

## 4. Encryption Parameters

> **CRITICAL:** These parameters MUST match EXACTLY between Lovable and Streamlit. Verified working Dec 15, 2025.

### 4.1 Algorithm Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Algorithm** | AES-256-GCM | Authenticated encryption |
| **Key Derivation** | PBKDF2-SHA256 | Password-based |
| **Iterations** | 600,000 | High for security |
| **Salt Length** | 32 bytes | Generated per vault |
| **IV/Nonce Length** | 12 bytes | GCM standard |
| **Key Length** | 256 bits | AES-256 |

### 4.2 Lovable Implementation (src/lib/encryption.ts)

```javascript
// Configuration - MUST MATCH PYTHON EXACTLY
const PBKDF2_ITERATIONS = 600000;  // 600K iterations
const IV_LENGTH_BYTES = 12;        // 12 bytes / 96 bits (GCM standard)
const SALT_LENGTH_BYTES = 32;      // 32 bytes for salt

// Key derivation
const key = await crypto.subtle.deriveKey(
  {
    name: "PBKDF2",
    salt: saltBytes.buffer,
    iterations: PBKDF2_ITERATIONS,
    hash: "SHA-256",
  },
  keyMaterial,
  { name: "AES-GCM", length: 256 },
  false,
  ["encrypt"]
);
```

### 4.3 Streamlit Implementation (utils/password_crypto.py)

```python
ITERATIONS = 600_000  # MUST MATCH JAVASCRIPT
SALT_LENGTH = 32
NONCE_LENGTH = 12

# Key derivation
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt_bytes,
    iterations=ITERATIONS,
)
key = kdf.derive(password.encode('utf-8'))
```

### 4.4 Data Format (Base64 encoded)

```
[12 bytes nonce][encrypted data + GCM tag]
```

Both systems produce/consume identical format.

### 4.5 Salt Storage

- Salt is generated once per vault (when vault is created)
- Stored in Supabase `anonymous_vaults.salt` column (base64)
- Lovable READS existing salt for encryption (does NOT generate new)
- Streamlit READS same salt for decryption

---

## 5. URL Parameter System

### 5.1 The ?mode= Parameter

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

### 5.2 The ?restore=cloud Parameter (NEW Dec 16, 2025)

For returning users, Lovable uses a different URL pattern:

```
?restore=cloud&vault_id=FF-XXXX-XXXX
```

**Implementation in app.py (lines 333-368):**

```python
# =============================================================================
# CREDENTIAL PARAMS - Receive vault_id/email from Lovable via URL
# =============================================================================
# IMPORTANT: Must run BEFORE restore handler which clears all params
vault_param = st.query_params.get("vault_id")
email_param = st.query_params.get("email")

if vault_param or email_param:
    if vault_param:
        st.session_state['vault_id'] = vault_param
        write_local_storage('ff_vault_id', vault_param)
    if email_param:
        st.session_state['user_email'] = email_param
        write_local_storage('ff_user_email', email_param)
    st.session_state['_credentials_loaded'] = True

# =============================================================================
# RESTORE SHORTCUT - Go directly to cloud restore
# =============================================================================
# NOTE: Credential params captured ABOVE before we clear params here
if st.query_params.get("restore") == "cloud":
    st.session_state.show_backup_signup = 'restore'
    st.session_state['_force_welcome'] = True
    st.query_params.clear()  # Safe now - credentials already saved
    st.rerun()
```

**Critical:** Credential params MUST be captured BEFORE the restore handler clears them!

### 5.3 Why Clear Query Params?

`st.query_params.clear()` is called to:
1. Clean up the URL (looks better)
2. Prevent re-triggering on page refresh
3. Allow normal navigation afterward

---

## 6. Data Transformer

> **NEW Dec 16, 2025:** Converts Lovable's nested data format to Streamlit's flat format.

### 6.1 The Problem

Lovable and Streamlit use different data structures:

**Lovable (nested):**
```json
{
  "profile": { "name": "John", "birthYear": 1963 },
  "income": { "salary": { "current": 5000 } },
  "expenses": { "housing": 2000 }
}
```

**Streamlit (flat):**
```json
{
  "input_user_name": "John",
  "input_age": 62,
  "input_salary_wages": 5000,
  "input_housing_expenses": 2000
}
```

### 6.2 The Solution

**File:** `utils/supabase_sync.py`
**Function:** `transform_lovable_to_streamlit(lovable_data: dict) -> dict`

```python
def transform_lovable_to_streamlit(lovable_data: dict) -> dict:
    """
    Transform Lovable INTAKE nested format to Streamlit flat format.
    Called automatically when Lovable data is detected (has 'profile' key).
    """
    result = {}

    # Profile
    profile = lovable_data.get('profile', {})
    result['input_user_name'] = profile.get('name', '')
    # Calculate age from birthYear
    birth_year = profile.get('birthYear', 0)
    if birth_year:
        result['input_age'] = datetime.now().year - birth_year

    # Income (7 fields)
    income = lovable_data.get('income', {})
    result['input_salary_wages'] = income.get('salary', {}).get('current', 0)
    # ... more mappings

    # Mark as Lovable source
    result['_lovable_source'] = True

    return result
```

### 6.3 Automatic Detection

In `load_anonymous_vault()`:

```python
if 'profile' in decrypted_data:
    # Lovable format detected - transform it
    decrypted_data = transform_lovable_to_streamlit(decrypted_data)
```

### 6.4 Field Mappings (Summary)

| Category | Lovable Path | Streamlit Key |
|----------|--------------|---------------|
| Profile | `profile.name` | `input_user_name` |
| Profile | `profile.birthYear` | `input_age` (calculated) |
| Income | `income.salary.current` | `input_salary_wages` |
| Income | `income.socialSecurity.user` | `input_social_security` |
| Expenses | `expenses.housing` | `input_housing_expenses` |
| Assets | `assets.retirement.401k` | `input_401k_balance` |
| Liabilities | `liabilities.mortgage` | `input_mortgage_balance` |

Full mapping: ~50 fields across Profile, Income, Expenses, Assets, Liabilities, Children, Inheritances, Goals.

### 6.5 Diagnostic Tool

**File:** `tests/diagnose_vault.py`

```bash
python tests/diagnose_vault.py FF-XXXX-XXXX YourPassword
```

Shows:
- Raw encrypted data from Supabase
- Decrypted JSON structure
- Which Streamlit fields are present/missing

---

## 7. Navigation Redirects

### 7.1 The Redirect Pattern

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

### 7.2 All Redirect Locations (as of Dec 13, 2025)

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

### 7.3 Locations NOT Redirected (Intentionally)

| File | Location | Why Not Redirected |
|------|----------|-------------------|
| `ui/welcome.py` | "Continue My Plan" button | Legacy localStorage users (currently non-existent, marketing paused) |
| `ui/cloud_backup_modal.py` | After backup signup | User already completed INTAKE, goes to Analysis |
| `ui/welcome.py` | Restore form success | User has data, goes to Analysis |

---

## 8. Data Sharing Strategy

### 8.1 The localStorage Problem

**Critical limitation:** localStorage is origin-specific.
- `intake.familyforecast.ai` has its OWN localStorage
- `app.familyforecast.ai` has its OWN localStorage
- They CANNOT share localStorage directly!

### 8.2 Solution: Supabase as Bridge

```
┌──────────────────┐         ┌──────────────┐         ┌──────────────────┐
│  Lovable INTAKE  │──save──▶│   SUPABASE   │◀──load──│  Streamlit App   │
│                  │         │              │         │                  │
│  intake.ff.ai    │         │  - Encrypted │         │  app.ff.ai       │
│                  │         │  - user_data │         │                  │
└──────────────────┘         │  - vaults    │         └──────────────────┘
                             └──────────────┘
```

### 8.3 Data Flow Details

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

### 8.4 Key Session State Variables

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

### 8.5 localStorage Keys (Streamlit side)

```javascript
ff_user_email    // User's email (account users)
ff_vault_id      // Vault ID (anonymous users)
ff_intake_data   // Encrypted intake data (legacy, being phased out)
ff_last_visit    // Timestamp of last visit
ff_user_name     // User's name (for "Welcome back" message)
```

---

## 9. File Reference

### 9.1 Core Navigation Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit app, mode routing, URL param handling |
| `ui/components/top_navigation.py` | Hamburger menu component |
| `ui/welcome.py` | Welcome page, signup forms, returning user detection |
| `ui/cloud_backup_modal.py` | Backup signup modal (shown after INTAKE) |

### 9.2 Module Pages

| File | Module |
|------|--------|
| `ui/results_page.py` | Analysis (Monte Carlo results) |
| `ui/healthcare_page.py` | Healthcare/Medicare |
| `ui/scenario_studio_page.py` | Scenarios (what-if) |
| `ui/social_security_page.py` | Social Security |
| `ui/historical_tracking.py` | History |

### 9.3 Data/Sync Files

| File | Purpose |
|------|---------|
| `utils/supabase_sync.py` | All Supabase operations (save, load, encrypt, decrypt) + transform_lovable_to_streamlit() |
| `utils/safe_local_storage.py` | Safe localStorage read (with polling) |
| `utils/password_crypto.py` | AES-256-GCM encryption/decryption |
| `utils/cookie_helper.py` | Returning user detection |
| `simulation/simulation_core.py` | Monte Carlo simulation engine |
| `tests/diagnose_vault.py` | Vault diagnostic tool (NEW Dec 16) |

---

## 10. Future: Adding Lovable Analysis

When you rebuild Analysis in Lovable, here's what to consider:

### 10.1 Option A: Full Lovable (Recommended for Display)

**For display-only results:**
```
Lovable INTAKE → Supabase → Streamlit (runs simulation, saves results) → Supabase → Lovable Analysis (displays)
```

**Pros:** Beautiful charts, responsive design
**Cons:** Need to run simulation somewhere (Streamlit API? Cloud function?)

### 10.2 Option B: Hybrid (Keep Streamlit for Calculation)

**For interactive scenarios:**
```
Lovable INTAKE → Supabase → Streamlit Analysis (calculate + display)
```

Then later add Lovable display layer that fetches pre-calculated results.

### 10.3 Key Considerations

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

### 10.4 Migration Path

1. **Phase 1 (Current):** Lovable INTAKE + Streamlit Analysis ✅
2. **Phase 2:** Add Lovable display for static results (view-only)
3. **Phase 3:** Move simulation to API endpoint
4. **Phase 4:** Full Lovable Analysis with real-time updates

### 10.5 URL Patterns for Lovable Analysis

```
# View specific scenario
https://analysis.familyforecast.ai/results?scenario_id=abc123

# View user's scenarios
https://analysis.familyforecast.ai/scenarios?user_id=xyz

# Direct from INTAKE
https://analysis.familyforecast.ai/results?intake_id=xxx&run_simulation=true
```

---

## 11. Debugging Tips

### 11.1 Check Which App You're On

```
familyforecast.ai        → Lovable Landing (check Lovable dashboard)
intake.familyforecast.ai → Lovable INTAKE (check Lovable dashboard)
app.familyforecast.ai    → Streamlit (check Streamlit Cloud logs)
```

### 11.2 Streamlit Debug Prints

The codebase has debug prints (search for `print(` or `🔥` or `🔐`):
```python
print(f"🔥 WELCOME REGISTRATION: user_email SET TO: {st.session_state.user_email}")
print(f"🔐 RESTORE MODAL: SET cloud_password (len={len(password)})")
```

View these in Streamlit Cloud logs or local terminal.

### 11.3 Common Issues

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

**"Data shows all zeros after restore"** (NEW Dec 16)
- Check: Was Lovable format detected? Look for `'profile' in decrypted_data`
- Check: Is `transform_lovable_to_streamlit()` being called?
- Use: `python tests/diagnose_vault.py FF-XXXX-XXXX password` to inspect data

### 11.4 Lovable → Streamlit Data Flow Debug

1. In Lovable INTAKE, after save, log the user_id/vault_id
2. Check Supabase dashboard for the record (`anonymous_vaults` table)
3. Verify `encrypted_data` column is NOT empty
4. In Streamlit, check if localStorage has the credentials
5. Check if `load_anonymous_vault()` is being called
6. Check if data transformation is triggered (look for `'profile' in data`)
7. Check if `st.session_state.intake_data` is populated

---

## 12. Common Pitfalls

### 12.1 localStorage Across Subdomains

**WRONG assumption:** "They share localStorage"
**REALITY:** Each subdomain has isolated localStorage

**Solution:** Use Supabase as the data bridge.

### 12.2 Forgetting st.stop()

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

### 12.3 Query Params Not Clearing

If you don't clear query params:
```python
st.query_params.clear()
```
The mode will re-trigger on every rerun, causing navigation loops.

### 12.4 Credential Params Cleared Too Early (Dec 16, 2025)

**WRONG:** Clearing params before capturing credentials
```python
if st.query_params.get("restore") == "cloud":
    st.query_params.clear()  # Loses vault_id!
    st.rerun()

vault_param = st.query_params.get("vault_id")  # Always None!
```

**RIGHT:** Capture credentials BEFORE clearing
```python
vault_param = st.query_params.get("vault_id")
if vault_param:
    st.session_state['vault_id'] = vault_param  # Save first!

if st.query_params.get("restore") == "cloud":
    st.query_params.clear()  # Now safe to clear
    st.rerun()
```

### 12.5 Hardcoded URLs

**Current hardcoded URLs:**
- `https://intake.familyforecast.ai/intake` (8+ locations)
- `https://app.familyforecast.ai` (in Lovable apps)

**Suggestion for future:** Create a config file:
```python
# config/urls.py
LOVABLE_INTAKE_URL = "https://intake.familyforecast.ai/intake"
STREAMLIT_APP_URL = "https://app.familyforecast.ai"
```

### 12.6 Mobile Sidebar Hidden

The sidebar is hidden on mobile (see `MOBILE_SIDEBAR_CSS` in app.py).
Users navigate via hamburger menu (`top_navigation.py`) on mobile.

### 12.7 The "or" vs "and" Bug (Dec 5, 2025)

In `safe_local_storage.py`, there was a bug:
```python
# WRONG: Required BOTH email AND vault
if ff_user_email == 0 or ff_vault_id == 0:

# RIGHT: Wait only if BOTH are still pending
if ff_user_email == 0 and ff_vault_id == 0:
```

Lesson: Users may have email OR vault, not both.

### 12.8 Encryption Parameter Mismatch

**CRITICAL:** Lovable and Streamlit MUST use identical encryption parameters.

| Parameter | Correct Value |
|-----------|---------------|
| PBKDF2 Iterations | 600,000 |
| Salt Length | 32 bytes |
| IV/Nonce Length | 12 bytes |
| Algorithm | AES-256-GCM |

If either side changes these values, decryption will fail silently (garbage output or wrong data).

---

## Appendix A: Git Commits Reference

Key commits for this integration:

```
# December 2025 - Lovable Integration
cf52f93 FEATURE: Add Lovable-to-Streamlit data transformer - Dec 16 2025
33fc846 FIX: Capture vault_id/email BEFORE clearing params in restore flow
0c17683 FEATURE: Lovable welcome flow + Mobile CSS contrast fix - Dec 16 2025
b4291a1 Architecture D implementation - Crypto test passed - Dec 15 2025

# Earlier commits
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
    salt,            -- 32 bytes base64 (NEW)
    created_at,
    updated_at
)

-- Anonymous vaults
anonymous_vaults (
    vault_id,        -- Format: FF-XXXX-XXXX
    encrypted_data,  -- AES-256-GCM encrypted JSON (nonce + ciphertext)
    salt,            -- 32 bytes base64 for PBKDF2
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
│ Landing + INTAKE: familyforecast.ai (MERGED Lovable project)│
│ INTAKE Route:     /intake                                   │
│ App (Streamlit):  app.familyforecast.ai                     │
├─────────────────────────────────────────────────────────────┤
│ New User:         ?mode=Analysis&vault_id=XXX               │
│ Returning User:   ?restore=cloud&vault_id=XXX               │
│ Data Bridge:      Supabase (encrypted)                      │
│ Auth:             ff_user_email OR ff_vault_id              │
├─────────────────────────────────────────────────────────────┤
│ Encryption:       AES-256-GCM, PBKDF2-SHA256, 600K iter     │
│ Salt:             32 bytes, stored in Supabase              │
│ Nonce:            12 bytes, prepended to ciphertext         │
├─────────────────────────────────────────────────────────────┤
│ Key Files:                                                  │
│   app.py                 - Main routing, URL params         │
│   ui/welcome.py          - Signup forms, Lovable welcome    │
│   utils/supabase_sync.py - Data sync + transformer          │
│   utils/password_crypto.py - Encryption/decryption          │
│   tests/diagnose_vault.py - Vault debugging tool            │
└─────────────────────────────────────────────────────────────┘
```

---

## Appendix D: Lovable Code Reference

Key files in Lovable project (for reference):

| File | Purpose |
|------|---------|
| `src/lib/encryption.ts` | AES-256-GCM encryption (Web Crypto API) |
| `src/lib/supabase.ts` | Supabase client configuration |
| `src/contexts/RegistrationContext.tsx` | Returning user detection + buttons |
| `IntakeReview.tsx` | Password dialog on submit |

---

**Document maintained by:** Development Team
**Last updated:** December 16, 2025
**Next review:** When adding Lovable Analysis module
