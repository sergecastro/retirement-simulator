# intake_app.py - Family Retirement Intake Questionnaire
# Step 3: Profile + Income + Expenses pages
import os
import json
import streamlit as st

# === Configuration ===
SHARED_DIR = r"C:\Users\serge\Desktop\retirement-simulator-dev\retirement-simulator\SHARED"
SHARED_PATH = os.path.join(SHARED_DIR, "intake_payload.json")

def ensure_shared_dir():
    os.makedirs(SHARED_DIR, exist_ok=True)

def load_existing_payload():
    """Load previous intake data if exists"""
    if os.path.exists(SHARED_PATH):
        try:
            with open(SHARED_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

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
pages = ['profile', 'income', 'expenses', 'assets', 'review']
current_idx = pages.index(st.session_state.current_page)
progress = (current_idx + 1) / len(pages)
st.progress(progress)
st.caption(f"Step {current_idx + 1} of {len(pages)}: {st.session_state.current_page.title()}")

# =====================================================
# PAGE 1: PROFILE
# =====================================================
if st.session_state.current_page == 'profile':
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
    
    # Validation hints
    if your_age > 95:
        st.warning("⚠️ Age over 95 is unusual. Please confirm this is correct.")
    if mode == "Couple" and partner_age and partner_age > 95:
        st.warning("⚠️ Partner age over 95 is unusual. Please confirm this is correct.")
    
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

# =====================================================
# PAGE 2: INCOME
# =====================================================
elif st.session_state.current_page == 'income':
    st.header("💰 Monthly Income")
    st.caption("Enter your typical monthly income from all sources")
    
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
    
    # Validation warnings
    if total_income < 500:
        st.warning("⚠️ Total income seems very low. Please verify your entries.")
    elif total_income > 100000:
        st.info("ℹ️ High income detected. Make sure all amounts are monthly (not annual).")
    
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
    
    # Calculate and show surplus/deficit
    total_income = float(existing.get("input_total_income", 0.0))
    if total_income > 0:
        surplus = total_income - total_expenses
        if surplus >= 0:
            st.success(f"✅ Monthly Surplus: ${surplus:,.2f}")
        else:
            st.error(f"⚠️ Monthly Deficit: ${abs(surplus):,.2f}")
    
    # Validation warnings
    if total_expenses < 500:
        st.warning("⚠️ Total expenses seem very low. Please verify your entries.")
    elif total_expenses > 50000:
        st.info("ℹ️ High expenses detected. Make sure all amounts are monthly (not annual).")
    
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
            st.success("✅ Expenses saved!")
            st.info("Assets page coming soon. For now, use 'Export to Simulator' below.")
    
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
# PLACEHOLDER FOR FUTURE PAGES
# =====================================================
elif st.session_state.current_page == 'assets':
    st.header("💎 Assets & Accounts")
    st.info("Coming in next step...")
    if st.button("← Back to Expenses"):
        go_to_page('expenses')

elif st.session_state.current_page == 'review':
    st.header("📋 Review & Export")
    st.info("Coming soon...")

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.caption("This intake app saves data to a shared file. Your main simulator loads it via 'Import from Intake App'.")
st.caption(f"📁 Save location: `{SHARED_PATH}`")