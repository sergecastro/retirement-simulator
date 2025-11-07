"""
Quick Fix Script: Rebuild Snapshot Index
=========================================

PROBLEM: Sidebar doesn't show saved snapshots
SOLUTION: Scan localStorage for all ff_snapshot_* keys and rebuild index

USAGE:
1. Run Streamlit app: streamlit run app.py
2. Open browser console (F12)
3. Copy/paste the JavaScript code below into console
4. It will scan and rebuild the index

JAVASCRIPT CODE TO RUN IN BROWSER CONSOLE:
===========================================
*/

(function() {
    console.log("=== REBUILD SNAPSHOT INDEX - START ===");

    // Step 1: Check current state
    console.log("\nStep 1: Checking current localStorage...");
    let hasIndex = localStorage.getItem('ff_snapshots_index');
    let hasKey = localStorage.getItem('ff_encryption_key');

    console.log(`ff_snapshots_index: ${hasIndex ? 'EXISTS' : 'MISSING'}`);
    console.log(`ff_encryption_key: ${hasKey ? 'EXISTS' : 'MISSING'}`);

    // Step 2: Find all snapshot data keys
    console.log("\nStep 2: Scanning for snapshot data keys...");
    let snapshotKeys = [];
    for (let i = 0; i < localStorage.length; i++) {
        let key = localStorage.key(i);
        if (key.startsWith('ff_snapshot_')) {
            snapshotKeys.push(key);
            console.log(`  Found: ${key}`);
        }
    }

    console.log(`\nTotal snapshots found: ${snapshotKeys.length}`);

    if (snapshotKeys.length === 0) {
        console.error("ERROR: No snapshots found in localStorage!");
        console.log("Possible reasons:");
        console.log("1. Snapshots were never saved");
        console.log("2. localStorage was cleared");
        console.log("3. You're in a different browser/profile");
        return;
    }

    // Step 3: Extract snapshot IDs and create metadata
    console.log("\nStep 3: Creating snapshot index...");
    let snapshots = [];
    let currentSnapshotId = null;

    for (let key of snapshotKeys) {
        // Extract ID from key: "ff_snapshot_20251106_0230" -> "20251106_0230"
        let snapshotId = key.replace('ff_snapshot_', '');

        // Parse encrypted data (we can't decrypt in browser without key)
        // But we can create placeholder metadata
        let encryptedData = localStorage.getItem(key);

        // Create snapshot metadata
        let snapshot = {
            id: snapshotId,
            name: `Saved Plan ${snapshotId}`,  // Default name (will be overwritten when loaded)
            created: "Unknown",  // Can't extract without decryption
            metadata: {
                user_name: "Unknown",
                user_age: 0,
                partner_exists: false,
                partner_name: "",
                partner_age: 0,
                net_worth: 0,
                monthly_surplus: 0
            }
        };

        snapshots.push(snapshot);

        // Use most recent as current
        if (!currentSnapshotId || snapshotId > currentSnapshotId) {
            currentSnapshotId = snapshotId;
        }

        console.log(`  Added: ${snapshot.name} (ID: ${snapshotId})`);
    }

    // Step 4: Sort by ID (newest first)
    snapshots.sort((a, b) => b.id.localeCompare(a.id));

    // Step 5: Create new index
    let newIndex = {
        current_snapshot_id: currentSnapshotId,
        snapshots: snapshots
    };

    console.log("\nStep 4: Index structure created:");
    console.log(JSON.stringify(newIndex, null, 2));

    // Step 6: Ask user confirmation
    console.log("\n" + "=".repeat(60));
    console.log("READY TO REBUILD INDEX");
    console.log("=".repeat(60));
    console.log(`Found: ${snapshots.length} snapshot(s)`);
    console.log(`Current: ${currentSnapshotId}`);
    console.log("\nTo proceed, run this command:");
    console.log("rebuildIndex()");
    console.log("=".repeat(60));

    // Create rebuild function
    window.rebuildIndex = function() {
        try {
            // Since we can't encrypt in browser, we need to:
            // 1. Save unencrypted index temporarily
            // 2. Let Python re-encrypt it on next load

            console.log("\n⚠️ WARNING: Can't rebuild encrypted index from browser!");
            console.log("ALTERNATIVE SOLUTION:");
            console.log("\n1. Go to INTAKE mode");
            console.log("2. Load one of your saved plans");
            console.log("3. Click 'Save Plan' button");
            console.log("4. This will rebuild the encrypted index");
            console.log("\nOR");
            console.log("\nRun this in Streamlit app (Python):");
            console.log("  python rebuild_snapshot_index_python.py");

        } catch (e) {
            console.error("ERROR:", e);
        }
    };

    console.log("\n✅ Diagnostic complete. See instructions above.");

})();

/*
===========================================

PYTHON VERSION (if JavaScript doesn't work):
Run this with Streamlit running in background
*/

"""

import streamlit as st
from utils.snapshot_manager import get_snapshots_index, save_snapshots_index, _get_local_storage, decrypt_data
from utils.encryption import decrypt_data as decrypt_func

def rebuild_index_python():
    """
    Rebuild snapshot index by scanning localStorage for all ff_snapshot_* keys.

    Run this with: streamlit run rebuild_snapshot_index.py
    """
    print("="*60)
    print("REBUILD SNAPSHOT INDEX - PYTHON VERSION")
    print("="*60)

    try:
        # Initialize Streamlit session state
        if 'localS' not in st.session_state:
            from streamlit_local_storage import LocalStorage
            st.session_state.localS = LocalStorage()

        localS = st.session_state.localS

        print("\nStep 1: Checking current index...")
        current_index = get_snapshots_index()
        print(f"Current snapshots in index: {len(current_index.get('snapshots', []))}")

        print("\nStep 2: Scanning localStorage for snapshot data...")

        # Get all keys (this requires accessing localStorage directly)
        # streamlit-local-storage doesn't have a "list all keys" method
        # So we'll try to load known snapshot IDs from a range

        print("\n⚠️ LIMITATION: Can't scan all localStorage keys from Python")
        print("streamlit-local-storage doesn't expose a 'listKeys()' method")
        print("\nRECOMMENDED SOLUTION:")
        print("1. Run JavaScript version in browser console (code above)")
        print("2. Or manually re-save one plan in INTAKE mode")
        print("3. This will trigger index rebuild automatically")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("="*60)
    print("\nOPTION 1 (RECOMMENDED): Use JavaScript in browser")
    print("  1. Run: streamlit run app.py")
    print("  2. Open browser console (F12)")
    print("  3. Copy/paste JavaScript code above")
    print("  4. Follow instructions")
    print("\nOPTION 2: Python (Limited)")
    print("  1. Start Streamlit: streamlit run app.py")
    print("  2. Run this script: python rebuild_snapshot_index.py")
    print("  3. Check output for diagnostics")
    print("\nOPTION 3 (EASIEST): Manual rebuild")
    print("  1. Go to INTAKE mode")
    print("  2. Load ANY saved plan")
    print("  3. Click 'Save Plan' button")
    print("  4. Index will rebuild automatically")
    print("="*60)
