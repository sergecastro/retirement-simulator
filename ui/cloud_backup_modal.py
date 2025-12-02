"""
Cloud Backup Modal for Family Forecast
======================================
Shows after user saves their plan locally.
Offers Anonymous Backup or Free Account options.
"""

import streamlit as st
from utils.password_crypto import validate_password_strength, generate_vault_id
from utils.supabase_sync import (
    create_anonymous_vault,
    create_user_account,
    load_anonymous_vault,
    sign_in_user
)


def show_cloud_backup_modal(user_data: dict) -> bool:
    """
    Display cloud backup options modal.

    Args:
        user_data: The financial data to backup

    Returns:
        True if user completed backup, False if skipped
    """

    # Initialize session state for modal
    if 'backup_modal_step' not in st.session_state:
        st.session_state.backup_modal_step = 'choose'  # choose, anonymous, account, success

    if 'backup_vault_id' not in st.session_state:
        st.session_state.backup_vault_id = None

    # Modal container with styling
    st.markdown("""
        <style>
        .backup-modal {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 16px;
            margin: 1rem 0;
        }
        .backup-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 0.5rem;
            text-align: center;
        }
        .backup-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .recommended-badge {
            background: #10b981;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # =========================================================================
    # STEP: CHOOSE
    # =========================================================================
    if st.session_state.backup_modal_step == 'choose':
        st.markdown("### 🔐 Protect Your Work?")
        st.markdown("Your data is saved locally. Want cloud backup too?")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🕵️ Anonymous Trial**
            - 30 days only
            - 3 scenarios max
            - No email required
            - No recovery option
            """)
            if st.button("Try Anonymous", key="choose_anonymous", use_container_width=True):
                st.session_state.backup_modal_step = 'anonymous'
                st.rerun()

        with col2:
            st.markdown("""
            **⭐ Free Account** ← RECOMMENDED
            - Unlimited access
            - Unlimited scenarios
            - Auto-sync on save
            - Password recovery
            """)
            if st.button("Create Free Account", key="choose_account", type="primary", use_container_width=True):
                st.session_state.backup_modal_step = 'account'
                st.rerun()

        st.markdown("")
        if st.button("Not now, maybe later", key="skip_backup"):
            st.session_state.backup_modal_step = 'choose'
            return False

        st.caption("Both options: Bank-grade AES-256 encryption. We never see your data.")
        return False

    # =========================================================================
    # STEP: ANONYMOUS BACKUP
    # =========================================================================
    elif st.session_state.backup_modal_step == 'anonymous':
        st.markdown("### 🕵️ Anonymous Backup")
        st.markdown("Create a password to protect your data.")

        password = st.text_input("Password", type="password", key="anon_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="anon_password_confirm")

        st.warning("⚠️ **30-day trial.** No recovery if you forget your password.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Back", key="anon_back"):
                st.session_state.backup_modal_step = 'choose'
                st.rerun()

        with col2:
            if st.button("Create Backup", key="anon_create", type="primary"):
                # Validate
                if not password:
                    st.error("Please enter a password")
                    return False

                if password != password_confirm:
                    st.error("Passwords don't match")
                    return False

                is_valid, msg = validate_password_strength(password)
                if not is_valid:
                    st.error(msg)
                    return False

                # Create vault
                with st.spinner("Creating encrypted backup..."):
                    vault_id, message = create_anonymous_vault(password, user_data)

                if vault_id:
                    st.session_state.backup_vault_id = vault_id
                    st.session_state.backup_modal_step = 'success_anonymous'
                    st.rerun()
                else:
                    st.error(f"Failed: {message}")
                    return False

        return False

    # =========================================================================
    # STEP: CREATE ACCOUNT
    # =========================================================================
    elif st.session_state.backup_modal_step == 'account':
        st.markdown("### ⭐ Create Free Account")

        email = st.text_input("Email", key="account_email")
        password = st.text_input("Password", type="password", key="account_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="account_password_confirm")

        st.success("✅ Unlimited access. Auto-sync. Recovery options.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Back", key="account_back"):
                st.session_state.backup_modal_step = 'choose'
                st.rerun()

        with col2:
            if st.button("Create Account", key="account_create", type="primary"):
                # Validate
                if not email or '@' not in email:
                    st.error("Please enter a valid email")
                    return False

                if not password:
                    st.error("Please enter a password")
                    return False

                if password != password_confirm:
                    st.error("Passwords don't match")
                    return False

                is_valid, msg = validate_password_strength(password)
                if not is_valid:
                    st.error(msg)
                    return False

                # Create account
                with st.spinner("Creating your account..."):
                    success, message = create_user_account(email, password, user_data)

                if success:
                    st.session_state.backup_user_email = email
                    st.session_state.backup_modal_step = 'success_account'
                    st.rerun()
                else:
                    st.error(f"Failed: {message}")
                    return False

        return False

    # =========================================================================
    # SUCCESS: ANONYMOUS
    # =========================================================================
    elif st.session_state.backup_modal_step == 'success_anonymous':
        st.markdown("### ✅ Backup Created!")

        vault_id = st.session_state.backup_vault_id

        st.markdown(f"""
        **Your Vault ID:**

        ### `{vault_id}`
        """)

        st.error("⚠️ **WRITE THIS DOWN** with your password! You need BOTH to restore your data.")

        col1, col2 = st.columns(2)

        with col1:
            # Copy button using Streamlit's built-in
            st.code(vault_id, language=None)

        with col2:
            if st.button("Continue to Analysis →", key="anon_continue", type="primary"):
                st.session_state.backup_modal_step = 'done'
                st.session_state.show_backup_modal = False
                st.session_state.current_mode = "Analysis"
                st.rerun()

        return False

    # =========================================================================
    # SUCCESS: ACCOUNT
    # =========================================================================
    elif st.session_state.backup_modal_step == 'success_account':
        st.markdown("### ✅ Account Created!")

        email = st.session_state.get('backup_user_email', 'your email')

        st.markdown(f"""
        You're all set! Sign in anytime with:

        **📧 {email}**

        Your data syncs automatically.
        """)

        if st.button("Continue to Analysis →", key="account_continue", type="primary"):
            st.session_state.backup_modal_step = 'done'
            st.session_state.show_backup_modal = False
            st.session_state.current_mode = "Analysis"
            st.rerun()

        return False

    # =========================================================================
    # DONE
    # =========================================================================
    elif st.session_state.backup_modal_step == 'done':
        return True

    return False


def show_restore_modal() -> dict:
    """
    Display restore options for returning users.

    Returns:
        Restored data dict or None
    """
    st.markdown("### 🔐 Restore Your Data")

    tab1, tab2 = st.tabs(["🕵️ Anonymous Vault", "📧 Sign In"])

    with tab1:
        vault_id = st.text_input("Vault ID (e.g., FF-X7K9-M2PL)", key="restore_vault_id")
        password = st.text_input("Password", type="password", key="restore_vault_password")

        if st.button("Restore Vault", key="restore_vault_btn"):
            if not vault_id or not password:
                st.error("Please enter both Vault ID and password")
                return None

            with st.spinner("Decrypting your data..."):
                data, message = load_anonymous_vault(vault_id, password)

            if data:
                st.success(message)
                return data
            else:
                st.error(message)
                return None

    with tab2:
        email = st.text_input("Email", key="restore_email")
        password = st.text_input("Password", type="password", key="restore_password")

        if st.button("Sign In", key="restore_signin_btn"):
            if not email or not password:
                st.error("Please enter email and password")
                return None

            with st.spinner("Signing in..."):
                data, message = sign_in_user(email, password)

            if data:
                st.success(message)
                return data
            else:
                st.error(message)
                return None

    return None


def reset_backup_modal():
    """Reset modal state for fresh start."""
    st.session_state.backup_modal_step = 'choose'
    st.session_state.backup_vault_id = None
    st.session_state.show_backup_modal = False
