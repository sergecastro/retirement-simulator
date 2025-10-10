# File: GROK_app_family_plus.py
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
show_scenario_comparison = st.sidebar.checkbox("Scenario Comparison Tool", value=False, key="show_scenarios")
show_extended_projections = st.sidebar.checkbox("Extended Projections (50+ years)", value=False, key="show_extended")
show_family_reports = st.sidebar.checkbox("Family Reports Generator", value=True, key="show_reports")
st.sidebar.markdown("**Visual Analytics Lab**")
show_sankey = st.sidebar.checkbox("Cash-Flow Sankey", value=True, key="show_sankey")
show_goals = st.sidebar.checkbox("Goal-Funding Gauges", value=True, key="show_goals")
show_calendar = st.sidebar.checkbox("Monthly Heatmap", value=False, key="show_calendar")
show_comparison = st.sidebar.checkbox("Competitive Analysis", value=True, key="show_comparison")

# Scenario Management
scenario_file = "family_scenarios.json"
if IS_TRUSTED_USER:
    saved_scenarios = data_manager.load_scenarios(scenario_file)
    if not saved_scenarios:
        saved_scenarios = {
            "Empty Scenario": {
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
                "simulation_years": 30
            },
            "70+ Retirement Scenario": {
                "input_style": "Detailed Breakdown",
                "age_group": "70+",
                "age": 76,
                "partner_name": "Judith",
                "partner_exists": True,
                "partner_age": 74,
                "partner_ira_balance": 200000.0,
                "partner_four01k_403b_balance": 150000.0,
                "partner_taxable_investment_accounts": 100000.0,
                "partner_other_assets": 50000.0,
                "partner_liabilities": 0.0,
                "salary_wages": 0.0,
                "self_employment_income": 0.0,
                "rental_income": 2000.0,
                "investment_income": 500.0,
                "social_security_income": 3600.0,
                "pension_income": 6000.0,
                "other_income": 0.0,
                "total_income": 12100.0,
                "housing_expenses": 0.0,  # Assuming paid off
                "utilities_expenses": 300.0,
                "groceries_expenses": 500.0,
                "transportation_expenses": 200.0,
                "healthcare_expenses": 1000.0,
                "insurance_expenses": 500.0,
                "real_estate_insurance_expenses": 200.0,
                "property_tax_expenses": 400.0,
                "entertainment_expenses": 300.0,
                "restaurant_expenses": 200.0,
                "travel_expenses": 500.0,
                "education_expenses": 0.0,
                "childcare_expenses": 0.0,
                "clothing_expenses": 100.0,
                "charitable_donations": 500.0,
                "miscellaneous_expenses": 200.0,
                "other_expenses": 0.0,
                "total_expenses": 4900.0,
                "primary_residence_value": 500000.0,
                "secondary_residence_value": 0.0,
                "ira_balance": 300000.0,
                "four01k_403b_balance": 200000.0,
                "taxable_investment_accounts": 150000.0,
                "pension_fund_value": 100000.0,
                "life_insurance_cash_value": 50000.0,
                "high_yield_savings_account": 100000.0,
                "hsa_balance": 20000.0,
                "five29_plan_balance": 0.0,
                "vehicles_value": 20000.0,
                "jewelry_collectibles_value": 10000.0,
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
                "tax_rate": 15.0,
                "inflation_rate": 2.5,
                "investment_return_rate": 5.0,
                "simulation_years": 20
            }
        }
        data_manager.save_scenarios(saved_scenarios, scenario_file)  # Save defaults if empty
else:
    saved_scenarios = {}

# Scenario selection
st.header("Scenario Management")
scenario_options = list(saved_scenarios.keys()) + ["New Scenario"]
selected_scenario = st.selectbox("Select Scenario", scenario_options)
st.session_state['selected_scenario'] = selected_scenario

