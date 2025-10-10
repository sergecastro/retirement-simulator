# File: GROK_app_family_plus.py - Portion 1 (Lines 1-550)
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import math
from datetime import date
import plotly.graph_objects as go
import calendar
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.warning("OpenAI not installed. AI consultation disabled.")
try:
    from dash import Dash, dcc, html
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    st.warning("Dash not installed. Timeline in preview mode.")
try:
    import household_events as he
    EVENTS_AVAILABLE = True
except ImportError:
    EVENTS_AVAILABLE = False
    st.error("household_events.py not found. Family events disabled.")

# Import sub-modules
import simulation
import visuals
import ai_consult
import financial_utils
import data_manager

st.set_page_config(page_title="Grok Family Retirement Plus", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")
st.title("🏠 Grok Family Retirement Planning Plus")
st.markdown("*Advanced Family Lifecycle Financial Simulation & Planning*")
st.header("🔒 Access Control")
password = st.text_input("Enter password:", type="password")
if password not in ["abcd123", "uhiRR2938foq"]:
    st.error("🚫 Incorrect password.")
    st.info("Demo: 'abcd123' | Trusted: 'uhiRR2938foq'")
    st.stop()
TRUSTED_PASSWORD = "uhiRR2938foq"
IS_TRUSTED_USER = (password == TRUSTED_PASSWORD)

# Sidebar
st.sidebar.header("🚀 Advanced Features")
st.sidebar.markdown("**Financial Health Dashboard**")
show_health_dashboard = st.sidebar.checkbox("Financial Health Scoring", value=True, key="show_health")
show_risk_analysis = st.sidebar.checkbox("Risk Analysis Matrix", value=True, key="show_risk")
st.sidebar.markdown("**🗓️ Interactive Timeline & Planning**")
show_timeline = st.sidebar.checkbox("Interactive Family Timeline", value=True, key="show_timeline")
show_scenario_comparison = st.sidebar.checkbox("Scenario Comparison Tool", value=True, key="show_scenarios")  # Changed to True by default
show_extended_projections = st.sidebar.checkbox("Extended Projections (50+ years)", value=False, key="show_extended")
show_family_reports = st.sidebar.checkbox("Family Reports Generator", value=True, key="show_reports")
st.sidebar.markdown("**Visual Analytics Lab**")
show_sankey = st.sidebar.checkbox("Cash-Flow Sankey", value=True, key="show_sankey")
show_goals = st.sidebar.checkbox("Goal-Funding Gauges", value=True, key="show_goals")
show_calendar = st.sidebar.checkbox("Monthly Heatmap", value=False, key="show_calendar")
show_comparison = st.sidebar.checkbox("Competitive Analysis", value=True, key="show_comparison")

# ──────────────────────────────────────────────────────────────────────────────
# Scenario Management
# ──────────────────────────────────────────────────────────────────────────────
st.header("🗂️ Scenario Management")
scenario_file = "saved_scenarios.json"
# Set EMBEDDED_SCENARIOS in session_state for data_manager
st.session_state['EMBEDDED_SCENARIOS'] = {
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
        "simulation_years": 14,
        "mc_iterations": 100,
        "college_inflation_pct": 4.0,
        "base_public_in": 20000.0,
        "base_public_out": 40000.0,
        "base_private": 60000.0
    },
    # Add more if needed
}
st.session_state['IS_TRUSTED_USER'] = IS_TRUSTED_USER

# Behavior:
# - TRUSTED password → load ONLY from saved_scenarios.json (your personal 70+ data)
# - PUBLIC password → load built-in demo scenarios (NO file access; never your personal data)
if password == TRUSTED_PASSWORD:
    # Load from file using data_manager
    saved_scenarios = data_manager.load_scenarios(scenario_file)
    if not saved_scenarios:
        st.warning("No scenarios loaded. Using fallback.")
