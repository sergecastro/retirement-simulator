"""
Safe localStorage read utility using streamlit-javascript.
Avoids the rerun loops caused by streamlit-local-storage package.

Created: December 4, 2025
Tested: Successfully reads localStorage without infinite loops

Usage:
    from utils.safe_local_storage import get_backup_credentials

    creds = get_backup_credentials()
    if creds['has_credentials']:
        email = creds['ff_user_email']
        vault_id = creds['ff_vault_id']
"""

from streamlit_javascript import st_javascript


def read_local_storage(key: str):
    """
    Safely read a single value from localStorage.

    Returns:
        - The actual value (str) if found
        - None if key doesn't exist
        - 0 if JS hasn't executed yet (will auto-rerun)

    Note: First call returns 0, subsequent call returns actual value.
    Page will auto-rerun once to get the real value.
    """
    return st_javascript(f"localStorage.getItem('{key}')")


def get_backup_credentials() -> dict:
    """
    Get user's backup credentials from localStorage.

    Returns dict with:
        - has_credentials: bool (True if user has registered)
        - ff_user_email: str or None
        - ff_vault_id: str or None
        - ready: bool (False if still waiting for JS, True when values loaded)

    Usage:
        creds = get_backup_credentials()
        if not creds['ready']:
            # Still loading, page will auto-rerun
            pass
        elif creds['has_credentials']:
            # User is registered
            email = creds['ff_user_email']
            vault_id = creds['ff_vault_id']
    """
    email = st_javascript("localStorage.getItem('ff_user_email')")
    vault_id = st_javascript("localStorage.getItem('ff_vault_id')")

    # st_javascript returns 0 on first call before JS executes
    # Only "not ready" if BOTH are 0 (first render before any JS runs)
    # If one is 0 and other has value, JS ran but that key doesn't exist
    if email == 0 and vault_id == 0:
        return {
            'has_credentials': False,
            'ff_user_email': None,
            'ff_vault_id': None,
            'ready': False
        }

    # Convert 0 to None (JS ran but key doesn't exist in localStorage)
    if email == 0:
        email = None
    if vault_id == 0:
        vault_id = None

    # Clean up values - localStorage returns null as string "null" or None
    if email in (None, "null", ""):
        email = None
    if vault_id in (None, "null", ""):
        vault_id = None

    return {
        'has_credentials': bool(email or vault_id),
        'ff_user_email': email,
        'ff_vault_id': vault_id,
        'ready': True
    }


def write_local_storage(key: str, value: str):
    """
    Write a value to localStorage using JavaScript.

    Note: For writes, the existing streamlit-browser-storage
    LocalStorage.set() also works fine. This is an alternative
    that uses the same st_javascript approach for consistency.
    """
    # Escape quotes in value
    escaped_value = value.replace("'", "\\'")
    st_javascript(f"localStorage.setItem('{key}', '{escaped_value}')")