if selected_scenario != "New Scenario":
    scenario_data = saved_scenarios[selected_scenario]
    # Load data into variables
    input_style = scenario_data["input_style"]
    age_group = scenario_data["age_group"]
    age = scenario_data["age"]
    partner_name = scenario_data["partner_name"]
    partner_exists = scenario_data["partner_exists"]
    partner_age = scenario_data["partner_age"]
    partner_ira_balance = scenario_data["partner_ira_balance"]
    partner_four01k_403b_balance = scenario_data["partner_four01k_403b_balance"]
    partner_taxable_investment_accounts = scenario_data["partner_taxable_investment_accounts"]
    partner_other_assets = scenario_data["partner_other_assets"]
    partner_liabilities = scenario_data["partner_liabilities"]
    salary_wages = scenario_data["salary_wages"]
    self_employment_income = scenario_data["self_employment_income"]
    rental_income = scenario_data["rental_income"]
    investment_income = scenario_data["investment_income"]
    social_security_income = scenario_data["social_security_income"]
    pension_income = scenario_data["pension_income"]
    other_income = scenario_data["other_income"]
    total_income = scenario_data["total_income"]
    housing_expenses = scenario_data["housing_expenses"]
    utilities_expenses = scenario_data["utilities_expenses"]
    groceries_expenses = scenario_data["groceries_expenses"]
    transportation_expenses = scenario_data["transportation_expenses"]
    healthcare_expenses = scenario_data["healthcare_expenses"]
    insurance_expenses = scenario_data["insurance_expenses"]
    real_estate_insurance_expenses = scenario_data["real_estate_insurance_expenses"]
    property_tax_expenses = scenario_data["property_tax_expenses"]
    entertainment_expenses = scenario_data["entertainment_expenses"]
    restaurant_expenses = scenario_data["restaurant_expenses"]
    travel_expenses = scenario_data["travel_expenses"]
    education_expenses = scenario_data["education_expenses"]
    childcare_expenses = scenario_data["childcare_expenses"]
    clothing_expenses = scenario_data["clothing_expenses"]
    charitable_donations = scenario_data["charitable_donations"]
    miscellaneous_expenses = scenario_data["miscellaneous_expenses"]
    other_expenses = scenario_data["other_expenses"]
    total_expenses = scenario_data["total_expenses"]
    primary_residence_value = scenario_data["primary_residence_value"]
    secondary_residence_value = scenario_data["secondary_residence_value"]
    ira_balance = scenario_data["ira_balance"]
    four01k_403b_balance = scenario_data["four01k_403b_balance"]
    taxable_investment_accounts = scenario_data["taxable_investment_accounts"]
    pension_fund_value = scenario_data["pension_fund_value"]
    life_insurance_cash_value = scenario_data["life_insurance_cash_value"]
    high_yield_savings_account = scenario_data["high_yield_savings_account"]
    hsa_balance = scenario_data["hsa_balance"]
    five29_plan_balance = scenario_data["five29_plan_balance"]
    vehicles_value = scenario_data["vehicles_value"]
    jewelry_collectibles_value = scenario_data["jewelry_collectibles_value"]
    business_ownership_value = scenario_data["business_ownership_value"]
    cryptocurrency_holdings = scenario_data["cryptocurrency_holdings"]
    other_assets = scenario_data["other_assets"]
    primary_residence_mortgage = scenario_data["primary_residence_mortgage"]
    secondary_residence_mortgage = scenario_data["secondary_residence_mortgage"]
    auto_loans = scenario_data["auto_loans"]
    student_loans = scenario_data["student_loans"]
    credit_card_debt = scenario_data["credit_card_debt"]
    personal_loans = scenario_data["personal_loans"]
    business_loans = scenario_data["business_loans"]
    other_liabilities = scenario_data["other_liabilities"]
    tax_rate = scenario_data["tax_rate"]
    inflation_rate = scenario_data["inflation_rate"]
    investment_return_rate = scenario_data["investment_return_rate"]
    simulation_years = scenario_data["simulation_years"]
