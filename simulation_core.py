# simulation_core.py - FIXED: Now uses actual total_income and total_expenses parameters + Custom_Expenses column
import pandas as pd
import numpy as np
from datetime import date
import streamlit as st
from household_events import build_child_objects, build_inheritances, make_family_cashflows
from financial_utils import safe_float, safe_int
from visualization.irmaa_analysis import calculate_magi, get_irmaa_bracket  # Added for IRMAA

# 2025 Tax Brackets (Single/Joint) - Update annually
TAX_BRACKETS_2025 = {
    'single': [
        {'min': 0, 'max': 11600, 'rate': 0.10},
        {'min': 11600, 'max': 47150, 'rate': 0.12},
        {'min': 47150, 'max': 100525, 'rate': 0.22},
        {'min': 100525, 'max': 191950, 'rate': 0.24},
        {'min': 191950, 'max': 243725, 'rate': 0.32},
        {'min': 243725, 'max': 609350, 'rate': 0.35},
        {'min': 609350, 'max': float('inf'), 'rate': 0.37}
    ],
    'joint': [
        {'min': 0, 'max': 23200, 'rate': 0.10},
        {'min': 23200, 'max': 94300, 'rate': 0.12},
        {'min': 94300, 'max': 201050, 'rate': 0.22},
        {'min': 201050, 'max': 383900, 'rate': 0.24},
        {'min': 383900, 'max': 487450, 'rate': 0.32},
        {'min': 487450, 'max': 731200, 'rate': 0.35},
        {'min': 731200, 'max': float('inf'), 'rate': 0.37}
    ]
}

# 2025 IRMAA Brackets (Single/Joint)
IRMAA_BRACKETS_2025 = {
    'single': [
        {'min': 0, 'max': 103000, 'surcharge_monthly': 0},
        {'min': 103000, 'max': 129000, 'surcharge_monthly': 14.50},
        {'min': 129000, 'max': 161000, 'surcharge_monthly': 36.20},
        {'min': 161000, 'max': 193000, 'surcharge_monthly': 58.00},
        {'min': 193000, 'max': 500000, 'surcharge_monthly': 63.10},
        {'min': 500000, 'max': float('inf'), 'surcharge_monthly': 68.30}
    ],
    'joint': [
        {'min': 0, 'max': 206000, 'surcharge_monthly': 0},
        {'min': 206000, 'max': 258000, 'surcharge_monthly': 14.50},
        {'min': 258000, 'max': 322000, 'surcharge_monthly': 36.20},
        {'min': 322000, 'max': 386000, 'surcharge_monthly': 58.00},
        {'min': 386000, 'max': 750000, 'surcharge_monthly': 63.10},
        {'min': 750000, 'max': float('inf'), 'surcharge_monthly': 68.30}
    ]
}

def calculate_taxes(income, filing_status='joint'):
    """Calculate federal taxes based on brackets"""
    brackets = TAX_BRACKETS_2025[filing_status]
    tax = 0
    for bracket in brackets:
        if income > bracket['min']:
            taxable_in_bracket = min(income, bracket['max']) - bracket['min']
            tax += taxable_in_bracket * bracket['rate']
        if income <= bracket['max']:
            break
    return tax

def optimize_roth_conversions(year_idx, current_magi, ira_balance, roth_conversion_annual, filing_status='joint'):
    """
    Optimize Roth conversion amount to fill lower tax brackets without jumping IRMAA tiers.
    Returns optimal conversion amount for the year.
    """
    if ira_balance <= 0 or roth_conversion_annual <= 0:
        return 0
    
    # Target: Fill up to next bracket or IRMAA threshold, up to user max
    max_conversion = min(ira_balance, roth_conversion_annual)
    
    # Get current tax bracket and next threshold
    brackets = TAX_BRACKETS_2025[filing_status]
    current_bracket_idx = next((i for i, b in enumerate(brackets) if b['min'] <= current_magi <= b['max']), len(brackets)-1)
    next_bracket_min = brackets[current_bracket_idx]['max'] if current_bracket_idx < len(brackets)-1 else float('inf')
    
    # Get next IRMAA threshold
    irmaa_brackets = IRMAA_BRACKETS_2025[filing_status]
    current_irmaa_idx = next((i for i, b in enumerate(irmaa_brackets) if b['min'] <= current_magi <= b['max']), 0)
    next_irmaa_min = irmaa_brackets[current_irmaa_idx + 1]['min'] if current_irmaa_idx < len(irmaa_brackets)-1 else float('inf')
    
    # Safe conversion: Min of next tax/IRMAA threshold, minus current MAGI
    safe_to_next_tax = max(0, next_bracket_min - current_magi)
    safe_to_next_irmaa = max(0, next_irmaa_min - current_magi)
    optimal = min(max_conversion, safe_to_next_tax, safe_to_next_irmaa)
    
    # Simulate tax savings: Compare tax now vs future (assume future rate 24%)
    current_tax = calculate_taxes(current_magi + optimal) - calculate_taxes(current_magi)
    future_tax_saved = optimal * 0.24  # Assumed future bracket
    if current_tax >= future_tax_saved:
        optimal = 0  # Not worth it if current tax > future savings
    
    return max(0, optimal)