else:
    # Public (demo) mode - use built-in demo scenarios only, no file access
    saved_scenarios = {
        "Demo Scenario 1": {
            "input_style": "Detailed Breakdown",
            "age_group": "25-55",
            "age": 35,
            "partner_name": "",
            "partner_exists": False,
            "partner_age": 35,
            "partner_ira_balance": 0.0,
            "partner_four01k_403b_balance": 0.0,
            "partner_taxable_investment_accounts": 0.0,
            "partner_other_assets": 0.0,
            "partner_liabilities": 0.0,
            "salary_wages": 5000.0,
            "self_employment_income": 0.0,
            "rental_income": 0.0,
            "investment_income": 0.0,
            "social_security_income": 0.0,
            "pension_income": 0.0,
            "other_income": 0.0,
            "total_income": 5000.0,
            "housing_expenses": 1500.0,
            "utilities_expenses": 300.0,
            "groceries_expenses": 600.0,
            "transportation_expenses": 400.0,
            "healthcare_expenses": 200.0,
            "insurance_expenses": 300.0,
            "real_estate_insurance_expenses": 100.0,
            "property_tax_expenses": 200.0,
            "entertainment_expenses": 200.0,
            "restaurant_expenses": 300.0,
            "travel_expenses": 200.0,
            "education_expenses": 0.0,
            "childcare_expenses": 0.0,
            "clothing_expenses": 100.0,
            "charitable_donations": 0.0,
            "miscellaneous_expenses": 100.0,
            "other_expenses": 0.0,
            "total_expenses": 4400.0,
            "primary_residence_value": 400000.0,
            "secondary_residence_value": 0.0,
            "ira_balance": 50000.0,
            "four01k_403b_balance": 75000.0,
            "taxable_investment_accounts": 25000.0,
            "pension_fund_value": 0.0,
            "life_insurance_cash_value": 0.0,
            "high_yield_savings_account": 20000.0,
            "hsa_balance": 5000.0,
            "five29_plan_balance": 10000.0,
            "vehicles_value": 25000.0,
            "jewelry_collectibles_value": 5000.0,
            "business_ownership_value": 0.0,
            "cryptocurrency_holdings": 0.0,
            "other_assets": 0.0,
            "primary_residence_mortgage": 300000.0,
            "secondary_residence_mortgage": 0.0,
            "auto_loans": 15000.0,
            "student_loans": 25000.0,
            "credit_card_debt": 5000.0,
            "personal_loans": 0.0,
            "business_loans": 0.0,
            "other_liabilities": 0.0,
            "tax_rate": 22.0,
            "inflation_rate": 3.0,
            "investment_return_rate": 7.0,
            "simulation_years": 30,
            "mc_iterations": 100,
            "college_inflation_pct": 4.0,
            "base_public_in": 20000.0,
            "base_public_out": 40000.0,
            "base_private": 60000.0
        },
        # Add more demo scenarios as needed
    }
    st.info("Demo mode: Using built-in scenarios only. No file access.")

# Always define scenario_data
scenario_data = {}
if 'selected_scenario' not in st.session_state:
    st.session_state['selected_scenario'] = "New Scenario"
if show_scenario_comparison:
    selected_scenario = st.sidebar.selectbox("Select Scenario", ["New Scenario"] + list(saved_scenarios.keys()), index=0)
    st.session_state['selected_scenario'] = selected_scenario
    if selected_scenario != "New Scenario" and selected_scenario in saved_scenarios:
        scenario_data = saved_scenarios[selected_scenario]
        st.sidebar.success("Scenario loaded.")
        st.write("Loaded Data for", selected_scenario, ": has", len(scenario_data), "keys")  # Debugging
    scenario_name = st.sidebar.text_input("Scenario Name (for save)", value=selected_scenario)
    if st.sidebar.button("Save Current Scenario") and IS_TRUSTED_USER:
        current_data = financial_utils.get_all_inputs_as_dict(locals())
        saved_scenarios[scenario_name] = current_data
        with open(scenario_file, "w") as f:
            json.dump(saved_scenarios, f, indent=2)
        st.sidebar.success("Scenario saved!")
    elif not IS_TRUSTED_USER:
        st.sidebar.warning("Demo users cannot save scenarios.")

st.header("Personal Information")