else:
    # Defaults for new scenario
    input_style = "Detailed Breakdown"
    age_group = "25-55"
    age = 35
    partner_name = ""
    partner_exists = False
    partner_age = 35
    partner_ira_balance = 0.0
    partner_four01k_403b_balance = 0.0
    partner_taxable_investment_accounts = 0.0
    partner_other_assets = 0.0
    partner_liabilities = 0.0
    salary_wages = 5000.0
    self_employment_income = 0.0
    rental_income = 0.0
    investment_income = 0.0
    social_security_income = 0.0
    pension_income = 0.0
    other_income = 0.0
    total_income = 5000.0
    housing_expenses = 1500.0
    utilities_expenses = 300.0
    groceries_expenses = 600.0
    transportation_expenses = 400.0
    healthcare_expenses = 200.0
    insurance_expenses = 300.0
    real_estate_insurance_expenses = 100.0
    property_tax_expenses = 200.0
    entertainment_expenses = 200.0
    restaurant_expenses = 300.0
    travel_expenses = 200.0
    education_expenses = 0.0
    childcare_expenses = 0.0
    clothing_expenses = 100.0
    charitable_donations = 0.0
    miscellaneous_expenses = 100.0
    other_expenses = 0.0
    total_expenses = 4400.0
    primary_residence_value = 400000.0
    secondary_residence_value = 0.0
    ira_balance = 50000.0
    four01k_403b_balance = 75000.0
    taxable_investment_accounts = 25000.0
    pension_fund_value = 0.0
    life_insurance_cash_value = 0.0
    high_yield_savings_account = 20000.0
    hsa_balance = 5000.0
    five29_plan_balance = 10000.0
    vehicles_value = 25000.0
    jewelry_collectibles_value = 5000.0
    business_ownership_value = 0.0
    cryptocurrency_holdings = 0.0
    other_assets = 0.0
    primary_residence_mortgage = 300000.0
    secondary_residence_mortgage = 0.0
    auto_loans = 15000.0
    student_loans = 25000.0
    credit_card_debt = 5000.0
    personal_loans = 0.0
    business_loans = 0.0
    other_liabilities = 0.0
    tax_rate = 22.0
    inflation_rate = 3.0
    investment_return_rate = 7.0
    simulation_years = 30

# Input sections (unchanged)
st.header("Personal Information")
age_group = st.selectbox("Age Group", options=["Under 25", "25-55", "55-70", "70+"], index=1 if age_group == "25-55" else 0)
age = st.number_input("Your Age", min_value=18, max_value=100, value=age)
partner_exists = st.checkbox("Has Partner?", value=partner_exists)
if partner_exists:
    partner_name = st.text_input("Partner's Name", value=partner_name)
    partner_age = st.number_input("Partner's Age", min_value=18, max_value=100, value=partner_age)

st.header("Income (Monthly)")
if input_style == "Detailed Breakdown":
    salary_wages = st.number_input("Salary/Wages", value=salary_wages)
    self_employment_income = st.number_input("Self-Employment Income", value=self_employment_income)
    rental_income = st.number_input("Rental Income", value=rental_income)
    investment_income = st.number_input("Investment Income", value=investment_income)
    social_security_income = st.number_input("Social Security Income", value=social_security_income)
    pension_income = st.number_input("Pension Income", value=pension_income)
    other_income = st.number_input("Other Income", value=other_income)
    total_income = financial_utils.calculate_total_income(salary_wages, self_employment_income, rental_income, investment_income, social_security_income, pension_income, other_income)
else:
    total_income = st.number_input("Total Monthly Income", value=total_income)

