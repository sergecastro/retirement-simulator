# HANDOFF: December 18, 2025 - Frictionless Flow Debugging

## Session Summary

**Date:** December 18, 2025 (Late Night Session)
**Status:** CRITICAL BUG FOUND - Table Missing in Supabase
**Next Action:** Create `pending_intake` table, then test end-to-end

---

## What Was Accomplished

### 1. Root Cause Analysis Complete

We traced the frictionless flow bug through multiple layers:

| Step | Finding |
|------|---------|
| 1 | User clicks "Continue to Analysis" but lands on empty page |
| 2 | URL had `?mode=Analysis` instead of `?session=TEMP-XXX` |
| 3 | Two buttons existed: dropdown (wrong) vs main button (correct) |
| 4 | Lovable fixed: hid Analysis from dropdown, made button always visible |
| 5 | Still failing - Supabase insert error |
| 6 | Found: `session_id` column was VARCHAR(20), but ID was 21 chars |
| 7 | Lovable fixed: Changed column to VARCHAR(50) |
| 8 | Still failing - **TABLE DOESN'T EXIST** |

### 2. Final Root Cause

**The `pending_intake` table was never created in Supabase.**

```
APIError: Could not find the table 'public.pending_intake' in the schema cache
Code: PGRST205
```

This explains why:
- Lovable's insert fails silently
- Streamlit's `load_pending_intake()` fails
- User sees empty Analysis page

---

## The Frictionless Flow Architecture

### Expected Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LOVABLE INTAKE (intake.familyforecast.ai)                                   │
│                                                                              │
│  1. User fills QuickIntake form                                             │
│  2. Clicks "Continue to Analysis"                                           │
│  3. handleGoToAnalysis() called                                              │
│  4. saveToTempSession() called                                               │
│  5. Generates session ID: TEMP-XXXXXXXXXXXXXXXX (21 chars)                  │
│  6. INSERT into pending_intake table                                         │
│  7. Redirect to: ?session=TEMP-XXX&then=Analysis                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SUPABASE (pending_intake table)                                             │
│                                                                              │
│  session_id: TEMP-835QSQSK58F7Z9K2                                          │
│  intake_data: { userAge: 65, userIncome: 5000, ... }                        │
│  expires_at: NOW() + 24 hours                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STREAMLIT (app.familyforecast.ai)                                           │
│                                                                              │
│  app.py lines 357-399:                                                       │
│  1. Captures ?session=TEMP-XXX from URL                                      │
│  2. Calls load_pending_intake(session_id)                                    │
│  3. Fetches data from Supabase                                               │
│  4. Transforms data if needed (Lovable → Streamlit format)                  │
│  5. Loads into st.session_state                                              │
│  6. Routes to Analysis page                                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Critical Files

### Streamlit Side (This Repo)

| File | Purpose | Key Lines |
|------|---------|-----------|
| `app.py` | URL parameter handling | 357-399 (frictionless flow) |
| `utils/supabase_sync.py` | `load_pending_intake()` | 365-418 |
| `utils/supabase_sync.py` | `transform_lovable_to_streamlit()` | 152-350 |

### Lovable Side (External Repo)

| File | Purpose |
|------|---------|
| `src/pages/intake/QuickReview.tsx` | Review page with "Continue to Analysis" button |
| `src/components/ModuleDropdown.tsx` | Header dropdown (Analysis option hidden on QuickReview) |
| `src/utils/externalNavigation.ts` | URL generation for Streamlit |

---

## Bugs Fixed Tonight

### Bug 1: Wrong Button (Lovable)
- **Problem:** User clicking "More Modules → Analysis" instead of "Continue to Analysis"
- **Fix:** Hide Analysis from ModuleDropdown on QuickReview page
- **Status:** FIXED by Lovable

### Bug 2: Session ID Too Long (Lovable/Supabase)
- **Problem:** `session_id` column was VARCHAR(20), generated ID was 21 chars
- **Error:** `value too long for type character varying(20)`
- **Fix:** ALTER COLUMN to VARCHAR(50)
- **Status:** FIXED by Lovable

### Bug 3: Table Doesn't Exist (Supabase)
- **Problem:** `pending_intake` table was never created
- **Error:** `Could not find the table 'public.pending_intake'`
- **Fix:** Run CREATE TABLE script (see below)
- **Status:** NOT FIXED - DO THIS TOMORROW

---

## TOMORROW'S FIRST ACTION

### Step 1: Create the Table

Run this SQL in **Supabase SQL Editor**:

```sql
-- Create pending_intake table for frictionless flow
CREATE TABLE IF NOT EXISTS pending_intake (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    intake_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- Enable RLS
ALTER TABLE pending_intake ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (from Lovable)
CREATE POLICY "Allow anonymous insert" ON pending_intake
FOR INSERT TO anon
WITH CHECK (true);

-- Allow anonymous select (from Streamlit)
CREATE POLICY "Allow anonymous select" ON pending_intake
FOR SELECT TO anon
USING (true);

-- Allow anonymous delete (for cleanup)
CREATE POLICY "Allow anonymous delete" ON pending_intake
FOR DELETE TO anon
USING (true);

-- Create indexes for performance
CREATE INDEX idx_pending_intake_session_id ON pending_intake(session_id);
CREATE INDEX idx_pending_intake_expires_at ON pending_intake(expires_at);
```