input_options = ["Quick Estimate", "Detailed Breakdown"]
default_input_style = scenario_data.get("input_style", "Detailed Breakdown")
input_style_index = input_options.index(default_input_style) if default_input_style in input_options else 1
input_style = st.radio("Input Style", input_options, index=input_style_index)

age_group_options = ["Under 25", "25-55", "Over 55", "70+"]
default_age_group = scenario_data.get("age_group", "25-55")
age_group_index = age_group_options.index(default_age_group) if default_age_group in age_group_options else 1
age_group = st.selectbox("Age Group", age_group_options, index=age_group_index)

default_age = scenario_data.get("age", 35)
age = st.number_input("Your Age", min_value=18, max_value=100, value=default_age)

partner_name = st.text_input("Partner's Name (if applicable)", value=scenario_data.get("partner_name", ""))

partner_exists = st.checkbox("Include Partner?", value=scenario_data.get("partner_exists", False))
if partner_exists:
    partner_age = st.number_input("Partner's Age", min_value=18, max_value=100, value=scenario_data.get("partner_age", 35))
    partner_ira_balance = st.number_input("Partner's IRA Balance", value=scenario_data.get("partner_ira_balance", 0.0))
    partner_four01k_403b_balance = st.number_input("Partner's 401k/403b Balance", value=scenario_data.get("partner_four01k_403b_balance", 0.0))
    partner_taxable_investment_accounts = st.number_input("Partner's Taxable Investment Accounts", value=scenario_data.get("partner_taxable_investment_accounts", 0.0))
    partner_other_assets = st.number_input("Partner's Other Assets", value=scenario_data.get("partner_other_assets", 0.0))
    partner_liabilities = st.number_input("Partner's Liabilities", value=scenario_data.get("partner_liabilities", 0.0))
else:
    partner_age = None
    partner_ira_balance = 0.0
    partner_four01k_403b_balance = 0.0
    partner_taxable_investment_accounts = 0.0
    partner_other_assets = 0.0
    partner_liabilities = 0.0

st.header("Income and Expenses")
if input_style == "Quick Estimate":
    total_income = st.number_input("Monthly Total Income", value=scenario_data.get("total_income", 5000.0))
    total_expenses = st.number_input("Monthly Total Expenses", value=scenario_data.get("total_expenses", 4400.0))
else:
    st.subheader("Income Breakdown")
    salary_wages = st.number_input("Salary/Wages", value=scenario_data.get("salary_wages", 5000.0))
    self_employment_income = st.number_input("Self-Employment Income", value=scenario_data.get("self_employment_income", 0.0))
    rental_income = st.number_input("Rental Income", value=scenario_data.get("rental_income", 0.0))
    investment_income = st.number_input("Investment Income", value=scenario_data.get("investment_income", 0.0))
    social_security_income = st.number_input("Social Security Income", value=scenario_data.get("social_security_income", 0.0))
    pension_income = st.number_input("Pension Income", value=scenario_data.get("pension_income", 0.0))
    other_income = st.number_input("Other Income", value=scenario_data.get("other_income", 0.0))
    total_income = financial_utils.calculate_total_income(salary_wages, self_employment_income, rental_income, investment_income, social_security_income, pension_income, other_income)

    st.subheader("Expenses Breakdown")
    housing_expenses = st.number_input("Housing", value=scenario_data.get("housing_expenses", 1500.0))
    utilities_expenses = st.number_input("Utilities", value=scenario_data.get("utilities_expenses", 300.0))
    groceries_expenses = st.number_input("Groceries", value=scenario_data.get("groceries_expenses", 600.0))
    transportation_expenses = st.number_input("Transportation", value=scenario_data.get("transportation_expenses", 400.0))
    healthcare_expenses = st.number_input("Healthcare", value=scenario_data.get("healthcare_expenses", 200.0))
    insurance_expenses = st.number_input("Insurance", value=scenario_data.get("insurance_expenses", 300.0))
    real_estate_insurance_expenses = st.number_input("Real Estate Insurance", value=scenario_data.get("real_estate_insurance_expenses", 100.0))
    property_tax_expenses = st.number_input("Property Tax", value=scenario_data.get("property_tax_expenses", 200.0))
    entertainment_expenses = st.number_input("Entertainment", value=scenario_data.get("entertainment_expenses", 200.0))
    restaurant_expenses = st.number_input("Restaurants", value=scenario_data.get("restaurant_expenses", 300.0))
    travel_expenses = st.number_input("Travel", value=scenario_data.get("travel_expenses", 200.0))
    education_expenses = st.number_input("Education", value=scenario_data.get("education_expenses", 0.0))
    childcare_expenses = st.number_input("Childcare", value=scenario_data.get("childcare_expenses", 0.0))
    clothing_expenses = st.number_input("Clothing", value=scenario_data.get("clothing_expenses", 100.0))
    charitable_donations = st.number_input("Charitable Donations", value=scenario_data.get("charitable_donations", 0.0))
    miscellaneous_expenses = st.number_input("Miscellaneous", value=scenario_data.get("miscellaneous_expenses", 100.0))
    other_expenses = st.number_input("Other Expenses", value=scenario_data.get("other_expenses", 0.0))
    total_expenses = financial_utils.calculate_total_expenses(housing_expenses, utilities_expenses, groceries_expenses, transportation_expenses, healthcare_expenses, insurance_expenses, real_estate_insurance_expenses, property_tax_expenses, entertainment_expenses, restaurant_expenses, travel_expenses, education_expenses, childcare_expenses, clothing_expenses, charitable_donations, miscellaneous_expenses, other_expenses)

