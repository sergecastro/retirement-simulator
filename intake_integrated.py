# intake_integrated.py - Intake Questionnaire Module (called from app.py)
# This module provides the Data Entry Mode questionnaire
import os
from ui.components.top_navigation import render_top_navigation
import json
import time
import streamlit as st
from pathlib import Path
from datetime import datetime
from intake_validation import (validate_age, validate_age_gap, validate_total_income,
                                validate_social_security, validate_income_mix,
                                validate_total_expenses, validate_housing_ratio,
                                validate_income_vs_expenses, show_validation_message)
from intake_review import show_assets_page, show_liabilities_page, show_family_page, show_review_page

# NEW: Snapshot versioning system
from utils.snapshot_manager import (
    save_snapshot, load_snapshot, list_snapshots,
    delete_snapshot, rename_snapshot, get_current_snapshot,
    export_all_snapshots, import_snapshots
)

# Legacy localStorage support (for backward compatibility)
from utils.local_storage_browser import load_from_local_storage_encrypted

# ========== SCROLL TO TOP FIX ==========
import streamlit.components.v1 as components

def scroll_to_top():
    """Force scroll to top using components.html for reliable execution"""
    components.html(
        """
        <script>
            // Immediate scroll
            window.scrollTo(0, 0);
            document.documentElement.scrollTo(0, 0);

            // Parent document (Streamlit iframe)
            if (window.parent) {
                window.parent.scrollTo(0, 0);
                var main = window.parent.document.querySelector('section.main');
                if (main) main.scrollTo(0, 0);
                var app = window.parent.document.querySelector('.stApp');
                if (app) app.scrollTo(0, 0);
            }

            // Delayed scroll after render
            setTimeout(function() {
                window.parent.scrollTo(0, 0);
                var main = window.parent.document.querySelector('section.main');
                if (main) main.scrollTo(0, 0);
            }, 50);

            setTimeout(function() {
                window.parent.scrollTo(0, 0);
                var main = window.parent.document.querySelector('section.main');
                if (main) main.scrollTo(0, 0);
            }, 150);
        </script>
        """,
        height=0
    )


# ========== EXIT WARNING FOR UNSAVED CHANGES ==========
UNSAVED_CHANGES_WARNING_JS = """
<script>
    // Warn user if they try to leave with unsaved changes
    window.addEventListener('beforeunload', function (e) {
        // Check if user has started filling the form
        // (we check if session has any intake data)
        var hasData = sessionStorage.getItem('intake_has_data');

        if (hasData === 'true') {
            // Show browser's default warning dialog
            e.preventDefault();
            e.returnValue = ''; // Chrome requires returnValue to be set
            return ''; // Some browsers show this message
        }
    });

    // Mark that user has started filling form
    sessionStorage.setItem('intake_has_data', 'true');
</script>
"""

# ========== HELPER FUNCTIONS ==========
def get_shared_path():
    """Get path to shared intake payload file (same logic as app.py)"""
    current_dir = os.getcwd()

    # Check if we're on Render (production) or local
    if os.path.exists("/opt/render"):
        shared_dir = Path("/opt/render/project/SHARED")
    else:
        root_dir = Path(current_dir).parent
        shared_dir = root_dir / "SHARED"

    shared_dir.mkdir(parents=True, exist_ok=True)
    return str(shared_dir / "intake_payload.json")

def load_template_data():
    """Load template data from ORIGINAL 70+ Retirement Scenario for first-time users"""
    from embedded_scenarios import EMBEDDED_SCENARIOS

    # Get the demo scenario as template
    scenario = EMBEDDED_SCENARIOS.get('ORIGINAL_70+_RETIREMENT_SCENARIO', {})

    # Map scenario fields to intake field names
    template = {
        "schema_version": "1.0",
        "is_demo": True,  # CRITICAL: Flag to identify demo data

        # Profile
        "input_user_name": scenario.get("user_name", ""),
        "input_age": scenario.get("age", 70),
        "input_partner_exists": scenario.get("partner_exists", False),
        "input_partner_name": scenario.get("partner_name", ""),
        "input_partner_age": scenario.get("partner_age", 68),

        # Income
        "input_salary_wages": scenario.get("salary_wages", 0.0),
        "input_self_employment_income": scenario.get("self_employment_income", 0.0),
        "input_rental_income": scenario.get("rental_income", 0.0),
        "input_investment_income": scenario.get("investment_income", 0.0),
        "input_social_security_income": scenario.get("social_security_income", 0.0),
        "input_pension_income": scenario.get("pension_income", 0.0),
        "input_other_income": scenario.get("other_income", 0.0),
        "input_total_income": scenario.get("total_income", 0.0),

        # Expenses
        "input_housing_expenses": scenario.get("housing_expenses", 0.0),
        "input_utilities_expenses": scenario.get("utilities_expenses", 0.0),
        "input_groceries_expenses": scenario.get("groceries_expenses", 0.0),
        "input_transportation_expenses": scenario.get("transportation_expenses", 0.0),
        "input_healthcare_expenses": scenario.get("healthcare_expenses", 0.0),
        "input_insurance_expenses": scenario.get("insurance_expenses", 0.0),
        "input_property_tax_expenses": scenario.get("property_tax_expenses", 0.0),
        "input_entertainment_expenses": scenario.get("entertainment_expenses", 0.0),
        "input_restaurant_expenses": scenario.get("restaurant_expenses", 0.0),
        "input_travel_expenses": scenario.get("travel_expenses", 0.0),
        "input_education_expenses": scenario.get("education_expenses", 0.0),
        "input_childcare_expenses": scenario.get("childcare_expenses", 0.0),
        "input_clothing_expenses": scenario.get("clothing_expenses", 0.0),
        "input_charitable_donations": scenario.get("charitable_donations", 0.0),
        "input_miscellaneous_expenses": scenario.get("miscellaneous_expenses", 0.0),
        "input_other_expenses": scenario.get("other_expenses", 0.0),
        "input_total_expenses": scenario.get("total_expenses", 0.0),

        # Assets
        "input_ira_balance": scenario.get("ira_balance", 0.0),
        "input_four01k_403b_balance": scenario.get("four01k_403b_balance", 0.0),
        "input_partner_ira_balance": scenario.get("partner_ira_balance", 0.0),
        "input_partner_four01k_403b_balance": scenario.get("partner_four01k_403b_balance", 0.0),
        "input_taxable_investment_accounts": scenario.get("taxable_investment_accounts", 0.0),
        "input_high_yield_savings_account": scenario.get("high_yield_savings_account", 0.0),
        "input_hsa_balance": scenario.get("hsa_balance", 0.0),
        "input_five29_plan_balance": scenario.get("five29_plan_balance", 0.0),
        "input_primary_residence_value": scenario.get("primary_residence_value", 0.0),
        "input_secondary_residence_value": scenario.get("secondary_residence_value", 0.0),
        "input_vehicles_value": scenario.get("vehicles_value", 0.0),
        "input_jewelry_collectibles_value": scenario.get("jewelry_collectibles_value", 0.0),
        "input_business_ownership_value": scenario.get("business_ownership_value", 0.0),
        "input_cryptocurrency_holdings": scenario.get("cryptocurrency_holdings", 0.0),
        "input_other_assets": scenario.get("other_assets", 0.0),

        # Liabilities
        "input_mortgage_balance": scenario.get("mortgage_balance", 0.0),
        "input_auto_loan_balance": scenario.get("auto_loans", 0.0),
        "input_student_loan_balance": scenario.get("student_loans", 0.0),
        "input_credit_card_debt": scenario.get("credit_card_debt", 0.0),
        "input_other_liabilities": scenario.get("other_liabilities", 0.0),

        # Family data
        "children_list": scenario.get("children_list", []),
        "children_rows": scenario.get("children_rows", []),
        "inheritance_list": scenario.get("inheritance_list", []),
        "inherit_rows": scenario.get("inherit_rows", []),
        "goals_list": scenario.get("goals_list", []),
        "goals_data": scenario.get("goals_data", []),
        "custom_expenses": [],
        "custom_expenses_list": [],
        "custom_income": [],
        "custom_income_list": []
    }

    # CRITICAL FIX: Copy template data into session_state
    for key, value in template.items():
        # WHITELIST: Only copy safe data keys, never widget keys
        if key.startswith(('input_', 'temp_', '_protected')) or key in (
            'children_list', 'children_rows', 'inheritance_list', 'inherit_rows',
            'goals_list', 'goals_data', 'custom_expenses', 'custom_expenses_list',
            'custom_income', 'custom_income_list', 'schema_version'
        ):
            if key not in st.session_state:
                st.session_state[key] = value

    return template