st.header("Expenses (Monthly)")
if input_style == "Detailed Breakdown":
    housing_expenses = st.number_input("Housing (Mortgage/Rent)", value=housing_expenses)
    utilities_expenses = st.number_input("Utilities", value=utilities_expenses)
    groceries_expenses = st.number_input("Groceries", value=groceries_expenses)
    transportation_expenses = st.number_input("Transportation", value=transportation_expenses)
    healthcare_expenses = st.number_input("Healthcare", value=healthcare_expenses)
    insurance_expenses = st.number_input("Insurance (Life, Auto, Health)", value=insurance_expenses)
    real_estate_insurance_expenses = st.number_input("Real Estate Insurance", value=real_estate_insurance_expenses)
    property_tax_expenses = st.number_input("Property Taxes", value=property_tax_expenses)
    entertainment_expenses = st.number_input("Entertainment", value=entertainment_expenses)
    restaurant_expenses = st.number_input("Restaurants", value=restaurant_expenses)
    travel_expenses = st.number_input("Travel", value=travel_expenses)
    education_expenses = st.number_input("Education", value=education_expenses)
    childcare_expenses = st.number_input("Childcare", value=childcare_expenses)
    clothing_expenses = st.number_input("Clothing", value=clothing_expenses)
    charitable_donations = st.number_input("Charitable Donations", value=charitable_donations)
    miscellaneous_expenses = st.number_input("Miscellaneous", value=miscellaneous_expenses)
    other_expenses = st.number_input("Other Expenses", value=other_expenses)
    total_expenses = financial_utils.calculate_total_expenses(housing_expenses, utilities_expenses, groceries_expenses, transportation_expenses, healthcare_expenses, insurance_expenses, real_estate_insurance_expenses, property_tax_expenses, entertainment_expenses, restaurant_expenses, travel_expenses, education_expenses, childcare_expenses, clothing_expenses, charitable_donations, miscellaneous_expenses, other_expenses)
else:
    total_expenses = st.number_input("Total Monthly Expenses", value=total_expenses)

monthly_surplus = total_income - total_expenses
st.metric("Monthly Surplus/Deficit", f"${monthly_surplus:,.2f}")

st.header("Assets")
primary_residence_value = st.number_input("Primary Residence Value", value=primary_residence_value)
secondary_residence_value = st.number_input("Secondary Residence Value", value=secondary_residence_value)
ira_balance = st.number_input("IRA Balance", value=ira_balance)
four01k_403b_balance = st.number_input("401k/403b Balance", value=four01k_403b_balance)
taxable_investment_accounts = st.number_input("Taxable Investment Accounts", value=taxable_investment_accounts)
pension_fund_value = st.number_input("Pension Fund Value", value=pension_fund_value)
life_insurance_cash_value = st.number_input("Life Insurance Cash Value", value=life_insurance_cash_value)
high_yield_savings_account = st.number_input("High-Yield Savings Account", value=high_yield_savings_account)
hsa_balance = st.number_input("HSA Balance", value=hsa_balance)
five29_plan_balance = st.number_input("529 Plan Balance", value=five29_plan_balance)
vehicles_value = st.number_input("Vehicles Value", value=vehicles_value)
jewelry_collectibles_value = st.number_input("Jewelry/Collectibles Value", value=jewelry_collectibles_value)
business_ownership_value = st.number_input("Business Ownership Value", value=business_ownership_value)
cryptocurrency_holdings = st.number_input("Cryptocurrency Holdings", value=cryptocurrency_holdings)
other_assets = st.number_input("Other Assets", value=other_assets)

combined_financial_assets = financial_utils.calculate_liquid_assets(ira_balance, four01k_403b_balance, taxable_investment_accounts, pension_fund_value, life_insurance_cash_value, high_yield_savings_account, hsa_balance, five29_plan_balance, partner_exists, partner_ira_balance, partner_four01k_403b_balance, partner_taxable_investment_accounts)
combined_other_assets_total = financial_utils.calculate_other_assets(vehicles_value, jewelry_collectibles_value, business_ownership_value, cryptocurrency_holdings, other_assets, partner_exists=partner_exists, partner_other=partner_other_assets)

if partner_exists:
    st.subheader("Partner's Assets")
    partner_ira_balance = st.number_input("Partner's IRA Balance", value=partner_ira_balance)
    partner_four01k_403b_balance = st.number_input("Partner's 401k/403b Balance", value=partner_four01k_403b_balance)
    partner_taxable_investment_accounts = st.number_input("Partner's Taxable Investment Accounts", value=partner_taxable_investment_accounts)
    partner_other_assets = st.number_input("Partner's Other Assets", value=partner_other_assets)

