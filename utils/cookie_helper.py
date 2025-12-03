"""
Cookie helper for Welcome Back feature.
Stores ONLY user's first name and last save date (non-sensitive).
Uses native JavaScript cookies - no Streamlit widget conflicts.
"""
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import json

def set_welcome_back_cookie(first_name: str, save_timestamp: str = None):
    """
    Save user's first name and save date to cookie via JavaScript.
    Called after SAVE to remember the user.
    """
    if first_name and first_name.strip():
        # Extract first name only (before any space)
        first_only = first_name.strip().split()[0]

        # Use current time if not provided
        if not save_timestamp:
            save_timestamp = datetime.now().isoformat()

        # Create cookie data as JSON
        cookie_data = json.dumps({"name": first_only, "last_save": save_timestamp})

        # Set cookie via JavaScript (expires in 365 days)
        js_code = f"""
        <script>
            document.cookie = "ff_welcome_back=" + encodeURIComponent('{cookie_data}') + "; path=/; max-age=31536000; SameSite=Lax";
        </script>
        """
        components.html(js_code, height=0)
        print(f"[COOKIE] Saved welcome back: {first_only}, {save_timestamp}")

def get_welcome_back_info() -> dict:
    """
    Get user's first name and last save date from cookies.
    Returns dict with 'name', 'last_save', 'formatted_date' keys.

    NOTE: This reads from session_state cache since JavaScript can't return values synchronously.
    The cookie is read on page load via _init_cookie_reader().
    """
    return st.session_state.get('_ff_welcome_back_data', {"name": "", "last_save": "", "formatted_date": ""})

def clear_welcome_back_cookies():
    """Clear the welcome back cookie via JavaScript."""
    js_code = """
    <script>
        document.cookie = "ff_welcome_back=; path=/; max-age=0; SameSite=Lax";
    </script>
    """
    components.html(js_code, height=0)
    # Also clear session state cache
    if '_ff_welcome_back_data' in st.session_state:
        del st.session_state['_ff_welcome_back_data']
    if '_ff_cookie_checked' in st.session_state:
        del st.session_state['_ff_cookie_checked']
    print("[COOKIE] Cleared welcome back cookies")

def has_returning_user() -> bool:
    """
    Check if we have a returning user.
    Returns True if welcome back data exists in session_state.
    """
    data = st.session_state.get('_ff_welcome_back_data', {})
    return bool(data.get('name'))

def init_cookie_reader():
    """
    Initialize cookie reader - call this ONCE at app start.
    Reads cookie via JavaScript and stores in session_state.
    """
    if st.session_state.get('_ff_cookie_checked', False):
        return  # Already checked this session

    st.session_state['_ff_cookie_checked'] = True

    # JavaScript to read cookie and post to Streamlit
    js_code = """
    <script>
        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
            return null;
        }

        const cookieData = getCookie('ff_welcome_back');
        if (cookieData) {
            // Store in localStorage temporarily for Python to read
            localStorage.setItem('_ff_cookie_transfer', cookieData);
        } else {
            localStorage.removeItem('_ff_cookie_transfer');
        }
    </script>
    """
    components.html(js_code, height=0)

def load_cookie_from_transfer():
    """
    Load cookie data from localStorage transfer.
    Call this after init_cookie_reader() has run.
    """
    if '_ff_welcome_back_data' in st.session_state and st.session_state['_ff_welcome_back_data'].get('name'):
        return  # Already loaded

    try:
        from streamlit_local_storage import LocalStorage
        ls = LocalStorage()
        cookie_json = ls.get('_ff_cookie_transfer')

        if cookie_json:
            data = json.loads(cookie_json)
            name = data.get('name', '')
            last_save = data.get('last_save', '')

            # Format date for display
            formatted_date = ""
            if last_save:
                try:
                    dt = datetime.fromisoformat(last_save)
                    day = dt.day
                    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
                    formatted_date = dt.strftime(f"%B {day}{suffix} at %-I:%M %p")
                except:
                    formatted_date = last_save

            st.session_state['_ff_welcome_back_data'] = {
                "name": name,
                "last_save": last_save,
                "formatted_date": formatted_date
            }
            print(f"[COOKIE] Loaded welcome back data: {name}")

            # Clean up transfer
            ls.set('_ff_cookie_transfer', '')
    except Exception as e:
        print(f"[COOKIE] Error loading cookie transfer: {e}")