def collect_current_form_data():
    """
    Collect CURRENT form data from st.session_state.
    
    FIXED: 
    1. Checks protected assets/liabilities first.
    2. Smartly handles Family data: ignores empty 'temp' widgets when on Review page
       so data doesn't disappear.
    """
    # Get protected data dicts
    asset_protected = st.session_state.get('_protected_asset_data', {})
    liability_protected = st.session_state.get('_protected_liability_data', {})

    def get_asset(key, default=0.0):
        return asset_protected.get(key, st.session_state.get(key, default))

    def get_liability(key, default=0.0):
        return liability_protected.get(key, st.session_state.get(key, default))

    # FIXED: Helper that checks ALL possible hiding spots for list data
    def hunt_for_data(primary_keys):
        print(f"[HUNT DEBUG] Searching keys: {primary_keys}")
        for key in primary_keys:
            data = st.session_state.get(key)
            print(f"[HUNT DEBUG] {key} = {type(data).__name__} | {data}")
            if data and isinstance(data, list) and len(data) > 0:
                print(f"[HUNT DEBUG] FOUND DATA in {key}\!")
                return data
        print(f"[HUNT DEBUG] NOTHING FOUND for {primary_keys}")
        return []

    data = {
        "schema_version": "1.0",

        # Profile
        "input_user_name": st.session_state.get("input_user_name", ""),
        "input_age": st.session_state.get("input_age", 0),
        "input_age_group": st.session_state.get("input_age_group", "70+"),
        "input_partner_exists": st.session_state.get("input_partner_exists", False),
        "input_partner_name": st.session_state.get("input_partner_name", ""),
        "input_partner_age": st.session_state.get("input_partner_age", 0),

        # Income
        "input_salary_wages": st.session_state.get("input_salary_wages", 0.0),
        "input_self_employment_income": st.session_state.get("input_self_employment_income", 0.0),
        "input_rental_income": st.session_state.get("input_rental_income", 0.0),
        "input_investment_income": st.session_state.get("input_investment_income", 0.0),
        "input_social_security_income": st.session_state.get("input_social_security_income", 0.0),
        "input_pension_income": st.session_state.get("input_pension_income", 0.0),
        "input_other_income": st.session_state.get("input_other_income", 0.0),
        "input_total_income": st.session_state.get("input_total_income", 0.0),

        # Expenses
        "input_housing_expenses": st.session_state.get("input_housing_expenses", 0.0),
        "input_utilities_expenses": st.session_state.get("input_utilities_expenses", 0.0),
        "input_groceries_expenses": st.session_state.get("input_groceries_expenses", 0.0),
        "input_transportation_expenses": st.session_state.get("input_transportation_expenses", 0.0),
        "input_healthcare_expenses": st.session_state.get("input_healthcare_expenses", 0.0),
        "input_insurance_expenses": st.session_state.get("input_insurance_expenses", 0.0),
        "input_property_tax_expenses": st.session_state.get("input_property_tax_expenses", 0.0),
        "input_entertainment_expenses": st.session_state.get("input_entertainment_expenses", 0.0),
        "input_restaurant_expenses": st.session_state.get("input_restaurant_expenses", 0.0),
        "input_travel_expenses": st.session_state.get("input_travel_expenses", 0.0),
        "input_education_expenses": st.session_state.get("input_education_expenses", 0.0),
        "input_childcare_expenses": st.session_state.get("input_childcare_expenses", 0.0),
        "input_clothing_expenses": st.session_state.get("input_clothing_expenses", 0.0),
        "input_charitable_donations": st.session_state.get("input_charitable_donations", 0.0),
        "input_miscellaneous_expenses": st.session_state.get("input_miscellaneous_expenses", 0.0),
        "input_other_expenses": st.session_state.get("input_other_expenses", 0.0),
        "input_total_expenses": st.session_state.get("input_total_expenses", 0.0),

        # Assets - USE PROTECTED DATA
        "input_ira_balance": get_asset("input_ira_balance", 0.0),
        "input_four01k_403b_balance": get_asset("input_four01k_403b_balance", 0.0),
        "input_pension_fund_value": get_asset("input_pension_fund_value", 0.0),
        "input_partner_ira_balance": get_asset("input_partner_ira_balance", 0.0),
        "input_partner_four01k_403b_balance": get_asset("input_partner_four01k_403b_balance", 0.0),
        "input_taxable_investment_accounts": get_asset("input_taxable_investment_accounts", 0.0),
        "input_high_yield_savings_account": get_asset("input_high_yield_savings_account", 0.0),
        "input_hsa_balance": get_asset("input_hsa_balance", 0.0),
        "input_five29_plan_balance": get_asset("input_five29_plan_balance", 0.0),
        "input_primary_residence_value": get_asset("input_primary_residence_value", 0.0),
        "input_secondary_residence_value": get_asset("input_secondary_residence_value", 0.0),
        "input_vehicles_value": get_asset("input_vehicles_value", 0.0),
        "input_jewelry_collectibles_value": get_asset("input_jewelry_collectibles_value", 0.0),
        "input_business_ownership_value": get_asset("input_business_ownership_value", 0.0),
        "input_cryptocurrency_holdings": get_asset("input_cryptocurrency_holdings", 0.0),
        "input_other_assets": get_asset("input_other_assets", 0.0),

        # Liabilities - USE PROTECTED DATA
        "input_mortgage_balance": get_liability("input_mortgage_balance", 0.0),
        "input_secondary_mortgage_balance": get_liability("input_secondary_mortgage_balance", 0.0),
        "input_auto_loan_balance": get_liability("input_auto_loan_balance", 0.0),
        "input_student_loan_balance": get_liability("input_student_loan_balance", 0.0),
        "input_credit_card_debt": get_liability("input_credit_card_debt", 0.0),
        "input_personal_loans": get_liability("input_personal_loans", 0.0),
        "input_other_liabilities": get_liability("input_other_liabilities", 0.0),

        # CRITICAL FIX: Hunt for Family Data in multiple locations
        "children_list": hunt_for_data(["children_rows", "children_list", "temp_children"]),
        "children_rows": hunt_for_data(["children_rows", "children_list", "temp_children"]),
        
        "inheritance_list": hunt_for_data(["inherit_rows", "inheritance_list", "temp_inherit"]),
        "inherit_rows": hunt_for_data(["inherit_rows", "inheritance_list", "temp_inherit"]),
        
        "goals_list": hunt_for_data(["goals_data", "goals_list", "temp_goals"]),
        "goals_data": hunt_for_data(["goals_data", "goals_list", "temp_goals"]),
        
        "custom_expenses": hunt_for_data(["custom_expenses", "custom_expenses_list"]),
        "custom_expenses_list": hunt_for_data(["custom_expenses", "custom_expenses_list"]),
        
        "custom_income": hunt_for_data(["custom_income", "custom_income_list"]),
        "custom_income_list": hunt_for_data(["custom_income", "custom_income_list"])
    }

    # Ensure lists are synced to session state so they don't disappear again
    if data["children_list"]: st.session_state["children_list"] = data["children_list"]
    if data["inheritance_list"]: st.session_state["inheritance_list"] = data["inheritance_list"]
    if data["goals_list"]: st.session_state["goals_list"] = data["goals_list"]

    return data


