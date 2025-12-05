# pages/user_inputs.py - Merged version with session state integration
import streamlit as st
from datetime import date
from financial_utils import calculate_total_income, calculate_total_expenses, calculate_liquid_assets, calculate_total_assets, calculate_total_liabilities, calculate_other_assets, parse_goal_costs, safe_int

def setup_sidebar(is_trusted_user):
    """
    Collect user demographic data (NOT feature toggles - those are in ui/navigation.py)

    NOTE: This function was refactored during modular cleanup.
    Feature toggles are now handled by ui/navigation.py show_feature_toggles()
    """
    # Simply call collect_user_inputs() - no feature toggles here
    return collect_user_inputs()

def collect_user_inputs():
    """Collect user inputs with session state integration for scenario loading"""
    st.header("👤 User Profile")

    # CRITICAL FIX: Age group options must match your JSON scenarios
    age_group_options = ["25-55", "56-69", "70+"]  # Fixed to match scenarios

    # Handle old format in scenarios - initialize session state if not set
    if 'input_age_group' not in st.session_state:
        st.session_state['input_age_group'] = '25-55'
    else:
        # Normalize old format values
        age_group_mapping = {
            "Under 25": "25-55",
            "25-55": "25-55",
            "55-70": "56-69",
            "56-69": "56-69",
            "70+": "70+"
        }
        current_val = st.session_state.get('input_age_group', '25-55')
        st.session_state['input_age_group'] = age_group_mapping.get(current_val, '25-55')

    age_group = st.selectbox(
        "Age Group:",
        age_group_options,
        key="input_age_group",
        disabled=True,
        help="📝 Edit in INTAKE mode"
    )
    
    # CRITICAL FIX: Initialize session_state BEFORE widget (avoid value/key conflict)
    if 'input_age' not in st.session_state or st.session_state.get('input_age', 0) < 18:
        st.session_state['input_age'] = 55  # Default if missing or invalid

    age = st.number_input(
        "Your Age:",
        min_value=18,
        max_value=120,
        key="input_age",  # NO value= parameter! Streamlit uses session_state
        disabled=True,
        help="📝 Edit in INTAKE mode"
    )
    
    # Initialize partner_exists before widget
    if 'input_partner_exists' not in st.session_state:
        st.session_state['input_partner_exists'] = False

    partner_exists = st.checkbox(
        "Have Partner?",
        key="input_partner_exists",  # NO value= parameter!
        disabled=True,
        help="📝 Edit in INTAKE mode"
    )
    
    partner_name = ""
    partner_age = age
    
    if partner_exists:
        # Initialize partner fields before widgets
        if 'input_partner_name' not in st.session_state:
            st.session_state['input_partner_name'] = ''
        if 'input_partner_age' not in st.session_state or st.session_state.get('input_partner_age', 0) < 18:
            st.session_state['input_partner_age'] = age

        partner_name = st.text_input(
            "Partner Name:",
            key="input_partner_name",  # NO value= parameter!
            disabled=True,
            help="📝 Edit in INTAKE mode"
        )
        partner_age = st.number_input(
            "Partner Age:",
            min_value=18,
            max_value=120,
            key="input_partner_age",  # NO value= parameter!
            disabled=True,
            help="📝 Edit in INTAKE mode"
        )
    else:
        # Clear partner data when not needed
        st.session_state['input_partner_name'] = ""
        st.session_state['input_partner_age'] = age
    
    return {
        'age_group': age_group,
        'age': safe_int(age, 35),
        'partner_exists': partner_exists,
        'partner_name': partner_name,
        'partner_age': safe_int(partner_age, 35)
    }