# basic_analysis.py - Health dashboard, goals (split, ~200 lines)
import streamlit as st
from datetime import date
import pandas as pd  # ADDED: Missing import for pd.DataFrame
from financial_utils import calculate_health_score  # Absolute

def run_simple_fallback_simulation(user_data, financial_data, family_data, sim_params):
    start_year = date.today().year
    years = list(range(start_year, start_year + sim_params['simulation_years']))
    
    current_savings = financial_data['liquid_assets']
    savings_trajectory = []
    income_trajectory = []
    expense_trajectory = []
    net_worth_trajectory = []
    inheritance_trajectory = []
    
    inheritance_events = {}
    if family_data and 'inheritances' in family_data:
        for inh in family_data['inheritances']:
            if inh.get('Amount', 0) > 0:
                inheritance_events[inh.get('Year', start_year)] = inh['Amount']
    
    for year_idx in range(sim_params['simulation_years']):
        annual_income = financial_data['total_income'] * 12 * (1 + sim_params['inflation_rate']/100) ** year_idx
        annual_expenses = financial_data['total_expenses'] * 12 * (1 + sim_params['inflation_rate']/100) ** year_idx
        inheritance = inheritance_events.get(start_year + year_idx, 0)
        net_flow = annual_income - annual_expenses + inheritance
        current_savings = current_savings * (1 + sim_params['investment_return_rate']/100) + net_flow
        current_savings = max(0, current_savings)
        
        savings_trajectory.append(current_savings)
        income_trajectory.append(annual_income)
        expense_trajectory.append(annual_expenses)
        net_worth_trajectory.append(current_savings + financial_data.get('primary_residence_value', 0) + financial_data.get('secondary_residence_value', 0) + financial_data.get('other_assets', 0) - financial_data['total_liabilities'])
        inheritance_trajectory.append(inheritance)
    
    final_savings = savings_trajectory[-1] if savings_trajectory else 0
    years_solvent = sum(1 for s in savings_trajectory if s > 0)
    final_net_worth = net_worth_trajectory[-1] if net_worth_trajectory else 0
    
    df = pd.DataFrame({
        'Year': years,
        'Total_Income': income_trajectory,
        'Total_Expenses': expense_trajectory,
        'Savings_End': savings_trajectory,
        'Net_Worth': net_worth_trajectory,
        'Inheritance_Inflow': inheritance_trajectory
    })
    
    emergency_months = financial_data['liquid_assets'] / (financial_data['total_expenses'] * 12) if financial_data['total_expenses'] > 0 else 0
    dti = financial_data['total_liabilities'] / (financial_data['total_income'] * 12) if financial_data['total_income'] > 0 else 0
    savings_rate = financial_data['monthly_surplus'] / financial_data['total_income'] if financial_data['total_income'] > 0 else 0
    health_score = calculate_health_score(emergency_months, dti, savings_rate, final_savings > 0)
    
    goal_achievement = {}
    for goal, data in financial_data.get('goal_costs', {}).items():
        year_index = data['year'] - start_year
        if 0 <= year_index < sim_params['simulation_years']:
            actual = savings_trajectory[year_index]
            achieved = actual >= data['amount']
            goal_achievement[goal] = {'target': data['amount'], 'year': data['year'], 'actual': actual, 'achieved': achieved}
        else:
            goal_achievement[goal] = {'target': data['amount'], 'year': data['year'], 'actual': 0, 'achieved': False}
    
    return {
        'df': df,
        'years_solvent': years_solvent,
        'final_savings': final_savings,
        'final_net_worth': final_net_worth,
        'emergency_fund_months': emergency_months,
        'debt_to_income': dti,
        'savings_rate': savings_rate,
        'health_score': health_score,
        'goal_achievement': goal_achievement
    }

def calculate_simple_health_score(emergency_months, dti, savings_rate, is_solvent=True):
    # Wrapper for calculate_health_score (matches params, clamps to 0-100)
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
    if is_solvent:
        score += 20
    return min(100, max(0, score))