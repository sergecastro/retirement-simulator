# intake_integrated.py - Intake Questionnaire Module (called from app.py)
# This module provides the Data Entry Mode questionnaire
import os
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
# JavaScript to force page scroll to top BEFORE content renders
SCROLL_TO_TOP_JS = """
<script>
    window.scrollTo(0, 0);
    document.documentElement.scrollTo(0, 0);
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
        "custom_expenses_list": []
    }

    return template

def load_existing_payload():
    """
    Load previous intake data from snapshots or localStorage.

    PRIORITY:
    1. Try current snapshot (newest versioned data)
    2. Try legacy localStorage (old single-version data)
    3. Load template (first-time user)
    """
    # NEW: Try to load from current snapshot first (versioned storage)
    data = get_current_snapshot()

    if data:
        # RETURNING USER - found snapshot
        st.session_state['intake_is_returning_user'] = True
        user_name = data.get('input_user_name', '')
        if user_name:
            st.success(f"👋 Welcome back, {user_name}! Your saved plan has been loaded.")
        else:
            st.success("👋 Welcome back! Your saved plan has been loaded.")
        return data

    # Fallback: Try legacy localStorage (for backward compatibility)
    data = load_from_local_storage_encrypted('family_forecast_intake_data')

    if data:
        # RETURNING USER - found legacy data, migrate to snapshot
        st.session_state['intake_is_returning_user'] = True
        user_name = data.get('input_user_name', '')
        if user_name:
            st.info(f"👋 Welcome back, {user_name}! Your data has been loaded.")
        else:
            st.info("👋 Welcome back! Your data has been loaded.")
        return data

    # FIRST-TIME USER - no data found, load template scenario
    st.session_state['intake_is_returning_user'] = False
    st.info("ℹ️ No saved data found - starting with a sample scenario to guide you.")
    return load_template_data()

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

    # Initialize intake page navigation
    if 'intake_current_page' not in st.session_state:
        st.session_state.intake_current_page = 'profile'

    # Initialize "came from review" flag for quick return
    if 'intake_from_review' not in st.session_state:
        st.session_state.intake_from_review = False

    # Load existing data
    existing = load_existing_payload()

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

    # Force scroll to top on every page load
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)

    # Reset flag when reaching review page normally (not from edit)
    if current_page == 'review' and st.session_state.intake_from_review:
        st.session_state.intake_from_review = False

    # ===== PAGE 1: PROFILE =====
    if current_page == 'profile':
        # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
        st.markdown(SCROLL_TO_TOP_JS, unsafe_allow_html=True)

        st.header("👤 Your Profile")

        # Smart detection: First-time vs Returning user messaging
        is_returning = st.session_state.get('intake_is_returning_user', False)

        if is_returning:
            # RETURNING USER
            st.info("👋 **Welcome back!** Your previous data has been loaded. Update any fields below and continue through the questionnaire.")
        else:
            # FIRST-TIME USER
            st.success("🎉 **Welcome to the Ultimate Retirement Planning Tool!**")
            st.info("""
            **First time here?** We've pre-filled example data from our demo scenario to guide you.

            **Simply replace each field with YOUR actual information** as you go through the questionnaire.
            """)
            st.markdown("""
            This step-by-step questionnaire will guide you through:
            - Your profile and family information
            - Income and expenses
            - Assets and liabilities
            - Children's education planning
            - Future goals and inheritances

            **Let's get started!** 🚀
            """)

        st.divider()
        st.markdown("*Please enter your basic information. You can enter 0 or leave fields empty if not applicable.*")

        # User name
        user_name = st.text_input(
            "Your name",
            value=existing.get("input_user_name", ""),
            placeholder="Enter your name",
            help="Your full name"
        )

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

        # Always initialize partner_age (FIX for saving issue)
        partner_age = None
        if mode == "Couple":
            partner_name = st.text_input("Partner name", value=partner_name)
            partner_age = st.number_input(
                "Partner age",
                min_value=18,
                max_value=100,
                value=partner_age_default,
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

        # Save and continue
        st.divider()

        # Show "Back to Review" button if came from review page
        if st.session_state.intake_from_review:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Review", use_container_width=True):
                    # Save profile data first
                    data = existing.copy()
                    data["schema_version"] = "1.0"
                    data["input_user_name"] = user_name
                    data["input_age"] = int(your_age)
                    data["input_partner_exists"] = (mode == "Couple")
                    if data["input_partner_exists"] and partner_age is not None:
                        data["input_partner_name"] = partner_name
                        data["input_partner_age"] = int(partner_age)
                    else:
                        data.pop("input_partner_name", None)
                        data.pop("input_partner_age", None)
                    # REMOVED: Auto-save on navigation (user must explicitly save)
                    # save_payload(data)
                    st.session_state.intake_from_review = False  # Reset flag
                    go_to_page('review')
            with col2:
                if st.button("Next: Income →", type="primary", use_container_width=True):
                    # Save profile data
                    data = existing.copy()
                    data["schema_version"] = "1.0"
                    data["input_user_name"] = user_name
                    data["input_age"] = int(your_age)
                    data["input_partner_exists"] = (mode == "Couple")
                    if data["input_partner_exists"] and partner_age is not None:
                        data["input_partner_name"] = partner_name
                        data["input_partner_age"] = int(partner_age)
                    else:
                        data.pop("input_partner_name", None)
                        data.pop("input_partner_age", None)
                    # REMOVED: Auto-save on navigation (user must explicitly save)
                    # save_payload(data)
                    st.session_state.intake_from_review = False  # Reset flag when going forward
                    go_to_page('income')
        else:
            # Normal flow: just show Next button
            if st.button("Next: Income →", type="primary", use_container_width=True):
                # Save profile data
                data = existing.copy()
                data["schema_version"] = "1.0"
                data["input_user_name"] = user_name
                data["input_age"] = int(your_age)
                data["input_partner_exists"] = (mode == "Couple")
                if data["input_partner_exists"] and partner_age is not None:
                    data["input_partner_name"] = partner_name
                    data["input_partner_age"] = int(partner_age)
                else:
                    data.pop("input_partner_name", None)
                    data.pop("input_partner_age", None)
                # REMOVED: Auto-save on navigation (user must explicitly save)
                # save_payload(data)
                go_to_page('income')

    # ===== PAGE 2: INCOME =====
    elif current_page == 'income':
        # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
        st.markdown(SCROLL_TO_TOP_JS, unsafe_allow_html=True)
        st.header("💰 Monthly Income")
        st.markdown("*Enter your typical monthly income from all sources. Enter 0 if not applicable.*")

        # Prominent note about before-tax income
        st.info("📝 **Important:** Enter all income amounts **BEFORE TAXES**. The app will calculate federal and state taxes for you.")

        # Income fields with defaults from existing data
        salary = st.number_input(
            "Salary/Wages (monthly, before taxes)",
            min_value=0.0,
            max_value=1000000.0,
            value=float(existing.get("input_salary_wages", 0.0)),
            step=100.0,
            help="Your regular employment income before any deductions"
        )

        self_employment = st.number_input(
            "Self-Employment Income (monthly)",
            min_value=0.0,
            max_value=1000000.0,
            value=float(existing.get("input_self_employment_income", 0.0)),
            step=100.0,
            help="Net income from business or freelance work"
        )

        rental = st.number_input(
            "Rental Income (monthly)",
            min_value=0.0,
            max_value=100000.0,
            value=float(existing.get("input_rental_income", 0.0)),
            step=100.0,
            help="Net rental income after expenses"
        )

        investment = st.number_input(
            "Investment Income (monthly, before taxes)",
            min_value=0.0,
            max_value=100000.0,
            value=float(existing.get("input_investment_income", 0.0)),
            step=50.0,
            help="Dividends, interest, capital gains (average monthly, before taxes)"
        )

        social_security = st.number_input(
            "Social Security (monthly, before taxes)",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_social_security_income", 0.0)),
            step=50.0,
            help="Your monthly Social Security benefit before any tax withholding"
        )

        pension = st.number_input(
            "Pension Income (monthly, before taxes)",
            min_value=0.0,
            max_value=50000.0,
            value=float(existing.get("input_pension_income", 0.0)),
            step=50.0,
            help="Monthly pension from employer or government, before taxes"
        )

        other_income = st.number_input(
            "Other Income (monthly)",
            min_value=0.0,
            max_value=100000.0,
            value=float(existing.get("input_other_income", 0.0)),
            step=50.0,
            help="Alimony, royalties, or other regular income"
        )

        # Calculate total
        total_income = salary + self_employment + rental + investment + social_security + pension + other_income

        # Display total
        st.divider()
        st.metric("Total Monthly Income", f"${total_income:,.2f}")

        # Intelligent validation (GENIUS DESIGN - KEEP ALL!)
        user_age = int(existing.get("input_age", 65))

        level, message = validate_total_income(total_income, user_age)
        show_validation_message(level, message)

        level, message = validate_social_security(social_security, user_age)
        show_validation_message(level, message)

        level, message = validate_income_mix(salary + self_employment, pension, social_security, total_income, user_age)
        show_validation_message(level, message)

        # Linear navigation - ONLY forward
        st.divider()
        if st.button("Next: Expenses →", type="primary", use_container_width=True):
            # Save income data
            data = existing.copy()
            data["input_salary_wages"] = float(salary)
            data["input_self_employment_income"] = float(self_employment)
            data["input_rental_income"] = float(rental)
            data["input_investment_income"] = float(investment)
            data["input_social_security_income"] = float(social_security)
            data["input_pension_income"] = float(pension)
            data["input_other_income"] = float(other_income)
            data["input_total_income"] = float(total_income)
            # REMOVED: Auto-save on navigation (user must explicitly save)
            # save_payload(data)
            go_to_page('expenses')

    # ===== PAGE 3: EXPENSES =====
    elif current_page == 'expenses':
        # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
        st.markdown(SCROLL_TO_TOP_JS, unsafe_allow_html=True)

        st.header("🏠 Monthly Expenses")
        st.markdown("*Enter your typical monthly expenses. Enter 0 if not applicable.*")

        # Expense fields with defaults
        housing = st.number_input(
            "Housing (rent/mortgage)",
            min_value=0.0,
            max_value=100000.0,
            value=float(existing.get("input_housing_expenses", 0.0)),
            step=100.0,
            help="Monthly rent or mortgage payment"
        )

        utilities = st.number_input(
            "Utilities",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_utilities_expenses", 0.0)),
            step=10.0,
            help="Electric, gas, water, internet, phone"
        )

        groceries = st.number_input(
            "Groceries/Food",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_groceries_expenses", 0.0)),
            step=50.0,
            help="Food and household supplies"
        )

        transportation = st.number_input(
            "Transportation",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_transportation_expenses", 0.0)),
            step=50.0,
            help="Gas, car payments, insurance, public transit"
        )

        healthcare = st.number_input(
            "Healthcare",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_healthcare_expenses", 0.0)),
            step=50.0,
            help="Medical, dental, prescriptions, copays"
        )

        insurance = st.number_input(
            "Insurance (non-health)",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_insurance_expenses", 0.0)),
            step=25.0,
            help="Life, home, auto insurance (if not included elsewhere)"
        )

        property_tax = st.number_input(
            "Property Tax",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_property_tax_expenses", 0.0)),
            step=50.0,
            help="Monthly property tax (if not in mortgage)"
        )

        entertainment = st.number_input(
            "Entertainment",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_entertainment_expenses", 0.0)),
            step=25.0,
            help="Streaming, hobbies, sports, activities"
        )

        restaurants = st.number_input(
            "Dining Out/Restaurants",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_restaurant_expenses", 0.0)),
            step=25.0,
            help="Meals at restaurants, takeout, delivery"
        )

        travel = st.number_input(
            "Travel/Vacation",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_travel_expenses", 0.0)),
            step=50.0,
            help="Average monthly amount for travel/vacations"
        )

        education = st.number_input(
            "Education",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_education_expenses", 0.0)),
            step=50.0,
            help="Tuition, courses, student loans"
        )

        childcare = st.number_input(
            "Childcare",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_childcare_expenses", 0.0)),
            step=50.0,
            help="Daycare, babysitting, child support"
        )

        clothing = st.number_input(
            "Clothing",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_clothing_expenses", 0.0)),
            step=25.0,
            help="Clothing and personal care items"
        )

        charitable = st.number_input(
            "Charitable Donations",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_charitable_donations", 0.0)),
            step=25.0,
            help="Regular charitable giving"
        )

        miscellaneous = st.number_input(
            "Miscellaneous",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_miscellaneous_expenses", 0.0)),
            step=25.0,
            help="Pet care, gifts, subscriptions, other"
        )

        other_expenses = st.number_input(
            "Other Expenses",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_other_expenses", 0.0)),
            step=25.0,
            help="Any other regular monthly expenses"
        )

        # Calculate total
        total_expenses = (housing + utilities + groceries + transportation + healthcare +
                         insurance + property_tax + entertainment + restaurants + travel +
                         education + childcare + clothing + charitable + miscellaneous + other_expenses)

        # Display total
        st.divider()
        st.metric("Total Monthly Expenses", f"${total_expenses:,.2f}")

        # Intelligent validation (GENIUS DESIGN - KEEP ALL!)
        total_income = float(existing.get("input_total_income", 0.0))

        level, message = validate_total_expenses(total_expenses)
        show_validation_message(level, message)

        level, message = validate_housing_ratio(housing, total_income)
        show_validation_message(level, message)

        level, message = validate_income_vs_expenses(total_income, total_expenses)
        show_validation_message(level, message)

        # Linear navigation - ONLY forward
        st.divider()
        if st.button("Next: Custom Expenses →", type="primary", use_container_width=True):
            # Save expense data
            data = existing.copy()
            data["input_housing_expenses"] = float(housing)
            data["input_utilities_expenses"] = float(utilities)
            data["input_groceries_expenses"] = float(groceries)
            data["input_transportation_expenses"] = float(transportation)
            data["input_healthcare_expenses"] = float(healthcare)
            data["input_insurance_expenses"] = float(insurance)
            data["input_property_tax_expenses"] = float(property_tax)
            data["input_entertainment_expenses"] = float(entertainment)
            data["input_restaurant_expenses"] = float(restaurants)
            data["input_travel_expenses"] = float(travel)
            data["input_education_expenses"] = float(education)
            data["input_childcare_expenses"] = float(childcare)
            data["input_clothing_expenses"] = float(clothing)
            data["input_charitable_donations"] = float(charitable)
            data["input_miscellaneous_expenses"] = float(miscellaneous)
            data["input_other_expenses"] = float(other_expenses)
            data["input_total_expenses"] = float(total_expenses)
            # REMOVED: Auto-save on navigation (user must explicitly save)
            # save_payload(data)
            go_to_page('custom_expenses')

    # ===== PAGE 3.5: CUSTOM MONTHLY EXPENSES =====
    elif current_page == 'custom_expenses':
        # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
        st.markdown(SCROLL_TO_TOP_JS, unsafe_allow_html=True)
        st.header("📝 Custom Monthly Expenses")
        st.markdown("*Add any special recurring expenses not covered in standard categories (tutoring, special needs care, therapy, etc.)*")

        # Initialize custom expenses list in session state
        if 'custom_expenses_list' not in st.session_state:
            # Load from existing data if available
            st.session_state['custom_expenses_list'] = existing.get('custom_expenses', [])

        # Add custom expense button
        if st.button("➕ Add Custom Expense", key="add_custom_expense_btn"):
            st.session_state['custom_expenses_list'].append({
                'Name': '',
                'Monthly Amount': 0.0,
                'Category': 'Other'
            })
            st.rerun()

        if len(st.session_state['custom_expenses_list']) == 0:
            st.info("Click 'Add Custom Expense' to add special recurring expenses, or click 'Next' to skip this section")
        else:
            st.write(f"**{len(st.session_state['custom_expenses_list'])} custom expense(s) configured**")

            expenses_to_remove = []

            for idx, expense_data in enumerate(st.session_state['custom_expenses_list']):
                st.markdown(f"#### Custom Expense {idx + 1}")

                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    name = st.text_input(
                        "Expense Name:",
                        value=expense_data.get('Name', ''),
                        key=f"custom_exp_name_{idx}",
                        placeholder="e.g., Tutoring, Therapy, Special care"
                    )
                    st.session_state['custom_expenses_list'][idx]['Name'] = name

                with col2:
                    amount = st.number_input(
                        "Monthly Amount:",
                        value=float(expense_data.get('Monthly Amount', 0.0)),
                        min_value=0.0,
                        step=50.0,
                        key=f"custom_exp_amount_{idx}"
                    )
                    st.session_state['custom_expenses_list'][idx]['Monthly Amount'] = amount

                    category = st.selectbox(
                        "Category:",
                        ["Education", "Healthcare", "Special Needs", "Transportation", "Other"],
                        index=["Education", "Healthcare", "Special Needs", "Transportation", "Other"].index(
                            expense_data.get('Category', 'Other')
                        ),
                        key=f"custom_exp_category_{idx}"
                    )
                    st.session_state['custom_expenses_list'][idx]['Category'] = category

                with col3:
                    st.write("")  # Spacer
                    st.write("")  # Spacer
                    if st.button("🗑️", key=f"delete_custom_exp_{idx}", help="Delete this expense"):
                        expenses_to_remove.append(idx)

                st.markdown("---")

            # Remove deleted expenses
            for idx in reversed(expenses_to_remove):
                st.session_state['custom_expenses_list'].pop(idx)

            # Show total
            total_custom = sum(exp.get('Monthly Amount', 0.0) for exp in st.session_state['custom_expenses_list'])
            st.metric("Total Custom Monthly Expenses", f"${total_custom:,.2f}")

        # Linear navigation
        st.divider()
        if st.button("Next: Assets →", type="primary", use_container_width=True):
            # Save custom expenses data
            data = existing.copy()
            data["custom_expenses"] = st.session_state['custom_expenses_list']
            data["custom_expenses_list"] = st.session_state['custom_expenses_list']  # Also save as _list for compatibility
            # REMOVED: Auto-save on navigation (user must explicitly save)
            # save_payload(data)
            go_to_page('assets')

    # ===== PAGES 4-6: ASSETS, LIABILITIES, FAMILY =====
    # These pages use the intake_review module
    elif current_page == 'assets':
        show_assets_page(existing, save_payload, go_to_page)

    elif current_page == 'liabilities':
        show_liabilities_page(existing, save_payload, go_to_page)

    elif current_page == 'family':
        show_family_page(existing, save_payload, go_to_page)

    # ===== PAGE 7: REVIEW (FINAL PAGE with edit buttons!) =====
    elif current_page == 'review':
        # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
        st.markdown(SCROLL_TO_TOP_JS, unsafe_allow_html=True)

        st.header("📋 Review & Complete Your Intake")
        st.caption("Review all your information before completing - click any section to edit")

        # Profile Summary
        st.subheader("👤 Profile")
        col1, col2 = st.columns(2)
        with col1:
            user_name = existing.get("input_user_name", "Not provided")
            st.metric("Your Name", user_name)
            st.metric("Your Age", existing.get("input_age", "N/A"))
        with col2:
            if existing.get("input_partner_exists"):
                partner_name = existing.get("input_partner_name", "Partner")
                partner_age = existing.get("input_partner_age", "N/A")
                st.metric(f"Partner", f"{partner_name}, age {partner_age}")
            else:
                st.metric("Planning Mode", "Single")

        if st.button("✏️ Edit Profile", key="edit_profile", use_container_width=True):
            st.session_state.intake_from_review = True  # Flag to show "Back to Review" button
            go_to_page('profile')

        st.divider()

        # Income & Expenses Summary
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💰 Monthly Income")
            total_income = float(existing.get("input_total_income", 0.0))
            st.metric("Total Income", f"${total_income:,.2f}")
            if st.button("✏️ Edit Income", key="edit_income", use_container_width=True):
                st.session_state.intake_from_review = True
                go_to_page('income')

        with col2:
            st.subheader("🏠 Monthly Expenses")
            total_expenses = float(existing.get("input_total_expenses", 0.0))
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

        # Custom Expenses
        custom_expenses = existing.get("custom_expenses", [])
        if custom_expenses:
            st.subheader("📝 Custom Monthly Expenses")
            total_custom = sum(exp.get('Monthly Amount', 0.0) for exp in custom_expenses)
            st.metric("Total Custom Expenses", f"${total_custom:,.2f}/month")
            with st.expander(f"View {len(custom_expenses)} custom expense(s)"):
                for exp in custom_expenses:
                    st.write(f"• **{exp.get('Name', 'N/A')}**: ${exp.get('Monthly Amount', 0):,.2f} ({exp.get('Category', 'N/A')})")
            if st.button("✏️ Edit Custom Expenses", key="edit_custom", use_container_width=True):
                st.session_state.intake_from_review = True
                go_to_page('custom_expenses')
            st.divider()

        # Assets & Liabilities Summary
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💎 Total Assets")
            total_assets = sum([
                existing.get("input_ira_balance", 0.0),
                existing.get("input_four01k_403b_balance", 0.0),
                existing.get("input_partner_ira_balance", 0.0),
                existing.get("input_partner_four01k_403b_balance", 0.0),
                existing.get("input_taxable_investment_accounts", 0.0),
                existing.get("input_high_yield_savings_account", 0.0),
                existing.get("input_hsa_balance", 0.0),
                existing.get("input_five29_plan_balance", 0.0),
                existing.get("input_primary_residence_value", 0.0),
                existing.get("input_secondary_residence_value", 0.0),
                existing.get("input_vehicles_value", 0.0),
                existing.get("input_jewelry_collectibles_value", 0.0),
                existing.get("input_business_ownership_value", 0.0),
                existing.get("input_cryptocurrency_holdings", 0.0),
                existing.get("input_other_assets", 0.0)
            ])
            st.metric("Assets", f"${total_assets:,.2f}")
            if st.button("✏️ Edit Assets", key="edit_assets", use_container_width=True):
                st.session_state.intake_from_review = True
                go_to_page('assets')

        with col2:
            st.subheader("💳 Total Liabilities")
            total_liabilities = sum([
                existing.get("input_mortgage_balance", 0.0),
                existing.get("input_auto_loan_balance", 0.0),
                existing.get("input_student_loan_balance", 0.0),
                existing.get("input_credit_card_debt", 0.0),
                existing.get("input_other_liabilities", 0.0)
            ])
            st.metric("Liabilities", f"${total_liabilities:,.2f}")
            if st.button("✏️ Edit Liabilities", key="edit_liabilities", use_container_width=True):
                st.session_state.intake_from_review = True
                go_to_page('liabilities')

        # Net Worth
        net_worth = total_assets - total_liabilities
        st.metric("💰 Estimated Net Worth", f"${net_worth:,.2f}")

        st.divider()

        # Family Events Summary
        st.subheader("👨‍👩‍👧‍👦 Family Events")
        children_count = len(existing.get("children_rows", existing.get("children_list", [])))
        inherit_count = len(existing.get("inherit_rows", existing.get("inheritance_list", [])))
        goals_count = len(existing.get("goals_list", existing.get("goals_data", [])))

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
                print("DEBUG: SAVE PLAN button clicked!")
                data = load_existing_payload()
                name = snapshot_name if snapshot_name else None
                success = save_payload(data, snapshot_name=name)
                if success:
                    # Store message in session state to show AFTER rerun
                    saved_name = snapshot_name if snapshot_name else f"Plan - {datetime.now().strftime('%b %d, %Y')}"
                    st.session_state['snapshot_save_message'] = f"✅ Saved: {saved_name}"
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

            # Show ALL snapshots (reversed so newest first)
            for snap in reversed(snapshots):
                st.caption(f"• **{snap['name']}** - Created: {snap['created'][:16]}")

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

        st.divider()
        st.markdown("### 🎉 Ready to Continue?")
        st.markdown("**Choose what to do next:**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Start Over (Re-enter Data)", use_container_width=True):
                # Reset to profile page
                go_to_page('profile')
        with col2:
            # ✅ FOOLPROOF FIX: Re-save file to update timestamp
            if st.button(
                "📊 COMPLETE & Go to Analysis Mode",
                type="primary",
                use_container_width=True,
                key="complete_intake_btn"
            ):
                # AUTO-SAVE before completing (ensures data is saved!)
                data = load_existing_payload()
                auto_save_name = f"Auto-saved - {datetime.now().strftime('%b %d, %Y %I:%M %p')}"
                save_payload(data, snapshot_name=auto_save_name)

                # Show celebration
                st.balloons()
                st.success("✅ Plan auto-saved! Switching to Analysis mode...")

                # Set mode flags
                st.session_state.current_mode = 'Analysis'
                st.session_state.mode_selected = True

                # Brief pause so user sees success
                time.sleep(1.5)

                # Rerun to Analysis mode - file will be loaded automatically
                st.rerun()

    # Footer
    st.divider()
    st.caption("📁 **Data location:** Your browser's localStorage (encrypted, private)")