def load_existing_payload():
    """
    Load previous intake data from snapshots or localStorage.

    CRITICAL FIX: Only load data ONCE per session to avoid overwriting user input!

    PRIORITY:
    1. Try current snapshot (newest versioned data)
    2. Try legacy localStorage (old single-version data)
    3. Load template (first-time user)
    """
    # ✅ CRITICAL: Check if we already loaded data this session
    if 'intake_data_loaded_once' in st.session_state:
        # Return empty dict - initialization blocks will use session_state values instead
        return {}


    # NEW: Try to load from current snapshot first (versioned storage)
    data = get_current_snapshot()

    if data:
        # RETURNING USER - found snapshot

        st.session_state['intake_is_returning_user'] = True
        st.session_state['intake_data_loaded_once'] = True  # Mark as loaded
        # DO NOT show welcome message here - it will show on EVERY page render!
        # Welcome message should only show ONCE on Profile page

        return data

    # Fallback: Try legacy localStorage (for backward compatibility)
    data = load_from_local_storage_encrypted('family_forecast_intake_data')

    if data:
        # RETURNING USER - found legacy data, migrate to snapshot

        st.session_state['intake_is_returning_user'] = True
        st.session_state['intake_data_loaded_once'] = True  # Mark as loaded
        # DO NOT show welcome message here - it will show on EVERY page render!

        return data

    # FIRST-TIME USER - no data found, load template scenario
    st.session_state['intake_is_returning_user'] = False
    st.session_state['intake_data_loaded_once'] = True  # Mark as loaded
    # DO NOT show info message here - it will show on EVERY page render!

    template = load_template_data()

    return template

    # OLD CODE (KEPT FOR ROLLBACK - DO NOT DELETE):
    # shared_path = get_shared_path()
    # if os.path.exists(shared_path):
    #     # RETURNING USER - load their data
    #     try:
    #         with open(shared_path, "r", encoding="utf-8") as f:
    #             data = json.load(f)
    #         st.session_state['intake_is_returning_user'] = True
    #         user_name = data.get('input_user_name', '')
    #         if user_name:
    #             st.success(f"👋 Welcome back, {user_name}! Your previous data has been loaded.")
    #         else:
    #             st.success("👋 Welcome back! Your previous data has been loaded.")
    #         return data
    #     except Exception as e:
    #         st.error(f"❌ Error loading saved data: {e}")
    #         pass

def save_payload(data, snapshot_name=None):
    """
    Save intake data as versioned snapshot (ENCRYPTED)

    PRIVACY FIX + VERSIONING:
    - Data saves to USER'S BROWSER as versioned snapshot
    - Each save creates new version (no overwriting)
    - Data is encrypted before storage
    - User can have multiple saved plans

    Args:
        data: Full INTAKE data dictionary
        snapshot_name: Optional custom name for this version
    """
    # NEW: Save as versioned snapshot
    snapshot_id = save_snapshot(data, snapshot_name)

    if snapshot_id:
        # Mark as saved
        st.session_state['intake_data_saved'] = True
        st.session_state['intake_data_timestamp'] = time.time()
        st.session_state['last_snapshot_id'] = snapshot_id

        # CRITICAL: Set this snapshot as current so Analysis loads it
        from utils.snapshot_manager import set_current_snapshot
        success = set_current_snapshot(snapshot_id)

        # Debug output

        return True

    return False

    # OLD CODE (KEPT FOR ROLLBACK - DO NOT DELETE):
    # success = save_to_local_storage_encrypted('family_forecast_intake_data', data)
    # shared_path = get_shared_path()  # ❌ BROKEN: Same file for all users!
    # with open(shared_path, "w", encoding="utf-8") as f:
    #     json.dump(data, f, indent=2)

def go_to_page(page_name):
    """Navigate to a different intake page"""
    st.session_state.intake_current_page = page_name
    st.rerun()


def load_demo_data():
    """Load demo data (John Smith) into all session_state fields for testing/demonstration"""
    # Profile
    st.session_state['input_user_name'] = "John Smith"
    st.session_state['input_age'] = 65
    st.session_state['input_partner_exists'] = True
    st.session_state['input_partner_name'] = "Jane Smith"
    st.session_state['input_partner_age'] = 63

    # Income
    st.session_state['input_salary_wages'] = 0.0
    st.session_state['input_self_employment_income'] = 0.0
    st.session_state['input_rental_income'] = 0.0
    st.session_state['input_investment_income'] = 2000.0
    st.session_state['input_social_security_income'] = 3000.0
    st.session_state['input_pension_income'] = 3000.0
    st.session_state['input_other_income'] = 0.0
    st.session_state['input_total_income'] = 8000.0

    # Expenses
    st.session_state['input_housing_expenses'] = 1500.0
    st.session_state['input_utilities_expenses'] = 300.0
    st.session_state['input_groceries_expenses'] = 600.0
    st.session_state['input_transportation_expenses'] = 400.0
    st.session_state['input_healthcare_expenses'] = 500.0
    st.session_state['input_insurance_expenses'] = 300.0
    st.session_state['input_property_tax_expenses'] = 400.0
    st.session_state['input_entertainment_expenses'] = 200.0
    st.session_state['input_restaurant_expenses'] = 300.0
    st.session_state['input_travel_expenses'] = 400.0
    st.session_state['input_education_expenses'] = 0.0
    st.session_state['input_childcare_expenses'] = 0.0
    st.session_state['input_clothing_expenses'] = 100.0
    st.session_state['input_charitable_donations'] = 200.0
    st.session_state['input_miscellaneous_expenses'] = 200.0
    st.session_state['input_other_expenses'] = 100.0
    st.session_state['input_total_expenses'] = 5000.0

    # Custom expenses (empty)
    st.session_state['custom_expenses_list'] = []
    st.session_state['custom_expenses'] = []

    # Assets
    st.session_state['input_ira_balance'] = 250000.0
    st.session_state['input_four01k_403b_balance'] = 250000.0
    st.session_state['input_partner_ira_balance'] = 150000.0
    st.session_state['input_partner_four01k_403b_balance'] = 150000.0
    st.session_state['input_taxable_investment_accounts'] = 100000.0
    st.session_state['input_high_yield_savings_account'] = 50000.0
    st.session_state['input_hsa_balance'] = 10000.0
    st.session_state['input_five29_plan_balance'] = 0.0
    st.session_state['input_primary_residence_value'] = 400000.0
    st.session_state['input_secondary_residence_value'] = 0.0
    st.session_state['input_vehicles_value'] = 30000.0
    st.session_state['input_jewelry_collectibles_value'] = 10000.0
    st.session_state['input_business_ownership_value'] = 0.0
    st.session_state['input_cryptocurrency_holdings'] = 0.0
    st.session_state['input_other_assets'] = 0.0

    # Liabilities
    st.session_state['input_mortgage_balance'] = 150000.0
    st.session_state['input_auto_loan_balance'] = 0.0
    st.session_state['input_student_loan_balance'] = 0.0
    st.session_state['input_credit_card_debt'] = 0.0
    st.session_state['input_other_liabilities'] = 0.0

    # Family data (empty - user can add their own)
    st.session_state['temp_children'] = []
    st.session_state['children_list'] = []
    st.session_state['children_rows'] = []
    st.session_state['temp_inherit'] = []
    st.session_state['inheritance_list'] = []
    st.session_state['inherit_rows'] = []
    st.session_state['temp_goals'] = []
    st.session_state['goals_list'] = []
    st.session_state['goals_data'] = []
    st.session_state['custom_expenses'] = []