monthly_surplus = total_income - total_expenses
st.metric("Monthly Surplus/Deficit", f"${monthly_surplus:,.2f}")

st.header("Assets and Liabilities")
primary_residence_value = st.number_input("Primary Residence Value", value=scenario_data.get("primary_residence_value", 400000.0))
secondary_residence_value = st.number_input("Secondary Residence Value", value=scenario_data.get("secondary_residence_value", 0.0))
ira_balance = st.number_input("IRA Balance", value=scenario_data.get("ira_balance", 50000.0))
four01k_403b_balance = st.number_input("401k/403b Balance", value=scenario_data.get("four01k_403b_balance", 75000.0))
taxable_investment_accounts = st.number_input("Taxable Investment Accounts", value=scenario_data.get("taxable_investment_accounts", 25000.0))
pension_fund_value = st.number_input("Pension Fund Value", value=scenario_data.get("pension_fund_value", 0.0))
life_insurance_cash_value = st.number_input("Life Insurance Cash Value", value=scenario_data.get("life_insurance_cash_value", 0.0))
high_yield_savings_account = st.number_input("High-Yield Savings Account", value=scenario_data.get("high_yield_savings_account", 20000.0))
hsa_balance = st.number_input("HSA Balance", value=scenario_data.get("hsa_balance", 5000.0))
five29_plan_balance = st.number_input("529 Plan Balance", value=scenario_data.get("five29_plan_balance", 10000.0))
vehicles_value = st.number_input("Vehicles Value", value=scenario_data.get("vehicles_value", 25000.0))
jewelry_collectibles_value = st.number_input("Jewelry/Collectibles Value", value=scenario_data.get("jewelry_collectibles_value", 5000.0))
business_ownership_value = st.number_input("Business Ownership Value", value=scenario_data.get("business_ownership_value", 0.0))
cryptocurrency_holdings = st.number_input("Cryptocurrency Holdings", value=scenario_data.get("cryptocurrency_holdings", 0.0))
other_assets = st.number_input("Other Assets", value=scenario_data.get("other_assets", 0.0))

combined_financial_assets = financial_utils.calculate_liquid_assets(ira_balance, four01k_403b_balance, taxable_investment_accounts, pension_fund_value, life_insurance_cash_value, high_yield_savings_account, hsa_balance, five29_plan_balance, partner_exists, partner_ira_balance, partner_four01k_403b_balance, partner_taxable_investment_accounts)
combined_other_assets_total = financial_utils.calculate_other_assets(vehicles_value, jewelry_collectibles_value, business_ownership_value, cryptocurrency_holdings, other_assets, partner_exists=partner_exists, partner_other=partner_other_assets)

