# CRITICAL PRIVACY BUG - Server-Side Snapshot Sharing

**Date Discovered:** November 26, 2025
**Severity:** CRITICAL
**Status:** NOT FIXED - Scheduled for tomorrow

---

## The Problem

The `.snapshot_cache/` folder on the server is SHARED by all users on Render.

When User A saves a snapshot, User B can see User A's data!

### How It Happens

1. User A visits familyforecast.ai
2. User A enters their financial data and saves
3. Code writes to `.snapshot_cache/snapshot_20251126_1234.json` on server
4. User B visits familyforecast.ai (even in incognito)
5. Code reads `.snapshot_cache/snapshots_index.json`
6. User B sees User A's data!

### Root Cause

The code has a HYBRID storage system:
- **Primary:** Browser localStorage (per-user, private) ✅
- **Backup:** `.snapshot_cache/` on server (SHARED!) ❌

The server-side backup was intended for development but is active in production.

---

## Files Involved

| File | Issue |
|------|-------|
| `utils/snapshot_manager.py` | Lines 190-193, 282-285, 549-552, 635-638 write/read from `.snapshot_cache/` |
| `utils/comparison_scenarios.py` | Multiple references to `.snapshot_cache/comparisons/` |
| `utils/historical_snapshots.py` | Uses `.snapshot_cache/historical/` |
| `healthcare/intake_integration.py` | Reads from `.snapshot_cache/` |

---

## How to Fix

### Option A: Remove Server-Side Caching Entirely (RECOMMENDED)

1. In `utils/snapshot_manager.py`:
   - Remove all `open(cache_file, 'w')` calls that write to `.snapshot_cache/`
   - Remove all `open(cache_file, 'r')` calls that read from `.snapshot_cache/`
   - Keep ONLY the browser localStorage code

2. In `utils/comparison_scenarios.py`:
   - Same approach - browser localStorage only

3. In `utils/historical_snapshots.py`:
   - Same approach - browser localStorage only

4. In `healthcare/intake_integration.py`:
   - Read from session_state or localStorage only

### Option B: Add User Isolation (More Complex)

1. Generate unique user ID on first visit (stored in localStorage)
2. Create user-specific folders: `.snapshot_cache/{user_id}/`
3. Update all file paths to include user_id

### Option C: Disable Server Writes in Production

1. Check for environment variable: `RENDER=true`
2. If production, skip all `.snapshot_cache/` writes
3. Rely entirely on browser localStorage

---

## Immediate Mitigation (Already Done)

We removed existing snapshot files from git tracking:
```bash
git rm --cached .snapshot_cache/*.json
git rm --cached .snapshot_cache/comparisons/*.json
```

Commit: `834685c` - "PRIVACY FIX: Remove user snapshot data from git tracking"

This prevents NEW deployments from having old test data, but does NOT fix the core issue.

---

## Testing After Fix

1. Deploy to Render
2. User A: Enter data, save snapshot
3. User B (incognito): Visit site
4. User B should see EMPTY fields, not User A's data
5. Verify no files in `.snapshot_cache/` on server (if using Option A)

---

## Code Locations to Modify

### utils/snapshot_manager.py

**Line 190-195 (get_snapshots_index):**
```python
# REMOVE THIS BLOCK:
cache_dir = os.path.join(os.path.dirname(__file__), '..', '.snapshot_cache')
cache_file = os.path.join(cache_dir, 'snapshots_index.json')
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        ...
```

**Line 282-287 (save_snapshots_index):**
```python
# REMOVE THIS BLOCK:
cache_dir = os.path.join(os.path.dirname(__file__), '..', '.snapshot_cache')
os.makedirs(cache_dir, exist_ok=True)
with open(cache_file, 'w') as f:
    json.dump(index, f, indent=2)
```

**Line 549-553 (save_snapshot):**
```python
# REMOVE THIS BLOCK:
cache_dir = os.path.join(os.path.dirname(__file__), '..', '.snapshot_cache')
os.makedirs(cache_dir, exist_ok=True)
with open(snapshot_file, 'w') as f:
    json.dump(data, f, indent=2)
```

**Line 635-639 (load_snapshot):**
```python
# REMOVE THIS BLOCK:
cache_dir = os.path.join(os.path.dirname(__file__), '..', '.snapshot_cache')
snapshot_file = os.path.join(cache_dir, f'snapshot_{snapshot_id}.json')
if os.path.exists(snapshot_file):
    with open(snapshot_file, 'r') as f:
        ...
```

---

## Questions for Serge

1. Should we keep demo_snapshots.json in `data/` folder? (This is OK - it's intentionally shared demo data)
2. Do we need any server-side backup for user data? Or is browser localStorage sufficient?
3. Should we add a "Export to file" feature so users can backup their own data?

---

## Priority

**FIX THIS BEFORE LAUNCH TO REAL USERS!**

Current state: Only test data is being shared. No real user data at risk yet.
