# financial_utils.py - Utility functions (copied intact, slimmed redundancies, ~200 lines)
import pandas as pd
import math
from datetime import date
import streamlit as st
import plotly.graph_objects as go

def safe_float(value, default=0.0):
    if pd.notna(value) and not math.isnan(value):
        return float(value)
    return default

def safe_int(value, default=0):
    if pd.notna(value) and not math.isnan(value):
        return int(value)
    return default

def fix_nan_in_df(df, defaults):
    for col, default in defaults.items():
        df[col] = df[col].fillna(default)

def calculate_total_income(*incomes):
    return sum(safe_float(i) for i in incomes)

def calculate_total_expenses(*expenses):
    return sum(safe_float(e) for e in expenses)

def calculate_total_assets(*assets):
    return sum(safe_float(a) for a in assets)

def calculate_total_liabilities(*liabilities):
    return sum(safe_float(l) for l in liabilities)

def calculate_partner_total_assets(partner_exists, *partner_assets):
    if not partner_exists:
        return 0.0
    return sum(safe_float(pa) for pa in partner_assets)

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
            current.append(safe_float(arg))
    total = sum(assets)
    if partner_exists:
        total += sum(partner_assets)
    return total

def calculate_other_assets(*assets, partner_exists=False, partner_other=0.0):
    total = sum(safe_float(a) for a in assets)
    if partner_exists:
        total += safe_float(partner_other)
    return total

def parse_goal_costs(goal_df):
    goal_costs = {}
    for _, row in goal_df.iterrows():
        if pd.notna(row.get('Goal')) and pd.notna(row.get('Target $')):
            goal_name = row.get('Goal', '')
            target_amount = safe_float(row.get('Target $'))
            target_year_str = row.get('Target Year Range', '')
            if not target_year_str.strip():
                target_year_str = f"{date.today().year + 20}"
            try:
                if '-' in target_year_str:
                    target_year = int(target_year_str.split('-')[0])
                else:
                    target_year = int(target_year_str)
            except ValueError:
                target_year = date.today().year + 20
            goal_costs[goal_name] = {'year': target_year, 'amount': target_amount}
    return goal_costs