primary_residence_mortgage = st.number_input("Primary Residence Mortgage", value=scenario_data.get("primary_residence_mortgage", 300000.0))
secondary_residence_mortgage = st.number_input("Secondary Residence Mortgage", value=scenario_data.get("secondary_residence_mortgage", 0.0))
auto_loans = st.number_input("Auto Loans", value=scenario_data.get("auto_loans", 15000.0))
student_loans = st.number_input("Student Loans", value=scenario_data.get("student_loans", 25000.0))
credit_card_debt = st.number_input("Credit Card Debt", value=scenario_data.get("credit_card_debt", 5000.0))
personal_loans = st.number_input("Personal Loans", value=scenario_data.get("personal_loans", 0.0))
business_loans = st.number_input("Business Loans", value=scenario_data.get("business_loans", 0.0))
other_liabilities = st.number_input("Other Liabilities", value=scenario_data.get("other_liabilities", 0.0))
total_liabilities_local = financial_utils.calculate_total_liabilities(primary_residence_mortgage, secondary_residence_mortgage, auto_loans, student_loans, credit_card_debt, personal_loans, business_loans, other_liabilities)
combined_total_liabilities = total_liabilities_local + partner_liabilities

st.header("Family and Life Events")
if EVENTS_AVAILABLE:
    st.subheader("Children")
    children_rows = st.data_editor(pd.DataFrame([financial_utils.child_defaults] * 3), column_config=financial_utils.child_column_config, num_rows="dynamic")
    st.session_state["children_rows"] = [row for row in children_rows.to_dict(orient="records") if row.get("Name")]
else:
    st.warning("Family events module not available.")

st.subheader("Inheritance Events")
inherit_rows = st.data_editor(pd.DataFrame([financial_utils.inherit_defaults] * 3), column_config=financial_utils.inherit_column_config, num_rows="dynamic")
st.session_state["inherit_rows"] = [row for row in inherit_rows.to_dict(orient="records") if row.get("Amount", 0) > 0]

st.subheader("Financial Goals")
goal_df = st.data_editor(pd.DataFrame({
    "Goal": ["Retirement", "Home Purchase", "Vacation"],
    "Target $": [1000000.0, 500000.0, 10000.0],
    "Target Year Range": [f"{date.today().year + 30}", f"{date.today().year + 5}", f"{date.today().year + 1}"]
}), num_rows="dynamic")

goal_costs = financial_utils.parse_goal_costs(goal_df)

st.header("Simulation Parameters")
tax_rate = st.number_input("Effective Tax Rate (%)", value=scenario_data.get("tax_rate", 22.0))
inflation_rate = st.number_input("Inflation Rate (%)", value=scenario_data.get("inflation_rate", 3.0))
investment_return_rate = st.number_input("Investment Return Rate (%)", value=scenario_data.get("investment_return_rate", 7.0))
simulation_years = st.number_input("Simulation Years", min_value=10, max_value=100, value=scenario_data.get("simulation_years", 30))
mc_iterations = st.number_input("Monte Carlo Iterations (0 to disable)", min_value=0, max_value=1000, value=scenario_data.get("mc_iterations", 100))
college_inflation_pct = st.number_input("College Inflation Rate (%)", value=scenario_data.get("college_inflation_pct", 4.0))
base_public_in = st.number_input("Base Public In-State Tuition", value=scenario_data.get("base_public_in", 20000.0))
base_public_out = st.number_input("Base Public Out-of-State Tuition", value=scenario_data.get("base_public_out", 40000.0))
base_private = st.number_input("Base Private Tuition", value=scenario_data.get("base_private", 60000.0))

roth_conversion_annual = st.number_input("Annual Roth Conversion Amount", value=scenario_data.get("roth_conversion_annual", 0.0))
itemize_deductions = st.checkbox("Itemize Deductions?", value=scenario_data.get("itemize_deductions", True))

