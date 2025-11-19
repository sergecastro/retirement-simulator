"""
Historical Snapshot Management
================================
Stores versioned snapshots of retirement plans over time.
Enables users to track progress quarterly/yearly and compare improvements.

Author: Family Forecast Development Team
Created: November 19, 2025
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from utils.encryption import encrypt_data, decrypt_data


# Storage configuration
SNAPSHOTS_DIR = ".snapshot_cache/historical/"
INDEX_FILE = ".snapshot_cache/historical_index.json"


def ensure_directories():
    """Create snapshot directories if they don't exist"""
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
    if not os.path.exists(INDEX_FILE):
        save_index([])


def save_historical_snapshot(
    user_data: Dict,
    simulation_results: Dict,
    snapshot_name: str,
    notes: str = ""
) -> str:
    """
    Save a historical snapshot with encryption

    Args:
        user_data: User demographic and financial data
        simulation_results: Simulation outcomes (success rate, net worth, etc.)
        snapshot_name: User-friendly name for this snapshot
        notes: Optional notes about changes since last snapshot

    Returns:
        snapshot_id: Timestamp-based unique identifier
    """
    ensure_directories()

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

    # Encrypt and save to file
    encrypted = encrypt_data(json.dumps(snapshot))
    filepath = os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.json")

    with open(filepath, 'w') as f:
        json.dump({"encrypted": encrypted}, f)

    # Update index for quick listing
    _add_to_index(snapshot_id, snapshot_name, snapshot["timestamp"])

    return snapshot_id


def load_historical_snapshot(snapshot_id: str) -> Optional[Dict]:
    """
    Load a historical snapshot by ID

    Args:
        snapshot_id: Unique snapshot identifier

    Returns:
        Decrypted snapshot data or None if not found
    """
    filepath = os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.json")

    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        decrypted = decrypt_data(data["encrypted"])
        return json.loads(decrypted)
    except Exception as e:
        print(f"Error loading snapshot {snapshot_id}: {e}")
        return None


def list_historical_snapshots() -> List[Dict]:
    """
    Get list of all snapshots with metadata (name, date, ID)

    Returns:
        List of snapshot metadata dictionaries
    """
    if not os.path.exists(INDEX_FILE):
        return []

    try:
        with open(INDEX_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []


def delete_historical_snapshot(snapshot_id: str) -> bool:
    """
    Delete a snapshot from storage

    Args:
        snapshot_id: Snapshot to delete

    Returns:
        True if deleted, False if not found
    """
    filepath = os.path.join(SNAPSHOTS_DIR, f"{snapshot_id}.json")

    if os.path.exists(filepath):
        os.remove(filepath)
        _remove_from_index(snapshot_id)
        return True
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
    save_index(index)


def _remove_from_index(snapshot_id: str):
    """Remove snapshot from index"""
    index = list_historical_snapshots()
    index = [s for s in index if s["id"] != snapshot_id]
    save_index(index)


def save_index(index: List[Dict]):
    """Save index file"""
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)


def export_all_snapshots() -> Dict:
    """
    Export all snapshots for backup/transfer

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
    Import snapshots from exported data

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
            imported += 1
        except Exception as e:
            print(f"Error importing snapshot: {e}")
            continue

    return imported
