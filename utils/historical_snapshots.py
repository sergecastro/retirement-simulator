"""
Historical Snapshot Management
================================
Stores versioned snapshots of retirement plans over time.
Enables users to track progress quarterly/yearly and compare improvements.

STORAGE: Uses browser localStorage (NOT disk cache!) for privacy/security.

Author: Family Forecast Development Team
Created: November 19, 2025
Updated: November 28, 2025 - Converted to localStorage only
"""

import json
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
from utils.encryption import encrypt_data, decrypt_data
# DISABLED: from streamlit_browser_storage import LocalStorage


# localStorage key prefix
HISTORICAL_INDEX_KEY = "ff_historical_index"
HISTORICAL_SNAPSHOT_PREFIX = "ff_historical_"


@st.cache_resource
def _get_local_storage():
    """Get localStorage instance (singleton-cached)."""
    # ========== TEMPORARY DEBUG: DISABLED TO FIND RERUN SOURCE ==========
    print("[DEBUG] historical_snapshots._get_local_storage DISABLED")
    return None
    # ========== END TEMPORARY DEBUG ==========
    if '_localStorage_singleton' not in st.session_state:
        st.session_state._localStorage_singleton = LocalStorage(key="forecash_local_storage")
    return st.session_state._localStorage_singleton


def save_historical_snapshot(
    user_data: Dict,
    simulation_results: Dict,
    snapshot_name: str,
    notes: str = ""
) -> str:
    """
    Save a historical snapshot with encryption to localStorage.

    Args:
        user_data: User demographic and financial data
        simulation_results: Simulation outcomes (success rate, net worth, etc.)
        snapshot_name: User-friendly name for this snapshot
        notes: Optional notes about changes since last snapshot

    Returns:
        snapshot_id: Timestamp-based unique identifier
    """
    # Generate snapshot ID (timestamp-based)
    snapshot_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build snapshot data structure
    snapshot = {
        "id": snapshot_id,
        "timestamp": datetime.now().isoformat(),
        "name": snapshot_name,
        "notes": notes,
        "user_data": user_data,
        "simulation_results": simulation_results,
        "version": "1.0"
    }

    try:
        localS = _get_local_storage()

        # Save encryption key if it's new
        if localS is not None and st.session_state.get('encryption_key_needs_save', False):
            localS.set('ff_encryption_key', st.session_state.encryption_key_b64)
            st.session_state.encryption_key_needs_save = False

        # Encrypt and save snapshot to localStorage
        encrypted = encrypt_data(snapshot, localS)
        storage_key = f"{HISTORICAL_SNAPSHOT_PREFIX}{snapshot_id}"
        if localS is not None:
            localS.set(storage_key, encrypted)
        else:
            print(f"[WARN] localStorage disabled - cannot save historical snapshot: {storage_key}")

        # Update index
        _add_to_index(snapshot_id, snapshot_name, snapshot["timestamp"])

        print(f"[HISTORICAL] Saved snapshot: {snapshot_name} (ID: {snapshot_id})")
        return snapshot_id

    except Exception as e:
        print(f"[HISTORICAL] Error saving snapshot: {e}")
        import traceback
        traceback.print_exc()
        return ""


def load_historical_snapshot(snapshot_id: str) -> Optional[Dict]:
    """
    Load a historical snapshot by ID from localStorage.

    Args:
        snapshot_id: Unique snapshot identifier

    Returns:
        Decrypted snapshot data or None if not found
    """
    try:
        localS = _get_local_storage()
        storage_key = f"{HISTORICAL_SNAPSHOT_PREFIX}{snapshot_id}"

        if localS is None:
            print(f"[WARN] localStorage disabled - cannot load historical snapshot: {snapshot_id}")
            return None
        encrypted = localS.get(storage_key)
        if not encrypted:
            print(f"[HISTORICAL] Snapshot not found: {snapshot_id}")
            return None

        snapshot = decrypt_data(encrypted, localS)
        if snapshot:
            print(f"[HISTORICAL] Loaded snapshot: {snapshot_id}")
            return snapshot
        else:
            print(f"[HISTORICAL] Decryption failed: {snapshot_id}")
            return None

    except Exception as e:
        print(f"[HISTORICAL] Error loading snapshot {snapshot_id}: {e}")
        return None


