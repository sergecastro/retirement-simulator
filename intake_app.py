# intake_app.py - Family Retirement Intake Questionnaire
# Step 3: Profile + Income + Expenses pages
import os
import json
import streamlit as st
from intake_validation import (validate_age, validate_age_gap, validate_total_income,
                                validate_social_security, validate_income_mix,
                                validate_total_expenses, validate_housing_ratio,
                                validate_income_vs_expenses, show_validation_message)

# === Configuration ===
# Use relative path for deployment compatibility
from pathlib import Path
SHARED_DIR = os.path.join(Path(__file__).parent.parent, "SHARED")
SHARED_PATH = os.path.join(SHARED_DIR, "intake_payload.json")

def ensure_shared_dir():
    os.makedirs(SHARED_DIR, exist_ok=True)

def load_existing_payload():
    """Load previous intake data if exists"""
    data = get_current_snapshot()
    if data:
        return data
    # Load demo if no snapshot
    return {
        "input_user_name": "John Smith",
        "input_age": 70,
        "input_partner_exists": True,
        "input_partner_name": "Jane Smith",
        "input_partner_age": 68,
        # Add other demo fields as needed
    }

def save_payload(data):
    """Save intake data to shared JSON file"""
    ensure_shared_dir()
    with open(SHARED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Page Navigation ===
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'profile'

def go_to_page(page_name):
    st.session_state.current_page = page_name
    st.rerun()

# === App Configuration ===
st.set_page_config(
    page_title="Family Retirement Intake", 
    page_icon="🧭", 
    layout="centered"
)

st.title("🧭 Family Retirement Intake Questionnaire")

# Load existing data
existing = load_existing_payload()

# === PROGRESS BAR ===
pages = ['profile', 'income', 'expenses', 'assets', 'liabilities', 'family', 'review']
current_idx = pages.index(st.session_state.current_page)
progress = (current_idx + 1) / len(pages)
st.progress(progress)
st.caption(f"Step {current_idx + 1} of {len(pages)}: {st.session_state.current_page.title()}")

# =====================================================
# PAGE 1: PROFILE
# =====================================================
if st.session_state.current_page == 'profile':
    st.header("👤 Your Profile")
    
    user_name_default = existing.get("input_user_name", "")
    user_name = st.text_input(
        "Your name",
        placeholder="Enter your name",
        help="Your full name",
        key="input_user_name",
        value=user_name_default
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
    
    if mode == "Couple":
        partner_name = st.text_input(
            "Partner name",
            placeholder="Enter your partner's name",
            help="Your partner's full name",
            key="input_partner_name",
            value=partner_name
        )
        partner_age = st.number_input(
            "Partner age",
            min_value=18,
            max_value=100,
            value=partner_age_default,
            step=1,
            key="input_partner_age"
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
            data["input_user_name"] = user_name
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

# =====================================================
# PAGE 2: INCOME
# =====================================================
elif st.session_state.current_page == 'income':
    st.header("💰 Monthly Income")
    st.caption("Enter your typical monthly income from all sources")

    # === TWO-PATH WORKFLOW CHOICE ===
    with st.expander("💡 **QUICK TIP: Two Ways to Enter Your Data**", expanded=False):
        st.markdown("""
        ### Choose Your Path:

        **📝 Path 1: Manual Entry (Recommended for first-time users)**
        - Simple, clean form below
        - Just enter your numbers manually
        - Perfect for getting started quickly

        **🚀 Path 2: Advanced PDF Parser (Power users / Bulk updates)**
        - Upload bank statements, credit cards, spreadsheets
        - AI-powered extraction with full audit trail
        - Interactive transaction review & reclassification
        - Smart baseline calculation
        - Perfect for quarterly/monthly updates

        ---

        ### Using the Advanced PDF Parser:

        1. **Run the parser tool**:
           ```
           streamlit run bulk_document_processor.py --server.port 8503
           ```

        2. **Upload your documents** (PDFs, images, etc.)

        3. **Review & validate** extracted data with full audit features

        4. **Export** to `intake_payload.json`

        5. **Return here** and use sidebar → "📂 Load from Path" to import

        ---

        **For now, you can continue with manual entry below** ⬇️
        """)

    st.divider()

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
        value=float(existing.get("input_rental_income", 1200.0)),
        step=100.0,
        help="Net rental income after expenses"
    )
    
    investment = st.number_input(
        "Investment Income (monthly)",
        min_value=0.0,
        max_value=100000.0,
        value=float(existing.get("input_investment_income", 400.0)),
        step=50.0,
        help="Dividends, interest, capital gains (average monthly)"
    )
    
    social_security = st.number_input(
        "Social Security (monthly)",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_social_security_income", 2600.0)),
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

    # Intelligent validation
    user_age = int(existing.get("input_age", 65))

    # Validate total income
    level, message = validate_total_income(total_income, user_age)
    show_validation_message(level, message)

    # Validate Social Security
    level, message = validate_social_security(social_security, user_age)
    show_validation_message(level, message)

    # Validate income mix
    level, message = validate_income_mix(salary + self_employment, pension, social_security, total_income, user_age)
    show_validation_message(level, message)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back", use_container_width=True):
            go_to_page('profile')
    with col3:
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

# =====================================================
# PAGE 3: EXPENSES
# =====================================================
elif st.session_state.current_page == 'expenses':
    st.header("🏠 Monthly Expenses")
    st.caption("Enter your typical monthly expenses")

    # === TWO-PATH WORKFLOW CHOICE ===
    with st.expander("💡 **QUICK TIP: Two Ways to Enter Your Data**", expanded=False):
        st.markdown("""
        ### Choose Your Path:

        **📝 Path 1: Manual Entry (Recommended for first-time users)**
        - Simple, clean form below
        - Just enter your numbers manually
        - Perfect for getting started quickly

        **🚀 Path 2: Advanced PDF Parser (Power users / Bulk updates)**
        - Upload bank statements, credit cards, spreadsheets
        - AI-powered extraction with full audit trail
        - Interactive transaction review & reclassification
        - Smart baseline calculation
        - Perfect for quarterly/monthly updates

        ---

        ### Using the Advanced PDF Parser:

        1. **Run the parser tool**:
           ```
           streamlit run bulk_document_processor.py --server.port 8503
           ```

        2. **Upload your documents** (PDFs, images, etc.)

        3. **Review & validate** extracted data with full audit features

        4. **Export** to `intake_payload.json`

        5. **Return here** and use sidebar → "📂 Load from Path" to import

        ---

        **For now, you can continue with manual entry below** ⬇️
        """)

    st.divider()

    # Expense fields with defaults
    housing = st.number_input(
        "Housing (rent/mortgage)",
        min_value=0.0,
        max_value=100000.0,
        value=float(existing.get("input_housing_expenses", 3200.0)),
        step=100.0,
        help="Monthly rent or mortgage payment"
    )
    
    utilities = st.number_input(
        "Utilities",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_utilities_expenses", 450.0)),
        step=10.0,
        help="Electric, gas, water, internet, phone"
    )
    
    groceries = st.number_input(
        "Groceries/Food",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_groceries_expenses", 900.0)),
        step=50.0,
        help="Food and household supplies"
    )
    
    transportation = st.number_input(
        "Transportation",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_transportation_expenses", 600.0)),
        step=50.0,
        help="Gas, car payments, insurance, public transit"
    )
    
    healthcare = st.number_input(
        "Healthcare",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_healthcare_expenses", 500.0)),
        step=50.0,
        help="Medical, dental, prescriptions, copays"
    )
    
    insurance = st.number_input(
        "Insurance (non-health)",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_insurance_expenses", 150.0)),
        step=25.0,
        help="Life, home, auto insurance (if not included elsewhere)"
    )
    
    property_tax = st.number_input(
        "Property Tax",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_property_tax_expenses", 900.0)),
        step=50.0,
        help="Monthly property tax (if not in mortgage)"
    )
    
    entertainment = st.number_input(
        "Entertainment",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_entertainment_expenses", 120.0)),
        step=25.0,
        help="Streaming, hobbies, sports, activities"
    )
    
    restaurants = st.number_input(
        "Dining Out/Restaurants",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_restaurant_expenses", 200.0)),
        step=25.0,
        help="Meals at restaurants, takeout, delivery"
    )
    
    travel = st.number_input(
        "Travel/Vacation",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_travel_expenses", 250.0)),
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
        value=float(existing.get("input_clothing_expenses", 60.0)),
        step=25.0,
        help="Clothing and personal care items"
    )
    
    charitable = st.number_input(
        "Charitable Donations",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_charitable_donations", 50.0)),
        step=25.0,
        help="Regular charitable giving"
    )
    
    miscellaneous = st.number_input(
        "Miscellaneous",
        min_value=0.0,
        max_value=10000.0,
        value=float(existing.get("input_miscellaneous_expenses", 75.0)),
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

    # Intelligent validation
    total_income = float(existing.get("input_total_income", 0.0))

    # Validate total expenses
    level, message = validate_total_expenses(total_expenses)
    show_validation_message(level, message)

    # Validate housing ratio
    level, message = validate_housing_ratio(housing, total_income)
    show_validation_message(level, message)

    # Validate income vs expenses (surplus/deficit)
    level, message = validate_income_vs_expenses(total_income, total_expenses)
    show_validation_message(level, message)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Income", use_container_width=True):
            go_to_page('income')
    with col3:
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
    
    # Temporary export button
    st.divider()
    if st.button("💾 Export to Simulator (Test)", use_container_width=True):
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
        st.success(f"✅ Saved to: {SHARED_PATH}")
        st.info("Now go to your Simulator app and click **'Load from path'** in the sidebar.")

# =====================================================
# PAGES 4-7: Import from separate module
# =====================================================
# =====================================================
# PAGES 4-7: Import from separate module
# =====================================================
elif st.session_state.current_page in ['assets', 'liabilities', 'family', 'review']:
    from intake_review import show_assets_page, show_liabilities_page, show_family_page, show_review_page
    
    if st.session_state.current_page == 'assets':
        show_assets_page(existing, save_payload, go_to_page)
    elif st.session_state.current_page == 'liabilities':
        show_liabilities_page(existing, save_payload, go_to_page)
    elif st.session_state.current_page == 'family':
        show_family_page(existing, save_payload, go_to_page)
    elif st.session_state.current_page == 'review':
        show_review_page(existing, SHARED_PATH, go_to_page)

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.caption("This intake app saves data to a shared file. Your main simulator loads it via 'Import from Intake App'.")
st.caption(f"📁 Save location: `{SHARED_PATH}`")