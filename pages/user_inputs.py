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
    current_age_group = st.session_state.get('input_age_group', '25-55')
    
    # Handle old format in scenarios
    age_group_mapping = {
        "Under 25": "25-55",
        "25-55": "25-55", 
        "55-70": "56-69",
        "56-69": "56-69",
        "70+": "70+"
    }
    current_age_group = age_group_mapping.get(current_age_group, '25-55')
    
    try:
        age_group_index = age_group_options.index(current_age_group)
    except ValueError:
        age_group_index = 0
    
    age_group = st.selectbox(
        "Age Group:", 
        age_group_options, 
        index=age_group_index,
        key="input_age_group"
    )
    
    # CRITICAL FIX: Read from session state for scenario loading
    age = st.number_input(
        "Your Age:", 
        min_value=18, 
        max_value=120, 
        value=safe_int(st.session_state.get('input_age', 35), 35),
        key="input_age"
    )
    
    partner_exists = st.checkbox(
        "Have Partner?", 
        value=st.session_state.get('input_partner_exists', False),
        key="input_partner_exists"
    )
    
    partner_name = ""
    partner_age = age
    
    if partner_exists:
        partner_name = st.text_input(
            "Partner Name:", 
            value=st.session_state.get('input_partner_name', ''),
            key="input_partner_name"
        )
        partner_age = st.number_input(
            "Partner Age:", 
            min_value=18, 
            max_value=120, 
            value=safe_int(st.session_state.get('input_partner_age', age), age),
            key="input_partner_age"
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