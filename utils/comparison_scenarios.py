"""
Comparison Scenarios Manager - Sub-Phase 2A
============================================
Stores and manages "what-if" comparison scenarios separately from base plans.
Each comparison scenario stores ONLY the adjustments, not full data.

Architecture:
- Base Plans (Snapshots) = Full INTAKE data (~50-200 KB)
- Comparison Scenarios = Only parameter adjustments (~1-5 KB)
- Each comparison links to a base plan via base_plan_id

Storage:
- Encrypted in browser localStorage using AES-256-GCM
- Index stored at: ff_comparisons_index
- Individual comparisons: ff_comparison_{id}

Author: Family Forecast Development Team
Created: November 14, 2025
"""

import json
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any
from utils.encryption import encrypt_data, decrypt_data
from streamlit_browser_storage import LocalStorage


# =============================================================================
# CONSTANTS
# =============================================================================

COMPARISONS_INDEX_KEY = "ff_comparisons_index"
COMPARISON_KEY_PREFIX = "ff_comparison_"


# =============================================================================
# LOCALSTORAGE CONNECTION
# =============================================================================

@st.cache_resource
def _get_local_storage():
    """Get localStorage instance (singleton-cached)."""
    if '_localStorage_singleton' not in st.session_state:
        print("[DEBUG comparison_scenarios] Creating localStorage singleton")
        st.session_state._localStorage_singleton = LocalStorage(key="forecash_local_storage")
    return st.session_state._localStorage_singleton


# =============================================================================
# COMPARISON ID GENERATION
# =============================================================================

def create_comparison_id() -> str:
    """
    Generate unique comparison ID using timestamp.

    Format: YYYYMMDD_HHMM
    Example: 20251114_0825

    Returns:
        Unique comparison ID string
    """
    return datetime.now().strftime("%Y%m%d_%H%M")


# =============================================================================
# SAVE COMPARISON SCENARIO
# =============================================================================

def save_comparison_scenario(
    base_plan_id: str,
    name: str,
    description: str,
    adjustments: Dict[str, Any],
    simulation_results: Optional[Dict[str, Any]] = None
) -> str:
    """
    Save a comparison scenario to encrypted localStorage.

    Args:
        base_plan_id: ID of the base plan this comparison is based on
        name: User-friendly name (e.g., "Retire at 67")
        description: Detailed description (e.g., "Delay retirement by 2 years")
        adjustments: Dict of parameter adjustments:
            - adjusted_income: float (annual income)
            - adjusted_expenses: float (annual expenses)
            - adjusted_return_rate: float (investment return %, as decimal)
            - adjusted_inflation_rate: float (inflation %, as decimal)
        simulation_results: Optional dict with simulation results for display

    Returns:
        comparison_id: Unique ID of saved comparison

    Example:
        >>> comparison_id = save_comparison_scenario(
        ...     base_plan_id="20251114_0800",
        ...     name="Retire at 67",
        ...     description="Delay retirement by 2 years, reduce expenses",
        ...     adjustments={
        ...         "adjusted_income": 85000,
        ...         "adjusted_expenses": 45000,
        ...         "adjusted_return_rate": 0.07,
        ...         "adjusted_inflation_rate": 0.03
        ...     }
        ... )
    """
    print(f"[SAVE COMPARISON] Starting save for base_plan_id: {base_plan_id}")

    # Generate unique comparison ID
    comparison_id = create_comparison_id()
    print(f"[SAVE COMPARISON] Generated comparison_id: {comparison_id}")

    # Build comparison data structure
    comparison_data = {
        "id": comparison_id,
        "base_plan_id": base_plan_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "adjustments": adjustments,
        "simulation_results": simulation_results or {}
    }

    print(f"[SAVE COMPARISON] Comparison data: {list(comparison_data.keys())}")

    try:
        # Encrypt comparison data
        localS = _get_local_storage()
        encrypted_data = encrypt_data(comparison_data, localS)
        print(f"[SAVE COMPARISON] Encrypted data length: {len(str(encrypted_data))}")

        # Save to localStorage
        storage_key = f"{COMPARISON_KEY_PREFIX}{comparison_id}"
        localS.setItem(storage_key, encrypted_data)
        print(f"[SAVE COMPARISON] Saved to localStorage: {storage_key}")

        # Update comparisons index
        _update_comparisons_index(comparison_id, base_plan_id, name)
        print(f"[SAVE COMPARISON] Updated index")

        print(f"[OK] Comparison scenario saved: {name} (ID: {comparison_id})")
        return comparison_id

    except Exception as e:
        print(f"[ERROR] Failed to save comparison scenario: {e}")
        import traceback
        traceback.print_exc()
        return ""


