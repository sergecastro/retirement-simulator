# ui/welcome.py
# Welcome page for Family Forecast
# Extracted from app.py for maintainability - Dec 2, 2025
# Updated: Dec 3, 2025 - Added Welcome Back prompt for returning users

import streamlit as st
from utils.cookie_helper import get_welcome_back_info, clear_welcome_back_cookies, has_returning_user, init_cookie_reader, load_cookie_from_transfer
# Safe localStorage read for cloud backup users
from utils.safe_local_storage import get_backup_credentials


def show_new_user_mode_selection():
    """Welcome page with mode selection and cloud backup options"""

    # ============ CHECK FOR RETURNING USER (reads localStorage once) ============
    from utils.cookie_helper import check_for_returning_user
    check_for_returning_user()

    # ============ TITLE + BETA WARNING ============
    st.markdown("### FAMILY FORECAST")

    st.markdown("""
    <div style='background-color: #FFF3CD; padding: 10px; border-radius: 6px; margin-bottom: 15px;'>
        <span style='color: #856404;'>⚠️ <strong>BETA</strong> — For educational purposes only. Not financial advice.</span>
    </div>
    """, unsafe_allow_html=True)

    # --- Cloud Backup User Recognition ---
    # Check session_state first (already loaded in app.py), avoid duplicate st_javascript calls
    cloud_email = st.session_state.get('user_email')
    cloud_vault = st.session_state.get('vault_id')

    if cloud_email or cloud_vault:
        st.success(f"☁️ **Welcome back!** You have a cloud backup.")
        if cloud_email:
            st.write(f"Signed in as: **{cloud_email}**")
        elif cloud_vault:
            st.write(f"Vault ID: **{cloud_vault}**")
        
        st.write("")  # Spacing
        if st.button("🔄 Restore My Plan", type="primary", use_container_width=True, key="cloud_restore"):
            st.session_state.show_backup_signup = 'restore'
            st.rerun()
        st.markdown("---")

    # ============ WELCOME BACK PROMPT (for returning users) ============
    if has_returning_user():
        welcome_info = get_welcome_back_info()
        user_name = welcome_info.get("name", "")
        formatted_date = welcome_info.get("formatted_date", "")

        # Build personalized message
        if user_name and formatted_date:
            welcome_msg = f"Welcome back, **{user_name}**! Would you like to continue working on your plan from **{formatted_date}**?"
        elif user_name:
            welcome_msg = f"Welcome back, **{user_name}**! Would you like to continue where you left off?"
        else:
            welcome_msg = "Welcome back! Would you like to continue where you left off?"

        st.markdown(f"""
        <div style='background-color: #E0F2FE; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #0891B2;'>
            <h4 style='margin: 0 0 10px 0; color: #0E7490;'>👋 {welcome_msg}</h4>
        </div>
        """, unsafe_allow_html=True)

        col_continue, col_fresh = st.columns(2)

        with col_continue:
            if st.button("✅ Continue My Plan", type="primary", use_container_width=True, key="welcome_back_continue"):
                # Load from localStorage and go to INTAKE
                st.session_state["intake_mode"] = "full"
                st.session_state["beta_agreement"] = True
                st.session_state.mode_selected = True
                st.session_state.current_mode = "INTAKE"
                st.session_state["load_from_local_storage"] = True  # Flag to trigger localStorage load
                st.rerun()

        with col_fresh:
            if st.button("🔄 Start Fresh", use_container_width=True, key="welcome_back_fresh"):
                # Clear cookies and show normal welcome
                clear_welcome_back_cookies()
                st.rerun()

        st.markdown("---")

    # ============ CUSTOM BUTTON STYLING (Colorful and Professional) ============
    st.markdown("""
    <style>
    /* Primary buttons - Vibrant Teal/Blue */
    .stButton > button[kind="primary"] {
        background-color: #0891B2 !important;
        border-color: #0891B2 !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #0E7490 !important;
        border-color: #0E7490 !important;
    }
    /* Secondary buttons - Soft purple outline */
    .stButton > button:not([kind="primary"]) {
        border-color: #7C3AED !important;
        color: #7C3AED !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background-color: #F3E8FF !important;
        border-color: #7C3AED !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ============ SECTION 1: HOW TO ENTER INFORMATION ============
    st.markdown("### 📋 Choose How to Enter Information")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### ⭐ Recommended")
        st.markdown("**Full Mode** — All fields, most accurate results")
        if st.button("Start Full Mode", type="primary", use_container_width=True, key="new_user_full"):
            st.session_state["intake_mode"] = "full"
            st.session_state["beta_agreement"] = True
            st.session_state.mode_selected = True
            st.session_state.current_mode = "INTAKE"
            st.rerun()

    with col_right:
        st.markdown("#### Other Option")
        st.markdown("**Quick Mode** — Essential fields only, faster setup")
        if st.button("Start Quick Mode", use_container_width=True, key="new_user_quick"):
            st.session_state["intake_mode"] = "quick"
            st.session_state["beta_agreement"] = True
            st.session_state.mode_selected = True
            st.session_state.current_mode = "INTAKE"
            st.rerun()

    # ============ SECTION 2: CLOUD BACKUP (OPTIONAL) ============
    # Only show if user hasn't already signed up
    has_account = st.session_state.get('user_email')
    has_vault = st.session_state.get('vault_id')

    if not has_account and not has_vault:
        st.markdown("---")
        st.markdown("### ☁️ Add Encrypted Cloud Backup (Optional)")

        col_account, col_anon = st.columns(2)

        with col_account:
            st.markdown("#### ⭐ Recommended")
            st.markdown("**Free Account** — Cloud backup, unlimited access")
            st.markdown("""
            <div style='font-size: 0.9em; color: #555; margin-bottom: 8px;'>
            ✓ Unlimited scenarios · ✓ Auto-sync · ✓ Password recovery
            </div>
            """, unsafe_allow_html=True)
            if st.button("Create Free Account", type="primary", use_container_width=True, key="welcome_account"):
                st.session_state.show_backup_signup = 'account'
                st.rerun()

        with col_anon:
            st.markdown("#### Other Option")
            st.markdown("**Anonymous Trial** — No email, 30 days, 3 scenarios")
            st.markdown("""
            <div style='font-size: 0.9em; color: #888; margin-bottom: 8px;'>
            ⚠️ No recovery if password forgotten
            </div>
            """, unsafe_allow_html=True)
            if st.button("Try Anonymous", use_container_width=True, key="welcome_anonymous"):
                st.session_state.show_backup_signup = 'anonymous'
                st.rerun()

        # Skip option
        st.markdown("")
        st.markdown("""
        <div style='text-align: center; font-size: 1.1em; color: #666; padding: 15px; background-color: #f8f9fa; border-radius: 6px;'>
        <strong>Or skip for now</strong> — you can add cloud backup after completing your plan.
        </div>
        """, unsafe_allow_html=True)

        # Restore option
        st.markdown("---")
        st.markdown("### 🔑 Already have a backup?")

        if st.button("Restore My Plan", key="welcome_restore", use_container_width=True):
            st.session_state.show_backup_signup = 'restore'
            st.rerun()

    else:
        # User already has account/vault - show confirmation
        st.markdown("---")
        if has_account:
            st.success(f"✅ Signed in as **{has_account}** — your data will sync automatically!")
        elif has_vault:
            st.success(f"✅ Vault **{has_vault}** ready — your data will sync automatically!")

    st.caption("By clicking any button above, you acknowledge this is beta software.")

    # ============ PRIVACY SECTION (Strong Security Message) ============
    st.markdown("---")
    st.markdown("""
    ### 🔒 Your Privacy Matters — Bank-Grade Security

    **Your data stays in YOUR browser.** Family Forecast uses **AES-256-GCM encryption** —
    the same military-grade standard used by banks and governments.

    **Zero-Knowledge Architecture (like 1Password & ProtonMail):**
    - ✅ Your data is encrypted **before** it ever leaves your device
    - ✅ Cloud backups stored on **Supabase** (enterprise-grade infrastructure used by Fortune 500 companies)
    - ✅ Even if our servers were breached, your data remains **unreadable**
    - ✅ We **cannot** see your financial information — ever
    - ✅ No backdoors. No exceptions. Your password is the **only** key.

    **What competitors do:** Store your data unencrypted on their servers where employees, hackers, or subpoenas can access it.

    **What we do:** True privacy. Your data, your control, your peace of mind.
    """)

    # ============ WHAT IS FAMILY FORECAST? ============
    st.markdown("---")
    st.markdown("""
    ### ℹ️ What is Family Forecast?

    Family Forecast is an **educational retirement planning tool** that helps you:
    - 📊 Run Monte Carlo simulations (1,000+ scenarios)
    - 💰 Project cash flow through retirement
    - 🏥 Calculate Medicare IRMAA costs
    - 📈 Compare different retirement strategies
    """)

    # ============ DISCLAIMERS ============
    st.markdown("---")
    st.markdown("""
    ### ⚖️ Important Disclaimers

    **Not Financial Advice:** Family Forecast is for educational and informational purposes only.
    It does NOT provide financial, tax, investment, or legal advice. All projections are estimates
    based on your inputs and assumptions.

    **Consult Professionals:** Before making any financial decisions, please consult with qualified
    financial advisors, tax professionals, or legal counsel.

    **No Guarantee:** Past performance and projections do not guarantee future results.
    Your actual retirement outcomes may differ significantly from any estimates shown.
    """)

    # ============ COPYRIGHT ============
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.85em;">
    © 2025 Family Forecast | <a href="mailto:support@familyforecast.ai">support@familyforecast.ai</a>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# SIGNUP FORMS (Called when user clicks signup buttons)
# =============================================================================

def show_account_signup_form():
    """Show email account signup form"""
    st.markdown("### 📧 Create Free Account")

    # If already signed up, show success + auto-redirect to INTAKE
    if st.session_state.get('account_signup_success'):
        email = st.session_state.get('user_email', '')
        st.success(f"✅ Account created for {email}! Redirecting to enter your information...")
        st.session_state.show_backup_signup = None
        st.session_state.account_signup_success = False
        # Redirect to Lovable INTAKE (1 second delay to show success message)
        st.markdown(
            '<meta http-equiv="refresh" content="1;url=https://intake.familyforecast.ai/intake">',
            unsafe_allow_html=True
        )
        st.stop()
        return

    # Show signup form
    st.markdown("Your data will sync automatically when you save your plan.")

    with st.form("account_signup_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password (min 8 characters)", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

        if cancel:
            st.session_state.show_backup_signup = None
            st.rerun()

        if submit:
            # Validation
            if not email or "@" not in email:
                st.error("Please enter a valid email address.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            elif password != password_confirm:
                st.error("Passwords do not match.")
            else:
                from utils.supabase_sync import signup_user_only
                success, message = signup_user_only(email, password)

                if success:
                    st.session_state.user_email = email
                    print(f"🔥 WELCOME REGISTRATION: user_email SET TO: {st.session_state.user_email}")
                    # DO NOT call _get_local_storage() here - it creates a component that causes duplicates
                    # localStorage will be saved when user completes intake and saves
                    st.session_state.account_signup_success = True
                    st.balloons()
                    st.rerun()  # Rerun to auto-redirect to INTAKE
                else:
                    st.error(message)


def show_anonymous_signup_form():
    """Show anonymous vault signup form"""
    st.markdown("### 🕵️ Create Anonymous Vault")

    # If already created vault, show Vault ID + require confirmation before redirect
    if st.session_state.get('anon_signup_success'):
        vault_id = st.session_state.get('vault_id', '')
        st.success("✅ Vault created!")
        st.markdown(f"""
        <div style='background-color: #fff3cd; padding: 15px; border-radius: 6px; margin: 8px 0; border: 2px solid #ffc107;'>
        <strong>YOUR VAULT ID:</strong> <span style='font-size: 1.3em; font-family: monospace;'>{vault_id}</span><br><br>
        <strong>⚠️ WRITE THIS DOWN with your password!</strong><br>
        There is NO recovery if you forget these!
        </div>
        """, unsafe_allow_html=True)

        # Require confirmation before continuing
        confirmed = st.checkbox(
            "I have saved my Vault ID and password in a safe place",
            key="vault_id_confirmed"
        )

        if confirmed:
            if st.button("Continue to My Plan", type="primary", use_container_width=True, key="anon_continue_btn"):
                # Redirect to Lovable INTAKE
                st.session_state.show_backup_signup = None
                st.session_state.anon_signup_success = False
                st.markdown(
                    '<meta http-equiv="refresh" content="0;url=https://intake.familyforecast.ai/intake">',
                    unsafe_allow_html=True
                )
                st.stop()
        else:
            st.warning("☝️ Please confirm you've saved your Vault ID before continuing.")
        return

    # Show signup form
    st.markdown("**Important:** Save your Vault ID and password — there is NO recovery!")

    with st.form("anonymous_signup_form"):
        password = st.text_input("Create Password (min 8 characters)", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")

        st.warning("Anonymous vaults expire after 30 days and are limited to 3 scenarios.")

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Create Vault", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)

        if cancel:
            st.session_state.show_backup_signup = None
            st.rerun()

        if submit:
            if len(password) < 8:
                st.error("Password must be at least 8 characters.")
            elif password != password_confirm:
                st.error("Passwords do not match.")
            else:
                from utils.supabase_sync import create_anonymous_vault_empty
                vault_id, message = create_anonymous_vault_empty(password)

                if vault_id:
                    st.session_state.vault_id = vault_id
                    st.session_state.anon_signup_success = True
                    st.balloons()
                    st.rerun()  # Rerun to show compact success view
                else:
                    st.error(message)


def show_restore_form(restore_type: str):
    """Show restore form (email or vault)"""
    from ui.cloud_backup_modal import show_restore_modal

    st.markdown("### 🔑 Restore Your Plan")

    if st.button("Back to Welcome", key="restore_back"):
        st.session_state.show_backup_signup = None
        st.session_state['_restore_success'] = False  # Clear restore success flag
        st.rerun()

    # Check if we already have a successful restore (from previous render)
    restore_already_done = st.session_state.get('_restore_success', False)

    if not restore_already_done:
        # Show the modal and try to restore
        restored_data = show_restore_modal()

        if restored_data:
            # Save vault credentials to localStorage BEFORE redirect
            vault_id = st.session_state.get('vault_id')
            user_email = st.session_state.get('user_email')

            # Inject JavaScript to save to localStorage (runs when page renders)
            js_commands = []
            if vault_id:
                js_commands.append(f"localStorage.setItem('ff_vault_id', '{vault_id}');")
            if user_email:
                js_commands.append(f"localStorage.setItem('ff_user_email', '{user_email}');")

            if js_commands:
                import streamlit.components.v1 as components
                js_code = " ".join(js_commands) + " console.log('Saved credentials to localStorage');"
                components.html(f"<script>{js_code}</script>", height=0)

            st.session_state.intake_data = restored_data
            st.session_state['_restore_success'] = True  # Mark restore as successful
            st.session_state['_credentials_loaded'] = True  # Prevent st_javascript reruns
            st.rerun()  # Rerun to show success screen

    # Show success screen if restore was successful
    if st.session_state.get('_restore_success', False):
        st.success("✅ Data restored successfully!")
        st.markdown(f"**Vault ID:** `{st.session_state.get('vault_id', 'N/A')}`")

        # Debug info
        st.info(f"🔐 Password saved: {'✅ Yes' if st.session_state.get('cloud_password') else '❌ No'}")

        # Show continue button with explicit key
        if st.button("🚀 Continue to Analysis", type="primary", use_container_width=True, key="restore_continue_to_analysis"):
            st.session_state.show_backup_signup = None
            st.session_state.mode_selected = True
            st.session_state.current_mode = "Analysis"
            st.session_state['_restore_success'] = False  # Clear flag
            st.rerun()
