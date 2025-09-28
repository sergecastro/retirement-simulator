# File: financial_utils.py
import pandas as pd
import math
from datetime import date
import streamlit as st
import plotly.graph_objects as go

def safe_float(value, default):
    if pd.notna(value) and not math.isnan(value):
        return float(value)
    return default

def safe_int(value, default):
    if pd.notna(value) and not math.isnan(value):
        return int(value)
    return default

def fix_nan_in_df(df, defaults):
    for col, default in defaults.items():
        df[col] = df[col].fillna(default)

def calculate_total_income(*incomes):
    return sum(incomes)

def calculate_total_expenses(*expenses):
    return sum(expenses)

def calculate_total_assets(*assets):
    return sum(assets)

def calculate_total_liabilities(*liabilities):
    return sum(liabilities)

def calculate_partner_total_assets(partner_exists, *partner_assets):
    return sum(partner_assets) if partner_exists else 0.0

def calculate_liquid_assets(*args):
    assets = []
    partner_assets = []
    current = assets
    partner_exists = False
    for arg in args:
        if isinstance(arg, bool):
            partner_exists = arg
            current = partner_assets
        else:
            asset_value = safe_float(arg, 0.0)
            current.append(asset_value)
    total = sum(assets)
    if partner_exists:
        total += sum(partner_assets)
    return total

def calculate_other_assets(*assets, partner_exists, partner_other):
    total = sum(assets)
    if partner_exists:
        total += partner_other
    return total

def parse_goal_costs(goal_df):
    goal_costs = {}
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
                goal_costs[goal_name] = {'year': target_year, 'amount': target_amount}
            except ValueError:
                goal_costs[goal_name] = {'year': date.today().year + 20, 'amount': target_amount}
    return goal_costs

def get_all_inputs_as_dict(app_locals):
    return {
        "input_style": app_locals['input_style'],
        "age_group": app_locals['age_group'],
        "age": app_locals['age'],
        "partner_name": app_locals['partner_name'],
        "partner_exists": app_locals['partner_exists'],
        "partner_age": app_locals['partner_age'],
        "partner_ira_balance": app_locals['partner_ira_balance'],
        "partner_four01k_403b_balance": app_locals['partner_four01k_403b_balance'],
        "partner_taxable_investment_accounts": app_locals['partner_taxable_investment_accounts'],
        "partner_other_assets": app_locals['partner_other_assets'],
        "partner_liabilities": app_locals['partner_liabilities'],
        "salary_wages": app_locals.get('salary_wages', 0.0),
        "self_employment_income": app_locals.get('self_employment_income', 0.0),
        "rental_income": app_locals.get('rental_income', 0.0),
        "investment_income": app_locals.get('investment_income', 0.0),
        "social_security_income": app_locals.get('social_security_income', 0.0),
        "pension_income": app_locals.get('pension_income', 0.0),
        "other_income": app_locals.get('other_income', 0.0),
        "total_income": app_locals['total_income'],
        "housing_expenses": app_locals.get('housing_expenses', 0.0),
        "utilities_expenses": app_locals.get('utilities_expenses', 0.0),
        "groceries_expenses": app_locals.get('groceries_expenses', 0.0),
        "transportation_expenses": app_locals.get('transportation_expenses', 0.0),
        "healthcare_expenses": app_locals.get('healthcare_expenses', 0.0),
        "insurance_expenses": app_locals.get('insurance_expenses', 0.0),
        "real_estate_insurance_expenses": app_locals.get('real_estate_insurance_expenses', 0.0),
        "property_tax_expenses": app_locals.get('property_tax_expenses', 0.0),
        "entertainment_expenses": app_locals.get('entertainment_expenses', 0.0),
        "restaurant_expenses": app_locals.get('restaurant_expenses', 0.0),
        "travel_expenses": app_locals.get('travel_expenses', 0.0),
        "education_expenses": app_locals.get('education_expenses', 0.0),
        "childcare_expenses": app_locals.get('childcare_expenses', 0.0),
        "clothing_expenses": app_locals.get('clothing_expenses', 0.0),
        "charitable_donations": app_locals.get('charitable_donations', 0.0),
        "miscellaneous_expenses": app_locals.get('miscellaneous_expenses', 0.0),
        "other_expenses": app_locals.get('other_expenses', 0.0),
        "total_expenses": app_locals['total_expenses'],
        "primary_residence_value": app_locals['primary_residence_value'],
        "secondary_residence_value": app_locals['secondary_residence_value'],
        "ira_balance": app_locals['ira_balance'],
        "four01k_403b_balance": app_locals['four01k_403b_balance'],
        "taxable_investment_accounts": app_locals['taxable_investment_accounts'],
        "pension_fund_value": app_locals['pension_fund_value'],
        "life_insurance_cash_value": app_locals['life_insurance_cash_value'],
        "high_yield_savings_account": app_locals['high_yield_savings_account'],
        "hsa_balance": app_locals['hsa_balance'],
        "five29_plan_balance": app_locals['five29_plan_balance'],
        "vehicles_value": app_locals['vehicles_value'],
        "jewelry_collectibles_value": app_locals['jewelry_collectibles_value'],
        "business_ownership_value": app_locals['business_ownership_value'],
        "cryptocurrency_holdings": app_locals['cryptocurrency_holdings'],
        "other_assets": app_locals['other_assets'],
        "primary_residence_mortgage": app_locals['primary_residence_mortgage'],
        "secondary_residence_mortgage": app_locals['secondary_residence_mortgage'],
        "auto_loans": app_locals['auto_loans'],
        "student_loans": app_locals['student_loans'],
        "credit_card_debt": app_locals['credit_card_debt'],
        "personal_loans": app_locals['personal_loans'],
        "business_loans": app_locals['business_loans'],
        "other_liabilities": app_locals['other_liabilities'],
        "tax_rate": app_locals['tax_rate'],
        "inflation_rate": app_locals['inflation_rate'],
        "investment_return_rate": app_locals['investment_return_rate'],
        "simulation_years": app_locals['simulation_years'],
        "mc_iterations": app_locals['mc_iterations'],
        "college_inflation_pct": app_locals['college_inflation_pct'],
        "base_public_in": app_locals['base_public_in'],
        "base_public_out": app_locals['base_public_out'],
        "base_private": app_locals['base_private']
    }

