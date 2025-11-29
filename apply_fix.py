#!/usr/bin/env python3
"""Apply the exact fixes from Gemini to intake_integrated.py"""

with open('intake_integrated.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# FIX 1: Replace collect_current_form_data with hunt_for_data version
# ============================================================

old_function = '''def collect_current_form_data():
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

    # HELPER: Smartly get list data (Fixes the "0 Children" bug)
    def get_list_data(temp_key, persistent_key):
        # 1. Try to get data from the temporary widget (if user is currently editing)
        temp_data = st.session_state.get(temp_key)

        # 2. If temp data exists and is not empty, use it
        if temp_data and len(temp_data) > 0:
            return temp_data

        # 3. Otherwise, fall back to the persistent saved list
        # (This saves us when the widget is gone on the Review page)
        return st.session_state.get(persistent_key, [])

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

        # Family data - FIXED LOGIC HERE
        "children_list": get_list_data("temp_children", "children_list"),
        "children_rows": get_list_data("temp_children", "children_rows"),
        "inheritance_list": get_list_data("temp_inherit", "inheritance_list"),
        "inherit_rows": get_list_data("temp_inherit", "inherit_rows"),
        "goals_list": get_list_data("temp_goals", "goals_list"),
        "goals_data": get_list_data("temp_goals", "goals_data"),

        "custom_expenses": st.session_state.get("custom_expenses", st.session_state.get("custom_expenses", [])),
        "custom_expenses_list": st.session_state.get("custom_expenses", st.session_state.get("custom_expenses_list", [])),
        "custom_income": st.session_state.get("custom_income", []),
        "custom_income_list": st.session_state.get("custom_income_list", [])
    }

    return data'''

new_function = '''def collect_current_form_data():
    """
    Collect CURRENT form data with AGGRESSIVE data hunting.
    Fixes the '0 Children' and missing Family/Goal data bug.
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
        for key in primary_keys:
            data = st.session_state.get(key)
            if data and isinstance(data, list) and len(data) > 0:
                return data
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
        # We check 'rows' (editor output) AND 'list' (saved data) AND 'temp' (widget key)
        "children_list": hunt_for_data(["children_rows", "children_list", "temp_children"]),
        "children_rows": hunt_for_data(["children_rows", "children_list", "temp_children"]),

        "inheritance_list": hunt_for_data(["inherit_rows", "inheritance_list", "temp_inherit"]),
        "inherit_rows": hunt_for_data(["inherit_rows", "inheritance_list", "temp_inherit"]),

        "goals_list": hunt_for_data(["goals_data", "goals_list", "temp_goals"]),
        "goals_data": hunt_for_data(["goals_data", "goals_list", "temp_goals"]),

        # Fix for Special/Custom Expenses
        "custom_expenses": hunt_for_data(["custom_expenses", "custom_expenses_list"]),
        "custom_expenses_list": hunt_for_data(["custom_expenses", "custom_expenses_list"]),

        "custom_income": hunt_for_data(["custom_income", "custom_income_list"]),
        "custom_income_list": hunt_for_data(["custom_income", "custom_income_list"])
    }

    # Ensure lists are synced to session state so they don't disappear again
    if data["children_list"]: st.session_state["children_list"] = data["children_list"]
    if data["inheritance_list"]: st.session_state["inheritance_list"] = data["inheritance_list"]
    if data["goals_list"]: st.session_state["goals_list"] = data["goals_list"]

    return data'''

content = content.replace(old_function, new_function)

# ============================================================
# FIX 2: Replace the BOTTOM rendering logic
# ============================================================

old_bottom = '''        # Show balloons if flag is set (after save rerun)
# Show balloons if flag is set (after save rerun)
        if st.session_state.get('show_balloons_on_load', False):
            st.balloons()
            del st.session_state['show_balloons_on_load']  # Clear flag

        # ═══════════════════════════════════════════════════════════════
        # ✅ COMPLETION SECTION (Fixed Visibility)
        # ═══════════════════════════════════════════════════════════════

        # Check if plan is saved (either just now OR previously OR any snapshot exists)
        has_any_snapshot = len(list_snapshots()) > 0
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
            st.info("💡 Please **Save your plan** above to enable the 'Go to Analysis' button.")'''

new_bottom = '''        # Show balloons if flag is set (after save rerun)
        if st.session_state.get('show_balloons_on_load', False):
            st.balloons()
            del st.session_state['show_balloons_on_load']

        # ═══════════════════════════════════════════════════════════════
        # ✅ COMPLETION SECTION (FIXED)
        # ═══════════════════════════════════════════════════════════════

        # Check if ANY plan exists (Relaxed check to ensure button appears)
        from utils.snapshot_manager import list_snapshots
        snapshots = list_snapshots()
        has_any_saved_plan = len(snapshots) > 0

        # Also check session flags
        just_saved = st.session_state.get('just_saved', False)

        if has_any_saved_plan or just_saved:
            if just_saved:
                st.success(f"✅ Plan saved successfully!")

            st.divider()
            st.markdown("### 🎉 Ready to Continue?")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Edit Plan", use_container_width=True):
                    st.session_state['just_saved'] = False
                    go_to_page('profile')

            with col2:
                # BUTTON IS NOW FORCED VISIBLE if any plan exists
                if st.button("📊 Go to Analysis", type="primary", use_container_width=True):
                    # 1. Force reload flags
                    st.session_state.current_mode = 'Analysis'
                    st.session_state.mode_selected = True
                    st.session_state['just_saved'] = False

                    # 2. Clear flags that might prevent loading
                    keys_to_clear = ['intake_data_loaded', 'scenario_auto_loaded', 'scenario_loaded']
                    for k in keys_to_clear:
                        if k in st.session_state: del st.session_state[k]

                    # 3. GO!
                    st.rerun()
        else:
            # Only show this if strictly NO plans exist
            st.info("💡 Please **Save your plan** above to enable the 'Go to Analysis' button.")'''

content = content.replace(old_bottom, new_bottom)

with open('intake_integrated.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("DONE! Both functions replaced successfully.")
