"""
ForeCash Authentication
=======================
User authentication and access control.

Author: ForeCash Development Team
Last Updated: October 22, 2025
"""

import streamlit as st


# =============================================================================
# PASSWORD CONFIGURATION
# =============================================================================

# Demo password (available to all)
DEMO_PASSWORD = "abcd123"

# Trusted user password (advanced features)
TRUSTED_PASSWORD = "uhiRR2938foq"


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def initialize_auth_state():
    """Initialize authentication state in session"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'IS_TRUSTED_USER' not in st.session_state:
        st.session_state.IS_TRUSTED_USER = False


# =============================================================================
# AUTHENTICATION UI
# =============================================================================

def show_login_screen():
    """
    Display login screen and handle authentication

    Returns:
        bool: True if authenticated, False if still showing login
    """
    st.title("🏠 ForeCash Family Lifecycle Retirement Planner v3.0")
    st.markdown("*Interactive Financial Planning & Simulation Tool*")

    # Password protection
    st.header("🔒 Access Control")
    st.markdown("Enter your password to access the retirement planning tools.")

    # Show demo password hint
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px; margin: 10px 0;'>
        <p style='margin: 0; color: #666; font-size: 14px;'><strong>Demo Access:</strong></p>
        <p style='margin: 5px 0 0 0; font-size: 20px; font-family: monospace;'>
            Password: <code style='background: #fff; padding: 5px 10px; border-radius: 3px; font-size: 20px;'>abcd123</code>
        </p>
    </div>
    """, unsafe_allow_html=True)

    password = st.text_input(
        "Enter password:",
        type="password",
        placeholder="Type or paste password here"
    )

    # Validate password
    if password and password not in [DEMO_PASSWORD, TRUSTED_PASSWORD]:
        st.error("🚫 Incorrect password. Please try again.")
        st.stop()
    elif not password:
        st.info("👆 Please enter a password to continue")
        st.stop()
    else:
        # Password correct - authenticate!
        st.session_state.authenticated = True
        st.session_state.IS_TRUSTED_USER = (password == TRUSTED_PASSWORD)
        return True

    return False


# =============================================================================
# AUTHENTICATION CHECK
# =============================================================================

def require_authentication():
    """
    Require authentication before proceeding
    Call this at the start of your app

    Returns:
        bool: True if authenticated (IS_TRUSTED_USER status set in session)
    """
    initialize_auth_state()

    if not st.session_state.authenticated:
        authenticated = show_login_screen()
        if authenticated:
            st.rerun()
        return False

    return True


def is_trusted_user():
    """
    Check if current user has trusted access

    Returns:
        bool: True if trusted user
    """
    return st.session_state.get('IS_TRUSTED_USER', False)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("✅ ForeCash Authentication Module")
    print(f"Demo password: {DEMO_PASSWORD}")
    print(f"Trusted password: [hidden]")
