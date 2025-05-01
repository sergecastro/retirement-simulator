import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import calendar
from datetime import datetime
from openai import OpenAI

# Title
st.title("Retirement Simulation App")

# Password Protection
st.header("🔒 Password Required")
password = st.text_input("Enter the password to access the app:", type="password")
if password not in ["abcd123", "uhiRR2938foq"]:
    st.error("Incorrect password. Please try again or contact the app owner for access.")
    st.stop()

# Embedded saved_scenarios.json data for trusted users (corrected values)
TRUSTED_PASSWORD = "uhiRR2938foq"
EMBEDDED_SCENARIOS = {
    "70+ Scenario": {
        "input_style": "Detailed Breakdown",
        "age_group": "70+",
        "age": 76,
        "partner_name": "Judith",
        "partner_exists": True,
        "partner_age": 74,
        "partner_ira_balance": 0.0,
        "partner_four01k_403b_balance": 0.0,
        "partner_taxable_investment_accounts": 0.0,
        "partner_other_assets": 0.0,
        "partner_liabilities": 0.0,
        "salary_wages": 0.0,
        "self_employment_income": 0.0,
        "rental_income": 2000.0,
        "investment_income": 0.0,
        "social_security_income": 3600.0,
        "pension_income": 6000.0,
        "other_income": 0.0,
        "total_income": 11600.0,
        "housing_expenses": 700.0,
        "utilities_expenses": 1000.0,
        "groceries_expenses": 2000.0,
        "transportation_expenses": 1500.0,
        "healthcare_expenses": 150.0,
        "insurance_expenses": 700.0,
        "real_estate_insurance_expenses": 1300.0,
        "property_tax_expenses": 1850.0,
        "entertainment_expenses": 50.0,
        "restaurant_expenses": 500.0,
        "travel_expenses": 300.0,
        "education_expenses": 0.0,
        "childcare_expenses": 0.0,
        "clothing_expenses": 100.0,
        "charitable_donations": 0.0,
        "miscellaneous_expenses": 0.0,
        "other_expenses": 1000.0,
        "total_expenses": 11150.0,
        "primary_residence_value": 2700000.0,
        "secondary_residence_value": 1700000.0,
        "ira_balance": 400000.0,
        "four01k_403b_balance": 0.0,
        "taxable_investment_accounts": 0.0,
        "pension_fund_value": 1400000.0,
        "life_insurance_cash_value": 0.0,
        "high_yield_savings_account": 0.0,
        "hsa_balance": 0.0,
        "five29_plan_balance": 0.0,
        "vehicles_value": 0.0,
        "jewelry_collectibles_value": 0.0,
        "business_ownership_value": 0.0,
        "cryptocurrency_holdings": 0.0,
        "other_assets": 0.0,
        "primary_residence_mortgage": 0.0,
        "secondary_residence_mortgage": 0.0,
        "auto_loans": 0.0,
        "student_loans": 0.0,
        "credit_card_debt": 0.0,
        "personal_loans": 0.0,
        "business_loans": 0.0,
        "other_liabilities": 0.0,
        "tax_rate": 25.0,
        "inflation_rate": 2.5,
        "investment_return_rate": 5.0,
        "simulation_years": 14
    }
}

# Scenario Management
st.header("🗂️ Scenario Management")
scenario_file = "saved_scenarios.json"

# Load scenarios based on password
if password == TRUSTED_PASSWORD:
    saved_scenarios = EMBEDDED_SCENARIOS
    if not os.path.exists(scenario_file):
        with open(scenario_file, "w") as f:
            json.dump(saved_scenarios, f)
else:
    # For general users, start with an empty scenarios file if it doesn't exist
    if os.path.exists(scenario_file):
        with open(scenario_file, "r") as f:
            saved_scenarios = json.load(f)
    else:
        saved_scenarios = {}

# Scenario selector
scenario_name = st.selectbox("Select Scenario:", ["New Scenario"] + list(saved_scenarios.keys()))
if scenario_name != "New Scenario":
    inputs = saved_scenarios[scenario_name]
else:
    inputs = {}

# Clear saved data and session state (only for general users)
if password != TRUSTED_PASSWORD:
    if st.button("Clear Saved Data and Session State"):
        if os.path.exists(scenario_file):
            os.remove(scenario_file)
        st.session_state.clear()
        st.success("All saved data and session state cleared!")
        st.rerun()
else:
    st.warning("Clearing saved data is disabled for this session to protect embedded scenarios.")

# Preferences
st.header("🧹 Preferences")
input_style = st.radio("Input Style:", ["Detailed Breakdown", "Gross Totals"], index=0 if inputs.get("input_style", "Detailed Breakdown") == "Detailed Breakdown" else 1)

# ───────── Sidebar visual controls ──────────
st.sidebar.header("🖼️ Visual Lab")
show_sankey   = st.sidebar.checkbox("Cash-Flow Sankey",          value=True)
show_goals    = st.sidebar.checkbox("Goal-Funding Gauges",       value=True)
show_calendar = st.sidebar.checkbox("Monthly Cash-Flow Heatmap", value=False)

# Primary User Age
st.header("👤 Primary User Information")
age_group = st.selectbox("Age Group:", ["25-55", "55-70", "70+"], index=0 if inputs.get("age_group", "25-55") == "25-55" else (1 if inputs.get("age_group") == "55-70" else 2))
default_age = inputs.get("age", 40 if age_group == "25-55" else 60 if age_group == "55-70" else 76)
age = st.number_input("Starting Age:", min_value=25, max_value=110, value=default_age)

# Partner Information
st.header("👥 Partner Information")
partner_name = st.text_input("Partner's Name:", value=inputs.get("partner_name", ""))
partner_exists = bool(partner_name.strip())  # Check if a partner name is entered
partner_age = 0
partner_ira_balance = 0.0
partner_four01k_403b_balance = 0.0
partner_taxable_investment_accounts = 0.0
partner_other_assets = 0.0
partner_liabilities = 0.0

