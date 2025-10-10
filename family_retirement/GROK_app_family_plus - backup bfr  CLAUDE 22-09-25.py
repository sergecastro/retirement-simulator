# File: GROK_app_family_plus.py - Part 1 (Lines 1-450 approx.)
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
                "simulation_years": 30,
                "mc_iterations": 0,
                "college_inflation_pct": 4.0,
                "base_public_in": 20000.0,
                "base_public_out": 40000.0,
                "base_private": 60000.0,
                "roth_conversion_annual": 0.0,
                "itemize_deductions": True
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
                "partner_taxable_investment_accounts": 50000.0,
                "partner_other_assets": 10000.0,
                "partner_liabilities": 5000.0,
                "salary_wages": 0.0,
                "self_employment_income": 0.0,
                "rental_income": 2000.0,
                "investment_income": 1000.0,
                "social_security_income": 3000.0,
                "pension_income": 2000.0,
                "other_income": 500.0,
                "total_income": 8500.0,
                "housing_expenses": 1000.0,
                "utilities_expenses": 200.0,
                "groceries_expenses": 400.0,
                "transportation_expenses": 200.0,
                "healthcare_expenses": 500.0,
                "insurance_expenses": 300.0,
                "real_estate_insurance_expenses": 100.0,
                "property_tax_expenses": 300.0,
                "entertainment_expenses": 200.0,
                "restaurant_expenses": 200.0,
                "travel_expenses": 300.0,
                "education_expenses": 0.0,
                "childcare_expenses": 0.0,
                "clothing_expenses": 100.0,
                "charitable_donations": 500.0,
                "miscellaneous_expenses": 100.0,
                "other_expenses": 0.0,
                "total_expenses": 4400.0,
                "primary_residence_value": 500000.0,
                "secondary_residence_value": 200000.0,
                "ira_balance": 300000.0,
                "four01k_403b_balance": 400000.0,
                "taxable_investment_accounts": 100000.0,
                "pension_fund_value": 50000.0,
                "life_insurance_cash_value": 20000.0,
                "high_yield_savings_account": 50000.0,
                "hsa_balance": 10000.0,
                "five29_plan_balance": 0.0,
                "vehicles_value": 15000.0,
                "jewelry_collectibles_value": 10000.0,
                "business_ownership_value": 0.0,
                "cryptocurrency_holdings": 5000.0,
                "other_assets": 0.0,
                "primary_residence_mortgage": 0.0,
                "secondary_residence_mortgage": 0.0,
                "auto_loans": 0.0,
                "student_loans": 0.0,
                "credit_card_debt": 0.0,
                "personal_loans": 0.0,
                "business_loans": 0.0,
                "other_liabilities": 0.0,
                "tax_rate": 22.0,
                "inflation_rate": 2.5,
                "investment_return_rate": 5.0,
                "simulation_years": 20,
                "mc_iterations": 0,
                "college_inflation_pct": 4.0,
                "base_public_in": 20000.0,
                "base_public_out": 40000.0,
                "base_private": 60000.0,
                "roth_conversion_annual": 0.0,
                "itemize_deductions": True
            }
        }
        data_manager.save_scenarios(saved_scenarios, scenario_file)
else:
    saved_scenarios = {}

# Scenario Selection
st.sidebar.header("Scenario Management")
scenario_names = list(saved_scenarios.keys()) + ["New Scenario"]
selected_scenario = st.sidebar.selectbox("Select Scenario", scenario_names, index=len(scenario_names)-1)
if selected_scenario != "New Scenario":
    scenario_data = saved_scenarios[selected_scenario]
    st.session_state.update(scenario_data)
scenario_name = st.sidebar.text_input("Scenario Name", value=selected_scenario if selected_scenario != "New Scenario" else "New Scenario")
if st.sidebar.button("Save Scenario"):
    current_inputs = financial_utils.get_all_inputs_as_dict(locals())
    saved_scenarios[scenario_name] = current_inputs
    data_manager.save_scenarios(saved_scenarios, scenario_file)
    st.sidebar.success("Scenario saved!")

# Main Input Sections
st.header("User Information")
age_group = st.selectbox("Age Group", ["Under 25", "25-55", "55-70", "70+"], key="age_group")
input_style = st.radio("Input Style", ["Quick Totals", "Detailed Breakdown"], key="input_style")
age = st.number_input("Your Age", min_value=18, max_value=120, value=35, key="age")
partner_exists = st.checkbox("Have a Partner?", key="partner_exists")
partner_name = st.text_input("Partner's Name", value="", key="partner_name") if partner_exists else ""
partner_age = st.number_input("Partner's Age", min_value=18, max_value=120, value=35, key="partner_age") if partner_exists else None