# ========== ✅ CRITICAL FIX: CALLBACK FUNCTION FOR COMPLETE BUTTON ==========
def transition_to_analysis():
    """
    Callback function that runs BEFORE st.rerun()
    Uses multiple strategies to ensure flags persist across st.rerun()
    """
    import time

    # Strategy 1: Delete old flags AGGRESSIVELY
    keys_to_delete = [
        'intake_data_loaded',
        'intake_data_loaded_message_shown',
        '_intake_loaded_timestamp'
    ]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]

    # Strategy 2: Set MULTIPLE reload flags (redundancy)
    st.session_state['force_reload_intake'] = True
    st.session_state['_force_reload_intake'] = True
    st.session_state['_reload_timestamp'] = time.time()

    # Strategy 3: Set mode flags
    st.session_state.current_mode = 'Analysis'
    st.session_state.mode_selected = True
    st.session_state.intake_completed = True

    # Strategy 4: Add verification flag
    st.session_state['callback_executed'] = True
    st.session_state['callback_timestamp'] = time.time()


# ========== MAIN INTAKE QUESTIONNAIRE ==========
def show_intake_questionnaire():
    """Main function to display the intake questionnaire"""
    # ===== CRITICAL: Clean up stale widget keys BEFORE any widgets render =====
    # This prevents 'cannot be modified after widget instantiated' errors
    widget_keys_to_clean = [
        'children_editor', 'inherit_editor', 'goals_editor', 'custom_expenses_editor',
        'custom_income_editor'  # Add any other data_editor keys here
    ]
    for wk in widget_keys_to_clean:
        if wk in st.session_state:
            del st.session_state[wk]
    
    # DEBUG: Track intake reruns
    import time
    intake_count = st.session_state.get('_debug_intake_count', 0) + 1
    st.session_state['_debug_intake_count'] = intake_count
    
    render_top_navigation(current="INTAKE")

    # Initialize intake page navigation
    if 'intake_current_page' not in st.session_state:
        st.session_state.intake_current_page = 'profile'

    # Initialize "came from review" flag for quick return
    if 'intake_from_review' not in st.session_state:
        st.session_state.intake_from_review = False

    # AUTO-LOAD saved snapshot if user has one (FIRST TIME entering INTAKE this session)
    if 'intake_initialized' not in st.session_state:
        st.session_state['intake_initialized'] = True

        # Check if user has saved snapshots
        from utils.snapshot_manager import get_current_snapshot, has_user_snapshots

        if has_user_snapshots():
            # Load most recent snapshot into session_state
            snapshot_data = get_current_snapshot()

            if snapshot_data:
                # Load all fields into session_state
                for key, value in snapshot_data.items():
                    # WHITELIST: Only copy safe data keys, never widget keys
                    if key.startswith(('input_', 'temp_', '_protected')) or key in (
                        'children_list', 'children_rows', 'inheritance_list', 'inherit_rows',
                        'goals_list', 'goals_data', 'custom_expenses', 'custom_expenses_list',
                        'custom_income', 'custom_income_list', 'schema_version'
                    ):
                        st.session_state[key] = value

                user_name = snapshot_data.get('input_user_name', 'Unknown')
            else:
                pass  # No snapshot data
        else:
            pass  # No user snapshots

    # Progress bar
    pages = ['profile', 'income', 'expenses', 'custom_expenses', 'assets', 'liabilities', 'family', 'review']
    current_idx = pages.index(st.session_state.intake_current_page)
    progress = (current_idx + 1) / len(pages)
    st.progress(progress)

    # Display step name (with better formatting for custom_expenses)
    display_name = st.session_state.intake_current_page.replace('_', ' ').title()
    st.caption(f"Step {current_idx + 1} of {len(pages)}: {display_name}")

    current_page = st.session_state.intake_current_page

    # Show "Return to Review" banner if editing from review page
    if st.session_state.intake_from_review and current_page != 'review':
        st.info("✏️ **Editing from Review Page** - Click the button below to save and return to review when done.")
        if st.button("← Save & Return to Review", type="secondary", use_container_width=True):
            st.session_state.intake_from_review = False
            go_to_page('review')
        st.divider()

    # Force scroll to top on EVERY page load (critical for UX)
    scroll_to_top()

    # Reset flag when reaching review page normally (not from edit)
    if current_page == 'review' and st.session_state.intake_from_review:
        st.session_state.intake_from_review = False

    # ===== PAGE 1: PROFILE =====
    if current_page == 'profile':
        # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
        scroll_to_top()

        # ⚠️  WARN USER ABOUT UNSAVED CHANGES
        st.markdown(UNSAVED_CHANGES_WARNING_JS, unsafe_allow_html=True)

        st.header("👤 Your Profile")

        # PRODUCTION: Auto-select FULL mode (BETA mode hidden for launch)
        # TODO: Restore BETA mode selector post-launch from yesterday's commits
        if "intake_mode" not in st.session_state:
            st.session_state.intake_mode = "full"

        # Clean start - form fields only

        # Widgets WITHOUT key= - we'll manually save on button click
        user_name = st.text_input(
            "Your name",
            value=st.session_state.get("input_user_name", ""),
            placeholder="Enter your name",
            help="Your full name"
        )

        # Single or Couple
        default_mode_is_couple = bool(st.session_state.get("input_partner_exists", False))

        mode = st.radio(
            "Are you planning as:",
            ["Single", "Couple"],
            index=1 if default_mode_is_couple else 0
        )
        partner_exists = (mode == "Couple")

        # Your age
        your_age = st.number_input(
            "Your age",
            min_value=18,
            max_value=100,
            value=st.session_state.get("input_age") or 55,
            step=1,
            help="Your current age"
        )

        # Partner fields (if couple)
        partner_name = ""
        partner_age = 18
        if mode == "Couple":
            partner_name = st.text_input(
                "Partner name",
                value=st.session_state.get("input_partner_name", "")
            )
            partner_age = st.number_input(
                "Partner age",
                min_value=18,
                max_value=100,
                value=st.session_state.get("input_partner_age") or 18,
                step=1
            )

        # Intelligent validation
        level, message = validate_age(your_age, is_partner=False)
        show_validation_message(level, message)

        if mode == "Couple" and partner_age:
            level, message = validate_age(partner_age, is_partner=True)
            show_validation_message(level, message)

            # Validate age gap
            level, message = validate_age_gap(your_age, partner_age)
            show_validation_message(level, message)

        # Navigation buttons
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            # BACK button (disabled on Page 1)
            st.button("← BACK", disabled=True, use_container_width=True)

        with col2:
            # Validate age before allowing NEXT
            age_valid = 18 <= your_age <= 100
            partner_age_valid = True
            if mode == "Couple":
                partner_age_valid = 18 <= partner_age <= 100
            can_proceed = age_valid and partner_age_valid

            # Show validation message if cannot proceed
            if not can_proceed:
                if not age_valid:
                    st.error("⚠️ Your age must be between 18 and 100 to continue.")
                if not partner_age_valid:
                    st.error("⚠️ Partner age must be between 18 and 100 to continue.")

            # NEXT button - disabled if validation fails
            if st.button("NEXT →", type="primary", use_container_width=True, disabled=not can_proceed):
                # CRITICAL: Explicitly save to session_state BEFORE navigating
                # (widgets with key= don't save until after script completes)
                st.session_state['input_user_name'] = user_name
                st.session_state['input_age'] = your_age
                st.session_state['input_partner_exists'] = partner_exists
                if mode == "Couple":
                    st.session_state['input_partner_name'] = partner_name
                    st.session_state['input_partner_age'] = partner_age

                # Navigate to next page
                go_to_page('income')

    # ===== PAGE 2: INCOME =====
    elif current_page == 'income':
        # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
        scroll_to_top()
        st.header("💰 Monthly Income")
        st.markdown("*Enter your typical monthly income from all sources. Enter 0 if not applicable.*")

        # Prominent note about before-tax income
        st.info("📝 **Important:** Enter all income amounts **BEFORE TAXES**. The app will calculate federal and state taxes for you.")

        # Income fields - NO key=, manual save on button click
        salary = st.number_input(
            "Salary/Wages (monthly, before taxes)",
            min_value=0.0,
            max_value=1000000.0,
            value=st.session_state.get("input_salary_wages", 0.0),
            step=100.0,
            help="Your regular employment income before any deductions"
        )

        self_employment = st.number_input(
            "Self-Employment Income (monthly)",
            min_value=0.0,
            max_value=1000000.0,
            value=st.session_state.get("input_self_employment_income", 0.0),
            step=100.0,
            help="Net income from business or freelance work"
        )

        rental = st.number_input(
            "Rental Income (monthly)",
            min_value=0.0,
            max_value=100000.0,
            value=st.session_state.get("input_rental_income", 0.0),
            step=100.0,
            help="Net rental income after expenses"
        )

        investment = st.number_input(
            "Investment Income (monthly, before taxes)",
            min_value=0.0,
            max_value=100000.0,
            value=st.session_state.get("input_investment_income", 0.0),
            step=50.0,
            help="Dividends, interest, capital gains (average monthly, before taxes)"
        )

        social_security = st.number_input(
            "Social Security (monthly, before taxes)",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_social_security_income", 0.0),
            step=50.0,
            help="Your monthly Social Security benefit before any tax withholding"
        )

        pension = st.number_input(
            "Pension Income (monthly, before taxes)",
            min_value=0.0,
            max_value=50000.0,
            value=st.session_state.get("input_pension_income", 0.0),
            step=50.0,
            help="Monthly pension from employer or government, before taxes"
        )

        other_income = st.number_input(
            "Other Income (monthly)",
            min_value=0.0,
            max_value=100000.0,
            value=st.session_state.get("input_other_income", 0.0),
            step=50.0,
            help="Alimony, royalties, or other regular income"
        )

        # Calculate total
        total_income = salary + self_employment + rental + investment + social_security + pension + other_income
        # Store total in session state
        st.session_state.input_total_income = total_income

        # Display total
        st.divider()
        st.metric("Total Monthly Income", f"${total_income:,.2f}")

        # Intelligent validation (GENIUS DESIGN - KEEP ALL!)
        user_age = int(65)

        level, message = validate_total_income(total_income, user_age)
        show_validation_message(level, message)

        level, message = validate_social_security(social_security, user_age)
        show_validation_message(level, message)

        level, message = validate_income_mix(salary + self_employment, pension, social_security, total_income, user_age)
        show_validation_message(level, message)

        # Navigation buttons
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            # BACK button to Page 1
            if st.button("← BACK to Profile", use_container_width=True):
                # CRITICAL: Save data BEFORE navigating back
                st.session_state['input_salary_wages'] = salary
                st.session_state['input_self_employment_income'] = self_employment
                st.session_state['input_rental_income'] = rental
                st.session_state['input_investment_income'] = investment
                st.session_state['input_social_security_income'] = social_security
                st.session_state['input_pension_income'] = pension
                st.session_state['input_other_income'] = other_income
                st.session_state['input_total_income'] = total_income
                go_to_page('profile')

        with col2:
            # NEXT button - manually save all income fields
            if st.button("NEXT →", type="primary", use_container_width=True):
                # CRITICAL: Explicitly save to session_state BEFORE navigating
                st.session_state['input_salary_wages'] = salary
                st.session_state['input_self_employment_income'] = self_employment
                st.session_state['input_rental_income'] = rental
                st.session_state['input_investment_income'] = investment
                st.session_state['input_social_security_income'] = social_security
                st.session_state['input_pension_income'] = pension
                st.session_state['input_other_income'] = other_income
                st.session_state['input_total_income'] = total_income
                go_to_page('expenses')

    # ===== PAGE 3: EXPENSES =====
    elif current_page == 'expenses':
        # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
        scroll_to_top()

        st.header("🏠 Monthly Expenses")
        st.markdown("*Enter your typical monthly expenses. Enter 0 if not applicable.*")

        # Expense fields - widgets WITHOUT key= - we'll manually save on button click
        housing = st.number_input(
            "Housing (rent/mortgage)",
            min_value=0.0,
            max_value=100000.0,
            value=st.session_state.get("input_housing_expenses", 0.0),
            step=100.0,
            help="Monthly rent or mortgage payment"
        )

        utilities = st.number_input(
            "Utilities",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_utilities_expenses", 0.0),
            step=10.0,
            help="Electric, gas, water, internet, phone"
        )

        groceries = st.number_input(
            "Groceries/Food",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_groceries_expenses", 0.0),
            step=50.0,
            help="Food and household supplies"
        )

        transportation = st.number_input(
            "Transportation",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_transportation_expenses", 0.0),
            step=50.0,
            help="Gas, car payments, insurance, public transit"
        )

        healthcare = st.number_input(
            "Healthcare",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_healthcare_expenses", 0.0),
            step=50.0,
            help="Medical, dental, prescriptions, copays"
        )

        insurance = st.number_input(
            "Insurance (non-health)",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_insurance_expenses", 0.0),
            step=25.0,
            help="Life, home, auto insurance (if not included elsewhere)"
        )

        property_tax = st.number_input(
            "Property Tax",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_property_tax_expenses", 0.0),
            step=50.0,
            help="Monthly property tax (if not in mortgage)"
        )

        entertainment = st.number_input(
            "Entertainment",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_entertainment_expenses", 0.0),
            step=25.0,
            help="Streaming, hobbies, sports, activities"
        )

        restaurants = st.number_input(
            "Dining Out/Restaurants",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_restaurant_expenses", 0.0),
            step=25.0,
            help="Meals at restaurants, takeout, delivery"
        )

        travel = st.number_input(
            "Travel/Vacation",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_travel_expenses", 0.0),
            step=50.0,
            help="Average monthly amount for travel/vacations"
        )

        education = st.number_input(
            "Education",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_education_expenses", 0.0),
            step=50.0,
            help="Tuition, courses, student loans"
        )

        childcare = st.number_input(
            "Childcare",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_childcare_expenses", 0.0),
            step=50.0,
            help="Daycare, babysitting, child support"
        )

        clothing = st.number_input(
            "Clothing",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_clothing_expenses", 0.0),
            step=25.0,
            help="Clothing and personal care items"
        )

        charitable = st.number_input(
            "Charitable Donations",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_charitable_donations", 0.0),
            step=25.0,
            help="Regular charitable giving"
        )

        miscellaneous = st.number_input(
            "Miscellaneous",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_miscellaneous_expenses", 0.0),
            step=25.0,
            help="Pet care, gifts, subscriptions, other"
        )

        other_expenses = st.number_input(
            "Other Expenses",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.get("input_other_expenses", 0.0),
            step=25.0,
            help="Any other regular monthly expenses"
        )

        # Calculate total
        total_expenses = (housing + utilities + groceries + transportation + healthcare +
                         insurance + property_tax + entertainment + restaurants + travel +
                         education + childcare + clothing + charitable + miscellaneous + other_expenses)
        # Store total in session state
        st.session_state.input_total_expenses = total_expenses

        # Display total
        st.divider()
        st.metric("Total Monthly Expenses", f"${total_expenses:,.2f}")

        # Intelligent validation (GENIUS DESIGN - KEEP ALL!)
        # Get total income from session_state for validation
        total_income = st.session_state.get('input_total_income', 0.0)

        level, message = validate_total_expenses(total_expenses)
        show_validation_message(level, message)

        level, message = validate_housing_ratio(housing, total_income)
        show_validation_message(level, message)

        level, message = validate_income_vs_expenses(total_income, total_expenses)
        show_validation_message(level, message)

        # Navigation with manual save
        st.divider()
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("← BACK to Income", use_container_width=True):
                # CRITICAL: Save data BEFORE navigating back
                st.session_state['input_housing_expenses'] = housing
                st.session_state['input_utilities_expenses'] = utilities
                st.session_state['input_groceries_expenses'] = groceries
                st.session_state['input_transportation_expenses'] = transportation
                st.session_state['input_healthcare_expenses'] = healthcare
                st.session_state['input_insurance_expenses'] = insurance
                st.session_state['input_property_tax_expenses'] = property_tax
                st.session_state['input_entertainment_expenses'] = entertainment
                st.session_state['input_restaurant_expenses'] = restaurants
                st.session_state['input_travel_expenses'] = travel
                st.session_state['input_education_expenses'] = education
                st.session_state['input_childcare_expenses'] = childcare
                st.session_state['input_clothing_expenses'] = clothing
                st.session_state['input_charitable_donations'] = charitable
                st.session_state['input_miscellaneous_expenses'] = miscellaneous
                st.session_state['input_other_expenses'] = other_expenses
                st.session_state['input_total_expenses'] = total_expenses
                go_to_page('income')

        with col2:
            if st.button("NEXT →", type="primary", use_container_width=True):
                # CRITICAL: Explicitly save to session_state BEFORE navigating
                st.session_state['input_housing_expenses'] = housing
                st.session_state['input_utilities_expenses'] = utilities
                st.session_state['input_groceries_expenses'] = groceries
                st.session_state['input_transportation_expenses'] = transportation
                st.session_state['input_healthcare_expenses'] = healthcare
                st.session_state['input_insurance_expenses'] = insurance
                st.session_state['input_property_tax_expenses'] = property_tax
                st.session_state['input_entertainment_expenses'] = entertainment
                st.session_state['input_restaurant_expenses'] = restaurants
                st.session_state['input_travel_expenses'] = travel
                st.session_state['input_education_expenses'] = education
                st.session_state['input_childcare_expenses'] = childcare
                st.session_state['input_clothing_expenses'] = clothing
                st.session_state['input_charitable_donations'] = charitable
                st.session_state['input_miscellaneous_expenses'] = miscellaneous
                st.session_state['input_other_expenses'] = other_expenses
                st.session_state['input_total_expenses'] = total_expenses
                go_to_page('custom_expenses')

    # ===== PAGE 3.5: CUSTOM MONTHLY INCOME SOURCES =====
    elif current_page == 'custom_expenses':
        # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
        scroll_to_top()
        st.header("💰 Custom Income Sources")
        st.markdown("*Add income sources not covered above (business income, consulting fees, bonuses, side gigs, investment income, etc.)*")

        # Initialize custom income list in session state
        if 'custom_income_list' not in st.session_state:
            # Load from existing data if available
            st.session_state['custom_income_list'] = []

        # Add custom income button
        if st.button("➕ Add Income Source", key="add_custom_income_btn"):
            st.session_state['custom_income_list'].append({
                'Name': '',
                'Monthly Amount': 0.0,
                'Category': 'Other'
            })
            st.rerun()

        if len(st.session_state['custom_income_list']) == 0:
            st.info("Click 'Add Income Source' to add additional income sources, or click 'Next' to skip this section")
        else:
            st.write(f"**{len(st.session_state['custom_income_list'])} custom income source(s) configured**")

            income_to_remove = []

            for idx, income_data in enumerate(st.session_state['custom_income_list']):
                st.markdown(f"#### Income Source {idx + 1}")

                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    name = st.text_input(
                        "Income Source Name:",
                        value=income_data.get('Name', ''),
                        key=f"custom_income_name_{idx}",
                        placeholder="e.g., Consulting, Side Gig, Bonuses"
                    )
                    st.session_state['custom_income_list'][idx]['Name'] = name

                with col2:
                    amount = st.number_input(
                        "Monthly Amount:",
                        value=float(income_data.get('Monthly Amount', 0.0)),
                        min_value=0.0,
                        step=50.0,
                        key=f"custom_income_amount_{idx}"
                    )
                    st.session_state['custom_income_list'][idx]['Monthly Amount'] = amount

                    # SAFE category index lookup (handles missing/invalid categories)
                    category_options = ["Business", "Consulting", "Freelance", "Investment", "Other"]
                    saved_category = income_data.get('Category', 'Other')
                    try:
                        category_index = category_options.index(saved_category)
                    except ValueError:
                        # If saved category not in list, default to "Other"
                        category_index = category_options.index("Other")

                    category = st.selectbox(
                        "Category:",
                        category_options,
                        index=category_index,
                        key=f"custom_income_category_{idx}"
                    )
                    st.session_state['custom_income_list'][idx]['Category'] = category

                with col3:
                    st.write("")  # Spacer
                    st.write("")  # Spacer
                    if st.button("🗑️", key=f"delete_custom_income_{idx}", help="Delete this income source"):
                        income_to_remove.append(idx)

                st.markdown("---")

            # Remove deleted income sources
            for idx in reversed(income_to_remove):
                st.session_state['custom_income_list'].pop(idx)

            # Show total
            total_custom_income = sum(inc.get('Monthly Amount', 0.0) for inc in st.session_state['custom_income_list'])
            st.metric("Total Custom Monthly Income", f"${total_custom_income:,.2f}")

        # Navigation with BACK button
        st.divider()
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("← BACK to Expenses", use_container_width=True):
                # Custom income is already saved directly to session_state during input (via key=)
                st.session_state['custom_income'] = st.session_state.get('custom_income_list', [])
                go_to_page('expenses')

        with col2:
            if st.button("NEXT →", type="primary", use_container_width=True):
                # Custom income is already saved directly to session_state during input
                st.session_state['custom_income'] = st.session_state.get('custom_income_list', [])
                go_to_page('assets')

    # ===== PAGES 4-6: ASSETS, LIABILITIES, FAMILY =====
    # These pages use the intake_review module
    # Pass session_state as existing so widgets load saved values
    elif current_page == 'assets':
        scroll_to_top()
        show_assets_page(dict(st.session_state), save_payload, go_to_page)

    elif current_page == 'liabilities':
        scroll_to_top()
        show_liabilities_page(dict(st.session_state), save_payload, go_to_page)

    elif current_page == 'family':
        scroll_to_top()
        show_family_page(dict(st.session_state), save_payload, go_to_page)

    # ===== PAGE 7: REVIEW (FINAL PAGE with edit buttons!) =====
    elif current_page == 'review':
        # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
        scroll_to_top()

        st.header("📋 Review & Complete Your Intake")
        st.caption("Review all your information before completing - click any section to edit")

        # Navigation: Back to Family button at top
        if st.button("← Back to Family Events", key="back_to_family_top"):
            go_to_page('family')
        st.divider()

        # Collect data from session_state (what user just typed in forms)
        review_data = collect_current_form_data()

        # Profile Summary - READ FROM COLLECTED DATA
        st.subheader("👤 Profile")
        col1, col2 = st.columns(2)
        with col1:
            user_name = review_data.get("input_user_name", "Not provided")
            st.metric("Your Name", user_name)
            st.metric("Your Age", review_data.get("input_age", "N/A"))
        with col2:
            if review_data.get("input_partner_exists"):
                partner_name = review_data.get("input_partner_name", "Partner")
                partner_age = review_data.get("input_partner_age", "N/A")
                st.metric(f"Partner", f"{partner_name}, age {partner_age}")
            else:
                st.metric("Planning Mode", "Single")

        if st.button("✏️ Edit Profile", key="edit_profile", use_container_width=True):
            st.session_state.intake_from_review = True  # Flag to show "Back to Review" button
            go_to_page('profile')

        st.divider()

        # Income & Expenses Summary - READ FROM COLLECTED DATA
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💰 Monthly Income")
            total_income = float(review_data.get("input_total_income", 0.0))
            st.metric("Total Income", f"${total_income:,.2f}")
            if st.button("✏️ Edit Income", key="edit_income", use_container_width=True):
                st.session_state.intake_from_review = True
                go_to_page('income')

        with col2:
            st.subheader("🏠 Monthly Expenses")
            total_expenses = float(review_data.get("input_total_expenses", 0.0))
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
            if st.button("✏️ Edit Expenses", key="edit_expenses", use_container_width=True):
                st.session_state.intake_from_review = True
                go_to_page('expenses')

        # Surplus/Deficit
        surplus = total_income - total_expenses
        if surplus >= 0:
            st.success(f"✅ Monthly Surplus: ${surplus:,.2f}")
        else:
            st.error(f"⚠️ Monthly Deficit: ${abs(surplus):,.2f}")

        st.divider()

        # Custom Income Sources - READ FROM COLLECTED DATA
        custom_income = review_data.get("custom_income", [])
        if custom_income:
            st.subheader("💰 Custom Income Sources")
            total_custom_income = sum(inc.get('Monthly Amount', 0.0) for inc in custom_income)
            st.metric("Total Custom Income", f"${total_custom_income:,.2f}/month")
            with st.expander(f"View {len(custom_income)} custom income source(s)"):
                for inc in custom_income:
                    st.write(f"• **{inc.get('Name', 'N/A')}**: ${inc.get('Monthly Amount', 0):,.2f} ({inc.get('Category', 'N/A')})")
            if st.button("✏️ Edit Custom Income", key="edit_custom_income", use_container_width=True):
                st.session_state.intake_from_review = True
                go_to_page('custom_expenses')  # Still uses 'custom_expenses' as page name for routing
            st.divider()

        # Custom Expenses (Family Support) - READ FROM COLLECTED DATA
        custom_expenses = review_data.get("custom_expenses", [])
        if custom_expenses:
            st.subheader("📝 Custom Monthly Expenses")
            total_custom = sum(exp.get('Monthly Amount', 0.0) for exp in custom_expenses)
            st.metric("Total Custom Expenses", f"${total_custom:,.2f}/month")
            with st.expander(f"View {len(custom_expenses)} custom expense(s)"):
                for exp in custom_expenses:
                    st.write(f"• **{exp.get('Name', 'N/A')}**: ${exp.get('Monthly Amount', 0):,.2f} ({exp.get('Category', 'N/A')})")
            if st.button("✏️ Edit Custom Expenses", key="edit_custom_expenses", use_container_width=True):
                st.session_state.intake_from_review = True
                go_to_page('family')  # Custom expenses are on family page now
            st.divider()

        # Assets & Liabilities Summary - READ FROM COLLECTED DATA
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💎 Total Assets")
            total_assets = sum([
                review_data.get("input_ira_balance", 0.0),
                review_data.get("input_four01k_403b_balance", 0.0),
                review_data.get("input_partner_ira_balance", 0.0),
                review_data.get("input_partner_four01k_403b_balance", 0.0),
                review_data.get("input_taxable_investment_accounts", 0.0),
                review_data.get("input_high_yield_savings_account", 0.0),
                review_data.get("input_hsa_balance", 0.0),
                review_data.get("input_five29_plan_balance", 0.0),
                review_data.get("input_primary_residence_value", 0.0),
                review_data.get("input_secondary_residence_value", 0.0),
                review_data.get("input_vehicles_value", 0.0),
                review_data.get("input_jewelry_collectibles_value", 0.0),
                review_data.get("input_business_ownership_value", 0.0),
                review_data.get("input_cryptocurrency_holdings", 0.0),
                review_data.get("input_other_assets", 0.0)
            ])
            st.metric("Assets", f"${total_assets:,.2f}")
            if st.button("✏️ Edit Assets", key="edit_assets", use_container_width=True):
                st.session_state.intake_from_review = True
                go_to_page('assets')

        with col2:
            st.subheader("💳 Total Liabilities")
            total_liabilities = sum([
                review_data.get("input_mortgage_balance", 0.0),
                review_data.get("input_auto_loan_balance", 0.0),
                review_data.get("input_student_loan_balance", 0.0),
                review_data.get("input_credit_card_debt", 0.0),
                review_data.get("input_other_liabilities", 0.0)
            ])
            st.metric("Liabilities", f"${total_liabilities:,.2f}")
            if st.button("✏️ Edit Liabilities", key="edit_liabilities", use_container_width=True):
                st.session_state.intake_from_review = True
                go_to_page('liabilities')

        # Net Worth
        net_worth = total_assets - total_liabilities
        st.metric("💰 Estimated Net Worth", f"${net_worth:,.2f}")

        st.divider()

        # Family Events Summary - READ FROM COLLECTED DATA
        st.subheader("👨‍👩‍👧‍👦 Family Events")
        children_count = len(review_data.get("children_rows", review_data.get("children_list", [])))
        inherit_count = len(review_data.get("inherit_rows", review_data.get("inheritance_list", [])))
        goals_count = len(review_data.get("goals_list", review_data.get("goals_data", [])))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Children", children_count)
        with col2:
            st.metric("Inheritances", inherit_count)
        with col3:
            st.metric("Goals", goals_count)

        if st.button("✏️ Edit Family Events", key="edit_family", use_container_width=True):
            st.session_state.intake_from_review = True
            go_to_page('family')

        # Final Completion Section
        st.divider()
        st.success("✅ **All sections complete! Review the summary above.**")
        st.info("💾 **Your data is automatically saved to your browser's localStorage (encrypted)**")

        # ═══════════════════════════════════════════════════════════════
        # 💾 SAVE YOUR PLAN - PROMINENT SECTION
        # ═══════════════════════════════════════════════════════════════
        st.divider()
        st.markdown("## 💾 SAVE YOUR RETIREMENT PLAN")
        st.markdown("**⚠️ IMPORTANT:** Save your plan to keep it safe!")

        # Snapshot name input
        col1, col2 = st.columns([3, 1])
        with col1:
            snapshot_name = st.text_input(
                "**Plan Name (optional):**",
                value="",
                placeholder="e.g., 'Conservative Retirement' or 'After Selling House'",
                help="Give this plan a custom name, or leave blank for auto-generated name",
                key="snapshot_name_input"
            )
        with col2:
            st.write("")  # Spacer
            st.write("")  # Spacer
            if st.button("💾 **SAVE PLAN**", type="primary", use_container_width=True, key="save_snapshot_btn"):
                # CRITICAL FIX: Collect CURRENT form data, not old snapshot!
                data = collect_current_form_data()
                name = snapshot_name if snapshot_name else None
                success = save_payload(data, snapshot_name=name)
                if success:
                    # Store message in session state to show AFTER rerun
                    saved_name = snapshot_name if snapshot_name else f"Plan - {datetime.now().strftime('%b %d, %Y')}"
                    st.session_state['snapshot_save_message'] = f"✅ Saved: {saved_name}"

                    # CRITICAL: Set just_saved flag so "Go to Analysis" button appears
                    st.session_state['just_saved'] = True
                    st.session_state['saved_snapshot_name'] = saved_name

                    # Set flag to show balloons AFTER rerun
                    st.session_state['show_balloons_on_load'] = True

                    st.rerun()

        # Show save success message if exists
        if 'snapshot_save_message' in st.session_state:
            st.success(st.session_state['snapshot_save_message'])
            del st.session_state['snapshot_save_message']  # Clear after showing

        # List existing snapshots (SHOW ALL, not just last 5!)
        snapshots = list_snapshots()
        if snapshots:
            st.markdown(f"### 📋 Your Saved Plans ({len(snapshots)} total)")
            if len(snapshots) >= 10:
                st.warning("⚠️ You have 10+ saved plans. Consider deleting old ones to save space.")

            # Show ALL snapshots (reversed so newest first) with DELETE buttons
            for idx, snap in enumerate(reversed(snapshots)):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.caption(f"• **{snap['name']}** - Created: {snap['created'][:16]}")
                with col2:
                    if st.button("🗑️", key=f"delete_snap_{idx}_{snap['id']}", help=f"Delete '{snap['name']}'"):
                        try:
                            from utils.snapshot_manager import delete_snapshot
                            delete_snapshot(snap['id'])
                            st.success(f"✅ Deleted: {snap['name']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Delete failed: {e}")

        # Export/Import Section
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📤 Export All Plans**")
            if st.button("📤 Export Backup (.ffb)", use_container_width=True, key="export_btn"):
                try:
                    backup = export_all_snapshots()
                    backup_json = json.dumps(backup, indent=2)
                    st.download_button(
                        label="📥 Download Backup File",
                        data=backup_json,
                        file_name=f"family_forecast_backup_{datetime.now().strftime('%Y%m%d')}.ffb",
                        mime="application/json",
                        help="Encrypted backup of all your saved plans",
                        use_container_width=True,
                        key="download_backup_btn"
                    )
                    st.success("✅ Backup created! Click Download button above.")
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")

        with col2:
            st.markdown("**📥 Import Plans**")
            uploaded_file = st.file_uploader(
                "Choose backup file (.ffb)",
                type=['ffb', 'json'],
                key="import_uploader",
                help="Import previously exported backup file"
            )
            if uploaded_file:
                try:
                    backup = json.loads(uploaded_file.read())
                    merge_mode = st.radio(
                        "Import mode:",
                        ["merge", "replace"],
                        index=0,
                        help="Merge: Add to existing plans | Replace: Delete all and import",
                        key="import_mode_radio"
                    )
                    if st.button("📥 Import", use_container_width=True, key="import_btn"):
                        success = import_snapshots(backup, merge_mode=merge_mode)
                        if success:
                            st.success("✅ Plans imported successfully!")
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ Import failed: {e}")

        # Show balloons if flag is set (after save rerun)