if partner_exists:
    partner_age = st.number_input("Partner's Age:", min_value=25, max_value=110, value=inputs.get("partner_age", age))
    partner_ira_balance = st.number_input("Partner's IRA Balance:", value=inputs.get("partner_ira_balance", 0.0))
    partner_four01k_403b_balance = st.number_input("Partner's 401k/403b Balance:", value=inputs.get("partner_four01k_403b_balance", 0.0))
    partner_taxable_investment_accounts = st.number_input("Partner's Taxable Investment Accounts:", value=inputs.get("partner_taxable_investment_accounts", 0.0))
    partner_other_assets = st.number_input("Partner's Other Assets (Savings, Vehicles, Collectibles):", value=inputs.get("partner_other_assets", 0.0))
    partner_liabilities = st.number_input("Partner's Liabilities (Mortgage, Loans, Credit Card Debt):", value=inputs.get("partner_liabilities", 0.0))

# Income & Expenses (Monthly)
st.header("💵 Income & Expenses (Monthly)")
if input_style == "Detailed Breakdown":
    st.subheader("Income")
    salary_wages = st.number_input("Salary/Wages:", value=inputs.get("salary_wages", 0.0))
    self_employment_income = st.number_input("Self-Employment Income:", value=inputs.get("self_employment_income", 0.0))
    rental_income = st.number_input("Rental Income:", value=inputs.get("rental_income", 0.0))
    investment_income = st.number_input("Investment Income:", value=inputs.get("investment_income", 0.0))
    social_security_income = st.number_input("Social Security Income:", value=inputs.get("social_security_income", 0.0))
    pension_income = st.number_input("Pension Income:", value=inputs.get("pension_income", 0.0))
    other_income = st.number_input("Other Income:", value=inputs.get("other_income", 0.0))

    total_income = (salary_wages + self_employment_income + rental_income + investment_income +
                    social_security_income + pension_income + other_income)
    st.write(f"**Total Income (Monthly):** ${total_income:,.2f}")

    st.subheader("Expenses")
    housing_expenses = st.number_input("Housing Expenses (Rent, Mortgage, Maintenance, Excluding Insurance):", value=inputs.get("housing_expenses", 0.0))
    utilities_expenses = st.number_input("Utilities Expenses (Electricity, Gas, Water, Telephone):", value=inputs.get("utilities_expenses", 0.0))
    groceries_expenses = st.number_input("Groceries Expenses:", value=inputs.get("groceries_expenses", 0.0))
    transportation_expenses = st.number_input("Transportation Expenses (Car Gas, Insurance, Maintenance):", value=inputs.get("transportation_expenses", 0.0))
    healthcare_expenses = st.number_input("Healthcare Expenses (Medical Bills, Prescriptions):", value=inputs.get("healthcare_expenses", 0.0))
    insurance_expenses = st.number_input("Insurance Expenses (Health, Life Insurance):", value=inputs.get("insurance_expenses", 0.0))
    real_estate_insurance_expenses = st.number_input("Real Estate Insurance Expenses (Homeowners, Renters Insurance):", value=inputs.get("real_estate_insurance_expenses", 0.0))
    property_tax_expenses = st.number_input("Property Tax Expenses:", value=inputs.get("property_tax_expenses", 0.0))
    entertainment_expenses = st.number_input("Entertainment Expenses (Movies, Concerts, Subscriptions):", value=inputs.get("entertainment_expenses", 0.0))
    restaurant_expenses = st.number_input("Restaurant Expenses:", value=inputs.get("restaurant_expenses", 0.0))
    travel_expenses = st.number_input("Travel Expenses (Vacations, Flights, Hotels):", value=inputs.get("travel_expenses", 0.0))
    education_expenses = st.number_input("Education Expenses (Tuition, Books, Courses):", value=inputs.get("education_expenses", 0.0))
    childcare_expenses = st.number_input("Childcare Expenses:", value=inputs.get("childcare_expenses", 0.0))
    clothing_expenses = st.number_input("Clothing Expenses:", value=inputs.get("clothing_expenses", 0.0))
    charitable_donations = st.number_input("Charitable Donations:", value=inputs.get("charitable_donations", 0.0))
    miscellaneous_expenses = st.number_input("Miscellaneous Expenses (Unexpected Costs, Gifts):", value=inputs.get("miscellaneous_expenses", 0.0))
    other_expenses = st.number_input("Other Expenses:", value=inputs.get("other_expenses", 0.0))

    total_expenses = (housing_expenses + utilities_expenses + groceries_expenses + transportation_expenses +
                      healthcare_expenses + insurance_expenses + real_estate_insurance_expenses + property_tax_expenses +
                      entertainment_expenses + restaurant_expenses + travel_expenses + education_expenses +
                      childcare_expenses + clothing_expenses + charitable_donations + miscellaneous_expenses + other_expenses)
    st.write(f"**Total Expenses (Monthly):** ${total_expenses:,.2f}")
else:
    total_income = st.number_input("Total Income (Monthly):", value=inputs.get("total_income", 0.0))
    st.write(f"**Total Income (Monthly):** ${total_income:,.2f}")
    total_expenses = st.number_input("Total Expenses (Monthly):", value=inputs.get("total_expenses", 0.0))
    st.write(f"**Total Expenses (Monthly):** ${total_expenses:,.2f}")