st.header("Income")
if input_style == "Detailed Breakdown":
    salary_wages = st.number_input("Salary/Wages ($/month)", value=5000.0, key="salary_wages")
    self_employment_income = st.number_input("Self-Employment Income ($/month)", value=0.0, key="self_employment_income")
    rental_income = st.number_input("Rental Income ($/month)", value=0.0, key="rental_income")
    investment_income = st.number_input("Investment Income ($/month)", value=0.0, key="investment_income")
    social_security_income = st.number_input("Social Security Income ($/month)", value=0.0, key="social_security_income")
    pension_income = st.number_input("Pension Income ($/month)", value=0.0, key="pension_income")
    other_income = st.number_input("Other Income ($/month)", value=0.0, key="other_income")
    total_income = financial_utils.calculate_total_income(salary_wages, self_employment_income, rental_income, investment_income, social_security_income, pension_income, other_income)
else:
    total_income = st.number_input("Total Monthly Income ($)", value=5000.0, key="total_income")

st.header("Expenses")
if input_style == "Detailed Breakdown":
    housing_expenses = st.number_input("Housing ($/month)", value=1500.0, key="housing_expenses")
    utilities_expenses = st.number_input("Utilities ($/month)", value=300.0, key="utilities_expenses")
    groceries_expenses = st.number_input("Groceries ($/month)", value=600.0, key="groceries_expenses")
    transportation_expenses = st.number_input("Transportation ($/month)", value=400.0, key="transportation_expenses")
    healthcare_expenses = st.number_input("Healthcare ($/month)", value=200.0, key="healthcare_expenses")
    insurance_expenses = st.number_input("Insurance ($/month)", value=300.0, key="insurance_expenses")
    real_estate_insurance_expenses = st.number_input("Real Estate Insurance ($/month)", value=100.0, key="real_estate_insurance_expenses")
    property_tax_expenses = st.number_input("Property Taxes ($/month)", value=200.0, key="property_tax_expenses")
    entertainment_expenses = st.number_input("Entertainment ($/month)", value=200.0, key="entertainment_expenses")
    restaurant_expenses = st.number_input("Restaurants ($/month)", value=300.0, key="restaurant_expenses")
    travel_expenses = st.number_input("Travel ($/month)", value=200.0, key="travel_expenses")
    education_expenses = st.number_input("Education ($/month)", value=0.0, key="education_expenses")
    childcare_expenses = st.number_input("Childcare ($/month)", value=0.0, key="childcare_expenses")
    clothing_expenses = st.number_input("Clothing ($/month)", value=100.0, key="clothing_expenses")
    charitable_donations = st.number_input("Charitable Donations ($/month)", value=0.0, key="charitable_donations")
    miscellaneous_expenses = st.number_input("Miscellaneous ($/month)", value=100.0, key="miscellaneous_expenses")
    other_expenses = st.number_input("Other Expenses ($/month)", value=0.0, key="other_expenses")
    total_expenses = financial_utils.calculate_total_expenses(housing_expenses, utilities_expenses, groceries_expenses, transportation_expenses, healthcare_expenses, insurance_expenses, real_estate_insurance_expenses, property_tax_expenses, entertainment_expenses, restaurant_expenses, travel_expenses, education_expenses, childcare_expenses, clothing_expenses, charitable_donations, miscellaneous_expenses, other_expenses)
else:
    total_expenses = st.number_input("Total Monthly Expenses ($)", value=4400.0, key="total_expenses")

monthly_surplus = total_income - total_expenses
st.metric("Monthly Surplus/Deficit", f"${monthly_surplus:,.2f}")

st.header("Assets")
primary_residence_value = st.number_input("Primary Residence Value ($)", value=400000.0, key="primary_residence_value")
secondary_residence_value = st.number_input("Secondary Residence Value ($)", value=0.0, key="secondary_residence_value")
ira_balance = st.number_input("IRA Balance ($)", value=50000.0, key="ira_balance")
four01k_403b_balance = st.number_input("401k/403b Balance ($)", value=75000.0, key="four01k_403b_balance")
taxable_investment_accounts = st.number_input("Taxable Investment Accounts ($)", value=25000.0, key="taxable_investment_accounts")
pension_fund_value = st.number_input("Pension Fund Value ($)", value=0.0, key="pension_fund_value")
life_insurance_cash_value = st.number_input("Life Insurance Cash Value ($)", value=0.0, key="life_insurance_cash_value")
high_yield_savings_account = st.number_input("High-Yield Savings Account ($)", value=20000.0, key="high_yield_savings_account")
hsa_balance = st.number_input("HSA Balance ($)", value=5000.0, key="hsa_balance")
five29_plan_balance = st.number_input("529 Plan Balance ($)", value=10000.0, key="five29_plan_balance")
vehicles_value = st.number_input("Vehicles Value ($)", value=25000.0, key="vehicles_value")
jewelry_collectibles_value = st.number_input("Jewelry/Collectibles Value ($)", value=5000.0, key="jewelry_collectibles_value")
business_ownership_value = st.number_input("Business Ownership Value ($)", value=0.0, key="business_ownership_value")
cryptocurrency_holdings = st.number_input("Cryptocurrency Holdings ($)", value=0.0, key="cryptocurrency_holdings")
other_assets = st.number_input("Other Assets ($)", value=0.0, key="other_assets")

