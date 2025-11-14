# utils/local_storage_fixed.py - WORKING localStorage using extra_streamlit_components
"""
Browser localStorage integration using CookieManager (works in iframes!).

This module provides encrypted localStorage persistence using a proven library
that handles the JavaScript/Python bridge properly.
"""

import streamlit as st
import json
from typing import Dict, Any, Optional
from utils.encryption import encrypt_data, decrypt_data
import extra_streamlit_components as stx


# Global cookie manager (reused across calls for efficiency)
_cookie_manager = None


def get_cookie_manager():
    """Get or create cookie manager instance."""
    global _cookie_manager
    if _cookie_manager is None:
        _cookie_manager = stx.CookieManager()
    return _cookie_manager


def save_to_local_storage_encrypted(key: str, data: Dict[str, Any]) -> bool:
    """
    Save ENCRYPTED data to browser's cookies using CookieManager (persistent storage).

    Uses browser cookies with 1-year expiration for persistence across sessions.
    Data is encrypted with AES-256-GCM before storing.

    Args:
        key: Storage key (e.g., 'family_forecast_snapshot_index')
        data: Dictionary to encrypt and save

    Returns:
        True if successful

    Example:
        >>> data = {"snapshots": [...]}
        >>> save_to_local_storage_encrypted('snapshot_index', data)
        True
    """
    try:
        print(f"[DEBUG] Starting save for key: {key}")

        # Encrypt the data
        encrypted_string = encrypt_data(data)
        print(f"[DEBUG] Encrypted data length: {len(encrypted_string)}")

        # Use the global CookieManager instance
        cookie_manager = get_cookie_manager()
        print(f"[DEBUG] Using CookieManager: {cookie_manager}")

        # IMPORTANT: CookieManager.set() is async - cookie won't be available until NEXT rerun
        # Use relaxed settings to ensure cookie gets saved
        print(f"[DEBUG] Calling cookie_manager.set() with key={key}")
        result = cookie_manager.set(
            cookie=key,  # Cookie name
            val=encrypted_string,  # Cookie value
            max_age=31536000,  # 1 year in seconds
            path='/',  # Available on all paths
            same_site='lax',  # Less restrictive than 'strict'
            key=f"set_{key}"  # Streamlit widget key (must be unique)
        )
        print(f"[DEBUG] cookie_manager.set() returned: {result}")

        print(f"[OK] Saved to cookies: {key} (available after page rerun)")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to save to cookies: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_from_local_storage_encrypted(key: str) -> Optional[Dict[str, Any]]:
    """
    Load and DECRYPT data from browser's cookies using CookieManager.

    Args:
        key: Storage key (e.g., 'family_forecast_snapshot_index')

    Returns:
        Decrypted dictionary, or None if not found

    Example:
        >>> data = load_from_local_storage_encrypted('snapshot_index')
        >>> if data:
        >>>     print(f"Loaded {len(data)} snapshots")
    """
    try:
        # Get cookie manager
        cookie_manager = get_cookie_manager()

        # Load all cookies
        cookies = cookie_manager.get_all()

        # DEBUG: Print what we got
        print(f"[DEBUG] Cookies from get_all(): {cookies}")
        print(f"[DEBUG] Looking for key: {key}")
        if cookies:
            print(f"[DEBUG] Available keys: {list(cookies.keys())}")

        if cookies and key in cookies:
            encrypted_string = cookies[key]
            print(f"[DEBUG] Found encrypted string, length: {len(encrypted_string)}")

            # Decrypt the data
            decrypted_data = decrypt_data(encrypted_string)

            if decrypted_data:
                print(f"[OK] Loaded from cookies: {key}")
                return decrypted_data
            else:
                print(f"[WARN] Decryption failed for: {key}")
                return None
        else:
            print(f"[INFO] No data in cookies for: {key}")
            return None

    except Exception as e:
        print(f"[ERROR] Failed to load from cookies: {e}")
        import traceback
        traceback.print_exc()
        return None


def delete_from_local_storage(key: str) -> bool:
    """
    Delete data from localStorage.

    Args:
        key: Storage key to delete

    Returns:
        True if successful
    """
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete(cookie=key, key=f"del_{key}")
        print(f"[OK] Deleted from localStorage: {key}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to delete from localStorage: {e}")
        return False
