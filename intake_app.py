# intake_app.py - Family Retirement Intake Questionnaire
# Step 2: Profile + Income pages
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
            st.success("✅ Income data saved!")
            st.info("Next page (Expenses) coming soon. For now, click 'Export to Simulator' below to test.")
    
    # Temporary export button (until we add more pages)
    st.divider()
    if st.button("💾 Export to Simulator (Test)", use_container_width=True):
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
        st.success(f"✅ Saved to: {SHARED_PATH}")
        st.info("Now go to your Simulator app and click **'Load from path'** in the sidebar.")

# =====================================================
# PLACEHOLDER FOR FUTURE PAGES
# =====================================================
elif st.session_state.current_page == 'expenses':
    st.header("🏠 Monthly Expenses")
    st.info("Coming in next step...")
    if st.button("← Back to Income"):
        go_to_page('income')

elif st.session_state.current_page == 'assets':
    st.header("💎 Assets & Accounts")
    st.info("Coming soon...")

elif st.session_state.current_page == 'review':
    st.header("📋 Review & Export")
    st.info("Coming soon...")

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.caption("This intake app saves data to a shared file. Your main simulator loads it via 'Import from Intake App'.")
st.caption(f"📁 Save location: `{SHARED_PATH}`")