st.header("Liabilities")
primary_residence_mortgage = st.number_input("Primary Residence Mortgage", value=primary_residence_mortgage)
secondary_residence_mortgage = st.number_input("Secondary Residence Mortgage", value=secondary_residence_mortgage)
auto_loans = st.number_input("Auto Loans", value=auto_loans)
student_loans = st.number_input("Student Loans", value=student_loans)
credit_card_debt = st.number_input("Credit Card Debt", value=credit_card_debt)
personal_loans = st.number_input("Personal Loans", value=personal_loans)
business_loans = st.number_input("Business Loans", value=business_loans)
other_liabilities = st.number_input("Other Liabilities", value=other_liabilities)
total_liabilities_local = financial_utils.calculate_total_liabilities(primary_residence_mortgage, secondary_residence_mortgage, auto_loans, student_loans, credit_card_debt, personal_loans, business_loans, other_liabilities)

if partner_exists:
    partner_liabilities = st.number_input("Partner's Liabilities", value=partner_liabilities)
else:
    partner_liabilities = 0.0

combined_total_liabilities = total_liabilities_local + partner_liabilities

st.header("Simulation Parameters")
tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=50.0, value=tax_rate, step=0.5)
inflation_rate = st.number_input("Inflation Rate (%)", min_value=0.0, max_value=10.0, value=inflation_rate, step=0.1)
investment_return_rate = st.number_input("Investment Return Rate (%)", min_value=0.0, max_value=15.0, value=investment_return_rate, step=0.1)
simulation_years = st.number_input("Simulation Years", min_value=1, max_value=100, value=simulation_years)
mc_iterations = st.number_input("Monte Carlo Iterations (0 to disable)", min_value=0, max_value=1000, value=0, step=10)

st.header("Financial Goals")
goal_columns = {
    "Goal": st.column_config.TextColumn("Goal", help="e.g., Retirement Fund, Home Purchase"),
    "Target $": st.column_config.NumberColumn("Target Amount ($)", min_value=0.0, step=1000.0),
    "Target Year Range": st.column_config.TextColumn("Target Year/Range", help="e.g., 2040 or 2040-2045")
}
goal_df = st.data_editor(pd.DataFrame(columns=["Goal", "Target $", "Target Year Range"]), num_rows="dynamic", column_config=goal_columns, use_container_width=True)
goal_costs = financial_utils.parse_goal_costs(goal_df)

# NEW: College Cost Assumptions (Fix for NameError)
st.header("College Cost Assumptions")
college_inflation_pct = st.number_input("College Inflation Rate (%)", min_value=0.0, max_value=10.0, value=4.0, step=0.1)
base_public_in = st.number_input("Base Public In-State Annual Cost ($)", min_value=0.0, value=20000.0, step=1000.0)
base_public_out = st.number_input("Base Public Out-of-State Annual Cost ($)", min_value=0.0, value=40000.0, step=1000.0)
base_private = st.number_input("Base Private Annual Cost ($)", min_value=0.0, value=60000.0, step=1000.0)

# NEW: Family Events (Restored kids/college/inheritance inputs)
st.header("Family Events")
st.subheader("Children and Education Plans")
num_children = st.number_input("Number of Children", min_value=0, max_value=10, value=0)
children_rows = []
if num_children > 0:
    from financial_utils import child_column_config, child_defaults
    children_df = pd.DataFrame([child_defaults] * num_children)
    edited_df = st.data_editor(
        children_df,
        num_rows="fixed",
        column_config=child_column_config,
        use_container_width=True,
        hide_index=False,
        key="children_editor"
    )
    children_rows = edited_df.to_dict('records')
st.session_state["children_rows"] = children_rows