# Assets & Liabilities (Primary User)
st.header("💰 Assets & Liabilities (Primary User)")
st.subheader("Assets")
primary_residence_value = st.number_input("Primary Residence Value:", value=inputs.get("primary_residence_value", 0.0))
secondary_residence_value = st.number_input("Secondary Residence Value:", value=inputs.get("secondary_residence_value", 0.0))
ira_balance = st.number_input("IRA Balance (Shared):", value=inputs.get("ira_balance", 0.0))
four01k_403b_balance = st.number_input("401k/403b Balance (Shared):", value=inputs.get("four01k_403b_balance", 0.0))
taxable_investment_accounts = st.number_input("Taxable Investment Accounts:", value=inputs.get("taxable_investment_accounts", 0.0))
pension_fund_value = st.number_input("Pension Fund Value (Savings from Employer Pension Plans, Shared):", value=inputs.get("pension_fund_value", 0.0))
life_insurance_cash_value = st.number_input("Life Insurance Cash Value:", value=inputs.get("life_insurance_cash_value", 0.0))
high_yield_savings_account = st.number_input("High-Yield Savings Account:", value=inputs.get("high_yield_savings_account", 0.0))
hsa_balance = st.number_input("HSA Balance (Health Savings Account):", value=inputs.get("hsa_balance", 0.0))
five29_plan_balance = st.number_input("529 Plan Balance (Education Savings):", value=inputs.get("five29_plan_balance", 0.0))
vehicles_value = st.number_input("Vehicles Value:", value=inputs.get("vehicles_value", 0.0))
jewelry_collectibles_value = st.number_input("Jewelry/Collectibles Value:", value=inputs.get("jewelry_collectibles_value", 0.0))
business_ownership_value = st.number_input("Business Ownership Value:", value=inputs.get("business_ownership_value", 0.0))
cryptocurrency_holdings = st.number_input("Cryptocurrency Holdings:", value=inputs.get("cryptocurrency_holdings", 0.0))
other_assets = st.number_input("Other Assets (Savings, Other Investments):", value=inputs.get("other_assets", 0.0))

total_assets = (primary_residence_value + secondary_residence_value + ira_balance + four01k_403b_balance +
                taxable_investment_accounts + pension_fund_value + life_insurance_cash_value +
                high_yield_savings_account + hsa_balance + five29_plan_balance + vehicles_value +
                jewelry_collectibles_value + business_ownership_value + cryptocurrency_holdings + other_assets)
st.write(f"**Total Assets:** ${total_assets:,.2f}")

st.subheader("Liabilities")
primary_residence_mortgage = st.number_input("Primary Residence Mortgage:", value=inputs.get("primary_residence_mortgage", 0.0))
secondary_residence_mortgage = st.number_input("Secondary Residence Mortgage:", value=inputs.get("secondary_residence_mortgage", 0.0))
auto_loans = st.number_input("Auto Loans:", value=inputs.get("auto_loans", 0.0))
student_loans = st.number_input("Student Loans:", value=inputs.get("student_loans", 0.0))
credit_card_debt = st.number_input("Credit Card Debt:", value=inputs.get("credit_card_debt", 0.0))
personal_loans = st.number_input("Personal Loans:", value=inputs.get("personal_loans", 0.0))
business_loans = st.number_input("Business Loans:", value=inputs.get("business_loans", 0.0))
other_liabilities = st.number_input("Other Liabilities (Other Debts):", value=inputs.get("other_liabilities", 0.0))

total_liabilities = (primary_residence_mortgage + secondary_residence_mortgage + auto_loans +
                     student_loans + credit_card_debt + personal_loans + business_loans + other_liabilities)
st.write(f"**Total Liabilities:** ${total_liabilities:,.2f}")

# Goals Input (Updated with Guidance)
st.subheader("🎯 Goals (optional)")
st.markdown("""
**How to Use the Goals Table:**
- **Goal**: Name your goal (e.g., "Annual Travel", "Buy Vacation Home").
- **Target $**: The amount needed for the goal (e.g., 10000 for $10,000). Enter a number without the $ symbol.
- **Target Year Range**: The years during which the goal applies (e.g., "2026-2030" or "2026" for a single year).
- **Recurring?**: How often the goal repeats:
  - "Yearly": Repeats every year within the Target Year Range.
  - "Every 2 Years": Repeats every 2 years within the range.
  - "Every 3 Years": Repeats every 3 years within the range.
  - "No": Occurs only once in the first year of the range.
- **Category**: How the goal affects your finances:
  - "Expense": Increases your annual expenses (e.g., travel, education).
  - "Investment": Deducts from cash flow but adds to savings (e.g., buying property).

**Example:**
- Goal: "Annual Travel", Target $: 5000, Target Year Range: 2026-2030, Recurring?: "Yearly", Category: "Expense"
  - This adds $5,000 to expenses each year from 2026 to 2030.
- Goal: "Buy Car", Target $: 30000, Target Year Range: 2028, Recurring?: "No", Category: "Expense"
  - This adds $30,000 to expenses in 2028 only.
""")
goal_df = st.data_editor(
    pd.DataFrame(columns=["Goal", "Target $", "Target Year Range", "Recurring?", "Category"]),
    num_rows="dynamic", use_container_width=True
)

# Simulation Settings
st.header("⚙️ Simulation Settings")
tax_rate = st.number_input("Tax Rate (%):", value=inputs.get("tax_rate", 25.0))
inflation_rate = st.number_input("Inflation Rate (%):", value=inputs.get("inflation_rate", 2.5))
investment_return_rate = st.number_input("Investment Return Rate (%):", value=inputs.get("investment_return_rate", 5.0))
simulation_years = st.number_input("Simulation Years:", value=inputs.get("simulation_years", 35))

# Monte Carlo Settings
st.header("🎲 Monte Carlo Simulation")
run_monte_carlo = st.checkbox("Run Monte Carlo Simulation", value=False)

# RMD Divisors (for both primary user and partner)
rmd_div = {i: 27-0.9*(i-72) for i in range(73,101)}