# =============================================================================
# LOAD COMPARISON SCENARIO
# =============================================================================

def load_comparison_scenario(comparison_id: str) -> Optional[Dict[str, Any]]:
    """
    Load a comparison scenario from localStorage.

    Args:
        comparison_id: ID of comparison to load

    Returns:
        Decrypted comparison data dict or None if not found

    Example:
        >>> comparison = load_comparison_scenario("20251114_0825")
        >>> if comparison:
        ...     print(f"Name: {comparison['name']}")
        ...     print(f"Adjustments: {comparison['adjustments']}")
    """
    print(f"[LOAD COMPARISON] Loading comparison: {comparison_id}")

    storage_key = f"{COMPARISON_KEY_PREFIX}{comparison_id}"

    try:
        localS = _get_local_storage()
        encrypted_data = localS.getItem(storage_key)

        if not encrypted_data:
            print(f"[WARN] Comparison not found: {storage_key}")
            return None

        print(f"[LOAD COMPARISON] Found encrypted data ({len(str(encrypted_data))} chars)")

        # Decrypt comparison data
        comparison_data = decrypt_data(encrypted_data, localS)

        if comparison_data:
            print(f"[OK] Loaded comparison: {comparison_data.get('name')}")
            return comparison_data
        else:
            print(f"[ERROR] Decryption failed for comparison: {comparison_id}")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to load comparison {comparison_id}: {e}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# GET COMPARISONS INDEX
# =============================================================================

def get_comparisons_index() -> List[Dict[str, str]]:
    """
    Get index of all saved comparison scenarios.

    Returns:
        List of comparison metadata dicts with keys:
        - id: comparison ID
        - base_plan_id: linked base plan ID
        - name: comparison name
        - created_at: ISO timestamp

    Example:
        >>> index = get_comparisons_index()
        >>> for comp in index:
        ...     print(f"{comp['name']} (base: {comp['base_plan_id']})")
    """
    print(f"[GET INDEX] Loading comparisons index")

    try:
        localS = _get_local_storage()
        encrypted_index = localS.getItem(COMPARISONS_INDEX_KEY)

        if not encrypted_index:
            print(f"[INFO] No comparisons index found, returning empty list")
            return []

        print(f"[GET INDEX] Found encrypted index ({len(str(encrypted_index))} chars)")

        # Decrypt index
        index_data = decrypt_data(encrypted_index, localS)
        comparisons = index_data.get("comparisons", [])

        print(f"[OK] Loaded {len(comparisons)} comparisons from index")
        return comparisons

    except Exception as e:
        print(f"[ERROR] Failed to load comparisons index: {e}")
        import traceback
        traceback.print_exc()
        return []


# =============================================================================
# GET COMPARISONS FOR SPECIFIC BASE PLAN
# =============================================================================

def get_comparisons_for_plan(base_plan_id: str) -> List[Dict[str, str]]:
    """
    Get all comparison scenarios for a specific base plan.

    Args:
        base_plan_id: ID of base plan (snapshot ID)

    Returns:
        List of comparisons linked to this base plan

    Example:
        >>> comparisons = get_comparisons_for_plan("20251114_0800")
        >>> print(f"Found {len(comparisons)} comparisons for this plan")
    """
    print(f"[GET COMPARISONS FOR PLAN] base_plan_id: {base_plan_id}")

    all_comparisons = get_comparisons_index()
    filtered = [c for c in all_comparisons if c.get("base_plan_id") == base_plan_id]

    print(f"[OK] Found {len(filtered)} comparisons for base plan {base_plan_id}")
    return filtered


