# utils/local_storage.py - Simple browser localStorage (NO encryption)
"""
Browser localStorage for Family Forecast retirement app.

PRIVACY MODEL:
- Data stored in USER'S BROWSER as plain JSON
- Each browser has isolated localStorage (cannot access other users' data)
- Data never sent to server
- Perfect for cloud deployment (Render, etc.)

NO ENCRYPTION:
- Data is already private (localStorage isolated per browser)
- Simplicity and reliability over obfuscation
- Users can inspect their own data if needed

IMPORTANT: LocalStorage must be initialized in your main app file like this:

    from streamlit_local_storage import LocalStorage

    if 'localS' not in st.session_state:
        st.session_state.localS = LocalStorage()
    localS = st.session_state.localS

Then pass localS to these functions.
"""

import streamlit as st
from streamlit_local_storage import LocalStorage
import json
from typing import Dict, Any, Optional


def save_to_local_storage(localS: LocalStorage, key: str, data: Dict[str, Any]) -> bool:
    """
    Save data to USER'S browser localStorage as plain JSON.

    Args:
        localS: LocalStorage instance (from st.session_state.localS)
        key: Storage key (e.g., 'snapshot_index')
        data: Dictionary to save

    Returns:
        True if successful

    Example:
        >>> localS = st.session_state.localS
        >>> data = {"user_name": "John", "age": 65}
        >>> save_to_local_storage(localS, 'my_data', data)
        True
    """
    try:
        # Convert dict to JSON string
        json_string = json.dumps(data, ensure_ascii=False)

        # Save to browser localStorage
        localS.setItem(key, json_string)

        print(f"[OK] Saved to browser localStorage: {key}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to save to browser localStorage: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_from_local_storage(localS: LocalStorage, key: str) -> Optional[Dict[str, Any]]:
    """
    Load data from USER'S browser localStorage.

    Args:
        localS: LocalStorage instance (from st.session_state.localS)
        key: Storage key (e.g., 'snapshot_index')

    Returns:
        Dictionary if found, None if not found

    Example:
        >>> localS = st.session_state.localS
        >>> data = load_from_local_storage(localS, 'my_data')
        >>> print(data)  # {"user_name": "John", "age": 65}
    """
    try:
        # Load from browser localStorage
        json_string = localS.getItem(key)

        if not json_string:
            print(f"[INFO] No data in browser localStorage for: {key}")
            return None

        # Parse JSON string to dict
        data = json.loads(json_string)

        print(f"[OK] Loaded from browser localStorage: {key}")
        return data

    except Exception as e:
        print(f"[ERROR] Failed to load from browser localStorage: {e}")
        import traceback
        traceback.print_exc()
        return None


def delete_from_local_storage(localS: LocalStorage, key: str) -> bool:
    """
    Delete data from USER'S browser localStorage.

    Args:
        localS: LocalStorage instance (from st.session_state.localS)
        key: Storage key to delete

    Returns:
        True if successful

    Example:
        >>> localS = st.session_state.localS
        >>> delete_from_local_storage(localS, 'my_data')
        True
    """
    try:
        localS.deleteItem(key)
        print(f"[OK] Deleted from browser localStorage: {key}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to delete from browser localStorage: {e}")
        return False
