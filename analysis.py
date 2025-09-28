# analysis.py - Analysis and Scenario Comparison Module
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

def run_enhanced_simulation_with_inheritance(user_data, financial_data, family_data, sim_params):
    """
    Enhanced simulation that properly incorporates inheritance events
    """
    years = sim_params['simulation_years']
    age = user_data['age']
    current_year = date.today().year
    
    # Initialize arrays
    savings_balance = [financial_data['liquid_assets']]
    net_worth = [financial_data['liquid_assets'] + financial_data['primary_residence_value'] + financial_data['secondary_residence_value'] - financial_data['total_liabilities']]
    annual_income = [financial_data['total_income'] * 12]
    annual_expenses = [financial_data['total_expenses'] * 12]
    
    # Process inheritance events into year-indexed dictionary - FIX 'amount' ERROR
    inheritance_by_year = {}
    if family_data and 'inheritances' in family_data:
        for inheritance in family_data['inheritances']:
            # FIX: Handle both 'Amount' and 'amount' keys safely
            amount = 0
            if 'Amount' in inheritance:
                amount = inheritance['Amount']
            elif 'amount' in inheritance:
                amount = inheritance['amount']
            else:
                continue  # Skip if no amount found
                
            # Convert to float safely
            try:
                amount = float(amount)
                if amount <= 0:
                    continue
            except (ValueError, TypeError):
                continue  # Skip invalid amounts
            
            # Get year safely
            year = inheritance.get('Year', inheritance.get('year', current_year))
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = current_year
                
            if year not in inheritance_by_year:
                inheritance_by_year[year] = 0
            inheritance_by_year[year] += amount
        
        # Debug output - but only if we found valid inheritances
        if inheritance_by_year:
            st.write(f"🎯 **INHERITANCE PROCESSING**: Found {len(inheritance_by_year)} years with inheritance events")
            for year, amount in inheritance_by_year.items():
                st.write(f"  • Year {year}: ${amount:,}")
    
    # Simple projection logic
    annual_surplus = financial_data['monthly_surplus'] * 12
    investment_return = sim_params['investment_return_rate'] / 100
    inflation_rate = sim_params['inflation_rate'] / 100
    
    current_savings = financial_data['liquid_assets']
    current_expenses = financial_data['total_expenses'] * 12
    current_income = financial_data['total_income'] * 12
    
    for year in range(1, years + 1):
        projection_year = current_year + year
        
        # Apply inflation to expenses
        current_expenses *= (1 + inflation_rate)
        
        # Apply investment returns to existing savings
        current_savings *= (1 + investment_return)
        
        # Add annual surplus (adjusted for inflation)
        real_surplus = annual_surplus * ((1 + inflation_rate) ** year)
        current_savings += real_surplus
        
        # ADD INHERITANCE EVENT - THIS WAS THE MISSING PIECE!
        if projection_year in inheritance_by_year:
            inheritance_amount = inheritance_by_year[projection_year]
            current_savings += inheritance_amount
            st.write(f"💰 **INHERITANCE APPLIED**: Year {projection_year} - Added ${inheritance_amount:,}")
        
        # Store values
        savings_balance.append(max(0, current_savings))
        annual_income.append(current_income * ((1 + inflation_rate) ** year))
        annual_expenses.append(current_expenses)
        
        # Enhanced net worth calculation including inheritance
        home_value = financial_data['primary_residence_value'] * ((1 + inflation_rate) ** year)
        net_worth.append(current_savings + home_value - financial_data['total_liabilities'])
    
    # Create DataFrame
    years_array = list(range(current_year, current_year + years + 1))
    df = pd.DataFrame({
        'Year': years_array,
        'Savings End': savings_balance,
        'Net Worth': net_worth,
        'Total Income': annual_income,
        'Total Expenses': annual_expenses
    })
    
    # Count solvent years
    years_positive = sum(1 for x in savings_balance if x > 0)
    
    # Add inheritance impact summary
    total_inheritance = sum(inheritance_by_year.values()) if inheritance_by_year else 0
    
    return {
        'df': df,
        'final_savings': savings_balance[-1],
        'final_net_worth': net_worth[-1],
        'years_solvent': years_positive,
        'years_positive': years_positive,
        'inheritance_total': total_inheritance,
        'inheritance_events': len(inheritance_by_year),
        'inheritance_years': list(inheritance_by_year.keys())
    }