### Step 2: Test End-to-End

1. Open incognito window
2. Go to: `https://intake.familyforecast.ai/intake/quick`
3. Fill minimal data (name, age, income)
4. Click "Continue to Review"
5. Click "Continue to Analysis"
6. **Expected:** Redirect to `https://app.familyforecast.ai?session=TEMP-XXX&then=Analysis`
7. **Expected:** Analysis page loads with data

### Step 3: Verify Data Format

If Analysis shows zeros, check data format. Run in Supabase:

```sql
SELECT session_id, intake_data FROM pending_intake ORDER BY created_at DESC LIMIT 1;
```

Check the keys in `intake_data`:
- If keys are `userAge`, `userIncome` → Need transform function
- If keys are `input_age`, `input_salary_wages` → Already correct
- If keys are `profile.name`, `income.salary.current` → Use existing transform

---

## Data Format Mapping (If Needed)

### Lovable QuickIntake Format (Likely)
```json
{
  "userAge": 65,
  "spouseAge": 62,
  "userIncome": 5000,
  "spouseIncome": 3000,
  "expenses": 4000,
  ...
}
```

### Streamlit Expected Format
```json
{
  "input_age": 65,
  "input_partner_age": 62,
  "input_salary_wages": 5000,
  "input_partner_salary": 3000,
  "input_total_expenses": 4000,
  ...
}
```

### If Transform Needed

Add to `utils/supabase_sync.py`:

```python
def transform_quick_intake_to_streamlit(quick_data: dict) -> dict:
    """
    Transform Lovable QuickIntake flat format to Streamlit format.
    QuickIntake uses: userAge, userIncome, etc.
    Streamlit uses: input_age, input_salary_wages, etc.
    """
    result = {}

    # Profile
    result['input_user_name'] = quick_data.get('planName', '')
    result['input_age'] = float(quick_data.get('userAge', 0))
    result['input_partner_exists'] = quick_data.get('spouseAge', 0) > 0
    result['input_partner_age'] = float(quick_data.get('spouseAge', 0))

    # Income
    result['input_salary_wages'] = float(quick_data.get('userIncome', 0))
    result['input_partner_salary'] = float(quick_data.get('spouseIncome', 0))

    # Expenses
    result['input_total_expenses'] = float(quick_data.get('expenses', 0))

    # Assets
    result['input_savings'] = float(quick_data.get('savings', 0))
    result['input_investments'] = float(quick_data.get('investments', 0))
    result['input_retirement_401k'] = float(quick_data.get('retirement', 0))

    # Retirement
    result['input_retirement_age'] = float(quick_data.get('retirementAge', 65))

    return result
```

Then update `load_pending_intake()` line ~404:

```python
# Check if this is Lovable FULL INTAKE format (nested with 'profile')
if 'profile' in intake_data:
    intake_data = transform_lovable_to_streamlit(intake_data)
# Check if this is Lovable QUICK INTAKE format (flat with 'userAge')
elif 'userAge' in intake_data:
    intake_data = transform_quick_intake_to_streamlit(intake_data)
```

---

## Commits Made Today

| Commit | Description |
|--------|-------------|
| `2e6d705` | FEATURE: Add frictionless flow for new users (pending_intake) |

This commit added:
- `load_pending_intake()` function
- `delete_pending_intake()` function
- `?session=TEMP-XXX` handler in app.py

---

## Session IDs to Test

| Session ID | Status |
|------------|--------|
| `TEMP-835QSQSK58F7Z9K2` | Created by Lovable, may have failed due to missing table |

After creating table, generate a fresh session ID by going through the flow.

---

## Contact Points

- **Streamlit issues:** Check this repo's `app.py` and `utils/supabase_sync.py`
- **Lovable issues:** External repo, communicate via handoff docs
- **Supabase issues:** Check SQL Editor and table policies

---

## Summary

**Tonight's Progress:**
1. Traced bug through entire stack (Lovable → Supabase → Streamlit)
2. Fixed wrong button issue (Lovable)
3. Fixed VARCHAR length issue (Supabase)
4. Discovered table missing (Supabase)

**Tomorrow's First Task:**
1. Create `pending_intake` table in Supabase
2. Test end-to-end flow
3. If data format wrong, add transform function

**Expected Result After Fix:**
- User completes QuickIntake
- Clicks "Continue to Analysis"
- Redirects to Streamlit with session ID
- Streamlit loads data from Supabase
- Analysis page shows user's data

---

*Document created: December 18, 2025, 11:59 PM PST*
*Next session: December 19, 2025*
