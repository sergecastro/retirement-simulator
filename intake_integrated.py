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
        st.markdown("*Please enter your basic information. You can enter 0 or leave fields empty if not applicable.*")

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

        # Save and continue (NO BACK BUTTON - linear progression only)
        st.divider()
        if st.button("Next: Income →", type="primary", use_container_width=True):
            # Save profile data
            data = existing.copy()
            data["schema_version"] = "1.0"
            data["input_age"] = int(your_age)
            data["input_partner_exists"] = (mode == "Couple")
            if data["input_partner_exists"] and partner_age is not None:  # FIX: Check partner_age is not None
                data["input_partner_name"] = partner_name
                data["input_partner_age"] = int(partner_age)
            else:
                data.pop("input_partner_name", None)
                data.pop("input_partner_age", None)
            save_payload(data)
            go_to_page('income')

    # ===== PAGE 2: INCOME =====
    elif current_page == 'income':
        st.header("💰 Monthly Income")
        st.markdown("*Enter your typical monthly income from all sources. Enter 0 if not applicable.*")

        # Income fields with defaults from existing data
        salary = st.number_input(
            "Salary/Wages (monthly)",
            min_value=0.0,
            max_value=1000000.0,
            value=float(existing.get("input_salary_wages", 0.0)),
            step=100.0,
            help="Your regular employment income (before taxes)"
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
            "Investment Income (monthly)",
            min_value=0.0,
            max_value=100000.0,
            value=float(existing.get("input_investment_income", 0.0)),
            step=50.0,
            help="Dividends, interest, capital gains (average monthly)"
        )

        social_security = st.number_input(
            "Social Security (monthly)",
            min_value=0.0,
            max_value=10000.0,
            value=float(existing.get("input_social_security_income", 0.0)),
            step=50.0,
            help="Your monthly Social Security benefit"
        )

        pension = st.number_input(
            "Pension Income (monthly)",
            min_value=0.0,
            max_value=50000.0,
            value=float(existing.get("input_pension_income", 0.0)),
            step=50.0,
            help="Monthly pension from employer or government"
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
            save_payload(data)
            go_to_page('expenses')

    # ===== PAGE 3: EXPENSES =====
    elif current_page == 'expenses':
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
        if st.button("Next: Assets →", type="primary", use_container_width=True):
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
            save_payload(data)
            go_to_page('assets')

    # ===== PAGES 4-6: PLACEHOLDER (Will integrate next) =====
    elif current_page in ['assets', 'liabilities', 'family']:
        st.header(f"📝 {current_page.title()} Page")
        st.markdown("*This page is being integrated. For now, proceed to next step.*")
        st.info(f"🚧 {current_page.title()} page will have full data entry fields (coming soon)")

        # Linear navigation - ONLY forward, no back, no escape
        st.divider()
        next_pages = {'assets': 'liabilities', 'liabilities': 'family', 'family': 'review'}
        next_page = next_pages.get(current_page, 'review')

        if st.button(f"Next: {next_page.title()} →", type="primary", use_container_width=True):
            go_to_page(next_page)

    # ===== PAGE 7: REVIEW (FINAL PAGE with celebration!) =====
    elif current_page == 'review':
        st.header("🎉 Review & Complete")

        # CELEBRATION BALLOONS!
        st.balloons()

        st.success("✅ **Congratulations! You've completed the questionnaire!**")

        st.markdown(f"""
        ### What's Next?

        Your data has been saved to:
        `{get_shared_path()}`

        **Choose what to do next:**
        """)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Start Over (Re-enter Data)", use_container_width=True):
                # Reset to profile page
                go_to_page('profile')
        with col2:
            if st.button("📊 Go to Main App (Analysis Mode)", type="primary", use_container_width=True):
                # Mark intake as complete and go to Analysis mode
                st.session_state.intake_in_progress = False
                st.session_state.app_mode = 'Analysis'
                st.session_state.intake_just_completed = True  # Flag to auto-load data
                st.rerun()

    # Footer
    st.divider()
    st.caption(f"📁 Data location: `{get_shared_path()}`")
