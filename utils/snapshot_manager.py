# utils/snapshot_manager.py - Snapshot Versioning System
"""
Manages multiple saved retirement plan snapshots with versioning.

FEATURES:
- Save multiple plan versions ("Conservative", "Aggressive", etc.)
- Each snapshot has unique ID, name, metadata
- Export all snapshots to encrypted backup file (.ffb)
- Import snapshots from backup file
- Compare snapshots side-by-side (future)
- Historical tracking for AI analysis (future)

SNAPSHOT STRUCTURE:
{
    "id": "20251106_0230",
    "name": "Initial Retirement Plan",
    "created": "2025-11-06T02:30:00",
    "metadata": {
        "user_name": "Serge Castro",
        "user_age": 65,
        "partner_age": 63,
        "net_worth": 850000,
        "monthly_surplus": 350
    },
    "data": { ... full intake data ... }
}
"""

import json
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional
from utils.local_storage import save_to_local_storage_encrypted, load_from_local_storage_encrypted
from utils.encryption import encrypt_data, decrypt_data


# =============================================================================
# SNAPSHOT ID GENERATION
# =============================================================================

def create_snapshot_id() -> str:
    """
    Create unique snapshot ID from current timestamp.

    Format: YYYYMMDD_HHMM
    Example: 20251106_0230 = Nov 6, 2025 @ 2:30 AM

    Returns:
        Snapshot ID string
    """
    return datetime.now().strftime("%Y%m%d_%H%M")


# =============================================================================
# SNAPSHOT INDEX MANAGEMENT
# =============================================================================

def get_snapshots_index() -> Dict[str, Any]:
    """
    Get snapshots index from session_state (TEMPORARY FIX).

    Returns:
        Index dict with current_snapshot_id and snapshots list
    """
    # TEMPORARY: Use session_state instead of localStorage
    # (localStorage retrieval has JavaScript async issues)
    if 'snapshots_index' not in st.session_state:
        st.session_state.snapshots_index = {
            "current_snapshot_id": None,
            "snapshots": []
        }

    return st.session_state.snapshots_index


def save_snapshots_index(index: Dict[str, Any]) -> bool:
    """
    Save snapshots index to session_state (TEMPORARY FIX).

    Args:
        index: Index dict with current_snapshot_id and snapshots list

    Returns:
        True if successful
    """
    # TEMPORARY: Use session_state instead of localStorage
    st.session_state.snapshots_index = index
    return True


# =============================================================================
# SNAPSHOT CRUD OPERATIONS
# =============================================================================

def save_snapshot(data: Dict[str, Any], snapshot_name: Optional[str] = None) -> str:
    """
    Save a new snapshot with unique ID and metadata.

    Args:
        data: Full INTAKE data dictionary
        snapshot_name: Optional custom name (e.g., "Conservative Plan")

    Returns:
        Snapshot ID (for reference)

    Example:
        >>> intake_data = {"input_user_name": "John", ...}
        >>> snapshot_id = save_snapshot(intake_data, "Initial Plan")
        >>> print(snapshot_id)  # "20251106_0230"
    """
    # Create unique ID
    snapshot_id = create_snapshot_id()

    # Generate default name if not provided
    if not snapshot_name:
        snapshot_name = f"Plan - {datetime.now().strftime('%b %d, %Y @ %I:%M %p')}"

    # Extract metadata from data
    metadata = {
        "user_name": data.get("input_user_name", "Unknown"),
        "user_age": data.get("input_age", 0),
        "partner_exists": data.get("input_partner_exists", False),
        "partner_name": data.get("input_partner_name", ""),
        "partner_age": data.get("input_partner_age", 0),
        # Calculate net worth
        "net_worth": _calculate_net_worth(data),
        "monthly_surplus": _calculate_monthly_surplus(data)
    }

    # Create snapshot object
    snapshot = {
        "id": snapshot_id,
        "name": snapshot_name,
        "created": datetime.now().isoformat(),
        "metadata": metadata
    }

    # Save snapshot data to localStorage (encrypted)
    snapshot_key = f"family_forecast_snapshot_{snapshot_id}"

    # DEBUG: Print what we're saving
    print(f"DEBUG: Saving snapshot '{snapshot_name}' with ID {snapshot_id}")

    success = save_to_local_storage_encrypted(snapshot_key, data)

    if not success:
        print(f"DEBUG: FAILED to save snapshot data for {snapshot_id}")
        return None

    # Update snapshots index
    index = get_snapshots_index()
    print(f"DEBUG: Current index before update: {len(index.get('snapshots', []))} snapshots")

    index["current_snapshot_id"] = snapshot_id
    index["snapshots"].append(snapshot)

    print(f"DEBUG: Updated index: {len(index['snapshots'])} snapshots")

    save_snapshots_index(index)

    return snapshot_id


