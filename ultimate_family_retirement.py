# Ultimate Family Retirement Planning Plus v3.0
# Combining best features from GROK and CLAUDE versions
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import math
from datetime import date, datetime
import plotly.graph_objects as go
import plotly.express as px
import calendar

# Conditional imports
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

try:
    import household_events as he
    EVENTS_AVAILABLE = True
except ImportError:
    EVENTS_AVAILABLE = False
    st.error("household_events.py not found. Family events disabled.")

# Page configuration
st.set_page_config(
    page_title="Ultimate Family Retirement Plus",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏠 Ultimate Family Retirement Planning Plus v3.0")
st.markdown("*The Most Advanced Family Lifecycle Financial Simulation & Planning Tool*")

# ─────────────────────────────────────────────────────────────────
# PASSWORD PROTECTION WITH SCENARIO DIFFERENTIATION
# ─────────────────────────────────────────────────────────────────
st.header("🔐 Access Control")
password = st.text_input("Enter password:", type="password")

if password not in ["abcd123", "uhiRR2938foq"]:
    st.error("🚫 Incorrect password.")
    st.info("Demo: 'abcd123' | Trusted: 'uhiRR2938foq'")
    st.stop()

TRUSTED_PASSWORD = "uhiRR2938foq"
IS_TRUSTED_USER = (password == TRUSTED_PASSWORD)

# Display user status
if IS_TRUSTED_USER:
    st.success("✅ **Trusted User Access Granted** - Full features and private scenarios enabled")
else:
    st.info("📌 **Demo Mode** - Basic features enabled")

# ─────────────────────────────────────────────────────────────────
# ENHANCED SIDEBAR CONFIGURATION
# ─────────────────────────────────────────────────────────────────
st.sidebar.header("🚀 Advanced Features")

# Financial Health Dashboard
st.sidebar.markdown("**📊 Financial Health Dashboard**")
show_health_dashboard = st.sidebar.checkbox("Financial Health Scoring", value=True)
show_risk_analysis = st.sidebar.checkbox("Risk Analysis Matrix", value=True)

# Interactive Planning
st.sidebar.markdown("**🗓️ Interactive Timeline & Planning**")
show_timeline = st.sidebar.checkbox("Interactive Family Timeline", value=True)
show_scenario_comparison = st.sidebar.checkbox("Scenario Comparison Tool", value=True)
show_extended_projections = st.sidebar.checkbox("Extended Projections (50+ years)", value=False)
show_family_reports = st.sidebar.checkbox("Family Reports Generator", value=True)

# Visual Analytics
st.sidebar.markdown("**📈 Visual Analytics Lab**")
show_sankey = st.sidebar.checkbox("Cash-Flow Sankey", value=True)
show_goals = st.sidebar.checkbox("Goal-Funding Gauges", value=True)
show_calendar = st.sidebar.checkbox("Monthly Heatmap", value=False)
show_comparison = st.sidebar.checkbox("Competitive Analysis", value=False)

# Monte Carlo
st.sidebar.markdown("**🎲 Advanced Simulations**")
show_monte_carlo = st.sidebar.checkbox("Monte Carlo Analysis", value=True)
show_stress_tests = st.sidebar.checkbox("Stress Testing", value=False)

# AI Features
if OPENAI_AVAILABLE and IS_TRUSTED_USER:
    st.sidebar.markdown("**🤖 AI Features**")
    show_ai_advisor = st.sidebar.checkbox("AI Financial Advisor", value=True)
    show_auto_optimization = st.sidebar.checkbox("Auto-Optimization", value=False)

# ─────────────────────────────────────────────────────────────────
# SCENARIO MANAGEMENT WITH PROPER DATA LOADING
# ─────────────────────────────────────────────────────────────────
st.header("📁 Scenario Management")

# Helper functions for scenario management
def load_scenarios(filename="family_scenarios.json"):
    """Load scenarios from file with proper error handling"""
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            st.warning(f"Error loading scenarios: {e}")
            return {}
    return {}

def save_scenarios(scenarios_dict, filename="family_scenarios.json"):
    """Save scenarios with atomic write"""
    try:
        tmp_file = filename + ".tmp"
        with open(tmp_file, "w") as f:
            json.dump(scenarios_dict, f, indent=2)
        os.replace(tmp_file, filename)
        return True
    except Exception as e:
        st.error(f"Error saving scenarios: {e}")
        return False

# Define default scenarios based on user type
if IS_TRUSTED_USER:
    DEFAULT_SCENARIOS = {
        "Empty Scenario": {
            "age": 35,
            "partner_name": "",
            "partner_age": 35,
            "total_income": 5000.0,
            "total_expenses": 4400.0,
            "ira_balance": 50000.0,
            "four01k_403b_balance": 75000.0,
            "primary_residence_value": 400000.0,
            "primary_residence_mortgage": 300000.0,
            "partner_ira_balance": 0.0,
            "partner_four01k_403b_balance": 0.0,
            "high_yield_savings_account": 20000.0,
            "taxable_investment_accounts": 25000.0,
            "tax_rate": 22.0,
            "inflation_rate": 3.0,
            "investment_return_rate": 7.0,
            "simulation_years": 30
        },
        "70+ Retirement Scenario (Private)": {
            "age": 76,
            "partner_name": "Judith",
            "partner_age": 74,
            "total_income": 12100.0,
            "total_expenses": 4900.0,
            "ira_balance": 300000.0,
            "four01k_403b_balance": 200000.0,
            "primary_residence_value": 500000.0,
            "secondary_residence_value": 200000.0,
            "primary_residence_mortgage": 0.0,
            "partner_ira_balance": 200000.0,
            "partner_four01k_403b_balance": 150000.0,
            "partner_taxable_investment_accounts": 100000.0,
            "high_yield_savings_account": 100000.0,
            "taxable_investment_accounts": 150000.0,
            "pension_fund_value": 100000.0,
            "life_insurance_cash_value": 50000.0,
            "tax_rate": 15.0,
            "inflation_rate": 2.5,
            "investment_return_rate": 5.0,
            "simulation_years": 20,
            "rental_income": 2000.0,
            "social_security_income": 3600.0,
            "pension_income": 6000.0,
            "investment_income": 500.0
        }
    }
else:
    DEFAULT_SCENARIOS = {
        "Demo Scenario": {
            "age": 35,
            "partner_name": "",
            "partner_age": 35,
            "total_income": 5000.0,
            "total_expenses": 4400.0,
            "ira_balance": 25000.0,
            "four01k_403b_balance": 35000.0,
            "primary_residence_value": 200000.0,
            "primary_residence_mortgage": 150000.0,
            "high_yield_savings_account": 10000.0,
            "tax_rate": 22.0,
            "inflation_rate": 3.0,
            "investment_return_rate": 7.0,
            "simulation_years": 30
        }
    }

# Load saved scenarios or use defaults
saved_scenarios = load_scenarios()
if not saved_scenarios:
    saved_scenarios = DEFAULT_SCENARIOS.copy()
    save_scenarios(saved_scenarios)

# Scenario selection
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    scenario_names = list(saved_scenarios.keys()) + ["New Scenario"]
    selected_scenario = st.selectbox("Select Scenario:", scenario_names)

# CRITICAL: Load scenario data into session state
if selected_scenario != "New Scenario" and selected_scenario in saved_scenarios:
    scenario_data = saved_scenarios[selected_scenario]
    # Update session state with scenario data
    for key, value in scenario_data.items():
        st.session_state[f"input_{key}"] = value
    st.success(f"✅ Loaded scenario: {selected_scenario}")

with col2:
    if st.button("💾 Save Current", type="primary"):
        scenario_name = st.text_input("Name:", value=selected_scenario if selected_scenario != "New Scenario" else "")
        if scenario_name:
            # Collect current values and save
            current_data = {key.replace("input_", ""): value for key, value in st.session_state.items() if key.startswith("input_")}
            saved_scenarios[scenario_name] = current_data
            save_scenarios(saved_scenarios)
            st.success(f"Saved: {scenario_name}")

with col3:
    if st.button("🗑️ Delete Scenario"):
        if selected_scenario != "New Scenario" and selected_scenario in saved_scenarios:
            del saved_scenarios[selected_scenario]
            save_scenarios(saved_scenarios)
            st.success(f"Deleted: {selected_scenario}")
            st.experimental_rerun()

# ─────────────────────────────────────────────────────────────────
# USER INFORMATION WITH PROPER VALUE LOADING
# ─────────────────────────────────────────────────────────────────
st.header("👤 User Information")

# Get values from session state or defaults
age = st.number_input(
    "Your Age:",
    min_value=18,
    max_value=110,
    value=st.session_state.get("input_age", 35),
    key="input_age"
)

partner_name = st.text_input(
    "Partner's Name (leave blank if none):",
    value=st.session_state.get("input_partner_name", ""),
    key="input_partner_name"
)

partner_exists = bool(partner_name.strip())

if partner_exists:
    partner_age = st.number_input(
        f"{partner_name}'s Age:",
        min_value=18,
        max_value=110,
        value=st.session_state.get("input_partner_age", 35),
        key="input_partner_age"
    )
else:
    partner_age = age

# ─────────────────────────────────────────────────────────────────
# INCOME & EXPENSES
# ─────────────────────────────────────────────────────────────────
st.header("💰 Monthly Income & Expenses")

# Income section
with st.expander("📈 Income Sources", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        salary_wages = st.number_input(
            "Salary/Wages:",
            value=st.session_state.get("input_salary_wages", 0.0),
            format="%.2f",
            key="input_salary_wages"
        )
        self_employment = st.number_input(
            "Self-Employment:",
            value=st.session_state.get("input_self_employment", 0.0),
            format="%.2f",
            key="input_self_employment"
        )
    
    with col2:
        rental_income = st.number_input(
            "Rental Income:",
            value=st.session_state.get("input_rental_income", 0.0),
            format="%.2f",
            key="input_rental_income"
        )
        investment_income = st.number_input(
            "Investment Income:",
            value=st.session_state.get("input_investment_income", 0.0),
            format="%.2f",
            key="input_investment_income"
        )
    
    with col3:
        social_security_income = st.number_input(
            "Social Security:",
            value=st.session_state.get("input_social_security_income", 0.0),
            format="%.2f",
            key="input_social_security_income"
        )
        pension_income = st.number_input(
            "Pension Income:",
            value=st.session_state.get("input_pension_income", 0.0),
            format="%.2f",
            key="input_pension_income"
        )

# Quick input option
use_quick_input = st.checkbox("Use Quick Totals Instead", value=False)

if use_quick_input:
    total_income = st.number_input(
        "Total Monthly Income:",
        value=st.session_state.get("input_total_income", 5000.0),
        format="%.2f",
        key="input_total_income"
    )
    total_expenses = st.number_input(
        "Total Monthly Expenses:",
        value=st.session_state.get("input_total_expenses", 4400.0),
        format="%.2f",
        key="input_total_expenses"
    )
else:
    # Calculate totals from components
    total_income = salary_wages + self_employment + rental_income + investment_income + social_security_income + pension_income
    
    # Detailed expenses
    with st.expander("💸 Monthly Expenses", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            housing = st.number_input("Housing:", value=st.session_state.get("input_housing", 1500.0), key="input_housing")
            utilities = st.number_input("Utilities:", value=st.session_state.get("input_utilities", 300.0), key="input_utilities")
            groceries = st.number_input("Groceries:", value=st.session_state.get("input_groceries", 600.0), key="input_groceries")
            
        with col2:
            transportation = st.number_input("Transportation:", value=st.session_state.get("input_transportation", 400.0), key="input_transportation")
            healthcare = st.number_input("Healthcare:", value=st.session_state.get("input_healthcare", 200.0), key="input_healthcare")
            insurance = st.number_input("Insurance:", value=st.session_state.get("input_insurance", 300.0), key="input_insurance")
            
        with col3:
            entertainment = st.number_input("Entertainment:", value=st.session_state.get("input_entertainment", 200.0), key="input_entertainment")
            other_expenses = st.number_input("Other:", value=st.session_state.get("input_other_expenses", 900.0), key="input_other_expenses")
        
        total_expenses = housing + utilities + groceries + transportation + healthcare + insurance + entertainment + other_expenses

# Display summary
monthly_surplus = total_income - total_expenses
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Monthly Income", f"${total_income:,.2f}")
with col2:
    st.metric("Monthly Expenses", f"${total_expenses:,.2f}")
with col3:
    color = "🟢" if monthly_surplus > 0 else "🔴"
    st.metric(f"{color} Monthly Surplus", f"${monthly_surplus:,.2f}")

# ─────────────────────────────────────────────────────────────────
# ASSETS & LIABILITIES
# ─────────────────────────────────────────────────────────────────
st.header("💎 Assets & Liabilities")

# Assets
with st.expander("📊 Assets", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Real Estate**")
        primary_residence_value = st.number_input(
            "Primary Residence:",
            value=st.session_state.get("input_primary_residence_value", 400000.0),
            key="input_primary_residence_value"
        )
        secondary_residence_value = st.number_input(
            "Secondary Residence:",
            value=st.session_state.get("input_secondary_residence_value", 0.0),
            key="input_secondary_residence_value"
        )
        
        st.markdown("**Retirement Accounts**")
        ira_balance = st.number_input(
            "IRA Balance:",
            value=st.session_state.get("input_ira_balance", 50000.0),
            key="input_ira_balance"
        )
        four01k_403b_balance = st.number_input(
            "401k/403b Balance:",
            value=st.session_state.get("input_four01k_403b_balance", 75000.0),
            key="input_four01k_403b_balance"
        )
        
    with col2:
        st.markdown("**Investment & Savings**")
        taxable_investment_accounts = st.number_input(
            "Taxable Investments:",
            value=st.session_state.get("input_taxable_investment_accounts", 25000.0),
            key="input_taxable_investment_accounts"
        )
        high_yield_savings_account = st.number_input(
            "Savings Account:",
            value=st.session_state.get("input_high_yield_savings_account", 20000.0),
            key="input_high_yield_savings_account"
        )
        
        st.markdown("**Other Assets**")
        pension_fund_value = st.number_input(
            "Pension Value:",
            value=st.session_state.get("input_pension_fund_value", 0.0),
            key="input_pension_fund_value"
        )
        life_insurance_cash_value = st.number_input(
            "Life Insurance Cash:",
            value=st.session_state.get("input_life_insurance_cash_value", 0.0),
            key="input_life_insurance_cash_value"
        )

# Partner assets if applicable
if partner_exists:
    st.subheader(f"👥 {partner_name}'s Assets")
    col1, col2 = st.columns(2)
    
    with col1:
        partner_ira_balance = st.number_input(
            f"{partner_name}'s IRA:",
            value=st.session_state.get("input_partner_ira_balance", 0.0),
            key="input_partner_ira_balance"
        )
        partner_four01k_403b_balance = st.number_input(
            f"{partner_name}'s 401k:",
            value=st.session_state.get("input_partner_four01k_403b_balance", 0.0),
            key="input_partner_four01k_403b_balance"
        )
    
    with col2:
        partner_taxable_investment_accounts = st.number_input(
            f"{partner_name}'s Investments:",
            value=st.session_state.get("input_partner_taxable_investment_accounts", 0.0),
            key="input_partner_taxable_investment_accounts"
        )
        partner_other_assets = st.number_input(
            f"{partner_name}'s Other Assets:",
            value=st.session_state.get("input_partner_other_assets", 0.0),
            key="input_partner_other_assets"
        )
else:
    partner_ira_balance = 0.0
    partner_four01k_403b_balance = 0.0
    partner_taxable_investment_accounts = 0.0
    partner_other_assets = 0.0

# Liabilities
with st.expander("📉 Liabilities", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        primary_residence_mortgage = st.number_input(
            "Primary Mortgage:",
            value=st.session_state.get("input_primary_residence_mortgage", 300000.0),
            key="input_primary_residence_mortgage"
        )
        auto_loans = st.number_input(
            "Auto Loans:",
            value=st.session_state.get("input_auto_loans", 15000.0),
            key="input_auto_loans"
        )
        
    with col2:
        student_loans = st.number_input(
            "Student Loans:",
            value=st.session_state.get("input_student_loans", 25000.0),
            key="input_student_loans"
        )
        credit_card_debt = st.number_input(
            "Credit Card Debt:",
            value=st.session_state.get("input_credit_card_debt", 5000.0),
            key="input_credit_card_debt"
        )

# Calculate totals
total_assets = (primary_residence_value + secondary_residence_value + ira_balance + 
                four01k_403b_balance + taxable_investment_accounts + high_yield_savings_account +
                pension_fund_value + life_insurance_cash_value)
total_liabilities = primary_residence_mortgage + auto_loans + student_loans + credit_card_debt

if partner_exists:
    total_assets += partner_ira_balance + partner_four01k_403b_balance + partner_taxable_investment_accounts + partner_other_assets

net_worth = total_assets - total_liabilities

# Display financial summary
st.subheader("📊 Financial Summary")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Assets", f"${total_assets:,.0f}")
with col2:
    st.metric("Total Liabilities", f"${total_liabilities:,.0f}")
with col3:
    st.metric("Net Worth", f"${net_worth:,.0f}")
with col4:
    liquid_assets = (ira_balance + four01k_403b_balance + taxable_investment_accounts + 
                    high_yield_savings_account + partner_ira_balance + partner_four01k_403b_balance +
                    partner_taxable_investment_accounts)
    st.metric("Liquid Assets", f"${liquid_assets:,.0f}")

# ─────────────────────────────────────────────────────────────────
# FAMILY EVENTS (if module available)
# ─────────────────────────────────────────────────────────────────
if EVENTS_AVAILABLE:
    st.header("👨‍👩‍👧‍👦 Family Lifecycle Planning")
    
    # Children & College
    st.subheader("🎓 Children & Education")
    
    default_children = [{
        "Name": "",
        "Birth Year": date.today().year - 5,
        "College Plan": "None",
        "Scholarship %": 0.0,
        "Start Age": 18,
        "Years": 4,
        "Use 529 First?": True
    }]
    
    children_data = st.data_editor(
        pd.DataFrame(st.session_state.get("children_rows", default_children)),
        num_rows="dynamic",
        column_config={
            "Name": st.column_config.TextColumn("Child's Name"),
            "Birth Year": st.column_config.NumberColumn("Birth Year", format="%d"),
            "College Plan": st.column_config.SelectboxColumn(
                "College Type",
                options=["None", "Public In-State", "Public Out-of-State", "Private"]
            ),
            "Scholarship %": st.column_config.NumberColumn("Scholarship %", min_value=0, max_value=100),
            "Start Age": st.column_config.NumberColumn("Start Age", min_value=16, max_value=25),
            "Years": st.column_config.NumberColumn("Duration", min_value=1, max_value=8),
            "Use 529 First?": st.column_config.CheckboxColumn("529 Priority")
        },
        key="children_editor"
    )
    st.session_state.children_rows = children_data.to_dict(orient="records")
    
    # Inheritance Events
    st.subheader("💰 Expected Inheritances")
    
    default_inherit = [{
        "Year": date.today().year + 10,
        "Amount": 0.0,
        "Taxable?": False
    }]
    
    inherit_data = st.data_editor(
        pd.DataFrame(st.session_state.get("inherit_rows", default_inherit)),
        num_rows="dynamic",
        column_config={
            "Year": st.column_config.NumberColumn("Year", format="%d"),
            "Amount": st.column_config.NumberColumn("Amount ($)", format="$%.0f"),
            "Taxable?": st.column_config.CheckboxColumn("Taxable")
        },
        key="inherit_editor"
    )
    st.session_state.inherit_rows = inherit_data.to_dict(orient="records")

# ─────────────────────────────────────────────────────────────────
# SIMULATION PARAMETERS
# ─────────────────────────────────────────────────────────────────
st.header("⚙️ Simulation Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    tax_rate = st.number_input(
        "Tax Rate (%):",
        value=st.session_state.get("input_tax_rate", 22.0),
        key="input_tax_rate"
    )
    inflation_rate = st.number_input(
        "Inflation Rate (%):",
        value=st.session_state.get("input_inflation_rate", 3.0),
        key="input_inflation_rate"
    )

with col2:
    investment_return_rate = st.number_input(
        "Investment Return (%):",
        value=st.session_state.get("input_investment_return_rate", 7.0),
        key="input_investment_return_rate"
    )
    simulation_years = st.number_input(
        "Simulation Years:",
        value=st.session_state.get("input_simulation_years", 30),
        min_value=5,
        max_value=75,
        key="input_simulation_years"
    )

with col3:
    if show_monte_carlo:
        mc_iterations = st.number_input(
            "Monte Carlo Iterations:",
            value=1000,
            min_value=0,
            max_value=10000,
            step=100,
            key="mc_iterations"
        )
    else:
        mc_iterations = 0

# ─────────────────────────────────────────────────────────────────
# RUN SIMULATION BUTTON
# ─────────────────────────────────────────────────────────────────
st.header("🚀 Run Simulation")

if st.button("🎯 Run Financial Simulation", type="primary", use_container_width=True):
    with st.spinner("Running simulation..."):
        # Simple simulation for demonstration
        # In production, this would call your simulation.py module
        import simulation
        results = simulation.run_simulation(
            age=age, 
            partner_exists=partner_exists, 
            partner_age=partner_age,
            total_income=total_income,
            total_expenses=total_expenses,
            combined_financial_assets=liquid_assets,
            primary_residence_value=primary_residence_value,
            secondary_residence_value=secondary_residence_value,
            combined_other_assets_total=0,  # Calculate if needed
            total_liabilities_local=total_liabilities,
            partner_liabilities=0,  # Add if tracking separately
            tax_rate=tax_rate,
            inflation_rate=inflation_rate,
            investment_return_rate=investment_return_rate,
            simulation_years=simulation_years,
            mc_iterations=mc_iterations,
            goal_costs={},  # Add goals if implemented
            college_inflation_pct=4.0,
            base_public_in=20000.0,
            base_public_out=40000.0,
            base_private=60000.0,
            ira_balance=ira_balance,
            four01k_403b_balance=four01k_403b_balance,
            partner_ira_balance=partner_ira_balance,
            partner_four01k_403b_balance=partner_four01k_403b_balance,
            monthly_surplus=monthly_surplus,
            combined_total_liabilities=total_liabilities
        )
         
    
        # Calculate simple projection
        years = list(range(date.today().year, date.today().year + simulation_years))
        savings = []
        current_savings = liquid_assets
        
        for year_idx in range(simulation_years):
            annual_income = total_income * 12 * (1 + inflation_rate/100) ** year_idx
            annual_expenses = total_expenses * 12 * (1 + inflation_rate/100) ** year_idx
            net_flow = annual_income - annual_expenses
            current_savings = current_savings * (1 + investment_return_rate/100) + net_flow
            savings.append(current_savings)
        
        # Store results
        results_df = pd.DataFrame({
            "Year": years,
            "Savings": savings,
            "Age": [age + i for i in range(simulation_years)]
        })
        
        st.session_state['simulation_results'] = {
            'df': results_df,
            'final_savings': savings[-1] if savings else 0,
            'years_positive': sum(1 for s in savings if s > 0)
        }
        
        st.success("✅ Simulation Complete!")

# ─────────────────────────────────────────────────────────────────
# DISPLAY RESULTS
# ─────────────────────────────────────────────────────────────────
if 'simulation_results' in st.session_state:
    results = st.session_state['simulation_results']
    
    st.header("📊 Results & Analysis")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Final Savings", f"${results['final_savings']:,.0f}")
    with col2:
        st.metric("Years Solvent", f"{results['years_positive']}/{simulation_years}")
    with col3:
        success_rate = (results['years_positive'] / simulation_years) * 100
        st.metric("Success Rate", f"{success_rate:.0f}%")
    with col4:
        health_score = min(100, int(success_rate + (20 if monthly_surplus > 0 else 0)))
        st.metric("Health Score", f"{health_score}/100")
    
    # Trajectory chart
    st.subheader("📈 Savings Trajectory")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=results['df']['Year'],
        y=results['df']['Savings'],
        mode='lines',
        name='Projected Savings',
        line=dict(color='blue', width=3)
    ))
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Savings ($)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Download results
    csv = results['df'].to_csv(index=False)
    st.download_button(
        "📥 Download Results (CSV)",
        csv,
        "retirement_projection.csv",
        "text/csv"
    )

# ─────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<p><strong>Ultimate Family Retirement Planning Plus v3.0</strong></p>
<p>Combining the best of GROK and CLAUDE architectures</p>
<p>Your trusted financial planning companion | 100% Private | AI-Powered</p>
</div>
""", unsafe_allow_html=True)