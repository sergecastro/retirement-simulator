# 🔧 QUICK FIX - Rebuild Snapshot Index

## Problem
Sidebar doesn't show your 3 saved snapshots.

## Root Cause
The `ff_snapshots_index` in localStorage might be corrupted or out of sync with actual snapshot data.

---

## ✅ SOLUTION 1: EASIEST (30 seconds)

**Just re-save one plan in INTAKE mode:**

1. Open app: `streamlit run app.py`
2. Go to **INTAKE** mode
3. Scroll to bottom (Review page)
4. Click **"💾 SAVE PLAN"** button
5. Name it anything (e.g., "Test Rebuild")
6. Go back to **Analysis** mode
7. Check sidebar - should now show all plans!

**Why this works:** Saving triggers a full index rebuild.

---

## ✅ SOLUTION 2: BROWSER CONSOLE (1 minute)

**Scan localStorage and show what's there:**

1. Open app in browser
2. Press **F12** to open Developer Console
3. Go to **Console** tab
4. Copy/paste this JavaScript:

```javascript
// QUICK DIAGNOSTIC
console.log("=== SNAPSHOT DIAGNOSTIC ===");

// Check encryption key
let hasKey = localStorage.getItem('ff_encryption_key');
console.log(`Encryption Key: ${hasKey ? '✅ EXISTS' : '❌ MISSING'}`);

// Check index
let indexRaw = localStorage.getItem('ff_snapshots_index');
console.log(`Snapshots Index: ${indexRaw ? '✅ EXISTS' : '❌ MISSING'}`);

// Find all snapshot data keys
let snapshotKeys = [];
for (let i = 0; i < localStorage.length; i++) {
    let key = localStorage.key(i);
    if (key.startsWith('ff_snapshot_')) {
        snapshotKeys.push(key);
    }
}

console.log(`\nSnapshot Data Files Found: ${snapshotKeys.length}`);
snapshotKeys.forEach(key => {
    let id = key.replace('ff_snapshot_', '');
    console.log(`  - ${id}`);
});

if (snapshotKeys.length > 0 && !indexRaw) {
    console.log("\n⚠️ PROBLEM FOUND: Snapshot data exists but index is missing!");
    console.log("SOLUTION: Go to INTAKE mode and re-save any plan to rebuild index.");
}

if (snapshotKeys.length === 0) {
    console.log("\n⚠️ PROBLEM: No snapshot data found in localStorage!");
    console.log("This means plans were never saved or localStorage was cleared.");
}

console.log("\n=========================");
```

5. Read the output
6. Follow the suggested solution

---

## ✅ SOLUTION 3: PYTHON SCRIPT (Advanced)

**If above solutions don't work:**

Create a test script to verify snapshot_manager works:

```python
# test_snapshots.py
import streamlit as st
from utils.snapshot_manager import get_snapshots_index

st.title("Snapshot Index Test")

try:
    index = get_snapshots_index()
    snapshots = index.get("snapshots", [])

    st.write(f"**Found {len(snapshots)} snapshots:**")
    for s in snapshots:
        st.write(f"- {s['name']} (ID: {s['id']})")

    if len(snapshots) == 0:
        st.warning("No snapshots found!")
        st.info("Go to INTAKE mode and save a plan to test.")

except Exception as e:
    st.error(f"Error: {e}")
    import traceback
    st.code(traceback.format_exc())
```

Run with: `streamlit run test_snapshots.py`

---

## 🔍 EXPECTED RESULTS

### If Working Correctly:
- ✅ Encryption key exists
- ✅ Index exists
- ✅ 3+ snapshot data files exist
- ✅ Sidebar shows all plans

### If Broken:
- ❌ Index missing (but data files exist) → **Use Solution 1**
- ❌ No data files exist → **Plans were never saved**
- ❌ Encryption key missing → **localStorage was cleared**

---

## 📞 STILL NOT WORKING?

**Check these:**

1. **Are you in the same browser?**
   - localStorage is per-browser
   - Chrome data ≠ Firefox data

2. **Same browser profile?**
   - Regular mode ≠ Incognito mode
   - Different profiles have different localStorage

3. **Was localStorage cleared?**
   - Browser settings → Clear browsing data
   - Extensions that clear localStorage

4. **Correct branch?**
   - Run: `git branch`
   - Should show: `* feature/scenario-comparison-enhanced`

---

## ✨ PREVENTION

**To avoid this in future:**

1. **Export backups regularly:**
   - INTAKE mode → Review page → "📤 Export Backup (.ffb)"
   - Keep .ffb files safe

2. **Don't clear browser data:**
   - Be careful with "Clear browsing data"
   - localStorage is included in "Site data"

3. **Use same browser:**
   - Stick to one browser for the app
   - Or export/import between browsers

---

**Most likely fix: Just re-save one plan in INTAKE mode!** ✅