# Chart Functions
def make_sankey(income, taxes, spending, savings, year):
    """Simple IN → OUT sankey for a specific year."""
    import plotly.graph_objects as go
    labels = ["Income", "Taxes", "Spending", "Savings"]
    values = [income, taxes, spending, savings]
    links = [0, 0, 0]  # Income splits
    targets = [1, 2, 3]
    fig = go.Figure(go.Sankey(
        node=dict(label=labels, pad=20, thickness=20),
        link=dict(source=links, target=targets, value=values[1:])  # skip Income self-link
    ))
    fig.update_layout(title=f"Where does {year}'s income go?")
    return fig

def make_fan_chart(mc_df):
    med = mc_df.median(axis=1)
    p10 = mc_df.quantile(.10, axis=1)
    p90 = mc_df.quantile(.90, axis=1)
    fig = go.Figure([
        go.Scatter(x=mc_df.index, y=p90, line=dict(width=0)),
        go.Scatter(x=mc_df.index, y=p10, fill='tonexty',
                   fillcolor='rgba(0,0,255,.25)', line=dict(width=0),
                   name='10-90% envelope'),
        go.Scatter(x=mc_df.index, y=med, line=dict(color='#0047ab'),
                   name='Median')
    ])
    fig.update_layout(title="Monte-Carlo Fan Chart",
                      xaxis_title="Year", yaxis_title="Savings ($)")
    return fig

def make_goal_gauge(goal_name, funded_pct):
    """Returns a little gauge for one goal."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=funded_pct*100,
        domain={'x':[0,1],'y':[0,1]},
        title={'text':goal_name},
        gauge={'axis':{'range':[0,100]},
               'bar':{'color':'royalblue'},
               'threshold':{'line':{'color':'red','width':4},
                            'value':100}}
    ))
    fig.update_layout(height=220, margin=dict(l=30,r=30,t=60,b=10))
    return fig

def make_calendar_heatmap(year, monthly_surplus):
    days = []
    for m, surplus in enumerate(monthly_surplus, start=1):
        for d in range(1, calendar.monthrange(year, m)[1] + 1):
            days.append(dict(
                Month = calendar.month_abbr[m],
                Day = d,
                Surplus = surplus / calendar.monthrange(year, m)[1]
            ))
    heat_df = pd.DataFrame(days)
    fig = px.density_heatmap(
        heat_df, x="Day", y="Month", z="Surplus",
        color_continuous_scale="RdYlGn",
        hover_data={"Surplus":":$.0f"}
    )
    fig.update_layout(title=f"Monthly Surplus/Deficit – {year}",
                      yaxis_title="", xaxis_title="")
    return fig

# Monte Carlo Engine
@st.cache_data(ttl=3600)
def run_mc(age, yrs, iters, seed_tuple):
    np.random.seed(hash(seed_tuple) % 2**32)
    out = np.zeros((yrs, iters))
    for c in range(iters):
        inc, exp, sav = tot_inc, tot_exp, init_sav
        for r in range(yrs):
            inc *= 1 + np.random.normal(infl/100, .03)
            exp *= 1 + np.random.normal(infl/100, .03)
            draw = exp - inc * (1 - tax/100)
            if age + r >= 73:
                d = rmd_div.get(age + r, 6.4); draw = max(0, draw - sav/d); sav -= sav/d
            sav = max((sav * (1 + np.random.normal(ret/100, .1))) - max(draw, 0), 0)
            out[r, c] = sav
    return pd.DataFrame(out, index=range(start_year, start_year + yrs))

# OpenAI Setup
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))
def ask(prompt, financial_summary=None):
    system_prompt = """
    You are a Certified Financial Planner (CFP) with deep expertise in retirement planning and financial analysis. Your role is to provide a comprehensive, professional, and insightful financial assessment based on the user's simulation results. The response must be at least 25 lines long and include the following:

    - A detailed analysis of the user's financial situation, including their age, income, expenses, savings, assets, and liabilities.
    - A comparison of the user's financial position to typical U.S. citizens in the same age group, using general statistical benchmarks (e.g., median savings, income levels, debt levels for their age).
    - An evaluation of the simulation results, including the final median savings, net worth, and liabilities, and how these compare to the benchmark provided.
    - Identification of potential risks (e.g., insufficient savings, high expenses, under-funded goals) and opportunities (e.g., investment growth, debt reduction).
    - Specific, actionable recommendations to improve the user's retirement outlook, tailored to their profile and simulation results.
    - If a specific question is provided, address it directly while still providing the broader financial analysis.

    Ensure the tone is professional, empathetic, and encouraging, offering clear next steps for the user to consider. Use precise financial terminology and provide numerical examples where relevant to support your analysis.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt if financial_summary is None else f"Context:\n{financial_summary}\n\nSummary to Analyze:\n{prompt}"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        timeout=30
    )
    return response.choices[0].message.content

# Simulation Logic
st.header("📊 Simulation Results")
if "simulation_results" not in st.session_state:
    st.session_state.simulation_results = None