def get_all_inputs_as_dict(app_locals):
    return {
        "input_style": app_locals.get('input_input_style', 'Detailed Breakdown'),
        "age_group": app_locals.get('input_age_group', '25-55'),
        "age": app_locals.get('input_age', 35),
        "partner_name": app_locals.get('input_partner_name', ''),
        "partner_exists": app_locals.get('input_partner_exists', False),
        "partner_age": app_locals.get('input_partner_age', 35),
        "partner_ira_balance": app_locals.get('input_partner_ira_balance', 0.0),
        "partner_four01k_403b_balance": app_locals.get('input_partner_four01k_403b_balance', 0.0),
        "partner_taxable_investment_accounts": app_locals.get('input_partner_taxable_investment_accounts', 0.0),
        "partner_other_assets": app_locals.get('input_partner_other_assets', 0.0),
        "partner_liabilities": app_locals.get('input_partner_liabilities', 0.0),
        "salary_wages": app_locals.get('input_salary_wages', 0.0),
        "self_employment_income": app_locals.get('input_self_employment_income', 0.0),
        "rental_income": app_locals.get('input_rental_income', 0.0),
        "investment_income": app_locals.get('input_investment_income', 0.0),
        "social_security_income": app_locals.get('input_social_security_income', 0.0),
        "pension_income": app_locals.get('input_pension_income', 0.0),
        "other_income": app_locals.get('input_other_income', 0.0),
        "total_income": app_locals.get('input_total_income', 0.0),
        "housing_expenses": app_locals.get('input_housing_expenses', 0.0),
        "utilities_expenses": app_locals.get('input_utilities_expenses', 0.0),
        "groceries_expenses": app_locals.get('input_groceries_expenses', 0.0),
        "transportation_expenses": app_locals.get('input_transportation_expenses', 0.0),
        "healthcare_expenses": app_locals.get('input_healthcare_expenses', 0.0),
        "insurance_expenses": app_locals.get('input_insurance_expenses', 0.0),
        "real_estate_insurance_expenses": app_locals.get('input_real_estate_insurance_expenses', 0.0),
        "property_tax_expenses": app_locals.get('input_property_tax_expenses', 0.0),
        "entertainment_expenses": app_locals.get('input_entertainment_expenses', 0.0),
        "restaurant_expenses": app_locals.get('input_restaurant_expenses', 0.0),
        "travel_expenses": app_locals.get('input_travel_expenses', 0.0),
        "education_expenses": app_locals.get('input_education_expenses', 0.0),
        "childcare_expenses": app_locals.get('input_childcare_expenses', 0.0),
        "clothing_expenses": app_locals.get('input_clothing_expenses', 0.0),
        "charitable_donations": app_locals.get('input_charitable_donations', 0.0),
        "miscellaneous_expenses": app_locals.get('input_miscellaneous_expenses', 0.0),
        "other_expenses": app_locals.get('input_other_expenses', 0.0),
        "total_expenses": app_locals.get('input_total_expenses', 0.0),
        "primary_residence_value": app_locals.get('input_primary_residence_value', 0.0),
        "secondary_residence_value": app_locals.get('input_secondary_residence_value', 0.0),
        "ira_balance": app_locals.get('input_ira_balance', 0.0),
        "four01k_403b_balance": app_locals.get('input_four01k_403b_balance', 0.0),
        "taxable_investment_accounts": app_locals.get('input_taxable_investment_accounts', 0.0),
        "pension_fund_value": app_locals.get('input_pension_fund_value', 0.0),
        "life_insurance_cash_value": app_locals.get('input_life_insurance_cash_value', 0.0),
        "high_yield_savings_account": app_locals.get('input_high_yield_savings_account', 0.0),
        "hsa_balance": app_locals.get('input_hsa_balance', 0.0),
        "five29_plan_balance": app_locals.get('input_five29_plan_balance', 0.0),
        "vehicles_value": app_locals.get('input_vehicles_value', 0.0),
        "jewelry_collectibles_value": app_locals.get('input_jewelry_collectibles_value', 0.0),
        "business_ownership_value": app_locals.get('input_business_ownership_value', 0.0),
        "cryptocurrency_holdings": app_locals.get('input_cryptocurrency_holdings', 0.0),
        "other_assets": app_locals.get('input_other_assets', 0.0),
        "primary_residence_mortgage": app_locals.get('input_primary_residence_mortgage', 0.0),
        "secondary_residence_mortgage": app_locals.get('input_secondary_residence_mortgage', 0.0),
        "auto_loans": app_locals.get('input_auto_loans', 0.0),
        "student_loans": app_locals.get('input_student_loans', 0.0),
        "credit_card_debt": app_locals.get('input_credit_card_debt', 0.0),
        "personal_loans": app_locals.get('input_personal_loans', 0.0),
        "business_loans": app_locals.get('input_business_loans', 0.0),
        "other_liabilities": app_locals.get('input_other_liabilities', 0.0),
        "tax_rate": app_locals.get('input_tax_rate', 22.0),
        "inflation_rate": app_locals.get('input_inflation_rate', 3.0),
        "investment_return_rate": app_locals.get('input_investment_return_rate', 7.0),
        "simulation_years": app_locals.get('input_simulation_years', 30),
        "mc_iterations": app_locals.get('input_mc_iterations', 1000),
        "college_inflation_pct": app_locals.get('input_college_inflation_pct', 4.0),
        "base_public_in": app_locals.get('input_base_public_in', 20000.0),
        "base_public_out": app_locals.get('input_base_public_out', 40000.0),
        "base_private": app_locals.get('input_base_private', 60000.0),
        # ADDED: Family fields for save/load restoration
        "children_rows": app_locals.get('input_children_rows', []),
        "inherit_rows": app_locals.get('input_inherit_rows', []),
        "children_data": app_locals.get('input_children_rows', []),
        "inheritance_data": app_locals.get('input_inherit_rows', []),
        "goals_data": app_locals.get('input_goals_data', [])
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
        st.metric("**Years Solvent**", f"{results.get('years_solvent', 0)}/{simulation_years}")
    with col2:
        st.metric("**Final Savings**", f"${results.get('final_savings', 0):,.2f}")
    with col3:
        st.metric("**Final Net Worth**", f"${results.get('final_net_worth', 0):,.2f}")
    with col4:
        st.metric("**Health Score**", f"{results.get('health_score', 0)}/100")

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

def display_health_dashboard(emergency_months, dti, savings_rate, health_score):
    """Display the financial health metrics in a dashboard format."""
    # Add help button for this dashboard
    from utils.chart_tooltips import add_chart_help_button
    add_chart_help_button("health_dashboard")

    st.subheader("Financial Health Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Emergency Fund", f"{emergency_months:.1f} months")
    col2.metric("Debt-to-Income", f"{dti:.2f}")
    col3.metric("Savings Rate", f"{savings_rate * 100:.1f}%")
    col4.metric("Health Score", f"{health_score}/100")