def list_historical_snapshots() -> List[Dict]:
    """
    Get list of all snapshots with metadata (name, date, ID).

    Returns:
        List of snapshot metadata dictionaries
    """
    try:
        localS = _get_local_storage()
        if localS is None:
            return []
        encrypted = localS.get(HISTORICAL_INDEX_KEY)

        if not encrypted:
            return []

        index = decrypt_data(encrypted, localS)
        if index:
            return index.get("snapshots", [])
        return []

    except Exception as e:
        print(f"[HISTORICAL] Error loading index: {e}")
        return []


def delete_historical_snapshot(snapshot_id: str) -> bool:
    """
    Delete a snapshot from localStorage.

    Args:
        snapshot_id: Snapshot to delete

    Returns:
        True if deleted, False if not found
    """
    try:
        localS = _get_local_storage()
        storage_key = f"{HISTORICAL_SNAPSHOT_PREFIX}{snapshot_id}"

        # Delete the snapshot
        if localS is not None:
            localS.delete(storage_key)
        else:
            print(f"[WARN] localStorage disabled - cannot delete: {storage_key}")

        # Update index
        _remove_from_index(snapshot_id)

        print(f"[HISTORICAL] Deleted snapshot: {snapshot_id}")
        return True

    except Exception as e:
        print(f"[HISTORICAL] Error deleting snapshot: {e}")
        return False


def get_snapshot_count() -> int:
    """Get total number of saved snapshots"""
    return len(list_historical_snapshots())


def _add_to_index(snapshot_id: str, name: str, timestamp: str):
    """Add snapshot metadata to index"""
    index = list_historical_snapshots()
    index.append({
        "id": snapshot_id,
        "name": name,
        "timestamp": timestamp
    })
    # Sort by timestamp (newest first)
    index.sort(key=lambda x: x["timestamp"], reverse=True)
    _save_index(index)


def _remove_from_index(snapshot_id: str):
    """Remove snapshot from index"""
    index = list_historical_snapshots()
    index = [s for s in index if s["id"] != snapshot_id]
    _save_index(index)


def _save_index(index: List[Dict]):
    """Save index to localStorage"""
    try:
        localS = _get_local_storage()

        # Save encryption key if it's new
        if localS is not None and st.session_state.get('encryption_key_needs_save', False):
            localS.set('ff_encryption_key', st.session_state.encryption_key_b64)
            st.session_state.encryption_key_needs_save = False

        index_data = {"snapshots": index}
        encrypted = encrypt_data(index_data, localS)
        if localS is not None:
            localS.set(HISTORICAL_INDEX_KEY, encrypted)
        else:
            print("[WARN] localStorage disabled - cannot save historical index")

    except Exception as e:
        print(f"[HISTORICAL] Error saving index: {e}")


def export_all_snapshots() -> Dict:
    """
    Export all snapshots for backup/transfer.

    Returns:
        Dictionary with all snapshot data
    """
    snapshots = list_historical_snapshots()

    export_data = {
        "export_date": datetime.now().isoformat(),
        "snapshot_count": len(snapshots),
        "snapshots": []
    }

    for s in snapshots:
        snapshot = load_historical_snapshot(s["id"])
        if snapshot:
            export_data["snapshots"].append(snapshot)

    return export_data


def import_snapshots(import_data: Dict) -> int:
    """
    Import snapshots from exported data.

    Args:
        import_data: Dictionary from export_all_snapshots()

    Returns:
        Number of snapshots imported
    """
    imported = 0

    for snapshot in import_data.get("snapshots", []):
        try:
            # Generate new ID to avoid conflicts
            snapshot_id = save_historical_snapshot(
                snapshot["user_data"],
                snapshot["simulation_results"],
                snapshot["name"] + " (imported)",
                snapshot.get("notes", "")
            )
            if snapshot_id:
                imported += 1
        except Exception as e:
            print(f"[HISTORICAL] Error importing snapshot: {e}")
            continue

    return imported