def load_snapshot(snapshot_id: str) -> Optional[Dict[str, Any]]:
    """
    Load snapshot data by ID.

    Args:
        snapshot_id: Snapshot ID (e.g., "20251106_0230")

    Returns:
        Full INTAKE data dict, or None if not found

    Example:
        >>> data = load_snapshot("20251106_0230")
        >>> if data:
        >>>     print(f"User: {data['input_user_name']}")
    """
    snapshot_key = f"family_forecast_snapshot_{snapshot_id}"
    return load_from_local_storage_encrypted(snapshot_key)


def list_snapshots() -> List[Dict[str, Any]]:
    """
    Get list of all saved snapshots (metadata only, not full data).

    Returns:
        List of snapshot metadata dicts

    Example:
        >>> snapshots = list_snapshots()
        >>> for snap in snapshots:
        >>>     print(f"{snap['name']} - {snap['created']}")
    """
    index = get_snapshots_index()
    return index.get("snapshots", [])


def delete_snapshot(snapshot_id: str) -> bool:
    """
    Delete a snapshot by ID.

    Args:
        snapshot_id: Snapshot ID to delete

    Returns:
        True if successful

    Example:
        >>> delete_snapshot("20251106_0230")
    """
    # Remove from localStorage
    snapshot_key = f"family_forecast_snapshot_{snapshot_id}"
    # TODO: Implement delete from localStorage
    # For now, just update index

    # Update index
    index = get_snapshots_index()
    index["snapshots"] = [s for s in index["snapshots"] if s["id"] != snapshot_id]

    # If we deleted current snapshot, clear current_snapshot_id
    if index["current_snapshot_id"] == snapshot_id:
        index["current_snapshot_id"] = None

    save_snapshots_index(index)
    return True


def rename_snapshot(snapshot_id: str, new_name: str) -> bool:
    """
    Rename a snapshot.

    Args:
        snapshot_id: Snapshot ID
        new_name: New name for snapshot

    Returns:
        True if successful
    """
    index = get_snapshots_index()

    for snapshot in index["snapshots"]:
        if snapshot["id"] == snapshot_id:
            snapshot["name"] = new_name
            save_snapshots_index(index)
            return True

    return False


def set_current_snapshot(snapshot_id: str) -> bool:
    """
    Set the current active snapshot.

    Args:
        snapshot_id: Snapshot ID to set as current

    Returns:
        True if successful
    """
    index = get_snapshots_index()
    index["current_snapshot_id"] = snapshot_id
    return save_snapshots_index(index)


def get_current_snapshot() -> Optional[Dict[str, Any]]:
    """
    Get the currently active snapshot data.

    Returns:
        Snapshot data dict, or None if no current snapshot
    """
    index = get_snapshots_index()
    current_id = index.get("current_snapshot_id")

    if current_id:
        return load_snapshot(current_id)

    return None


# =============================================================================
# EXPORT / IMPORT ALL SNAPSHOTS
# =============================================================================