if st.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        results = simulation.run_simulation(
            age=age, partner_exists=partner_exists, partner_age=partner_age,
            total_income=total_income, total_expenses=total_expenses,
            combined_financial_assets=combined_financial_assets,
            primary_residence_value=primary_residence_value,
            secondary_residence_value=secondary_residence_value,
            combined_other_assets_total=combined_other_assets_total,
            total_liabilities_local=total_liabilities_local, partner_liabilities=partner_liabilities,
            tax_rate=tax_rate, inflation_rate=inflation_rate,
            investment_return_rate=investment_return_rate,
            simulation_years=simulation_years, mc_iterations=mc_iterations, goal_costs=goal_costs,
            college_inflation_pct=college_inflation_pct, base_public_in=base_public_in,
            base_public_out=base_public_out, base_private=base_private,
            ira_balance=ira_balance, four01k_403b_balance=four01k_403b_balance,
            partner_ira_balance=partner_ira_balance, partner_four01k_403b_balance=partner_four01k_403b_balance,
            monthly_surplus=monthly_surplus, combined_total_liabilities=combined_total_liabilities,
            roth_conversion_annual=roth_conversion_annual, itemize_deductions=itemize_deductions,
            five29_plan_balance=five29_plan_balance
        )
        if results:
            st.session_state['results'] = results
            st.session_state['sim_params'] = financial_utils.get_all_inputs_as_dict(locals())  # For reruns
else:
    results = st.session_state.get('results', None)