if partner_exists:
    st.subheader("Partner's Assets")
    partner_ira_balance = st.number_input("Partner's IRA Balance ($)", value=0.0, key="partner_ira_balance")
    partner_four01k_403b_balance = st.number_input("Partner's 401k/403b Balance ($)", value=0.0, key="partner_four01k_403b_balance")
    partner_taxable_investment_accounts = st.number_input("Partner's Taxable Investment Accounts ($)", value=0.0, key="partner_taxable_investment_accounts")
    partner_other_assets = st.number_input("Partner's Other Assets ($)", value=0.0, key="partner_other_assets")
else:
    partner_ira_balance = partner_four01k_403b_balance = partner_taxable_investment_accounts = partner_other_assets = 0.0

combined_financial_assets = financial_utils.calculate_liquid_assets(high_yield_savings_account, ira_balance, four01k_403b_balance, taxable_investment_accounts, pension_fund_value, life_insurance_cash_value, hsa_balance, five29_plan_balance, cryptocurrency_holdings, partner_exists, partner_ira_balance, partner_four01k_403b_balance, partner_taxable_investment_accounts)
combined_other_assets_total = financial_utils.calculate_other_assets(vehicles_value, jewelry_collectibles_value, business_ownership_value, other_assets, partner_exists=partner_exists, partner_other=partner_other_assets)

st.header("Liabilities")
primary_residence_mortgage = st.number_input("Primary Residence Mortgage ($)", value=300000.0, key="primary_residence_mortgage")
secondary_residence_mortgage = st.number_input("Secondary Residence Mortgage ($)", value=0.0, key="secondary_residence_mortgage")
auto_loans = st.number_input("Auto Loans ($)", value=15000.0, key="auto_loans")
student_loans = st.number_input("Student Loans ($)", value=25000.0, key="student_loans")
credit_card_debt = st.number_input("Credit Card Debt ($)", value=5000.0, key="credit_card_debt")
personal_loans = st.number_input("Personal Loans ($)", value=0.0, key="personal_loans")
business_loans = st.number_input("Business Loans ($)", value=0.0, key="business_loans")
other_liabilities = st.number_input("Other Liabilities ($)", value=0.0, key="other_liabilities")

if partner_exists:
    partner_liabilities = st.number_input("Partner's Liabilities ($)", value=0.0, key="partner_liabilities")
else:
    partner_liabilities = 0.0

total_liabilities_local = financial_utils.calculate_total_liabilities(primary_residence_mortgage, secondary_residence_mortgage, auto_loans, student_loans, credit_card_debt, personal_loans, business_loans, other_liabilities)
combined_total_liabilities = total_liabilities_local + partner_liabilities

st.header("Assumptions")
tax_rate = st.number_input("Effective Tax Rate (%)", value=22.0, key="tax_rate")
inflation_rate = st.number_input("Inflation Rate (%)", value=3.0, key="inflation_rate")
investment_return_rate = st.number_input("Investment Return Rate (%)", value=7.0, key="investment_return_rate")
simulation_years = st.number_input("Simulation Years", min_value=10, max_value=100, value=30, key="simulation_years")
mc_iterations = st.number_input("Monte Carlo Iterations (0 to disable)", min_value=0, max_value=10000, value=0, key="mc_iterations")

st.header("Family Events")
if EVENTS_AVAILABLE:
    st.subheader("Children & College Plans")
    children_df = st.data_editor(
        pd.DataFrame(st.session_state.get("children_rows", [financial_utils.child_defaults] * 1)),
        column_config=financial_utils.child_column_config,
        num_rows="dynamic",
        key="children_editor"
    )
    st.session_state["children_rows"] = children_df.to_dict(orient="records")

    st.subheader("Inheritance Events")
    inherit_df = st.data_editor(
        pd.DataFrame(st.session_state.get("inherit_rows", [financial_utils.inherit_defaults] * 1)),
        column_config=financial_utils.inherit_column_config,
        num_rows="dynamic",
        key="inherit_editor"
    )
    st.session_state["inherit_rows"] = inherit_df.to_dict(orient="records")

st.header("College Cost Assumptions")
college_inflation_pct = st.number_input("College Inflation Rate (%)", value=4.0, key="college_inflation_pct")
base_public_in = st.number_input("Base Public In-State Annual Cost ($)", value=20000.0, key="base_public_in")
base_public_out = st.number_input("Base Public Out-of-State Annual Cost ($)", value=40000.0, key="base_public_out")
base_private = st.number_input("Base Private Annual Cost ($)", value=60000.0, key="base_private")