def run_simulation(age, partner_exists, partner_age, total_income, total_expenses, combined_financial_assets, primary_residence_value, secondary_residence_value, combined_other_assets_total, total_liabilities_local, partner_liabilities, tax_rate, inflation_rate, investment_return_rate, simulation_years, mc_iterations, goal_costs, college_inflation_pct, base_public_in, base_public_out, base_private, ira_balance, four01k_403b_balance, partner_ira_balance, partner_four01k_403b_balance, monthly_surplus, combined_total_liabilities, roth_conversion_annual=0, itemize_deductions=True, five29_plan_balance=0.0, tax_exempt_interest=0.0, custom_expenses_total=0.0):
    
    # Initialize results dictionary at the start
    results = {
        'df': None,
        'years_solvent': 0,
        'final_savings': 0,
        'final_net_worth': 0,
        'emergency_fund_months': 0,
        'debt_to_income': 0,
        'savings_rate': 0,
        'health_score': 0,
        'goal_achievement': {}
    }
    
    try:
        # NaN guards with defaults
        age = safe_int(age, 35)
        simulation_years = safe_int(simulation_years, 30)
        partner_age = safe_int(partner_age, age)
        
        # CRITICAL FIX: Store the ACTUAL passed parameters
        base_total_income = safe_float(total_income)
        base_total_expenses = safe_float(total_expenses)
        
        combined_financial_assets = safe_float(combined_financial_assets)
        primary_residence_value = safe_float(primary_residence_value)
        secondary_residence_value = safe_float(secondary_residence_value)
        combined_other_assets_total = safe_float(combined_other_assets_total)
        total_liabilities_local = safe_float(total_liabilities_local)
        partner_liabilities = safe_float(partner_liabilities)
        tax_rate = safe_float(tax_rate, 22.0)
        inflation_rate = safe_float(inflation_rate, 3.0)
        investment_return_rate = safe_float(investment_return_rate, 7.0)
        mc_iterations = safe_int(mc_iterations, 0)
        college_inflation_pct = safe_float(college_inflation_pct, 4.0)
        base_public_in = safe_float(base_public_in, 20000.0)
        base_public_out = safe_float(base_public_out, 40000.0)
        base_private = safe_float(base_private, 60000.0)
        ira_balance = safe_float(ira_balance)
        four01k_403b_balance = safe_float(four01k_403b_balance)
        partner_ira_balance = safe_float(partner_ira_balance)
        partner_four01k_403b_balance = safe_float(partner_four01k_403b_balance)
        
        tax_exempt_interest = safe_float(tax_exempt_interest, 0.0)  # Added for MAGI
        custom_expenses_total = safe_float(custom_expenses_total, 0.0)  # Added for custom expenses
        
        # Track retirement balances for RMD calculations
        user_retirement_balance = ira_balance + four01k_403b_balance
        partner_retirement_balance = partner_ira_balance + partner_four01k_403b_balance
        
        monthly_surplus = safe_float(monthly_surplus)
        combined_total_liabilities = safe_float(combined_total_liabilities)
        five29_plan_balance = safe_float(five29_plan_balance)

        # Family events
        children = build_child_objects(st.session_state.get("children_rows", []))
        inheritances = build_inheritances(st.session_state.get("inherit_rows", []))
        start_year = date.today().year
        horizon_end = start_year + simulation_years - 1
        family_cashflows = make_family_cashflows(
            children, inheritances, start_year, horizon_end, college_inflation_pct,
            base_public_in, base_public_out, base_private
        )

        # Initialize lists for all columns in LOGICAL ORDER
        years = list(range(start_year, start_year + simulation_years))
        
        # Basic info
        year_list = years
        age_list = [age + i for i in range(simulation_years)]
        partner_age_list = [partner_age + i for i in range(simulation_years)] if partner_exists else [0] * simulation_years
        
        # Income components
        total_income_list = []
        salary_wages_list = []
        rental_income_list = []
        investment_income_list = []
        social_security_list = []
        pension_income_list = []
        other_income_list = []
        
        # RMD calculations (SEPARATED)
        user_rmd_list = []
        partner_rmd_list = []
        total_rmd_list = []
        
        # Roth conversions (Added)
        roth_conversion_list = []
        
        # Expense components
        total_expenses_list = []
        housing_expenses_list = []
        utilities_list = []
        groceries_list = []
        transportation_list = []
        healthcare_list = []
        insurance_list = []
        entertainment_list = []
        travel_list = []
        other_expenses_list = []
        custom_expenses_list = []
        
        # Special expenses
        college_expenses_list = []
        inheritance_inflow_list = []
        
        # Net calculations
        taxes_paid_list = []
        net_income_before_special_list = []
        net_income_after_special_list = []
        
        # Savings and assets
        savings_start_list = []
        investment_return_list = []
        savings_end_list = []
        total_assets_list = []
        total_liabilities_list = []
        net_worth_list = []
        
        # Goal tracking
        goal_progress_list = []
        
        # IRMAA costs (Added for IRMAA)
        irmaa_cost_list = []
        
        # RMD factors (IRS Uniform Lifetime Table)
        rmd_factors = {
            73: 27.4, 74: 26.5, 75: 25.5, 76: 24.6, 77: 23.7, 
            78: 22.9, 79: 22.0, 80: 21.1, 81: 20.2, 82: 19.4,
            83: 18.5, 84: 17.7, 85: 16.8, 86: 16.0, 87: 15.2,
            88: 14.4, 89: 13.7, 90: 12.9, 91: 12.2, 92: 11.5,
            93: 10.8, 94: 10.1, 95: 9.5, 96: 8.9, 97: 8.4,
            98: 7.8, 99: 7.3, 100: 6.8
        }
        
        # Initial savings
        current_savings = combined_financial_assets

        # CRITICAL FIX: Use actual income/expenses
        savings = combined_financial_assets
        five29_balance = five29_plan_balance
        
        for year_idx in range(simulation_years):
            year = start_year + year_idx
            user_age = age + year_idx
            partner_age = partner_age + year_idx if partner_exists else 0
            
            # Initialize annual values
            annual_income = base_total_income * (1 + inflation_rate / 100) ** year_idx
            annual_expenses = base_total_expenses * (1 + inflation_rate / 100) ** year_idx
            
            # Income components (simplified - use total income for now)
            salary_wages = annual_income * 0.5  # Placeholder
            rental_income = annual_income * 0.1
            investment_income = annual_income * 0.1
            social_security = annual_income * 0.2
            pension_income = annual_income * 0.05
            other_income = annual_income * 0.05
            
            # RMD calculations
            user_rmd = 0
            partner_rmd = 0
            if user_age >= 73 and user_retirement_balance > 0:
                factor = rmd_factors.get(user_age, 27.4)
                user_rmd = user_retirement_balance / factor
                user_retirement_balance -= user_rmd

            if partner_exists and partner_age >= 73 and partner_retirement_balance > 0:
                factor = rmd_factors.get(partner_age, 27.4)
                partner_rmd = partner_retirement_balance / factor
                partner_retirement_balance -= partner_rmd
            
            total_rmd = user_rmd + partner_rmd
            
            # Total income including RMDs
            total_income = salary_wages + rental_income + investment_income + social_security + pension_income + other_income + total_rmd
            
            # Expense components (simplified - use total expenses for now)
            housing_expenses = annual_expenses * 0.3
            utilities = annual_expenses * 0.1
            groceries = annual_expenses * 0.1
            transportation = annual_expenses * 0.1
            healthcare = annual_expenses * 0.15
            insurance = annual_expenses * 0.1
            entertainment = annual_expenses * 0.05
            travel = annual_expenses * 0.05
            other_expenses = annual_expenses * 0.05
            custom_expenses = custom_expenses_total * 12 * (1 + inflation_rate / 100) ** year_idx
            
            # Family events (college, inheritances)
            family_expense = family_cashflows.get(year, {}).get('expense_delta', 0.0)
            family_inflow = family_cashflows.get(year, {}).get('inflow_delta', 0.0)
            
            # Apply 529 plan for college expenses
            if family_expense > 0 and five29_balance > 0:
                from_529 = min(five29_balance, family_expense)
                five29_balance -= from_529
                family_expense -= from_529
            
            # Total expenses including college
            total_expenses = housing_expenses + utilities + groceries + transportation + healthcare + insurance + entertainment + travel + other_expenses + custom_expenses + family_expense
            
            # Taxes and IRMAA
            filing_status = 'joint' if partner_exists else 'single'
            magi = calculate_magi(total_income, tax_exempt_interest)
            
            # Optimized Roth conversion
            roth_conversion = 0
            if roth_conversion_annual > 0 and year_idx >= (65 - age):
                roth_conversion = optimize_roth_conversions(year_idx, magi, ira_balance, roth_conversion_annual, filing_status)
                if roth_conversion > 0:
                    ira_balance -= roth_conversion
                    magi += roth_conversion
                    user_retirement_balance -= roth_conversion
            
            taxes_paid = calculate_taxes(magi, filing_status)
            irmaa_bracket = get_irmaa_bracket(magi, filing_status)
            irmaa_cost = irmaa_bracket['surcharge_monthly'] * 12 * (2 if partner_exists else 1)
            
            # Net calculations
            net_before_special = total_income - total_expenses - taxes_paid
            net_after_special = net_before_special - family_expense + family_inflow - irmaa_cost
            
            # Savings and investment returns
            savings_start = savings
            savings += net_after_special
            investment_return = savings * (investment_return_rate / 100)
            savings += investment_return
            savings = max(0, savings)
            
            # Assets and net worth
            total_assets = savings + primary_residence_value * (1 + 2.0 / 100) ** year_idx + \
                          secondary_residence_value * (1 + 2.0 / 100) ** year_idx + \
                          combined_other_assets_total
            net_worth = total_assets - combined_total_liabilities
            
            # Goal progress
            goal_progress = {}
            for goal, data in goal_costs.items():
                if data['year'] == year:
                    actual = savings
                    achieved = actual >= data['amount']
                    goal_progress[goal] = {
                        'target': data['amount'],
                        'year': data['year'],
                        'actual': actual,
                        'achieved': achieved
                    }
            
            # Store results
            total_income_list.append(total_income)
            salary_wages_list.append(salary_wages)
            rental_income_list.append(rental_income)
            investment_income_list.append(investment_income)
            social_security_list.append(social_security)
            pension_income_list.append(pension_income)
            other_income_list.append(other_income)
            
            user_rmd_list.append(user_rmd)
            partner_rmd_list.append(partner_rmd)
            total_rmd_list.append(total_rmd)
            
            roth_conversion_list.append(roth_conversion)
            
            total_expenses_list.append(total_expenses)
            housing_expenses_list.append(housing_expenses)
            utilities_list.append(utilities)
            groceries_list.append(groceries)
            transportation_list.append(transportation)
            healthcare_list.append(healthcare)
            insurance_list.append(insurance)
            entertainment_list.append(entertainment)
            travel_list.append(travel)
            other_expenses_list.append(other_expenses)
            custom_expenses_list.append(custom_expenses)
            
            college_expenses_list.append(family_expense)
            inheritance_inflow_list.append(family_inflow)
            
            taxes_paid_list.append(taxes_paid)
            net_income_before_special_list.append(net_before_special)
            net_income_after_special_list.append(net_after_special)
            
            savings_start_list.append(savings_start)
            investment_return_list.append(investment_return)
            savings_end_list.append(savings)
            total_assets_list.append(total_assets)
            total_liabilities_list.append(combined_total_liabilities)
            net_worth_list.append(net_worth)
            
            goal_progress_list.append(goal_progress)
            
            irmaa_cost_list.append(irmaa_cost)
        
        # Create DataFrame
        df_data = {
            'Year': year_list,
            'User_Age': age_list,
            'Partner_Age': partner_age_list,
            
            'Salary_Wages': salary_wages_list,
            'Rental_Income': rental_income_list,
            'Investment_Income': investment_income_list,
            'Social_Security': social_security_list,
            'Pension_Income': pension_income_list,
            'Other_Income': other_income_list,
            'Base_Income_Subtotal': [salary_wages_list[i] + rental_income_list[i] + investment_income_list[i] + 
                                    social_security_list[i] + pension_income_list[i] + other_income_list[i] 
                                    for i in range(simulation_years)],
            
            'User_RMD': user_rmd_list,
            'Partner_RMD': partner_rmd_list,
            'Total_RMD': total_rmd_list,
            
            'Roth_Conversion': roth_conversion_list,
            
            'Total_Income': total_income_list,
            
            'Housing_Expenses': housing_expenses_list,
            'Utilities': utilities_list,
            'Groceries': groceries_list,
            'Transportation': transportation_list,
            'Healthcare': healthcare_list,
            'Insurance': insurance_list,
            'Entertainment': entertainment_list,
            'Travel': travel_list,
            'Other_Expenses': other_expenses_list,
            'Custom_Expenses': custom_expenses_list,
            'Base_Expenses_Subtotal': [housing_expenses_list[i] + utilities_list[i] + groceries_list[i] + 
                                      transportation_list[i] + healthcare_list[i] + insurance_list[i] + 
                                      entertainment_list[i] + travel_list[i] + other_expenses_list[i] + 
                                      custom_expenses_list[i] 
                                      for i in range(simulation_years)],
            
            'College_Expenses': college_expenses_list,
            'Inheritance_Inflow': inheritance_inflow_list,
            
            'IRMAA_Annual_Cost': irmaa_cost_list,
            
            'Total_Expenses': total_expenses_list,
            
            'Taxes_Paid': taxes_paid_list,
            'Net_Income_Before_Special': net_income_before_special_list,
            'Net_Income_After_Special': net_income_after_special_list,
            
            'Savings_Start': savings_start_list,
            'Investment_Return': investment_return_list,
            'Savings_End': savings_end_list,
            'Total_Assets': total_assets_list,
            'Total_Liabilities': total_liabilities_list,
            'Net_Worth': net_worth_list,
            
            'Goal_Progress': goal_progress_list
        }
        
        df = pd.DataFrame(df_data)
        
        # Calculate metrics
        final_savings = df['Savings_End'].iloc[-1]
        years_solvent = sum(1 for s in df['Savings_End'] if s > 0)
        final_net_worth = df['Net_Worth'].iloc[-1]
        
        emergency_months = combined_financial_assets / base_total_expenses if base_total_expenses > 0 else 0
        dti = combined_total_liabilities / base_total_income if base_total_income > 0 else 0
        savings_rate = monthly_surplus / base_total_income if base_total_income > 0 else 0
        
        health_score = 0
        if emergency_months >= 6:
            health_score += 30
        elif emergency_months >= 3:
            health_score += 20
        if dti <= 0.36:
            health_score += 30
        elif dti <= 0.5:
            health_score += 20
        if savings_rate >= 0.2:
            health_score += 20
        elif savings_rate >= 0.1:
            health_score += 10
        if final_savings > 0:
            health_score += 20
        
        goal_achievement = {}
        for goal, data in goal_costs.items():
            year_index = data['year'] - start_year
            if 0 <= year_index < simulation_years:
                actual = df['Savings_End'].iloc[year_index]
                achieved = actual >= data['amount']
                goal_achievement[goal] = {
                    'target': data['amount'], 
                    'year': data['year'], 
                    'actual': actual, 
                    'achieved': achieved
                }
        
        results.update({
            'df': df,
            'years_solvent': years_solvent,
            'final_savings': final_savings,
            'final_net_worth': final_net_worth,
            'emergency_fund_months': emergency_months,
            'debt_to_income': dti,
            'savings_rate': savings_rate,
            'health_score': health_score,
            'goal_achievement': goal_achievement
        })

        # Monte Carlo if requested
        if mc_iterations > 0:
            try:
                from monte_carlo import run_simple_monte_carlo
                mc_results = run_simple_monte_carlo(
                    {'total_income': base_total_income, 'total_expenses': base_total_expenses, 'liquid_assets': combined_financial_assets},
                    {'simulation_years': simulation_years, 'investment_return_rate': investment_return_rate, 'inflation_rate': inflation_rate, 'mc_iterations': mc_iterations},
                    family_cashflows
                )
                results['monte_carlo_results'] = mc_results
            except Exception as mc_error:
                st.warning(f"Monte Carlo simulation failed: {str(mc_error)}")
        
        return results

    except Exception as e:
        st.error(f"Simulation error: {str(e)}")
        return results