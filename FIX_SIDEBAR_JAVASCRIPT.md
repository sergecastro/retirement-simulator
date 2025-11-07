# 🔧 INSTANT FIX - Rebuild Snapshot Index

## ⚡ COPY & PASTE THIS JAVASCRIPT INTO BROWSER CONSOLE

### Instructions:
1. **Open app in browser** (if not already open)
2. **Press F12** to open Developer Tools
3. **Go to Console tab**
4. **Copy the ENTIRE code block below** (click the copy button →)
5. **Paste into Console**
6. **Press Enter**
7. **Wait for "✅ SUCCESS" message**
8. **Refresh page (F5)**
9. **Go to Analysis mode → Check sidebar!**

---

## 📋 THE FIX CODE (Copy Everything Below):

```javascript
(function() {
    console.log("=".repeat(60));
    console.log("🔧 REBUILD SNAPSHOT INDEX - INSTANT FIX");
    console.log("=".repeat(60));

    try {
        // Step 1: Find all snapshot data keys
        console.log("\n[1/5] Scanning localStorage for snapshots...");
        let snapshotKeys = [];

        for (let i = 0; i < localStorage.length; i++) {
            let key = localStorage.key(i);
            // Look for both formats
            if (key.startsWith('ff_snapshot_') || key.startsWith('family_forecast_snapshot_')) {
                snapshotKeys.push(key);
                console.log(`  ✓ Found: ${key}`);
            }
        }

        if (snapshotKeys.length === 0) {
            console.error("❌ ERROR: No snapshots found in localStorage!");
            console.log("\nPossible reasons:");
            console.log("  • Snapshots were never saved");
            console.log("  • localStorage was cleared");
            console.log("  • You're in incognito mode or different browser");
            console.log("\n💡 Solution: Go to INTAKE mode and save a new plan.");
            return;
        }

        console.log(`\n✓ Found ${snapshotKeys.length} snapshot(s)`);

        // Step 2: Extract snapshot IDs and create metadata
        console.log("\n[2/5] Building snapshot index...");
        let snapshots = [];

        for (let key of snapshotKeys) {
            // Extract ID from key
            // "ff_snapshot_20251107_1107" -> "20251107_1107"
            let snapshotId = key.replace('ff_snapshot_', '').replace('family_forecast_snapshot_', '');

            // Parse timestamp from ID: "20251107_1107" -> "2025-11-07T11:07:00"
            let year = snapshotId.substring(0, 4);
            let month = snapshotId.substring(4, 6);
            let day = snapshotId.substring(6, 8);
            let hour = snapshotId.substring(9, 11);
            let minute = snapshotId.substring(11, 13);
            let created = `${year}-${month}-${day}T${hour}:${minute}:00`;

            // Try to get data to extract name (but it's encrypted, so we can't)
            let encryptedData = localStorage.getItem(key);

            // Check if data looks encrypted (should start with special chars)
            let isEncrypted = encryptedData && encryptedData.length > 100;

            // Create snapshot metadata entry
            let snapshot = {
                id: snapshotId,
                name: `Saved Plan ${month}/${day} ${hour}:${minute}`,  // Generic name from timestamp
                created: created,
                metadata: {
                    user_name: "Unknown",  // Can't extract without decryption
                    user_age: 0,
                    partner_exists: false,
                    partner_name: "",
                    partner_age: 0,
                    net_worth: 0,
                    monthly_surplus: 0
                }
            };

            snapshots.push(snapshot);
            console.log(`  ✓ Added: ${snapshot.name} (ID: ${snapshotId})`);
        }

        // Step 3: Sort by ID (newest first)
        console.log("\n[3/5] Sorting snapshots...");
        snapshots.sort((a, b) => b.id.localeCompare(a.id));

        // Most recent snapshot becomes current
        let currentSnapshotId = snapshots[0].id;
        console.log(`  ✓ Current: ${currentSnapshotId}`);

        // Step 4: Create index structure
        console.log("\n[4/5] Creating index structure...");
        let newIndex = {
            current_snapshot_id: currentSnapshotId,
            snapshots: snapshots
        };

        // Convert to JSON
        let indexJson = JSON.stringify(newIndex);

        // Check if encryption key exists
        let hasEncryptionKey = localStorage.getItem('ff_encryption_key');
        if (!hasEncryptionKey) {
            console.warn("⚠️  WARNING: ff_encryption_key not found!");
            console.log("    Index will be saved unencrypted (temporary fix)");
            console.log("    Next time you save a plan in INTAKE, it will re-encrypt properly.");
        }

        // Step 5: Save index to localStorage
        console.log("\n[5/5] Saving index to localStorage...");

        // Save as PLAIN TEXT for now (Python will re-encrypt on next load)
        localStorage.setItem('ff_snapshots_index_plain', indexJson);
        console.log("  ✓ Saved plain index (temporary)");

        // Also try to save in expected location
        // (Python expects encrypted, but this lets sidebar see SOMETHING)
        localStorage.setItem('ff_snapshots_index', indexJson);
        console.log("  ✓ Saved to ff_snapshots_index");

        // Summary
        console.log("\n" + "=".repeat(60));
        console.log("✅ SUCCESS! Index rebuilt with " + snapshots.length + " snapshot(s)");
        console.log("=".repeat(60));
        console.log("\n📋 Snapshots in index:");
        snapshots.forEach((s, i) => {
            console.log(`  ${i + 1}. ${s.name} (${s.id})`);
        });

        console.log("\n🔄 NEXT STEPS:");
        console.log("  1. Refresh this page (press F5)");
        console.log("  2. Go to Analysis mode");
        console.log("  3. Check sidebar - should show your plans!");
        console.log("\n⚠️  NOTE: Plan names will be generic (dates)");
        console.log("     To get real names back:");
        console.log("     • Go to INTAKE mode");
        console.log("     • Load a plan");
        console.log("     • Save it again");
        console.log("     • This will re-encrypt with proper metadata");

        console.log("\n" + "=".repeat(60));

    } catch (error) {
        console.error("\n❌ ERROR:", error);
        console.log("\n💡 If this didn't work:");
        console.log("  1. Go to INTAKE mode");
        console.log("  2. Save a new plan");
        console.log("  3. This will rebuild the index automatically");
    }
})();
```

