"""
Welcome Back helper for returning users.
Checks localStorage directly for saved snapshot data.
No cookies needed - localStorage already has the user's data!
"""
import streamlit as st
from datetime import datetime

def check_for_returning_user():
    """
    Check localStorage for returning user data.
    Call this ONCE at Welcome page start.
    Sets session_state with user info if found.

    Returns True if returning user found, False otherwise.
    """
    # Only check ONCE per session to prevent rerun loops
    if st.session_state.get('_ff_returning_user_checked', False):
        return st.session_state.get('_ff_is_returning_user', False)

    st.session_state['_ff_returning_user_checked'] = True
    st.session_state['_ff_is_returning_user'] = False

    try:
        from utils.snapshot_manager import _get_local_storage, decrypt_data

        localS = _get_local_storage()
        if not localS:
            return False

        # Try to read encrypted index from localStorage
        encrypted_index = localS.get('ff_snapshots_index')
        if not encrypted_index:
            print("[WELCOME BACK] No snapshots index in localStorage")
            return False

        # Decrypt and check for snapshots
        index = decrypt_data(encrypted_index, localS)
        if not index or not index.get('snapshots'):
            print("[WELCOME BACK] No snapshots in index")
            return False

        # Get most recent snapshot
        most_recent = index['snapshots'][-1]
        snapshot_id = most_recent['id']

        # Try to load snapshot to get user name
        encrypted_data = localS.get(f'ff_snapshot_{snapshot_id}')
        if encrypted_data:
            snapshot_data = decrypt_data(encrypted_data, localS)
            if snapshot_data:
                user_name = snapshot_data.get('input_user_name', '')
                if user_name:
                    # Extract first name only
                    first_name = user_name.strip().split()[0]

                    # Get snapshot date
                    created = most_recent.get('created', '')
                    formatted_date = ""
                    if created:
                        try:
                            dt = datetime.fromisoformat(created)
                            day = dt.day
                            suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
                            formatted_date = dt.strftime(f"%B {day}{suffix} at %-I:%M %p")
                        except:
                            formatted_date = created[:10] if len(created) > 10 else created

                    # Store in session_state
                    st.session_state['_ff_returning_user_name'] = first_name
                    st.session_state['_ff_returning_user_date'] = formatted_date
                    st.session_state['_ff_is_returning_user'] = True
                    print(f"[WELCOME BACK] Found returning user: {first_name}")
                    return True

        return False

    except Exception as e:
        print(f"[WELCOME BACK] Error checking localStorage: {e}")
        return False

def has_returning_user() -> bool:
    """Check if we detected a returning user."""
    return st.session_state.get('_ff_is_returning_user', False)

def get_welcome_back_info() -> dict:
    """Get returning user info from session_state."""
    return {
        "name": st.session_state.get('_ff_returning_user_name', ''),
        "formatted_date": st.session_state.get('_ff_returning_user_date', '')
    }

def clear_returning_user():
    """Clear returning user status (for Start Fresh)."""
    st.session_state['_ff_is_returning_user'] = False
    st.session_state['_ff_returning_user_name'] = ''
    st.session_state['_ff_returning_user_date'] = ''
    st.session_state['_ff_returning_user_checked'] = False
    print("[WELCOME BACK] Cleared returning user status")

# Keep these for backward compatibility (no-op now)
def set_welcome_back_cookie(first_name: str, save_timestamp: str = None):
    """No longer uses cookies - localStorage has the data."""
    pass

def clear_welcome_back_cookies():
    """Alias for clear_returning_user."""
    clear_returning_user()

def init_cookie_reader():
    """No longer needed - using localStorage directly."""
    pass

def load_cookie_from_transfer():
    """No longer needed - using localStorage directly."""
    pass