if results:
    financial_utils.display_summary_metrics(results, simulation_years)
    if show_health_dashboard:
        financial_utils.display_health_dashboard(combined_financial_assets, total_expenses, total_income, combined_total_liabilities, results)
    financial_utils.display_goal_achievement(results)
    visuals.show_trajectories(results)
    if mc_iterations > 0:
        visuals.show_monte_carlo(results)
    if show_scenario_comparison:
        st.subheader("Sensitivity Analysis")
        income_adj = st.slider("Income Adjustment (%)", -50, 50, 0)
        expenses_adj = st.slider("Expenses Adjustment (%)", -50, 50, 0)
        tax_adj = st.slider("Tax Rate Adjustment (%)", -10, 10, 0)
        inflation_adj = st.slider("Inflation Adjustment (%)", -2, 2, 0)
        return_adj = st.slider("Return Adjustment (%)", -5, 5, 0)
        if st.button("Run Adjusted Simulation"):
            adj_goal_costs = {}
            for _, row in goal_df.dropna().iterrows():
                try:
                    yr_range = str(row["Target Year Range"]).strip()
                    if pd.isna(yr_range) or yr_range == "":
                        yr_range = f"{date.today().year + 20}"
                    if "-" in yr_range:
                        start_yr, end_yr = map(int, yr_range.split("-"))
                    else:
                        end_yr = int(yr_range)
                        start_yr = end_yr
                    adj_goal_costs[row["Goal"]] = {'year': end_yr, 'amount': float(row["Target $"])}
                except (ValueError, TypeError):
                    continue
            adj_results = simulation.run_simulation(
                age=age, partner_exists=partner_exists, partner_age=partner_age,
                total_income=total_income * (1 + income_adj / 100),
                total_expenses=total_expenses * (1 + expenses_adj / 100),
                combined_financial_assets=combined_financial_assets,
                primary_residence_value=primary_residence_value,
                secondary_residence_value=secondary_residence_value,
                combined_other_assets_total=combined_other_assets_total,
                total_liabilities_local=total_liabilities_local, partner_liabilities=partner_liabilities,
                tax_rate=tax_rate + tax_adj, inflation_rate=inflation_rate + inflation_adj,
                investment_return_rate=investment_return_rate + return_adj,
                simulation_years=simulation_years, mc_iterations=mc_iterations, goal_costs=adj_goal_costs,
                college_inflation_pct=college_inflation_pct, base_public_in=base_public_in, base_public_out=base_public_out, base_private=base_private,
                ira_balance=ira_balance, four01k_403b_balance=four01k_403b_balance,
                partner_ira_balance=partner_ira_balance if partner_exists else 0.0,
                partner_four01k_403b_balance=partner_four01k_403b_balance if partner_exists else 0.0,
                monthly_surplus=monthly_surplus, combined_total_liabilities=combined_total_liabilities,
                roth_conversion_annual=roth_conversion_annual, itemize_deductions=itemize_deductions,
                five29_plan_balance=five29_plan_balance
            )
            # Derive final_balances for adj too
            if 'monte_carlo_results' in adj_results and 'mc_df' in adj_results['monte_carlo_results']:
                mc_df = adj_results['monte_carlo_results']['mc_df']
                adj_results['monte_carlo_results']['final_balances'] = mc_df.iloc[-1].values
            if adj_results:
                st.subheader("Comparison: Baseline vs Adjusted")
                comparison_data = {
                    "Metric": ["Final Savings", "Final Net Worth", "Years Solvent", "Emergency Fund (Months)", "Debt-to-Income", "Savings Rate", "Health Score"],
                    "Baseline": [
                        f"${results['final_savings']:,.2f}",
                        f"${results['final_net_worth']:,.2f}",
                        results['years_solvent'],
                        f"{results['emergency_fund_months']:.1f}",
                        f"{results['debt_to_income']:.2%}",
                        f"{results['savings_rate']:.2%}",
                        f"{results['health_score']:.1f}"
                    ],
                    "Adjusted": [
                        f"${adj_results['final_savings']:,.2f}",
                        f"${adj_results['final_net_worth']:,.2f}",
                        adj_results['years_solvent'],
                        f"{adj_results['emergency_fund_months']:.1f}",
                        f"{adj_results['debt_to_income']:.2%}",
                        f"{adj_results['savings_rate']:.2%}",
                        f"{adj_results['health_score']:.1f}"
                    ],
                    "Change": [
                        f"{(adj_results['final_savings'] - results['final_savings']):,.2f}",
                        f"{(adj_results['final_net_worth'] - results['final_net_worth']):,.2f}",
                        adj_results['years_solvent'] - results['years_solvent'],
                        f"{(adj_results['emergency_fund_months'] - results['emergency_fund_months']):,.1f}",
                        f"{(adj_results['debt_to_income'] - results['debt_to_income']):,.2%}",
                        f"{(adj_results['savings_rate'] - results['savings_rate']):,.2%}",
                        f"{(adj_results['health_score'] - results['health_score']):,.1f}"
                    ]
                }
                comparison_df = pd.DataFrame(comparison_data)
                def safe_float_convert(v):
                    try:
                        return float(v.replace('$', '').replace(',', '').replace('%', ''))
                    except:
                        return 0.0
                st.dataframe(comparison_df.style.apply(lambda x: ['color: green' if ('%' in str(v) or '$' in str(v)) and safe_float_convert(str(v)) > 0 else 'color: red' if ('%' in str(v) or '$' in str(v)) and safe_float_convert(str(v)) < 0 else '' for v in x], axis=1, subset=pd.IndexSlice[:, 'Change']))
                visuals.show_comparison(results, adj_results)  # Side-by-side trajectories

st.subheader("Detailed Annual Projections")
if results and 'df' in results:
    st.dataframe(results['df'].style.format("{:,.2f}"))
    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        results['df'].to_excel(writer, sheet_name='Projections', index=False)
    buffer.seek(0)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="Download Detailed Projections as Excel",
        data=buffer,
        file_name=f"detailed_projections_{timestamp}.xlsx",
        mime="application/vnd.ms-excel"
    )

if results:
    visuals.show_sankey(results, show_sankey)
    visuals.show_goals(results, show_goals)
    visuals.show_calendar(results, show_calendar)
    visuals.show_timeline(results, show_timeline, partner_name, DASH_AVAILABLE, age, partner_age, partner_exists)
    if OPENAI_AVAILABLE and IS_TRUSTED_USER:
        user_inputs = financial_utils.get_all_inputs_as_dict(locals())
        scenario_name = st.session_state.get('selected_scenario', "New Scenario")
        ai_consult.integrate_ai_section(results, user_inputs, scenario_name)
    if show_comparison:
        visuals.show_competitive_analysis()
st.markdown("---")
st.markdown("**Grok Family Retirement Plus** | Built with ❤️ by xAI | v2.4 | MIT License")