st.subheader("Expected Inheritances")
num_inherit = st.number_input("Number of Expected Inheritances", min_value=0, max_value=5, value=0)
inherit_rows = []
if num_inherit > 0:
    from financial_utils import inherit_column_config, inherit_defaults
    inherit_df = pd.DataFrame([inherit_defaults] * num_inherit)
    edited_inherit_df = st.data_editor(
        inherit_df,
        num_rows="fixed",
        column_config=inherit_column_config,
        use_container_width=True,
        hide_index=False,
        key="inherit_editor"
    )
    inherit_rows = edited_inherit_df.to_dict('records')
st.session_state["inherit_rows"] = inherit_rows

# Simulation button (unchanged)
if st.button("📈 Run Simulation"):
    with st.spinner("Running simulation..."):
        results = simulation.run_simulation(
            age=age, partner_exists=partner_exists, partner_age=partner_age,
            total_income=total_income, total_expenses=total_expenses,
            combined_financial_assets=combined_financial_assets,
            primary_residence_value=primary_residence_value, secondary_residence_value=secondary_residence_value,
            combined_other_assets_total=combined_other_assets_total,
            total_liabilities_local=total_liabilities_local, partner_liabilities=partner_liabilities,
            tax_rate=tax_rate, inflation_rate=inflation_rate, investment_return_rate=investment_return_rate,
            simulation_years=simulation_years, mc_iterations=mc_iterations, goal_costs=goal_costs,
            college_inflation_pct=college_inflation_pct, base_public_in=base_public_in, base_public_out=base_public_out, base_private=base_private,
            ira_balance=ira_balance, four01k_403b_balance=four01k_403b_balance,
            partner_ira_balance=partner_ira_balance if partner_exists else 0.0,
            partner_four01k_403b_balance=partner_four01k_403b_balance if partner_exists else 0.0,
            monthly_surplus=monthly_surplus, combined_total_liabilities=combined_total_liabilities
        )
        if results:
            financial_utils.display_summary_metrics(results, simulation_years)
            if show_health_dashboard:
                financial_utils.display_health_dashboard(combined_financial_assets, total_expenses, total_income * 12, combined_total_liabilities, results)
            if 'monte_carlo_results' in results:
                visuals.show_monte_carlo(results)
            visuals.show_trajectories(results)
            if show_goals:
                financial_utils.display_goal_achievement(results)

# Scenario saving (unchanged)
if IS_TRUSTED_USER and st.button("Save Scenario"):
    scenario_name = st.text_input("Scenario Name", value=selected_scenario if selected_scenario != "New Scenario" else "")
    if scenario_name:
        scenario_data = {
            "input_style": input_style,
            "age_group": age_group,
            "age": age,
            "partner_name": partner_name,
            "partner_exists": partner_exists,
            "partner_age": partner_age,
            "partner_ira_balance": partner_ira_balance,
            "partner_four01k_403b_balance": partner_four01k_403b_balance,
            "partner_taxable_investment_accounts": partner_taxable_investment_accounts,
            "partner_other_assets": partner_other_assets,
            "partner_liabilities": partner_liabilities,
            "salary_wages": salary_wages,
            "self_employment_income": self_employment_income,
            "rental_income": rental_income,
            "investment_income": investment_income,
            "social_security_income": social_security_income,
            "pension_income": pension_income,
            "other_income": other_income,
            "total_income": total_income,
            "housing_expenses": housing_expenses,
            "utilities_expenses": utilities_expenses,
            "groceries_expenses": groceries_expenses,
            "transportation_expenses": transportation_expenses,
            "healthcare_expenses": healthcare_expenses,
            "insurance_expenses": insurance_expenses,
            "real_estate_insurance_expenses": real_estate_insurance_expenses,
            "property_tax_expenses": property_tax_expenses,
            "entertainment_expenses": entertainment_expenses,
            "restaurant_expenses": restaurant_expenses,
            "travel_expenses": travel_expenses,
            "education_expenses": education_expenses,
            "childcare_expenses": childcare_expenses,
            "clothing_expenses": clothing_expenses,
            "charitable_donations": charitable_donations,
            "miscellaneous_expenses": miscellaneous_expenses,
            "other_expenses": other_expenses,
            "total_expenses": total_expenses,
            "primary_residence_value": primary_residence_value,
            "secondary_residence_value": secondary_residence_value,
            "ira_balance": ira_balance,
            "four01k_403b_balance": four01k_403b_balance,
            "taxable_investment_accounts": taxable_investment_accounts,
            "pension_fund_value": pension_fund_value,
            "life_insurance_cash_value": life_insurance_cash_value,
            "high_yield_savings_account": high_yield_savings_account,
            "hsa_balance": hsa_balance,
            "five29_plan_balance": five29_plan_balance,
            "vehicles_value": vehicles_value,
            "jewelry_collectibles_value": jewelry_collectibles_value,
            "business_ownership_value": business_ownership_value,
            "cryptocurrency_holdings": cryptocurrency_holdings,
            "other_assets": other_assets,
            "primary_residence_mortgage": primary_residence_mortgage,
            "secondary_residence_mortgage": secondary_residence_mortgage,
            "auto_loans": auto_loans,
            "student_loans": student_loans,
            "credit_card_debt": credit_card_debt,
            "personal_loans": personal_loans,
            "business_loans": business_loans,
            "other_liabilities": other_liabilities,
            "tax_rate": tax_rate,
            "inflation_rate": inflation_rate,
            "investment_return_rate": investment_return_rate,
            "simulation_years": simulation_years
        }
        saved_scenarios[scenario_name] = scenario_data
        data_manager.save_scenarios(saved_scenarios, scenario_file)
        st.success(f"Scenario '{scenario_name}' saved.")

