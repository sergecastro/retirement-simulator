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
    print(f"[MODAL DEBUG] backup_modal_step = {st.session_state.get('backup_modal_step', 'NOT SET')}")
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
            st.markdown("#### ⭐ Recommended")
            st.markdown("""
            **Free Account** — Unlimited access
            - Auto-sync on save
            - Unlimited scenarios
            - Password recovery
            """)
            if st.button("Create Free Account", key="choose_account", type="primary", use_container_width=True):
                print("[MODAL DEBUG] >>> 'Create Free Account' button was CLICKED!")
                st.session_state.backup_modal_step = 'account'
                st.rerun()

        with col2:
            st.markdown("#### Other Option")
            st.markdown("""
            **Anonymous Trial** — No email, 30 days
            - No email required
            - No recovery option
            - 3 scenarios max
            """)
            print(f"[MODAL DEBUG] About to show 'Try Anonymous' button")
            if st.button("Try Anonymous", key="choose_anonymous", use_container_width=True):
                print("[MODAL DEBUG] >>> 'Try Anonymous' button was CLICKED!")
                st.session_state.backup_modal_step = 'anonymous'
                st.rerun()

        st.markdown("")
        if st.button("Not now, maybe later", key="skip_backup"):
            st.session_state.backup_modal_step = 'choose'
            st.session_state['show_cloud_backup_offer'] = False  # Clear flag so "Go to Analysis" appears
            return False

        st.caption("Both options: Bank-grade AES-256 encryption. We never see your data.")
        return False

    # =========================================================================
    # STEP: ANONYMOUS BACKUP
    # =========================================================================
    elif st.session_state.backup_modal_step == 'anonymous':
        st.markdown("### 🕵️ Anonymous Backup")
        st.markdown("Create a password to protect your data.")
        st.info("🔑 **Password requirements:** 8+ characters, uppercase, lowercase, and a number")

        password = st.text_input("Password", type="password", key="anon_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="anon_password_confirm")

        st.warning("⚠️ **30-day trial.** No recovery if you forget your password.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Back", key="anon_back"):
                st.session_state.backup_modal_step = 'choose'
                st.rerun()

        with col2:
            print(f"[MODAL DEBUG] About to show 'Create Backup' button")
            print(f"[MODAL DEBUG] password length: {len(password) if password else 0}, confirm length: {len(password_confirm) if password_confirm else 0}")

            if st.button("Create Backup", key="anon_create", type="primary"):
                print("[MODAL DEBUG] >>> 'Create Backup' CLICKED!")
                # Validate
                if not password:
                    print("[MODAL DEBUG] Validation failed: no password")
                    st.error("Please enter a password")
                    return False

                if password != password_confirm:
                    print("[MODAL DEBUG] Validation failed: passwords don't match")
                    st.error("Passwords don't match")
                    return False

                is_valid, msg = validate_password_strength(password)
                if not is_valid:
                    print(f"[MODAL DEBUG] Validation failed: {msg}")
                    st.error(msg)
                    return False

                # Create vault
                print("[MODAL DEBUG] Validation passed, creating vault...")
                try:
                    print(f"[MODAL DEBUG] Calling create_anonymous_vault...")
                    with st.spinner("Creating encrypted backup..."):
                        vault_id, message = create_anonymous_vault(password, user_data)
                    print(f"[MODAL DEBUG] Result: vault_id={vault_id}, message={message}")
                except Exception as e:
                    print(f"[MODAL ERROR] Exception during vault creation: {e}")
                    import traceback
                    traceback.print_exc()
                    st.error(f"Error: {e}")
                    return False

                if vault_id:
                    print(f"[MODAL DEBUG] Vault created successfully: {vault_id}")
                    st.session_state.backup_vault_id = vault_id

                    # Save vault_id to localStorage for persistence
                    from utils.snapshot_manager import _get_local_storage
                    ls = _get_local_storage()
                    ls.set('ff_vault_id', vault_id)
                    print(f"[MODAL DEBUG] Saved vault_id to localStorage: {vault_id}")

                    st.session_state.backup_modal_step = 'success_anonymous'
                    print(f"[MODAL DEBUG] Transitioning to success_anonymous, vault_id={vault_id}")
                    st.rerun()
                else:
                    print(f"[MODAL DEBUG] Vault creation failed: {message}")
                    st.error(f"Failed: {message}")
                    return False

        return False

    # =========================================================================
    # STEP: CREATE ACCOUNT
    # =========================================================================
    elif st.session_state.backup_modal_step == 'account':
        st.markdown("### ⭐ Create Free Account")

        email = st.text_input("Email", key="account_email")
        st.info("🔑 **Password requirements:** 8+ characters, uppercase, lowercase, and a number")
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
        print("[MODAL DEBUG] >>> RENDERING success_anonymous screen")
        st.markdown("### ✅ Vault Created Successfully!")

        vault_id = st.session_state.backup_vault_id

        st.markdown(f"### 🔑 Your Vault ID: `{vault_id}`")

        st.warning("⚠️ **WRITE THIS DOWN!** There is no recovery without your Vault ID and password.")
        st.code(vault_id, language=None)

        st.markdown("---")
        confirmed = st.checkbox("I confirm I have saved my Vault ID and password", key="vault_confirm_checkbox")

        if confirmed:
            if st.button("Continue to Analysis →", key="anon_continue", type="primary"):
                st.session_state.show_cloud_backup_offer = False
                st.session_state.backup_modal_step = 'done'
                st.session_state.current_mode = "Analysis"
                st.rerun()
        else:
            st.button("Continue to Analysis →", key="anon_continue_disabled", type="primary", disabled=True)
            st.info("☝️ Please confirm you saved your Vault ID before continuing.")

        return False

    # =========================================================================
    # SUCCESS: ACCOUNT
    # =========================================================================
    elif st.session_state.backup_modal_step == 'success_account':
        st.markdown("### ✅ Account Created Successfully!")

        email = st.session_state.get('backup_user_email', 'your email')

        st.success(f"Your account **{email}** is ready!")

        st.markdown("""
        **What's next:**
        - Your data syncs automatically when you save
        - Sign in anytime with your email and password
        - Access your plans from any device
        """)

        if st.button("Continue to Analysis →", key="account_continue", type="primary"):
            st.session_state.show_cloud_backup_offer = False
            st.session_state.backup_modal_step = 'done'
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

    tab1, tab2 = st.tabs(["🔑 Using Vault ID & Password", "📧 Using Email & Password"])

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
