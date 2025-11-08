# utils/local_storage_browser.py - TRUE browser localStorage using streamlit-local-storage
"""
Browser localStorage integration using streamlit-local-storage library.

This stores data in the USER'S BROWSER, not on the server.
Perfect for cloud deployment (Render, etc.)

DATA STAYS IN USER'S BROWSER ON THEIR COMPUTER.
"""

import streamlit as st
import json
from typing import Dict, Any, Optional
from utils.encryption import encrypt_data, decrypt_data

# Import the cached function from snapshot_manager
from utils.snapshot_manager import _get_local_storage


def save_to_local_storage_encrypted(key: str, data: Dict[str, Any]) -> bool:
    """
    Save ENCRYPTED data to USER'S browser localStorage.

    Data is encrypted and stored in the browser. Does NOT go to server.

    Args:
        key: Storage key (e.g., 'snapshot_index')
        data: Dictionary to encrypt and save

    Returns:
        True if successful
    """
    try:
        # Encrypt the data
        encrypted_string = encrypt_data(data)

        # Get localStorage instance
        localS = _get_local_storage()

        # Save to browser localStorage
        localS.setLocalStorageVal(key, encrypted_string)

        print(f"[OK] Saved to browser localStorage: {key}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to save to browser localStorage: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_from_local_storage_encrypted(key: str) -> Optional[Dict[str, Any]]:
    """
    Load and DECRYPT data from USER'S browser localStorage.

    Args:
        key: Storage key (e.g., 'snapshot_index')

    Returns:
        Decrypted dictionary, or None if not found
    """
    try:
        # Get localStorage instance
        localS = _get_local_storage()

        # Load from browser localStorage
        encrypted_string = localS.getLocalStorageVal(key)

        if not encrypted_string:
            print(f"[INFO] No data in browser localStorage for: {key}")
            return None

        # streamlit-local-storage returns the raw string value
        # Decrypt the data
        decrypted_data = decrypt_data(encrypted_string)

        if decrypted_data:
            print(f"[OK] Loaded from browser localStorage: {key}")
            return decrypted_data
        else:
            print(f"[WARN] Decryption failed for: {key}")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to load from browser localStorage: {e}")
        import traceback
        traceback.print_exc()
        return None


def delete_from_local_storage(key: str) -> bool:
    """
    Delete data from USER'S browser localStorage.

    Args:
        key: Storage key to delete

    Returns:
        True if successful
    """
    try:
        # Get localStorage instance
        localS = _get_local_storage()

        localS.deleteLocalStorageVal(key)
        print(f"[OK] Deleted from browser localStorage: {key}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to delete from browser localStorage: {e}")
        return False