# Adjusted simulation (unchanged)
st.header("Scenario Adjustment & Comparison")
col1, col2 = st.columns(2)
with col1:
    income_adj = st.slider("Adjust Income (%):", -50.0, 50.0, 0.0, step=1.0, key="income_adj")
    expenses_adj = st.slider("Adjust Expenses (%):", -50.0, 50.0, 0.0, step=1.0, key="expenses_adj")
with col2:
    tax_adj = st.slider("Adjust Tax Rate (%):", -10.0, 10.0, 0.0, step=0.5, key="tax_adj")
    return_adj = st.slider("Adjust Investment Return (%):", -5.0, 5.0, 0.0, step=0.1, key="return_adj")
    inflation_adj = st.slider("Adjust Inflation Rate (%):", -5.0, 5.0, 0.0, step=0.1, key="inflation_adj")

def safe_float_convert(s):
    try:
        return float(s.replace('%', '').replace('$', '').replace(',', '').replace('+', ''))
    except ValueError:
        return 0.0

if st.button("Run Adjusted Simulation & Compare"):
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
        monthly_surplus=monthly_surplus, combined_total_liabilities=combined_total_liabilities
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
        st.dataframe(comparison_df.style.apply(lambda x: ['color: green' if ('%' in str(v) or '$' in str(v)) and safe_float_convert(str(v)) > 0 else 'color: red' if ('%' in str(v) or '$' in str(v)) and safe_float_convert(str(v)) < 0 else '' for v in x], axis=1, subset=pd.IndexSlice[:, 'Change']))
        visuals.show_comparison(results, adj_results)  # Side-by-side trajectories

st.subheader("Detailed Annual Projections")
if 'df' in results:
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
visuals.show_sankey(results, show_sankey)
visuals.show_goals(results, show_goals)
visuals.show_calendar(results, show_calendar)
visuals.show_timeline(results, show_timeline, partner_name, DASH_AVAILABLE, age, partner_age, partner_exists)
if OPENAI_AVAILABLE and IS_TRUSTED_USER:
    user_inputs = financial_utils.get_all_inputs_as_dict(locals())
    scenario_name = st.session_state.get('selected_scenario', "New Scenario")
    ai_consult.integrate_ai_section(results, user_inputs, scenario_name)
st.markdown("---")
st.markdown("**Grok Family Retirement Plus** | Built with ❤️ by xAI | v2.1 | MIT License")