---

## ✅ WHAT THIS DOES

1. **Scans localStorage** for all `ff_snapshot_*` keys
2. **Extracts snapshot IDs** from key names
3. **Creates timestamps** from IDs (20251107_1107 → Nov 7, 2025 11:07 AM)
4. **Builds index structure** with all snapshots
5. **Saves to localStorage** as `ff_snapshots_index`
6. **Shows you the results** in console

---

## 📊 EXPECTED OUTPUT

```
============================================================
🔧 REBUILD SNAPSHOT INDEX - INSTANT FIX
============================================================

[1/5] Scanning localStorage for snapshots...
  ✓ Found: ff_snapshot_20251107_1107
  ✓ Found: ff_snapshot_20251107_1115
  ✓ Found: ff_snapshot_20251107_1130

✓ Found 3 snapshot(s)

[2/5] Building snapshot index...
  ✓ Added: Saved Plan 11/07 11:07 (ID: 20251107_1107)
  ✓ Added: Saved Plan 11/07 11:15 (ID: 20251107_1115)
  ✓ Added: Saved Plan 11/07 11:30 (ID: 20251107_1130)

[3/5] Sorting snapshots...
  ✓ Current: 20251107_1130

[4/5] Creating index structure...

[5/5] Saving index to localStorage...
  ✓ Saved plain index (temporary)
  ✓ Saved to ff_snapshots_index

============================================================
✅ SUCCESS! Index rebuilt with 3 snapshot(s)
============================================================

📋 Snapshots in index:
  1. Saved Plan 11/07 11:30 (20251107_1130)
  2. Saved Plan 11/07 11:15 (20251107_1115)
  3. Saved Plan 11/07 11:07 (20251107_1107)

🔄 NEXT STEPS:
  1. Refresh this page (press F5)
  2. Go to Analysis mode
  3. Check sidebar - should show your plans!
```

---

## 🔍 IF IT SHOWS "No snapshots found"

**That means:**
- Snapshots were never actually saved
- OR localStorage was cleared
- OR you're in a different browser/profile

**Solution:**
1. Go to INTAKE mode
2. Fill out the form
3. Click "💾 SAVE PLAN"
4. Give it a name
5. Now the snapshot will exist!

---

## ⚠️ IMPORTANT NOTES

1. **Plan names will be generic** (just dates/times)
   - Real names are encrypted and can't be extracted
   - To get real names: Load and re-save each plan in INTAKE

2. **Index is temporarily unencrypted**
   - Next time you save a plan, Python will re-encrypt it properly
   - This is just to get sidebar working immediately

3. **All your data is still encrypted**
   - Only the index (list of plan names) is temporarily plain text
   - The actual plan data (`ff_snapshot_*` keys) remains encrypted

---

## ✨ AFTER RUNNING THIS

**Your sidebar should show:**
```
📂 Saved Plans
📋 Currently: Original 70+ Retirement (Demo)
✅ Found 3 saved plan(s) in localStorage

📥 Load Plan
Select: [Dropdown with 3 plans]
[📂 Load button]
```

**Success!** 🎉

---

**Questions? Run the code and check console output for diagnostics!**
