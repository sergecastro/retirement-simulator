# Troubleshooting Guide - November 28, 2025
## Family Forecast Retirement Planner - Critical Bug Fixes

**Session Duration:** ~8 hours
**Issues Resolved:** 12 major bugs
**Files Modified:** 15+ files

---

## Table of Contents
1. [4-Second Automatic Rerun Loop](#1-4-second-automatic-rerun-loop)
2. [Data Vanishing After 90 Seconds](#2-data-vanishing-after-90-seconds)
3. [Widget Key Collision Errors](#3-widget-key-collision-errors)
4. [Dangerous session_state Loops](#4-dangerous-session_state-loops)
5. [Age None Comparison Error](#5-age-none-comparison-error)
6. [Empty Else Block Syntax Errors](#6-empty-else-block-syntax-errors)
7. [Sidebar Pages Menu Showing](#7-sidebar-pages-menu-showing)
8. [BETA Mode Hidden for Launch](#8-beta-mode-hidden-for-launch)
9. [Debug Print Statements Cleanup](#9-debug-print-statements-cleanup)

---

## 1. 4-Second Automatic Rerun Loop

### Symptom
- App constantly rerunning every 4-5 seconds automatically
- Flickering, constant page refreshes
- Users couldn't interact with the app

### Root Cause
The `streamlit-browser-storage` package's `LocalStorage` component uses bidirectional JavaScript communication that polls every ~4 seconds, triggering Streamlit reruns.

**The mere IMPORT of the component caused reruns, even if not used!**

### Solution
Comment out all imports of `LocalStorage` from `streamlit_browser_storage`:

**Files Modified:**
- `utils/snapshot_manager.py`
- `utils/comparison_scenarios.py`
- `utils/historical_snapshots.py`

**Before:**
```python
from streamlit_browser_storage import LocalStorage
```

**After:**
```python
# DISABLED: from streamlit_browser_storage import LocalStorage
```

Also disabled the `_get_local_storage()` functions:
```python
@st.cache_resource
def _get_local_storage():
    # ========== TEMPORARY DEBUG: DISABLED TO FIND RERUN SOURCE ==========
    print("[DEBUG] _get_local_storage DISABLED")
    return None
```

### Future Fix (POST-LAUNCH)
Use `streamlit-javascript` package instead:
```python
from streamlit_js_eval import streamlit_js_eval
value = streamlit_js_eval("localStorage.getItem('key')")
```
This provides localStorage access WITHOUT polling/reruns.

---

## 2. Data Vanishing After 90 Seconds

### Symptom
- User enters data on Page 5 (Assets)
- Navigates to Page 6 (Liabilities)
- After ~90 seconds idle, returns to Page 5
- All data is GONE (reset to 0)
- Session ID stays the same (not a session recreation issue)

### Root Cause
**Streamlit garbage collects widget keys that aren't currently rendered.**

When a widget has `key="input_ira_balance"`, Streamlit stores the value in `st.session_state['input_ira_balance']`. But when that widget is NOT rendered (user is on a different page), Streamlit may garbage collect that key after ~90 seconds.

### Solution: Protected Data Pattern
Store data in a SEPARATE dictionary inside session_state that is NOT a widget key:

**Files Modified:**
- `intake_review.py` - Pages 5, 6, 7, 8

**Pattern:**
```python
def show_assets_page(existing, save_payload, go_to_page):
    # ===== PROTECTED DATA STORE =====
    if '_protected_asset_data' not in st.session_state:
        st.session_state._protected_asset_data = {}
    protected = st.session_state._protected_asset_data

    # Initialize from existing data
    asset_keys = ['input_ira_balance', 'input_four01k_403b_balance', ...]
    for key in asset_keys:
        if key not in protected:
            val = st.session_state.get(key, existing.get(key, 0.0))
            protected[key] = float(val) if val else 0.0

    # Widget uses protected for VALUE
    ira = st.number_input(
        "Your IRA Balance",
        key="input_ira_balance",
        value=protected.get("input_ira_balance", 0.0)  # <-- VALUE from protected
    )

    # After widget, SAVE BACK to protected
    protected['input_ira_balance'] = ira
```

### Why This Works
- `_protected_asset_data` is a dictionary, not a widget key
- It persists in session_state regardless of what's rendered
- Widget keys can be GC'd, but we always have the backup in protected dict

---

## 3. Widget Key Collision Errors

### Symptom
```
st.session_state.custom_expenses_editor cannot be modified after the widget
with key custom_expenses_editor is instantiated.
```

### Root Cause
Two scenarios cause this:

1. **Old widget keys in saved data:** If a snapshot/JSON contains widget keys like `custom_expenses_editor`, and code tries to write these to session_state AFTER the widget is created.

2. **Loop copying ALL keys:** Code like this copies widget keys:
   ```python
   for key, value in data.items():
       st.session_state[key] = value  # DANGER: includes widget keys!
   ```

### Solution A: Whitelist Approach
Only copy SAFE data keys, never widget keys:

```python
for key, value in data.items():
    # WHITELIST: Only copy safe data keys, never widget keys
    if key.startswith(('input_', 'temp_', '_protected')) or key in (
        'children_list', 'children_rows', 'inheritance_list', 'inherit_rows',
        'goals_list', 'goals_data', 'custom_expenses', 'custom_expenses_list',
        'custom_income', 'custom_income_list', 'schema_version'
    ):
        st.session_state[key] = value
```

### Solution B: Widget Key Cleanup
Delete stale widget keys BEFORE widgets are created:

```python
def show_intake_questionnaire():
    # ===== CRITICAL: Clean up stale widget keys BEFORE any widgets render =====
    widget_keys_to_clean = [
        'children_editor', 'inherit_editor', 'goals_editor', 'custom_expenses_editor',
        'custom_income_editor'
    ]
    for wk in widget_keys_to_clean:
        if wk in st.session_state:
            del st.session_state[wk]

    # ... rest of function
```

**Files Modified with Cleanup:**
- `intake_integrated.py` - Added at start of `show_intake_questionnaire()`
- `intake_review.py` - Added at start of `show_family_page()`

---

## 4. Dangerous session_state Loops

### The Problem
Multiple files had loops that copied ALL keys from dictionaries to session_state:

```python
for key, value in snapshot_data.items():
    st.session_state[key] = value  # DANGER!
```

### All Locations Fixed (8 total in 7 files)

| File | Line | Variable |
|------|------|----------|
| `intake_review.py` | 677 | `data.items()` |
| `intake_integrated.py` | 188 | `template.items()` |
| `intake_integrated.py` | 575 | `snapshot_data.items()` |
| `app.py` | 257 | `intake_data.items()` |
| `app.py` | 654 | `snapshot_data.items()` |
| `sidebar_snapshot_manager.py` | 67 | `scenario_data.items()` |
| `data_manager.py` | 58 | `scenario_data.items()` |
| `data_manager_cloud.py` | 33 | `scenario_data.items()` |
| `app_oct24.py` | 107 | `intake_data.items()` |

### Fix Applied to All
```python
for key, value in data.items():
    # WHITELIST: Only copy safe data keys, never widget keys
    if key.startswith(('input_', 'temp_', '_protected')) or key in (
        'children_list', 'children_rows', 'inheritance_list', 'inherit_rows',
        'goals_list', 'goals_data', 'custom_expenses', 'custom_expenses_list',
        'custom_income', 'custom_income_list', 'schema_version'
    ):
        st.session_state[key] = value
```

### Verification Script
```python
# Run this to find any remaining dangerous loops:
import glob
for f in glob.glob('*.py') + glob.glob('*/*.py'):
    with open(f) as file:
        content = file.read()
    if 'for ' in content and '.items()' in content and 'session_state[' in content:
        if 'WHITELIST' not in content:
            print(f"DANGER: {f}")
```

---

## 5. Age None Comparison Error

### Symptom
```
'<' not supported between instances of 'NoneType' and 'int'
```

### Root Cause
We changed age defaults from `18` to `None` to show empty fields, but `st.number_input` with `min_value=18` can't compare `None < 18`.

### Solution
Use `or 18` to provide fallback:

**Before:**
```python
value=st.session_state.get("input_age", None)
```

**After:**
```python
value=st.session_state.get("input_age") or 18
```

**Files Modified:**
- `intake_integrated.py` - Lines 668, 685, 675

---

## 6. Empty Else Block Syntax Errors

### Symptom
```
IndentationError: expected an indented block after 'else' statement on line 270
```

### Root Cause
When removing debug print statements, some `else:` blocks were left empty:
```python
else:
    print(f"[DEBUG] something")  # <-- removed this

# Now the else: block is empty!
except Exception:
```

### Solution
Add `pass` to empty blocks:
```python
else:
    pass  # No intake data to load
```

**Files Modified:**
- `app.py` - Lines 270, 277

---

## 7. Sidebar Pages Menu Showing

### Symptom
Sidebar shows unwanted menu items:
- app
- family inputs
- financial inputs
- medigap comparison
- roth calculator
- social security optimizer
- user inputs

Users thought this was a menu and got confused.

### Root Cause
Streamlit's multipage app feature auto-detects `.py` files in the `pages/` folder and creates a navigation menu.

### Solution
Add CSS to hide Streamlit's auto-generated navigation:

**File Modified:** `config/settings.py`

```css
/* HIDE Streamlit's auto-generated pages navigation in sidebar */
[data-testid="stSidebarNav"] {
    display: none !important;
}
```

### Why Not Rename/Delete Pages Folder?
The `pages/*.py` files are imported by `app.py`:
```python
from pages.user_inputs import setup_sidebar as collect_user_data
from pages.financial_inputs import collect_financial_data
from pages.family_inputs import collect_family_events
```

Deleting them would break imports. The CSS solution hides the menu while keeping the imports working.

---

## 8. BETA Mode Hidden for Launch

### Symptom
BETA mode was showing same forms as FULL mode (not simplified).

### Decision
Hide BETA mode selector for launch, restore post-launch from yesterday's commits.

### Solution
Auto-select FULL mode without showing selector:

**File Modified:** `intake_integrated.py`

**Before (~45 lines of mode selector UI):**
```python
if "intake_mode" not in st.session_state:
    st.markdown("### Choose Your Experience:")
    col1, col2 = st.columns(2)
    # ... FULL MODE button, BETA MODE button, journey info ...
    st.stop()
```

**After (3 lines):**
```python
# PRODUCTION: Auto-select FULL mode (BETA mode hidden for launch)
# TODO: Restore BETA mode selector post-launch from yesterday's commits
if "intake_mode" not in st.session_state:
    st.session_state.intake_mode = "full"
```

---

## 9. Debug Print Statements Cleanup

### Problem
68 debug print statements cluttering the console.

### Patterns Removed
- `print(f"[DEBUG...")`
- `print(f"[PAGE...")`
- `print(f"[INTAKE...")`
- `print(f"=====")`
- `print(f"  PROTECTED...")`
- `print(f"  INIT...")`
- `print(f"  KEPT...")`

### Files Cleaned
- `intake_integrated.py` - 28 prints removed
- `intake_review.py` - 25 prints removed
- `app.py` - 10 prints removed

### Remaining Legitimate Prints
- Sentry initialization messages (`app.py`)
- Healthcare import warnings (`app.py`)
- `[WARN]` messages for actual warnings

### Cleanup Script
```python
import os
for filepath in ['intake_integrated.py', 'intake_review.py', 'app.py']:
    with open(filepath, 'r') as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith('print(') and any(p in line for p in
            ['[DEBUG', '[PAGE', '[INTAKE', 'PROTECTED', '=====']):
            continue
        new_lines.append(line)
    with open(filepath, 'w') as f:
        f.writelines(new_lines)
```

---

## Quick Reference: File Locations

| Issue | Primary File(s) |
|-------|-----------------|
| Rerun loop | `utils/snapshot_manager.py`, `utils/comparison_scenarios.py`, `utils/historical_snapshots.py` |
| Data persistence | `intake_review.py` (protected data pattern) |
| Widget collisions | `intake_integrated.py`, `intake_review.py` (cleanup code) |
| session_state loops | 7 files (see Section 4) |
| Age error | `intake_integrated.py` |
| Syntax errors | `app.py` |
| Sidebar menu | `config/settings.py` (CSS) |
| BETA mode | `intake_integrated.py` |
| Debug prints | `intake_integrated.py`, `intake_review.py`, `app.py` |

---

## Prevention Checklist for Future Development

### Before Adding New Code:
- [ ] Never copy ALL keys from a dict to session_state
- [ ] Always use WHITELIST approach for session_state writes
- [ ] Widget keys should only be set BY the widget, never manually
- [ ] Use `_protected_*` dicts for data that must persist across page changes
- [ ] Test with 2+ minute idle times to catch GC issues
- [ ] Don't use `streamlit-browser-storage` (causes reruns)

### Before Deploying:
- [ ] Remove all debug print statements
- [ ] Verify no empty `else:` or `except:` blocks
- [ ] Test all INTAKE pages (5, 6, 7, 8) navigation
- [ ] Check sidebar doesn't show unwanted menu items
- [ ] Verify Python syntax: `python -m py_compile app.py`

---

## Git Commands for Recovery

### See what changed today:
```bash
git diff HEAD~10 intake_integrated.py
git diff HEAD~10 intake_review.py
git log --oneline -20
```

### Restore a specific file from commit:
```bash
git show COMMIT_HASH:filename > filename.restored
```

### Find when BETA mode worked:
```bash
git log --all --oneline --source -- intake_integrated.py | grep -i beta
```

---

## Contact / Attribution

**Session Date:** November 28, 2025
**Duration:** ~8 hours debugging session
**AI Assistant:** Claude (Anthropic)
**Developer:** Serge Castro

*This document serves as institutional knowledge for future troubleshooting.*