# Show balloons if flag is set (after save rerun)
        if st.session_state.get('show_balloons_on_load', False):
            st.balloons()
            del st.session_state['show_balloons_on_load']  # Clear flag

        # ═══════════════════════════════════════════════════════════════
        # ✅ COMPLETION SECTION (Fixed Visibility)
        # ═══════════════════════════════════════════════════════════════
        
        # Check if plan is saved (either just now OR previously OR any snapshot exists)
        # Also check session_state cache in case localStorage is disabled
        snapshots = list_snapshots()
        cached_index = st.session_state.get('_cached_snapshots_index', {})
        cached_snapshots = cached_index.get('snapshots', []) if cached_index else []
        has_any_snapshot = len(snapshots) > 0 or len(cached_snapshots) > 0 or st.session_state.get('just_saved', False)
        plan_is_saved = st.session_state.get('just_saved', False) or st.session_state.get('intake_data_saved', False) or has_any_snapshot

        if plan_is_saved:
            # Get the name of the plan to display
            plan_name = st.session_state.get('saved_snapshot_name', 'Your Plan')
            
            # If just saved this second, show success message
            if st.session_state.get('just_saved', False):
                st.success(f"✅ Plan saved successfully: **{plan_name}**")

            st.divider()
            st.markdown("### 🎉 Ready to Continue?")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Edit Plan", use_container_width=True):
                    # Allow user to go back and edit
                    st.session_state['just_saved'] = False
                    go_to_page('profile')
                    st.rerun()

            with col2:
                # This button is now ALWAYS visible if data is saved
                if st.button(
                    "📊 Go to Analysis",
                    type="primary",
                    use_container_width=True
                ):
                    # Show balloons celebration for completing INTAKE!
                    st.balloons()

                    # CRITICAL: Clear intake_data_loaded flag to force Analysis to load saved snapshot
                    if 'intake_data_loaded' in st.session_state:
                        del st.session_state['intake_data_loaded']

                    # Clear scenario auto-load flags to prevent demo override
                    if 'scenario_auto_loaded' in st.session_state:
                        del st.session_state['scenario_auto_loaded']
                    if 'scenario_loaded' in st.session_state:
                        del st.session_state['scenario_loaded']

                    # Set mode flags
                    st.session_state.current_mode = 'Analysis'
                    st.session_state.mode_selected = True
                    st.session_state['just_saved'] = False  # Reset for next time

                    # Switch to Analysis mode
                    st.rerun()
        else:
            # Show info message when not saved yet
            st.info("💡 Please **Save your plan** above to enable the 'Go to Analysis' button.")


    # Footer
    st.divider()
    st.caption("📁 **Data location:** Your browser's localStorage (encrypted, private)")
    st.caption("🔐 **Coming Soon:** Plaid for secure bank data import • Stripe for premium features")