if st.button("Run Simulation"):
    age = int(age)
    sim_years = int(simulation_years)
    mc_iters = 1000 if run_monte_carlo else 0
    tot_inc = float(total_income * 12)
    tot_exp = float(total_expenses * 12)
    init_sav = float(ira_balance + four01k_403b_balance + taxable_investment_accounts +
                     high_yield_savings_account + hsa_balance + five29_plan_balance +
                     life_insurance_cash_value + cryptocurrency_holdings + pension_fund_value)
    infl = float(inflation_rate)
    tax = float(tax_rate)
    ret = float(investment_return_rate)
    start_year = 2025

    if age_group == "25-55" and (age < 25 or age > 55):
        st.error("Starting Age must be between 25 and 55 for the 25-55 age group.")
    elif age_group == "55-70" and (age < 55 or age > 70):
        st.error("Starting Age must be between 55 and 70 for the 55-70 age group.")
    elif age_group == "70+" and age < 70:
        st.error("Starting Age must be 70 or higher for the 70+ age group.")
    else:
        financial_assets = (
            ira_balance + four01k_403b_balance + taxable_investment_accounts +
            high_yield_savings_account + hsa_balance + five29_plan_balance +
            life_insurance_cash_value + cryptocurrency_holdings + pension_fund_value
        )
        other_assets_total = vehicles_value + jewelry_collectibles_value + business_ownership_value + other_assets
        primary_home_value = primary_residence_value
        secondary_home_value = secondary_residence_value
        total_liabilities = (
            primary_residence_mortgage + secondary_residence_mortgage + auto_loans +
            student_loans + credit_card_debt + personal_loans + business_loans + other_liabilities
        )

        partner_financial_assets = (
            partner_ira_balance + partner_four01k_403b_balance + partner_taxable_investment_accounts
        ) if partner_exists else 0.0
        partner_other_assets_total = partner_other_assets if partner_exists else 0.0
        partner_total_liabilities = partner_liabilities if partner_exists else 0.0

        combined_financial_assets = financial_assets + partner_financial_assets
        combined_other_assets_total = other_assets_total + partner_other_assets_total
        combined_total_liabilities = total_liabilities + partner_total_liabilities

        total_ira = ira_balance + (partner_ira_balance if partner_exists else 0.0)
        total_401k = four01k_403b_balance + (partner_four01k_403b_balance if partner_exists else 0.0)
        primary_ira_for_rmd = total_ira / 2
        partner_ira_for_rmd = total_ira / 2
        primary_401k_for_rmd = total_401k / 2
        partner_401k_for_rmd = total_401k / 2

        years = list(range(2025, 2025 + sim_years))
        ages = list(range(int(age), int(age + sim_years)))
        total_incomes = []
        total_expenses_list = []
        net_draws = []
        rmd_pers1 = []
        rmd_pers2 = []
        total_rmd_before_tax = []
        net_rmd_used_list = []
        cash_used_from_savings_list = []
        savings_open = []
        savings_growth = []
        savings_before_draw = []
        savings_end = []
        primary_home_values = []
        secondary_home_values = []
        total_assets_list = []
        total_liabilities_list = []
        net_worth_list = []
        goal_costs = {}  # Track cumulative cost of each goal

        current_savings = combined_financial_assets
        current_primary_home = primary_home_value
        current_secondary_home = secondary_home_value
        current_liabilities = combined_total_liabilities
        annual_income = total_income * 12
        annual_expenses = total_expenses * 12
        initial_annual_expenses = annual_expenses

        rmd_primary = 0.0
        rmd_partner = 0.0
        for year in range(int(sim_years)):
            current_age = age + year
            current_partner_age = partner_age + year if partner_exists else 0

            annual_income *= (1 + infl / 100)
            if social_security_income > 0:
                annual_income += (social_security_income * 12 * (infl / 100))

            annual_expenses *= (1 + infl / 100)

            # Apply goal cash-flows
            for _, row in goal_df.dropna().iterrows():
                try:
                    target_amount = float(row["Target $"])
                    if target_amount > 1_000_000:
                        st.warning(f"Goal '{row['Goal']}' has a very large Target $ (${target_amount:,.0f}). Please confirm this is correct.")
                    
                    # Parse Target Year Range (e.g., "2026-2030" or "2026")
                    year_range = row["Target Year Range"].strip()
                    if "-" in year_range:
                        start_yr, end_yr = map(int, year_range.split("-"))
                    else:
                        start_yr = end_yr = int(year_range)
                    
                    if not (start_year <= start_yr <= start_year + sim_years - 1):
                        continue
                    if not (start_year <= end_yr <= start_year + sim_years - 1):
                        end_yr = start_year + sim_years - 1

                    # Parse Recurring? frequency
                    recurring = row["Recurring?"].strip().lower()
                    frequency = 1  # Default: every year
                    if recurring == "yearly":
                        frequency = 1
                    elif recurring.startswith("every "):
                        try:
                            freq_num = int(recurring.split(" ")[1])
                            frequency = freq_num
                        except (IndexError, ValueError):
                            frequency = 1 if recurring != "no" else None
                    elif recurring == "no":
                        frequency = None

                    # Apply goal if within the year range and matches frequency
                    if start_yr <= years[year] <= end_yr:
                        if frequency is None:  # Apply only in the start year
                            if years[year] != start_yr:
                                continue
                        elif frequency > 1:  # Apply every N years
                            if (years[year] - start_yr) % frequency != 0:
                                continue

                        category = row["Category"].strip().lower()
                        goal_name = row["Goal"]
                        goal_costs[goal_name] = goal_costs.get(goal_name, 0) + target_amount

                        if category.startswith("exp"):
                            annual_expenses += target_amount
                        else:
                            annual_expenses += target_amount
                            current_savings += target_amount
                except (ValueError, TypeError) as e:
                    st.error(f"Error processing goal '{row['Goal']}': {str(e)}. Please ensure Target $ and Target Year Range are valid numbers or ranges (e.g., '2026' or '2026-2030').")

            annual_net_income = annual_income * (1 - tax / 100)
            net_draw = annual_expenses - annual_net_income

            rmd_primary_ira = 0.0
            rmd_primary_401k = 0.0
            if current_age >= 73:
                divisor = rmd_div.get(current_age, 6.4)
                rmd_primary_ira = primary_ira_for_rmd / divisor
                rmd_primary_401k = primary_401k_for_rmd / divisor
            rmd_primary = rmd_primary_ira + rmd_primary_401k
            net_rmd_primary = rmd_primary * (1 - tax / 100)

            rmd_partner_ira = 0.0
            rmd_partner_401k = 0.0
            if partner_exists and current_partner_age >= 73:
                divisor = rmd_div.get(current_partner_age, 6.4)
                rmd_partner_ira = partner_ira_for_rmd / divisor
                rmd_partner_401k = partner_401k_for_rmd / divisor
            rmd_partner = rmd_partner_ira + rmd_partner_401k
            net_rmd_partner = rmd_partner * (1 - tax / 100)

            total_rmd_before = rmd_primary + rmd_partner
            total_net_rmd = net_rmd_primary + net_rmd_partner
            cash_used_from_savings = max(0, net_draw - total_net_rmd)

            if current_age >= 73:
                primary_ira_for_rmd -= rmd_primary_ira
                primary_401k_for_rmd -= rmd_primary_401k
            if partner_exists and current_partner_age >= 73:
                partner_ira_for_rmd -= rmd_partner_ira
                partner_401k_for_rmd -= rmd_partner_401k

            savings_open_value = current_savings
            savings_growth_value = current_savings * (ret / 100)
            savings_before_draw_value = current_savings + savings_growth_value
            current_savings = savings_before_draw_value - cash_used_from_savings

            current_savings = (
                (primary_ira_for_rmd + partner_ira_for_rmd) +
                (primary_401k_for_rmd + partner_401k_for_rmd) +
                taxable_investment_accounts +
                high_yield_savings_account + hsa_balance + five29_plan_balance +
                life_insurance_cash_value + cryptocurrency_holdings + pension_fund_value +
                (partner_taxable_investment_accounts if partner_exists else 0.0)
            )

            current_primary_home *= 1.03
            current_secondary_home *= 1.03
            current_liabilities = max(0, current_liabilities - (combined_total_liabilities / sim_years))
            total_assets = current_savings + current_primary_home + current_secondary_home + combined_other_assets_total
            current_net_worth = total_assets - current_liabilities

            total_incomes.append(round(annual_income, 2))
            total_expenses_list.append(round(annual_expenses, 2))
            net_draws.append(round(net_draw, 2))
            rmd_pers1.append(round(rmd_primary, 2))
            rmd_pers2.append(round(rmd_partner, 2))
            total_rmd_before_tax.append(round(total_rmd_before, 2))
            net_rmd_used_list.append(round(total_net_rmd, 2))
            cash_used_from_savings_list.append(round(cash_used_from_savings, 2))
            savings_open.append(round(savings_open_value, 2))
            savings_growth.append(round(savings_growth_value, 2))
            savings_before_draw.append(round(savings_before_draw_value, 2))
            savings_end.append(round(current_savings, 2))
            primary_home_values.append(round(current_primary_home, 2))
            secondary_home_values.append(round(current_secondary_home, 2))
            total_assets_list.append(round(total_assets, 2))
            total_liabilities_list.append(round(current_liabilities, 2))
            net_worth_list.append(round(current_net_worth, 2))

        df = pd.DataFrame({
            "Year": years,
            "Age": ages,
            "Total Income": total_incomes,
            "Total Expenses": total_expenses_list,
            "Net Draw": net_draws,
            "RMD (Pers1)": rmd_pers1,
            "RMD (Pers2)": rmd_pers2,
            "Total RMD Before Tax": total_rmd_before_tax,
            "Net Total RMD Used": net_rmd_used_list,
            "Cash Used from Savings": cash_used_from_savings_list,
            "Savings Open": savings_open,
            "Savings Growth": savings_growth,
            "Savings Before Draw": savings_before_draw,
            "Savings End": savings_end,
            "Primary Home Value": primary_home_values,
            "Secondary Home Value": secondary_home_values,
            "Total Assets": total_assets_list,
            "Total Liabilities": total_liabilities_list,
            "Net Worth": net_worth_list
        })

        st.session_state.simulation_results = {
            "df": df,
            "years": years,
            "combined_financial_assets": combined_financial_assets,
            "primary_ira_for_rmd": primary_ira_for_rmd,
            "partner_ira_for_rmd": partner_ira_for_rmd,
            "primary_401k_for_rmd": primary_401k_for_rmd,
            "partner_401k_for_rmd": partner_401k_for_rmd,
            "total_ira": total_ira,
            "total_401k": total_401k,
            "combined_other_assets_total": combined_other_assets_total,
            "partner_exists": partner_exists,
            "partner_age": partner_age,
            "initial_annual_expenses": initial_annual_expenses,
            "total_liabilities": total_liabilities,
            "partner_total_liabilities": partner_total_liabilities,
            "annual_income": annual_income,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "total_assets_list": total_assets_list,
            "primary_home_values": primary_home_values,
            "secondary_home_values": secondary_home_values,
            "savings_end": savings_end,
            "age": age,
            "sim_years": sim_years,
            "mc_iters": mc_iters,
            "tot_inc": tot_inc,
            "tot_exp": tot_exp,
            "init_sav": init_sav,
            "infl": infl,
            "tax": tax,
            "ret": ret,
            "start_year": start_year,
            "annual_expenses": annual_expenses,
            "net_draws": net_draws,
            "rmd_pers1": rmd_pers1,
            "rmd_pers2": rmd_pers2,
            "net_worth_list": net_worth_list,
            "total_liabilities_list": total_liabilities_list,
            "goal_costs": goal_costs,
            "total_incomes": total_incomes,  # Added to session state
            "total_expenses_list": total_expenses_list  # Added to session state
        }