def calculate_health_score(emergency_months, dti, savings_rate, final_positive):
    score = 0
    if emergency_months >= 6:
        score += 30
    elif emergency_months >= 3:
        score += 20
    if dti <= 0.36:
        score += 30
    elif dti <= 0.5:
        score += 20
    if savings_rate >= 0.2:
        score += 20
    elif savings_rate >= 0.1:
        score += 10
    if final_positive:
        score += 20
    return score

def display_summary_metrics(results, simulation_years):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("**Years Solvent**", f"{results['years_solvent']}/{simulation_years}")
    with col2:
        st.metric("**Final Savings**", f"${results['final_savings']:,.2f}")
    with col3:
        st.metric("**Final Net Worth**", f"${results['final_net_worth']:,.2f}")
    with col4:
        st.metric("**Health Score**", f"{results['health_score']}/100")

def display_health_dashboard(liquid_assets, total_expenses, total_income, total_liabilities, results):
    st.subheader("Financial Health Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Emergency Fund", f"{results['emergency_fund_months']:.1f} months")
    with col2:
        st.metric("Debt-to-Income", f"{results['debt_to_income']:.2%}")
    with col3:
        st.metric("Savings Rate", f"{results['savings_rate']:.2%}")

def display_goal_achievement(results):
    st.subheader("Goal Achievement")
    for goal, data in results['goal_achievement'].items():
        status = "✅" if data['achieved'] else "❌"
        st.write(f"**{goal}**: {status} (Target ${data['target']:,.2f} by {data['year']}, Actual ${data['actual']:,.2f})")

def run_sensitivity_analysis(*params, results):
    # Implement sensitivity sliders and adjusted sim
    # Use simulation.run_simulation with adjusted params
    pass

child_column_config = {
    "Name": st.column_config.TextColumn("Name", help="Child's name", default=""),
    "Birth Year": st.column_config.NumberColumn("Birth Year", help="Year of birth", format="%d", min_value=1900, max_value=date.today().year + 20, default=date.today().year - 5),
    "College Plan": st.column_config.SelectboxColumn("Education Type", help="Education type", options=["None", "Public In-State", "Public Out-of-State", "Private"], default="None"),
    "Scholarship %": st.column_config.NumberColumn("Scholarship %", help="Expected scholarship percentage", min_value=0.0, max_value=100.0, format="%.1f", default=0.0),
    "Start Age": st.column_config.NumberColumn("Start Age", help="Age to start college", min_value=16, max_value=25, format="%d", default=18),
    "Years": st.column_config.NumberColumn("Years", help="Duration of education", min_value=1, max_value=8, format="%d", default=4),
    "Use 529 First?": st.column_config.CheckboxColumn("Use 529 First?", help="Prioritize 529 plan for payments", default=True)
}

child_defaults = {
    "Name": "",
    "Birth Year": date.today().year - 5,
    "College Plan": "None",
    "Scholarship %": 0.0,
    "Start Age": 18,
    "Years": 4,
    "Use 529 First?": True
}

inherit_column_config = {
    "Year": st.column_config.NumberColumn("Year", help="Year of inheritance", format="%d", min_value=date.today().year, max_value=date.today().year + 100, default=date.today().year + 10),
    "Amount": st.column_config.NumberColumn("Amount", help="Expected amount", format="$%.2f", min_value=0.0, default=0.0),
    "Taxable?": st.column_config.CheckboxColumn("Taxable?", help="Is the inheritance taxable?", default=False)
}

inherit_defaults = {
    "Year": date.today().year + 10,
    "Amount": 0.0,
    "Taxable?": False
}