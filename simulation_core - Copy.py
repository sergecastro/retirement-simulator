# simulation_core.py - FIXED: Now uses actual total_income and total_expenses parameters
import pandas as pd
import numpy as np
from datetime import date
import streamlit as st
from household_events import build_child_objects, build_inheritances, make_family_cashflows
from financial_utils import safe_float, safe_int
from visualization.irmaa_analysis import calculate_magi, get_irmaa_bracket  # Added for IRMAA

def run_simulation(age, partner_exists, partner_age, total_income, total_expenses, combined_financial_assets, primary_residence_value, secondary_residence_value, combined_other_assets_total, total_liabilities_local, partner_liabilities, tax_rate, inflation_rate, investment_return_rate, simulation_years, mc_iterations, goal_costs, college_inflation_pct, base_public_in, base_public_out, base_private, ira_balance, four01k_403b_balance, partner_ira_balance, partner_four01k_403b_balance, monthly_surplus, combined_total_liabilities, roth_conversion_annual=0, itemize_deductions=True, five29_plan_balance=0.0, tax_exempt_interest=0.0):
    
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
        
        # Track retirement balances for RMD calculations
        user_retirement_balance = ira_balance + four01k_403b_balance
        partner_retirement_balance = partner_ira_balance + partner_four01k_403b_balance
        
        # DEBUG OUTPUT
        print(f"\n{'='*60}")
        print(f"🔍 SIMULATION PARAMETERS")
        print(f"{'='*60}")
        print(f"Total Income (Monthly): ${base_total_income:,.2f}")
        print(f"Total Expenses (Monthly): ${base_total_expenses:,.2f}")
        print(f"Partner Exists: {partner_exists}")
        print(f"Partner Age: {partner_age}")
        print(f"Partner Total Retirement: ${partner_retirement_balance:,.2f}")
        print(f"User Age: {age}")
        print(f"User Total Retirement: ${user_retirement_balance:,.2f}")
        print(f"{'='*60}\n")
        
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
        
        # Track first RMD for debug
        first_user_rmd_logged = False
        first_partner_rmd_logged = False
        
        # CRITICAL FIX: Define income/expense distribution proportions
        # These proportions allow us to break down total_income and total_expenses
        # Default proportions (can be customized if needed)
        income_proportions = {
            'salary': 0.0,
            'rental': 0.15,
            'investment': 0.05,
            'social_security': 0.30,
            'pension': 0.50,
            'other': 0.0
        }
        
        expense_proportions = {
            'housing': 0.0,
            'utilities': 0.08,
            'groceries': 0.14,
            'transportation': 0.05,
            'healthcare': 0.25,
            'insurance': 0.13,
            'entertainment': 0.08,
            'travel': 0.13,
            'other': 0.14
        }
        
        for year_idx in range(simulation_years):
            current_year = start_year + year_idx
            current_age = age + year_idx
            current_partner_age = partner_age + year_idx if partner_exists else 0
            
            # Inflation adjustment
            inf_factor = (1 + inflation_rate/100) ** year_idx
            
            # =========================
            # INCOME CALCULATIONS - FIXED TO USE ACTUAL PARAMETERS
            # =========================
            
            # CRITICAL FIX: Use the ACTUAL total_income parameter and distribute proportionally
            annual_base_income = base_total_income * 12 * inf_factor
            
            # Distribute income across components using proportions
            salary = annual_base_income * income_proportions['salary']
            rental = annual_base_income * income_proportions['rental']
            investment = annual_base_income * income_proportions['investment']
            ss = annual_base_income * income_proportions['social_security']
            pension = annual_base_income * income_proportions['pension']
            other = annual_base_income * income_proportions['other']
            
            base_income = salary + rental + investment + ss + pension + other
            
            # =========================
            # RMD CALCULATIONS (SEPARATED WITH DEBUG)
            # =========================
            
            # User RMD
            user_rmd = 0.0
            if current_age >= 73 and user_retirement_balance > 0:
                rmd_divisor = rmd_factors.get(current_age, 20.0)
                user_rmd = user_retirement_balance / rmd_divisor
                user_retirement_balance = max(0, user_retirement_balance - user_rmd)
                
                if not first_user_rmd_logged:
                    print(f"✅ USER RMD STARTED - Year {current_year}, Age {current_age}")
                    print(f"   Balance: ${user_retirement_balance + user_rmd:,.2f}")
                    print(f"   Divisor: {rmd_divisor}")
                    print(f"   RMD Amount: ${user_rmd:,.2f}\n")
                    first_user_rmd_logged = True
            
            # Partner RMD
            partner_rmd = 0.0
            if partner_exists and current_partner_age >= 73 and partner_retirement_balance > 0:
                rmd_divisor = rmd_factors.get(current_partner_age, 20.0)
                partner_rmd = partner_retirement_balance / rmd_divisor
                partner_retirement_balance = max(0, partner_retirement_balance - partner_rmd)
                
                if not first_partner_rmd_logged:
                    print(f"💰 PARTNER RMD STARTED - Year {current_year}, Age {current_partner_age}")
                    print(f"   Balance: ${partner_retirement_balance + partner_rmd:,.2f}")
                    print(f"   Divisor: {rmd_divisor}")
                    print(f"   RMD Amount: ${partner_rmd:,.2f}\n")
                    first_partner_rmd_logged = True
            
            total_rmd = user_rmd + partner_rmd
            
            # Total income including RMD
            total_income_year = base_income + total_rmd
            
            # NEW: Calculate MAGI and IRMAA costs
            magi = calculate_magi(total_income_year, tax_exempt_interest)
            filing_status = 'joint' if partner_exists else 'single'
            irmaa_bracket = get_irmaa_bracket(magi, filing_status)
            irmaa_cost = irmaa_bracket['surcharge_monthly'] * 12  # Annual Part B surcharge
            irmaa_cost += irmaa_bracket['part_d_base'] * 12  # Annual Part D surcharge
            if partner_exists:
                irmaa_cost *= 2  # Double for both spouses
            
            # =========================
            # EXPENSE CALCULATIONS - FIXED TO USE ACTUAL PARAMETERS
            # =========================
            
            # CRITICAL FIX: Use the ACTUAL total_expenses parameter and distribute proportionally
            annual_base_expenses = base_total_expenses * 12 * inf_factor
            
            # Distribute expenses across components using proportions
            housing = annual_base_expenses * expense_proportions['housing']
            utilities = annual_base_expenses * expense_proportions['utilities']
            groceries = annual_base_expenses * expense_proportions['groceries']
            transportation = annual_base_expenses * expense_proportions['transportation']
            healthcare = annual_base_expenses * expense_proportions['healthcare']
            insurance = annual_base_expenses * expense_proportions['insurance']
            entertainment = annual_base_expenses * expense_proportions['entertainment']
            travel = annual_base_expenses * expense_proportions['travel']
            other_exp = annual_base_expenses * expense_proportions['other']
            
            base_expenses = housing + utilities + groceries + transportation + healthcare + insurance + entertainment + travel + other_exp
            
            # =========================
            # SPECIAL CASH FLOWS
            # =========================
            
            family_flow = family_cashflows.get(current_year, {})
            inheritance = family_flow.get('inflow_delta', 0) * inf_factor
            college = family_flow.get('expense_delta', 0) * inf_factor
            
            total_expenses_year = base_expenses + college + irmaa_cost  # Added irmaa_cost
            
            # =========================
            # NET INCOME CALCULATIONS
            # =========================
            
            taxes_paid = total_income_year * (tax_rate / 100)
            net_before_special = total_income_year - total_expenses_year - taxes_paid
            net_after_special = net_before_special + inheritance
            
            # =========================
            # SAVINGS & ASSETS
            # =========================
            
            savings_start = current_savings
            investment_return = savings_start * (investment_return_rate / 100)
            current_savings = savings_start + investment_return + net_after_special
            current_savings = max(0, current_savings)
            savings_end = current_savings
            
            total_assets = savings_end + primary_residence_value + secondary_residence_value + combined_other_assets_total
            net_worth = total_assets - combined_total_liabilities
            
            # =========================
            # GOAL PROGRESS
            # =========================
            
            cumulative_goals = sum(data['amount'] for data in goal_costs.values() if data['year'] <= current_year)
            goal_progress = savings_end / cumulative_goals if cumulative_goals > 0 else 1.0
            
            # =========================
            # APPEND TO LISTS
            # =========================
            
            salary_wages_list.append(salary)
            rental_income_list.append(rental)
            investment_income_list.append(investment)
            social_security_list.append(ss)
            pension_income_list.append(pension)
            other_income_list.append(other)
            total_income_list.append(total_income_year)
            
            user_rmd_list.append(user_rmd)
            partner_rmd_list.append(partner_rmd)
            total_rmd_list.append(total_rmd)
            
            housing_expenses_list.append(housing)
            utilities_list.append(utilities)
            groceries_list.append(groceries)
            transportation_list.append(transportation)
            healthcare_list.append(healthcare)
            insurance_list.append(insurance)
            entertainment_list.append(entertainment)
            travel_list.append(travel)
            other_expenses_list.append(other_exp)
            total_expenses_list.append(total_expenses_year)
            
            college_expenses_list.append(college)
            inheritance_inflow_list.append(inheritance)
            
            taxes_paid_list.append(taxes_paid)
            net_income_before_special_list.append(net_before_special)
            net_income_after_special_list.append(net_after_special)
            
            savings_start_list.append(savings_start)
            investment_return_list.append(investment_return)
            savings_end_list.append(savings_end)
            total_assets_list.append(total_assets)
            total_liabilities_list.append(combined_total_liabilities)
            net_worth_list.append(net_worth)
            
            goal_progress_list.append(goal_progress)
            
            irmaa_cost_list.append(irmaa_cost)  # Added for IRMAA
        
        # =========================
        # CREATE DATAFRAME IN LOGICAL ORDER
        # =========================
        
        df_data = {
            # Basic Info
            'Year': year_list,
            'User_Age': age_list,
            'Partner_Age': partner_age_list,
            
            # Income Components
            'Salary_Wages': salary_wages_list,
            'Rental_Income': rental_income_list,
            'Investment_Income': investment_income_list,
            'Social_Security': social_security_list,
            'Pension_Income': pension_income_list,
            'Other_Income': other_income_list,
            'Base_Income_Subtotal': [salary_wages_list[i] + rental_income_list[i] + investment_income_list[i] + 
                                      social_security_list[i] + pension_income_list[i] + other_income_list[i] 
                                      for i in range(simulation_years)],
            
            # RMD (SEPARATED)
            'User_RMD': user_rmd_list,
            'Partner_RMD': partner_rmd_list,
            'Total_RMD': total_rmd_list,
            
            # Total Income
            'Total_Income': total_income_list,
            
            # Expense Components
            'Housing_Expenses': housing_expenses_list,
            'Utilities': utilities_list,
            'Groceries': groceries_list,
            'Transportation': transportation_list,
            'Healthcare': healthcare_list,
            'Insurance': insurance_list,
            'Entertainment': entertainment_list,
            'Travel': travel_list,
            'Other_Expenses': other_expenses_list,
            'Base_Expenses_Subtotal': [housing_expenses_list[i] + utilities_list[i] + groceries_list[i] + 
                                        transportation_list[i] + healthcare_list[i] + insurance_list[i] + 
                                        entertainment_list[i] + travel_list[i] + other_expenses_list[i] 
                                        for i in range(simulation_years)],
            
            # Special Cash Flows
            'College_Expenses': college_expenses_list,
            'Inheritance_Inflow': inheritance_inflow_list,
            
            # IRMAA Costs (Added for IRMAA)
            'IRMAAnnualCost': irmaa_cost_list,
            
            # Total Expenses
            'Total_Expenses': total_expenses_list,
            
            # Net Calculations
            'Taxes_Paid': taxes_paid_list,
            'Net_Income_Before_Special': net_income_before_special_list,
            'Net_Income_After_Special': net_income_after_special_list,
            
            # Savings & Assets
            'Savings_Start': savings_start_list,
            'Investment_Return': investment_return_list,
            'Savings_End': savings_end_list,
            'Total_Assets': total_assets_list,
            'Total_Liabilities': total_liabilities_list,
            'Net_Worth': net_worth_list,
            
            # Goals
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
        
        # Debug final results
        print(f"\n{'='*60}")
        print(f"📊 SIMULATION RESULTS")
        print(f"{'='*60}")
        print(f"Final Savings: ${final_savings:,.2f}")
        print(f"Final Net Worth: ${final_net_worth:,.2f}")
        print(f"Years Solvent: {years_solvent}/{simulation_years}")
        print(f"{'='*60}\n")
        
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
        st.error(f"Simulation error details: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return results