# =============================================================================
# DELETE COMPARISON SCENARIO
# =============================================================================

def delete_comparison_scenario(comparison_id: str) -> bool:
    """
    Delete a comparison scenario from localStorage.

    Args:
        comparison_id: ID of comparison to delete

    Returns:
        True if deleted successfully, False otherwise

    Example:
        >>> success = delete_comparison_scenario("20251114_0825")
        >>> if success:
        ...     print("Comparison deleted")
    """
    print(f"[DELETE COMPARISON] Deleting comparison: {comparison_id}")

    storage_key = f"{COMPARISON_KEY_PREFIX}{comparison_id}"

    try:
        localS = _get_local_storage()

        # Remove from localStorage
        localS.removeItem(storage_key)
        print(f"[DELETE COMPARISON] Removed from localStorage: {storage_key}")

        # Update index
        _remove_from_comparisons_index(comparison_id)
        print(f"[DELETE COMPARISON] Updated index")

        print(f"[OK] Comparison deleted: {comparison_id}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to delete comparison {comparison_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# LIST ALL COMPARISON SCENARIOS
# =============================================================================

def list_comparison_scenarios() -> List[Dict[str, Any]]:
    """
    List all comparison scenarios with full details.

    Returns:
        List of all comparison scenario objects (fully loaded)

    Example:
        >>> all_comparisons = list_comparison_scenarios()
        >>> for comp in all_comparisons:
        ...     print(f"{comp['name']}: {comp['description']}")
    """
    print(f"[LIST COMPARISONS] Loading all comparison scenarios")

    index = get_comparisons_index()
    comparisons = []

    for meta in index:
        comp_data = load_comparison_scenario(meta["id"])
        if comp_data:
            comparisons.append(comp_data)

    print(f"[OK] Loaded {len(comparisons)} full comparison scenarios")
    return comparisons


# =============================================================================
# INTERNAL HELPER FUNCTIONS
# =============================================================================

def _update_comparisons_index(
    comparison_id: str,
    base_plan_id: str,
    name: str
) -> None:
    """
    Internal: Update the comparisons index with new comparison.

    Args:
        comparison_id: New comparison ID
        base_plan_id: Base plan this comparison links to
        name: Comparison name
    """
    print(f"[UPDATE INDEX] Adding comparison to index: {comparison_id}")

    # Load existing index
    index = get_comparisons_index()

    # Add new comparison metadata
    index.append({
        "id": comparison_id,
        "base_plan_id": base_plan_id,
        "name": name,
        "created_at": datetime.now().isoformat()
    })

    print(f"[UPDATE INDEX] Index now has {len(index)} comparisons")

    try:
        localS = _get_local_storage()

        # Encrypt and save updated index
        index_data = {"comparisons": index}
        encrypted_index = encrypt_data(index_data, localS)
        localS.setItem(COMPARISONS_INDEX_KEY, encrypted_index)

        print(f"[OK] Updated comparisons index")

    except Exception as e:
        print(f"[ERROR] Failed to update comparisons index: {e}")
        import traceback
        traceback.print_exc()


def _remove_from_comparisons_index(comparison_id: str) -> None:
    """
    Internal: Remove comparison from index.

    Args:
        comparison_id: ID of comparison to remove
    """
    print(f"[REMOVE FROM INDEX] Removing comparison from index: {comparison_id}")

    # Load existing index
    index = get_comparisons_index()

    # Filter out the deleted comparison
    updated_index = [c for c in index if c["id"] != comparison_id]

    print(f"[REMOVE FROM INDEX] Index reduced from {len(index)} to {len(updated_index)} comparisons")

    try:
        localS = _get_local_storage()

        # Encrypt and save updated index
        index_data = {"comparisons": updated_index}
        encrypted_index = encrypt_data(index_data, localS)
        localS.setItem(COMPARISONS_INDEX_KEY, encrypted_index)

        print(f"[OK] Removed comparison from index")

    except Exception as e:
        print(f"[ERROR] Failed to remove from comparisons index: {e}")
        import traceback
        traceback.print_exc()
