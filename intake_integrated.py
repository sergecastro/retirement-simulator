# intake_integrated.py - Intake Questionnaire Module (called from app.py)
# This module provides the Data Entry Mode questionnaire
import os
import json
import streamlit as st
from pathlib import Path
from intake_validation import (validate_age, validate_age_gap, validate_total_income,
                                validate_social_security, validate_income_mix,
                                validate_total_expenses, validate_housing_ratio,
                                validate_income_vs_expenses, show_validation_message)
from intake_review import show_assets_page, show_liabilities_page, show_family_page, show_review_page

# ========== HELPER FUNCTIONS ==========
def get_shared_path():
    """Get path to shared intake payload file"""
    current_dir = os.getcwd()
    root_dir = Path(current_dir).parent
    shared_dir = root_dir / "SHARED"
    shared_dir.mkdir(exist_ok=True)
    return str(shared_dir / "intake_payload.json")

def load_existing_payload():
    """Load previous intake data if exists"""
    shared_path = get_shared_path()
    if os.path.exists(shared_path):
        try:
            with open(shared_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_payload(data):
    """Save intake data to shared JSON file"""
    shared_path = get_shared_path()
    with open(shared_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def go_to_page(page_name):
    """Navigate to a different intake page"""
    st.session_state.intake_current_page = page_name
    st.rerun()

# ========== MAIN INTAKE QUESTIONNAIRE ==========
def show_intake_questionnaire():
    """Main function to display the intake questionnaire"""

    # Initialize intake page navigation
    if 'intake_current_page' not in st.session_state:
        st.session_state.intake_current_page = 'profile'

    # Load existing data
    existing = load_existing_payload()

    # Progress bar
    pages = ['profile', 'income', 'expenses', 'assets', 'liabilities', 'family', 'review']
    current_idx = pages.index(st.session_state.intake_current_page)
    progress = (current_idx + 1) / len(pages)
    st.progress(progress)
    st.caption(f"Step {current_idx + 1} of {len(pages)}: {st.session_state.intake_current_page.title()}")

    current_page = st.session_state.intake_current_page

    # ===== PAGE 1: PROFILE =====
    if current_page == 'profile':
        st.header("👤 Your Profile")

        # Single or Couple
        default_mode_is_couple = bool(existing.get("input_partner_exists", True))
        mode = st.radio(
            "Are you planning as:",
            ["Single", "Couple"],
            index=1 if default_mode_is_couple else 0
        )

        # Your age
        your_age_default = int(existing.get("input_age", 70))
        your_age = st.number_input(
            "Your age",
            min_value=18,
            max_value=100,
            value=your_age_default,
            step=1,
            help="Your current age"
        )

        # Partner fields (if couple)
        partner_name = existing.get("input_partner_name", "")
        partner_age_default = int(existing.get("input_partner_age", 68)) if "input_partner_age" in existing else 68

        if mode == "Couple":
            partner_name = st.text_input("Partner name", value=partner_name)
            partner_age = st.number_input(
                "Partner age",
                min_value=18,
                max_value=100,
                value=partner_age_default,
                step=1
            )
        else:
            partner_age = None

        # Intelligent validation
        level, message = validate_age(your_age, is_partner=False)
        show_validation_message(level, message)

        if mode == "Couple" and partner_age:
            level, message = validate_age(partner_age, is_partner=True)
            show_validation_message(level, message)

            # Validate age gap
            level, message = validate_age_gap(your_age, partner_age)
            show_validation_message(level, message)

        # Save and continue
        col1, col2 = st.columns([1, 1])
        with col2:
            if st.button("Next: Income →", type="primary", use_container_width=True):
                # Save profile data
                data = existing.copy()
                data["schema_version"] = "1.0"
                data["input_age"] = int(your_age)
                data["input_partner_exists"] = (mode == "Couple")
                if data["input_partner_exists"]:
                    data["input_partner_name"] = partner_name
                    data["input_partner_age"] = int(partner_age)
                else:
                    data.pop("input_partner_name", None)
                    data.pop("input_partner_age", None)
                save_payload(data)
                go_to_page('income')

    # ===== PAGES 2-7: PLACEHOLDER (Will integrate next) =====
    elif current_page in ['income', 'expenses', 'assets', 'liabilities', 'family', 'review']:
        st.markdown(f"### 📝 {current_page.title()} Page")
        st.info(f"🚧 {current_page.title()} page integration in progress...")
        st.info(f"💾 Data is being saved to: `{get_shared_path()}`")

        # Navigation
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back to Profile", use_container_width=True):
                go_to_page('profile')
        with col2:
            if st.button("🎯 Go to Analysis Mode", type="primary", use_container_width=True):
                st.session_state.app_mode = 'Analysis'
                st.rerun()

    # Footer
    st.divider()
    st.caption(f"📁 Data saves to: `{get_shared_path()}`")
    st.caption("💡 Use 'Load from Path' in Analysis Mode to import this data into your scenario.")