def run_scenario_comparison(user_data, financial_data, sim_params, base_results):
    """
    Run scenario comparisons with different parameters
    """
    st.subheader("🔄 Scenario Comparison Tool")
    
    st.markdown("**Adjust parameters to see impact on your financial future:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        adj_income = st.slider(
            "Income Adjustment (%)",
            min_value=-50, max_value=100, value=0, step=5,
            help="Adjust monthly income by percentage"
        )
        
    with col2:
        adj_expenses = st.slider(
            "Expense Adjustment (%)", 
            min_value=-50, max_value=50, value=0, step=5,
            help="Adjust monthly expenses by percentage"
        )
        
    with col3:
        adj_return = st.slider(
            "Return Rate Adjustment (%)",
            min_value=-5.0, max_value=5.0, value=0.0, step=0.5,
            help="Adjust investment return rate"
        )
    
    # Apply adjustments
    if adj_income != 0 or adj_expenses != 0 or adj_return != 0:
        adjusted_financial_data = financial_data.copy()
        adjusted_sim_params = sim_params.copy()
        
        # Adjust income and expenses
        adjusted_financial_data['total_income'] *= (1 + adj_income/100)
        adjusted_financial_data['total_expenses'] *= (1 + adj_expenses/100)
        adjusted_financial_data['monthly_surplus'] = adjusted_financial_data['total_income'] - adjusted_financial_data['total_expenses']
        
        # Adjust return rate
        adjusted_sim_params['investment_return_rate'] += adj_return
        
        # Run adjusted simulation
        adj_results = run_simple_simulation(user_data, adjusted_financial_data, adjusted_sim_params)
        
        # Show comparison metrics
        col1, col2, col3 = st.columns(3)
        
        base_final = base_results.get('final_savings', 0)
        adj_final = adj_results.get('final_savings', 0)
        difference = adj_final - base_final
        
        with col1:
            st.metric("Base Scenario", f"${base_final:,.0f}")
        with col2:
            st.metric("Adjusted Scenario", f"${adj_final:,.0f}")
        with col3:
            delta_color = "normal" if difference >= 0 else "inverse"
            st.metric("Difference", f"${adj_final:,.0f}", f"${difference:,.0f}")
        
        return adj_results
    
    return None

def analyze_inheritance_impact(family_data, financial_data, sim_params):
    """
    Analyze the impact of inheritance events
    """
    if not family_data or 'inheritances' not in family_data:
        return {}
    
    inheritances = family_data['inheritances']
    current_year = date.today().year
    
    inheritance_impact = {}
    total_inheritance = 0
    
    for inheritance in inheritances:
        if inheritance.get('Amount', 0) > 0:
            year = inheritance.get('Year', current_year)
            amount = inheritance['Amount']
            years_from_now = year - current_year
            
            # Calculate present value impact
            discount_rate = sim_params.get('investment_return_rate', 7) / 100
            present_value = amount / ((1 + discount_rate) ** years_from_now) if years_from_now > 0 else amount
            
            inheritance_impact[year] = {
                'amount': amount,
                'years_from_now': years_from_now,
                'present_value': present_value,
                'description': inheritance.get('Description', f'Inheritance {year}')
            }
            
            total_inheritance += amount
    
    return {
        'events': inheritance_impact,
        'total_amount': total_inheritance,
        'total_present_value': sum(event['present_value'] for event in inheritance_impact.values())
    }

def create_stress_scenarios(base_results, financial_data, sim_params):
    """
    Create stress test scenarios
    """
    stress_scenarios = {}
    
    # Market crash scenario
    stress_params = sim_params.copy()
    stress_params['investment_return_rate'] = max(0, stress_params['investment_return_rate'] - 3)
    
    # High inflation scenario  
    inflation_params = sim_params.copy()
    inflation_params['inflation_rate'] = min(10, inflation_params['inflation_rate'] + 4)
    
    # Job loss scenario
    job_loss_data = financial_data.copy()
    job_loss_data['total_income'] *= 0.5  # 50% income reduction
    job_loss_data['monthly_surplus'] = job_loss_data['total_income'] - job_loss_data['total_expenses']
    
    return {
        'market_crash': stress_params,
        'high_inflation': inflation_params, 
        'job_loss': job_loss_data
    }