st.header("Goals")
goal_df = st.data_editor(
    pd.DataFrame([{"Goal": "", "Target $": 0.0, "Target Year Range": ""}] * 3),
    column_config={
        "Goal": st.column_config.TextColumn("Goal"),
        "Target $": st.column_config.NumberColumn("Target $", min_value=0.0),
        "Target Year Range": st.column_config.TextColumn("Target Year Range (e.g., 2030-2035 or 2040)")
    },
    num_rows="dynamic",
    key="goal_editor"
)
goal_costs = financial_utils.parse_goal_costs(goal_df)

st.header("Advanced Tax Strategies")
roth_conversion_annual = st.number_input("Annual Roth Conversion Amount ($)", value=0.0, key="roth_conversion_annual")
itemize_deductions = st.checkbox("Itemize Deductions?", value=True, key="itemize_deductions")

# End of Part 1
# File: GROK_app_family_plus.py - Part 2 (Continuing from Part 1)
if st.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        results = simulation.run_simulation(
            age=age, partner_exists=partner_exists, partner_age=partner_age,
            total_income=total_income,
            total_expenses=total_expenses,
            combined_financial_assets=combined_financial_assets,
            primary_residence_value=primary_residence_value,
            secondary_residence_value=secondary_residence_value,
            combined_other_assets_total=combined_other_assets_total,
            total_liabilities_local=total_liabilities_local, partner_liabilities=partner_liabilities,
            tax_rate=tax_rate, inflation_rate=inflation_rate,
            investment_return_rate=investment_return_rate,
            simulation_years=simulation_years, mc_iterations=mc_iterations, goal_costs=goal_costs,
            college_inflation_pct=college_inflation_pct, base_public_in=base_public_in, base_public_out=base_public_out, base_private=base_private,
            ira_balance=ira_balance, four01k_403b_balance=four01k_403b_balance,
            partner_ira_balance=partner_ira_balance,
            partner_four01k_403b_balance=partner_four01k_403b_balance,
            monthly_surplus=monthly_surplus, combined_total_liabilities=combined_total_liabilities,
            roth_conversion_annual=roth_conversion_annual, itemize_deductions=itemize_deductions,
            five29_plan_balance=five29_plan_balance
        )
        st.session_state['results'] = results
        st.session_state['sim_params'] = locals()  # For AI opt rerun

results = st.session_state.get('results', None)
if results:
    if show_health_dashboard:
        financial_utils.display_summary_metrics(results, simulation_years)
        financial_utils.display_health_dashboard(combined_financial_assets, total_expenses, total_income * 12, combined_total_liabilities, results)
        financial_utils.display_goal_achievement(results)

    visuals.show_trajectories(results)
    if mc_iterations > 0:
        visuals.show_monte_carlo(results)

    if show_risk_analysis:
        st.subheader("Risk Analysis Matrix")
        risk_data = {
            "Risk Factor": ["Market Downturn", "High Inflation", "Health Event", "Job Loss"],
            "Probability": ["Medium", "Low", "Medium", "Low"],
            "Impact": ["High", "Medium", "High", "Medium"],
            "Mitigation": ["Diversify", "Adjust Budget", "Insurance", "Emergency Fund"]
        }
        st.table(pd.DataFrame(risk_data))

    if show_scenario_comparison:
        st.subheader("Scenario Comparison Tool")
        income_adj = st.slider("Income Adjustment (%)", -50, 50, 0)
        expenses_adj = st.slider("Expenses Adjustment (%)", -50, 50, 0)
        tax_adj = st.slider("Tax Rate Adjustment (%)", -10, 10, 0)
        inflation_adj = st.slider("Inflation Adjustment (%)", -2, 5, 0)
        return_adj = st.slider("Return Rate Adjustment (%)", -5, 5, 0)
        adj_goal_costs = {}
        for _, row in goal_df.iterrows():
            if pd.notna(row.get('Goal')) and pd.notna(row.get('Target $')):
                goal_name = row.get('Goal', '')
                target_amount = row.get('Target $', 0.0)
                target_year_str = row.get('Target Year Range', '')
                if not target_year_str or not str(target_year_str).strip():
                    target_year_str = f"{date.today().year + 20}"
                try:
                    if '-' in target_year_str:
                        target_year = int(target_year_str.split('-')[0])
                    else:
                        target_year = int(target_year_str)
                    adj_goal_costs[goal_name] = {'year': target_year, 'amount': target_amount}
                except ValueError:
                    adj_goal_costs[goal_name] = {'year': date.today().year + 20, 'amount': target_amount}
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