# Display Simulation Results if Available
if st.session_state.simulation_results:
    df = st.session_state.simulation_results["df"]
    years = st.session_state.simulation_results["years"]
    combined_financial_assets = st.session_state.simulation_results["combined_financial_assets"]
    primary_ira_for_rmd = st.session_state.simulation_results["primary_ira_for_rmd"]
    partner_ira_for_rmd = st.session_state.simulation_results["partner_ira_for_rmd"]
    primary_401k_for_rmd = st.session_state.simulation_results["primary_401k_for_rmd"]
    partner_401k_for_rmd = st.session_state.simulation_results["partner_401k_for_rmd"]
    total_ira = st.session_state.simulation_results["total_ira"]
    total_401k = st.session_state.simulation_results["total_401k"]
    combined_other_assets_total = st.session_state.simulation_results["combined_other_assets_total"]
    partner_exists = st.session_state.simulation_results["partner_exists"]
    partner_age = st.session_state.simulation_results["partner_age"]
    initial_annual_expenses = st.session_state.simulation_results["initial_annual_expenses"]
    total_liabilities = st.session_state.simulation_results["total_liabilities"]
    partner_total_liabilities = st.session_state.simulation_results["partner_total_liabilities"]
    annual_income = st.session_state.simulation_results["annual_income"]
    total_income = st.session_state.simulation_results["total_income"]
    total_expenses = st.session_state.simulation_results["total_expenses"]
    total_assets_list = st.session_state.simulation_results["total_assets_list"]
    primary_home_values = st.session_state.simulation_results["primary_home_values"]
    secondary_home_values = st.session_state.simulation_results["secondary_home_values"]
    savings_end = st.session_state.simulation_results["savings_end"]
    age = st.session_state.simulation_results["age"]
    sim_years = st.session_state.simulation_results["sim_years"]
    mc_iters = st.session_state.simulation_results["mc_iters"]
    tot_inc = st.session_state.simulation_results["tot_inc"]
    tot_exp = st.session_state.simulation_results["tot_exp"]
    init_sav = st.session_state.simulation_results["init_sav"]
    infl = st.session_state.simulation_results["infl"]
    tax = st.session_state.simulation_results["tax"]
    ret = st.session_state.simulation_results["ret"]
    start_year = st.session_state.simulation_results["start_year"]
    annual_expenses = st.session_state.simulation_results["annual_expenses"]
    net_draws = st.session_state.simulation_results["net_draws"]
    rmd_pers1 = st.session_state.simulation_results["rmd_pers1"]
    rmd_pers2 = st.session_state.simulation_results["rmd_pers2"]
    net_worth_list = st.session_state.simulation_results["net_worth_list"]
    total_liabilities_list = st.session_state.simulation_results.get("total_liabilities_list", [0])
    goal_costs = st.session_state.simulation_results.get("goal_costs", {})
    total_incomes = st.session_state.simulation_results.get("total_incomes", [])
    total_expenses_list = st.session_state.simulation_results.get("total_expenses_list", [])

    # Compute funded percentages for goals, considering cumulative cost
    goals = []
    for _, row in goal_df.dropna().iterrows():
        try:
            target_amount = float(row["Target $"])
            goal_name = row["Goal"]
            cumulative_cost = goal_costs.get(goal_name, target_amount)
            if cumulative_cost > 0:
                # Compare final savings to the cumulative cost of the goal
                funded = savings_end[-1] / cumulative_cost
                goals.append((goal_name, min(funded, 1.5)))  # cap 150%
        except (ValueError, TypeError):
            continue

    # Display Results
    st.subheader("Simulation Results")
    st.dataframe(df)

    # Graph 1: Savings and Net Worth
    st.subheader("Savings and Net Worth Over Time")
    st.line_chart(df.set_index("Age")[["Savings End", "Net Worth"]])

    # Graph 2: Income vs. Expenses
    st.subheader("Income vs. Expenses Over Time")
    chart_data = df.set_index("Age")[["Total Income", "Total Expenses"]]
    chart_data.index = years  # Use years instead of age for clarity
    st.line_chart(chart_data)

    if run_monte_carlo:
        st.subheader("Monte Carlo Simulation Results (Total Savings)")
        mc_df = run_mc(age, sim_years, mc_iters, seed_tuple=(tot_inc, tot_exp, ret, infl))
        med = mc_df.median(axis=1)
        p10, p90 = mc_df.quantile(.1, axis=1), mc_df.quantile(.9, axis=1)
        fig = go.Figure([
            go.Scatter(x=mc_df.index, y=p90, line=dict(width=0)),
            go.Scatter(x=mc_df.index, y=p10, fill='tonexty', fillcolor='rgba(0,0,255,.2)', line=dict(width=0)),
            go.Scatter(x=mc_df.index, y=med, line=dict(color='royalblue'))
        ])
        fig.update_layout(title="Monte‑Carlo Fan Chart", xaxis_title="Year", yaxis_title="Savings ($)")
        st.plotly_chart(fig, use_container_width=True)

        # Block G2: Monte Carlo probability of success for goals
        prob_lines = []
        goal_probabilities = {}
        for _, row in goal_df.dropna().iterrows():
            try:
                yr_range = row["Target Year Range"].strip()
                if "-" in yr_range:
                    start_yr, end_yr = map(int, yr_range.split("-"))
                else:
                    start_yr = end_yr = int(yr_range)
                yr = end_yr  # Use the end year for probability calculation
                tgt = float(row["Target $"])
                if yr in mc_df.index:
                    prob = (mc_df.loc[yr] >= tgt).mean() * 100
                    prob_lines.append(f"**{row['Goal']}** → {prob:.0f}% of trials meet the target")
                    goal_probabilities[row["Goal"]] = prob
            except (ValueError, TypeError):
                continue

        # 1️⃣ Sankey
        if show_sankey:
            taxes = annual_income * tax / 100
            spending = annual_expenses
            savings = annual_income - taxes - spending
            st.plotly_chart(make_sankey(annual_income, taxes, spending, max(savings, 0), start_year),
                            use_container_width=True)

        # 2️⃣ Fan chart
        if run_monte_carlo:
            st.plotly_chart(make_fan_chart(mc_df), use_container_width=True)

        # 3️⃣ Goal gauges
        if show_goals and goals:
            st.subheader("Goal-Funding Gauges")
            st.markdown("**How to Read the Gauges:** The percentage shows how well-funded your goal is based on your final savings compared to the total cost of the goal over its duration. 100% means you can meet the goal exactly; above 100% means you have extra savings.")
            gcols = st.columns(min(3, len(goals)))
            for (gname, pct), col in zip(goals, gcols):
                col.plotly_chart(make_goal_gauge(gname, pct), use_container_width=True)
                
                if pct >= 1:
                    surplus = (pct - 1) * 100
                    col.success(f"**{surplus:.0f}% over-funded** – you can meet this goal and still have savings left.")
                else:
                    gap = (1 - pct) * 100
                    col.warning(f"**{gap:.0f}% short** – consider increasing savings or adjusting the goal.")

                row_prob = goal_probabilities.get(gname, 0)
                if row_prob < 70:
                    caption = f"{row_prob:.0f}% success • needs attention"
                else:
                    caption = f"{row_prob:.0f}% success"
                col.caption(caption)

            if goals:
                st.markdown("#### Goal-Funding Summary")
                goal_table = pd.DataFrame([
                    {"Goal": g, "Funded %": f"{pct*100:.0f}%", 
                     "Status": "On track" if pct>=1 else "Shortfall"}
                    for g, pct in goals
                ])
                st.dataframe(goal_table, use_container_width=True)

            if prob_lines:
                st.markdown("##### Goal Success Probabilities (Monte-Carlo)")
                st.markdown("\n\n".join(prob_lines))

        # 4️⃣ Calendar heatmap
        if show_calendar:
            if total_incomes and total_expenses_list:  # Ensure lists are not empty
                monthly = [(total_incomes[0] - total_expenses_list[0]) / 12] * 12
                st.plotly_chart(make_calendar_heatmap(start_year, monthly),
                                use_container_width=True)
            else:
                st.warning("Please run the simulation first to generate the cash-flow heatmap.")

        # AI Financial Assessment
        bench = 185_000 if age < 65 else 164_000 if age < 75 else 83_000
        summary = f"""## Summary\nFinal Median: ${med.iloc[-1]:,.0f}\nBenchmark: ${bench:,.0f}"""
        st.markdown(summary)

        financial_summary = f"""
        User Profile:
        - Primary User Age: {age}
        - Partner: {'Present' if partner_exists else 'Not Present'}
        - Partner's Age: {partner_age if partner_exists else 'N/A'}
        - Annual Income: ${(total_income * 12):,.2f}
        - Annual Expenses: ${(total_expenses * 12):,.2f}

        Initial Financial Position:
        - Initial Savings (Combined): ${combined_financial_assets:,.2f}
          - Shared IRA: ${total_ira:,.2f}
          - Shared 401k/403b: ${total_401k:,.2f}
          - Pension Fund: ${pension_fund_value:,.2f}
        - Total Assets (Initial): ${total_assets_list[0] if total_assets_list else 0:,.2f}
          - Primary Home Value: ${primary_home_values[0] if primary_home_values else 0:,.2f}
          - Secondary Home Value: ${secondary_home_values[0] if secondary_home_values else 0:,.2f}
          - Other Assets (Primary + Partner): ${combined_other_assets_total:,.2f}
        - Total Liabilities (Initial): ${total_liabilities if total_liabilities is not None else 0:,.2f}
          - Primary User Liabilities: ${(total_liabilities - partner_total_liabilities) if total_liabilities is not None and partner_total_liabilities is not None else 0:,.2f}
          - Partner Liabilities: ${partner_total_liabilities if partner_exists and partner_total_liabilities is not None else 0:,.2f}

        Simulation Results (After {sim_years} Years):
        - Final Savings: ${savings_end[-1] if savings_end else 0:,.2f}
        - Final Net Worth: ${net_worth_list[-1] if net_worth_list else 0:,.2f}
        - Final Total Assets: ${total_assets_list[-1] if total_assets_list else 0:,.2f}
        - Final Total Liabilities: ${total_liabilities_list[-1] if total_liabilities_list else 0:,.2f}
        - RMD (Pers1, First Year): ${rmd_pers1[0] if rmd_pers1 else 0:,.2f}
        - RMD (Pers2, First Year): ${rmd_pers2[0] if rmd_pers2 else 0:,.2f}

        Trends Over Simulation Period:
        - Income vs. Expenses: Annual net draw started at ${net_draws[0] if net_draws else 0:,.2f} and ended at ${net_draws[-1] if net_draws else 0:,.2f}.
        - Savings Trend: Savings changed from ${savings_end[0] if savings_end else 0:,.2f} to ${savings_end[-1] if savings_end else 0:,.2f}.
        - Net Worth Trend: Net worth changed from ${net_worth_list[0] if net_worth_list else 0:,.2f} to ${net_worth_list[-1] if net_worth_list else 0:,.2f}.
        """
        if st.button("AI Feedback"):
            st.markdown(ask(summary, financial_summary))

        st.write("")
        st.subheader("Ask a Question About Your Financial Future or Calculations")
        st.write("You can ask specific questions about your financial future or calculations here:")
        with st.form(key="question_form"):
            user_question = st.text_area("Enter your question (e.g., 'What happens if I reduce my expenses by 20%?' or 'How are RMDs calculated?'):", height=100, key="user_question_form")
            submit_button = st.form_submit_button(label="Submit Question")
        question_response_output = st.empty()
        if submit_button and user_question:
            question_response = ask(f"Context:\n{financial_summary}\n\nQuestion:\n{user_question}")
            question_response_output.markdown(
                f'<div style="font-family: monospace; white-space: pre-wrap; min-height: 150px;">**Response to Your Question:**\n{question_response}</div>',
                unsafe_allow_html=True
            )

    # Download Results
    csv = df.to_csv(index=False)
    st.download_button("Download Results as CSV", csv, "retirement_simulation.csv", "text/csv")
else:
    st.write("Click 'Run Simulation' to see results.")