def export_all_snapshots() -> Dict[str, Any]:
    """
    Export all snapshots to a single encrypted backup object.

    Returns:
        Backup object containing:
        - All snapshot metadata
        - All snapshot data (encrypted)
        - Export timestamp
        - Version info

    Example:
        >>> backup = export_all_snapshots()
        >>> json_str = json.dumps(backup)
        >>> # User can download this as .ffb file
    """
    index = get_snapshots_index()
    snapshots_data = []

    # Load full data for each snapshot
    for snapshot in index["snapshots"]:
        snapshot_id = snapshot["id"]
        data = load_snapshot(snapshot_id)

        if data:
            snapshots_data.append({
                "metadata": snapshot,
                "data": data
            })

    # Create backup object
    backup = {
        "version": "1.0",
        "app": "Family Forecast",
        "exported": datetime.now().isoformat(),
        "snapshot_count": len(snapshots_data),
        "current_snapshot_id": index.get("current_snapshot_id"),
        "snapshots": snapshots_data
    }

    return backup


def import_snapshots(backup: Dict[str, Any], merge_mode: str = "merge") -> bool:
    """
    Import snapshots from backup object.

    Args:
        backup: Backup object from export_all_snapshots()
        merge_mode: "merge" (add to existing) or "replace" (clear existing)

    Returns:
        True if successful

    Example:
        >>> # User uploads .ffb file
        >>> backup = json.loads(file_content)
        >>> import_snapshots(backup, merge_mode="merge")
    """
    try:
        # Validate backup format
        if backup.get("app") != "Family Forecast":
            st.error("❌ Invalid backup file format")
            return False

        # Get current index
        index = get_snapshots_index()

        if merge_mode == "replace":
            # Clear existing snapshots
            index = {
                "current_snapshot_id": None,
                "snapshots": []
            }

        # Import each snapshot
        for snapshot_obj in backup.get("snapshots", []):
            metadata = snapshot_obj["metadata"]
            data = snapshot_obj["data"]
            snapshot_id = metadata["id"]

            # Save snapshot data
            snapshot_key = f"family_forecast_snapshot_{snapshot_id}"
            save_to_local_storage_encrypted(snapshot_key, data)

            # Add to index (avoid duplicates)
            if not any(s["id"] == snapshot_id for s in index["snapshots"]):
                index["snapshots"].append(metadata)

        # Set current snapshot if provided
        if backup.get("current_snapshot_id"):
            index["current_snapshot_id"] = backup["current_snapshot_id"]

        # Save updated index
        save_snapshots_index(index)

        return True

    except Exception as e:
        st.error(f"❌ Import failed: {e}")
        return False


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _calculate_net_worth(data: Dict[str, Any]) -> float:
    """Calculate net worth from intake data"""
    assets = sum([
        data.get("input_ira_balance", 0),
        data.get("input_four01k_403b_balance", 0),
        data.get("input_partner_ira_balance", 0),
        data.get("input_partner_four01k_403b_balance", 0),
        data.get("input_taxable_investment_accounts", 0),
        data.get("input_high_yield_savings_account", 0),
        data.get("input_hsa_balance", 0),
        data.get("input_five29_plan_balance", 0),
        data.get("input_primary_residence_value", 0),
        data.get("input_secondary_residence_value", 0),
        data.get("input_vehicles_value", 0),
        data.get("input_jewelry_collectibles_value", 0),
        data.get("input_business_ownership_value", 0),
        data.get("input_cryptocurrency_holdings", 0),
        data.get("input_other_assets", 0)
    ])

    liabilities = sum([
        data.get("input_mortgage_balance", 0),
        data.get("input_auto_loan_balance", 0),
        data.get("input_student_loan_balance", 0),
        data.get("input_credit_card_debt", 0),
        data.get("input_other_liabilities", 0)
    ])

    return assets - liabilities


def _calculate_monthly_surplus(data: Dict[str, Any]) -> float:
    """Calculate monthly surplus/deficit from intake data"""
    income = data.get("input_total_income", 0)
    expenses = data.get("input_total_expenses", 0)
    return income - expenses
