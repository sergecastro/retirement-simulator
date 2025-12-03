# ui/welcome.py
# Welcome page for Family Forecast
# Extracted from app.py for maintainability - Dec 2, 2025
# Updated: Dec 2, 2025 - Improved layout, headers, and professional colors

import streamlit as st


def show_new_user_mode_selection():
    """Welcome page with mode selection and cloud backup options"""

    # ============ TITLE + BETA WARNING ============
    st.title("Welcome to Family Forecast!")

    st.markdown("""
    <div style='background-color: #FFF3CD; padding: 10px; border-radius: 6px; margin-bottom: 15px;'>
        <span style='color: #856404;'>⚠️ <strong>BETA</strong> — For educational purposes only. Not financial advice.</span>
    </div>
    """, unsafe_allow_html=True)

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

    # ============ SKIP OPTION (Visible) ============
    st.markdown("")
    st.markdown("""
    <div style='text-align: center; font-size: 1.1em; color: #666; padding: 15px; background-color: #f8f9fa; border-radius: 6px;'>
    <strong>Or skip for now</strong> — you can add cloud backup after completing your plan.
    </div>
    """, unsafe_allow_html=True)
    st.caption("By clicking any button above, you acknowledge this is beta software.")

    # ============ RESTORE OPTION ============
    st.markdown("---")
    st.markdown("### 🔑 Already have a backup? Restore here")

    restore_col1, restore_col2 = st.columns(2)

    with restore_col1:
        if st.button("Restore from Email Account", key="welcome_restore_email", use_container_width=True):
            st.session_state.show_backup_signup = 'restore_email'
            st.rerun()

    with restore_col2:
        if st.button("Restore from Vault ID", key="welcome_restore_vault", use_container_width=True):
            st.session_state.show_backup_signup = 'restore_vault'
            st.rerun()

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
