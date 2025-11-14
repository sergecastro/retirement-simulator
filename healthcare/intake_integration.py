"""
Healthcare Hub - INTAKE Data Integration
==========================================
Automatically loads user data from saved INTAKE snapshots to pre-fill
the Healthcare Hub calculator forms.

Author: Family Forecast Development Team
Created: November 14, 2025
"""

import json
import os
from typing import Dict, Optional, Any


def load_user_data_for_healthcare() -> Dict[str, Any]:
    """
    Load user's INTAKE data for Healthcare Hub auto-fill.

    Reads the current snapshot from .snapshot_cache and extracts
    relevant fields for the IRMAA calculator.

    Returns:
        dict: User data with the following keys:
            - age: int (user's current age)
            - partner_exists: bool (has partner/spouse)
            - filing_status: str ("single" or "married")
            - total_income: float (annual income)
            - social_security_income: float (SS benefits)
            - pension_income: float (pension/annuity)
            - investment_income: float (dividends, interest)
            - partner_age: int or None (partner's age if exists)
            - user_name: str (for personalization)
            - data_loaded: bool (True if snapshot found, False otherwise)

    Example:
        >>> data = load_user_data_for_healthcare()
        >>> print(f"Age: {data['age']}, Income: ${data['total_income']:,.0f}")
        Age: 76, Income: $6,000
    """

    # Default return structure (if no data found)
    default_data = {
        'age': 65,
        'partner_exists': False,
        'filing_status': 'single',
        'total_income': 100000,
        'social_security_income': 30000,
        'pension_income': 0,
        'investment_income': 0,
        'partner_age': None,
        'user_name': '',
        'data_loaded': False
    }

    try:
        # Step 1: Find the snapshot cache directory
        # Go up one level from healthcare/ to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        snapshot_cache = os.path.join(project_root, '.snapshot_cache')

        if not os.path.exists(snapshot_cache):
            print("[HEALTHCARE INTEGRATION] Warning: .snapshot_cache directory not found")
            return default_data

        # Step 2: Read the snapshots index to get current snapshot ID
        index_file = os.path.join(snapshot_cache, 'snapshots_index.json')

        if not os.path.exists(index_file):
            print("[HEALTHCARE INTEGRATION] Warning: snapshots_index.json not found")
            return default_data

        with open(index_file, 'r') as f:
            index_data = json.load(f)

        current_snapshot_id = index_data.get('current_snapshot_id')

        if not current_snapshot_id:
            print("[HEALTHCARE INTEGRATION] Warning: No current_snapshot_id in index")
            return default_data

        # Step 3: Load the current snapshot file
        snapshot_file = os.path.join(snapshot_cache, f'snapshot_{current_snapshot_id}.json')

        if not os.path.exists(snapshot_file):
            print(f"[HEALTHCARE INTEGRATION] Warning: Snapshot file not found: {snapshot_file}")
            return default_data

        with open(snapshot_file, 'r') as f:
            snapshot_data = json.load(f)

        print(f"[HEALTHCARE INTEGRATION] OK - Loaded snapshot: {current_snapshot_id}")

        # Step 4: Extract relevant fields
        user_age = int(snapshot_data.get('input_age', 65))
        partner_exists = bool(snapshot_data.get('input_partner_exists', False))
        partner_age = int(snapshot_data.get('input_partner_age', 0)) if partner_exists else None

        # Determine filing status
        filing_status = 'married' if partner_exists else 'single'

        # Extract income sources
        total_income = float(snapshot_data.get('input_total_income', 0))
        social_security = float(snapshot_data.get('input_social_security_income', 0))
        pension = float(snapshot_data.get('input_pension_income', 0))
        investment = float(snapshot_data.get('input_investment_income', 0))

        # User name for personalization
        user_name = snapshot_data.get('input_user_name', '')

        # Build result
        result = {
            'age': user_age,
            'partner_exists': partner_exists,
            'filing_status': filing_status,
            'total_income': total_income,
            'social_security_income': social_security,
            'pension_income': pension,
            'investment_income': investment,
            'partner_age': partner_age,
            'user_name': user_name,
            'data_loaded': True
        }

        print(f"[HEALTHCARE INTEGRATION] OK - Extracted data:")
        print(f"  - User: {user_name}")
        print(f"  - Age: {user_age}")
        print(f"  - Filing Status: {filing_status}")
        print(f"  - Total Income: ${total_income:,.0f}")
        print(f"  - Social Security: ${social_security:,.0f}")

        return result

    except Exception as e:
        print(f"[HEALTHCARE INTEGRATION] ERROR - Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return default_data


def get_snapshot_name() -> str:
    """
    Get the name of the current snapshot for display purposes.

    Returns:
        str: Snapshot name (e.g., "11/14/2025 REALISTIC SERGE RETIREMENT PLAN")
             or empty string if not found
    """
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        index_file = os.path.join(project_root, '.snapshot_cache', 'snapshots_index.json')

        if not os.path.exists(index_file):
            return ""

        with open(index_file, 'r') as f:
            index_data = json.load(f)

        current_snapshot_id = index_data.get('current_snapshot_id')

        if not current_snapshot_id:
            return ""

        # Find the snapshot with matching ID
        snapshots = index_data.get('snapshots', [])
        for snapshot in snapshots:
            if snapshot.get('id') == current_snapshot_id:
                return snapshot.get('name', '')

        return ""

    except Exception as e:
        print(f"[HEALTHCARE INTEGRATION] Error getting snapshot name: {e}")
        return ""


# Test function (for debugging)
if __name__ == "__main__":
    print("Testing INTAKE Integration...")
    print("=" * 50)

    data = load_user_data_for_healthcare()

    print("\nLoaded Data:")
    for key, value in data.items():
        print(f"  {key}: {value}")

    snapshot_name = get_snapshot_name()
    if snapshot_name:
        print(f"\nSnapshot Name: {snapshot_name}")
