# File: simulation.py  
import pandas as pd  
import numpy as np  
from datetime import date  
import streamlit as st  
import financial_utils  
try:  
    import household_events as he  
    EVENTS_AVAILABLE = True  
except ImportError:  
    EVENTS_AVAILABLE = False  

def run_simulation(age, partner_exists, partner_age, total_income, total_expenses, combined_financial_assets, primary_residence_value, secondary_residence_value, combined_other_assets_total, total_liabilities_local, partner_liabilities, tax_rate, inflation_rate, investment_return_rate, simulation_years, mc_iterations, goal_costs, college_inflation_pct, base_public_in, base_public_out, base_private, ira_balance, four01k_403b_balance, partner_ira_balance, partner_four01k_403b_balance, monthly_surplus, combined_total_liabilities, roth_conversion_annual=0, itemize_deductions=True, five29_plan_balance=0.0):  
    # NaN guards and defaults  
    partner_age = int(partner_age) if pd.notna(partner_age) else age  
    total_income = float(total_income) if pd.notna(total_income) else 0.0  
    total_expenses = float(total_expenses) if pd.notna(total_expenses) else 0.0  
    combined_financial_assets = float(combined_financial_assets) if pd.notna(combined_financial_assets) else 0.0  
    primary_residence_value = float(primary_residence_value) if pd.notna(primary_residence_value) else 0.0  
    secondary_residence_value = float(secondary_residence_value) if pd.notna(secondary_residence_value) else 0.0  
    combined_other_assets_total = float(combined_other_assets_total) if pd.notna(combined_other_assets_total) else 0.0  
    total_liabilities_local = float(total_liabilities_local) if pd.notna(total_liabilities_local) else 0.0  
    partner_liabilities = float(partner_liabilities) if pd.notna(partner_liabilities) else 0.0  
    tax_rate = float(tax_rate) if pd.notna(tax_rate) else 22.0  
    inflation_rate = float(inflation_rate) if pd.notna(inflation_rate) else 3.0  
    investment_return_rate = float(investment_return_rate) if pd.notna(investment_return_rate) else 7.0  
    simulation_years = int(simulation_years) if pd.notna(simulation_years) else 30  
    mc_iterations = int(mc_iterations) if pd.notna(mc_iterations) else 0  
    college_inflation_pct = float(college_inflation_pct) if pd.notna(college_inflation_pct) else 4.0  
    base_public_in = float(base_public_in) if pd.notna(base_public_in) else 20000.0  
    base_public_out = float(base_public_out) if pd.notna(base_public_out) else 40000.0  
    base_private = float(base_private) if pd.notna(base_private) else 60000.0  
    ira_balance = float(ira_balance) if pd.notna(ira_balance) else 0.0  
    four01k_403b_balance = float(four01k_403b_balance) if pd.notna(four01k_403b_balance) else 0.0  
    partner_ira_balance = float(partner_ira_balance) if pd.notna(partner_ira_balance) else 0.0  
    partner_four01k_403b_balance = float(partner_four01k_403b_balance) if pd.notna(partner_four01k_403b_balance) else 0.0  
    monthly_surplus = float(monthly_surplus) if pd.notna(monthly_surplus) else 0.0  
    combined_total_liabilities = float(combined_total_liabilities) if pd.notna(combined_total_liabilities) else 0.0  
    five29_plan_balance = float(five29_plan_balance) if pd.notna(five29_plan_balance) else 0.0  

    try:  
        # Family events  
        children = he.build_child_objects(st.session_state.get("children_rows", [])) if EVENTS_AVAILABLE else []  
        inheritances = he.build_inheritances(st.session_state.get("inherit_rows", [])) if EVENTS_AVAILABLE else []  
        start_year = date.today().year  
        family_cashflows = he.make_family_cashflows(children, inheritances, start_year, start_year + simulation_years - 1, college_inflation_pct, base_public_in, base_public_out, base_private) if EVENTS_AVAILABLE else {}  

        # Initial setup  
        current_age = age  
        current_partner_age = partner_age if partner_exists else None  
        initial_annual_income = total_income * 12  
        initial_annual_expenses = total_expenses * 12  
        current_savings = combined_financial_assets  
        current_primary_home = primary_residence_value  
        current_secondary_home = secondary_residence_value  
        current_liabilities = total_liabilities_local + partner_liabilities  

        # RMD factors  
        rmd_factors = {73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4}  

        # Tracking lists  
        years = []  
        ages = []  
        total_incomes = []  
        total_expenses_list = []  
        event_deltas = []  
        net_draws = []  
        rmd_primary = []  
        rmd_partner = []  
        total_rmd_before_tax = []  
        net_rmd_used_list = []  
        cash_used_from_savings_list = []  
        savings_open = []  
        savings_growth = []  
        savings_before_draw = []  
        savings_end = []  
        primary_home_values = []  
        secondary_home_values = []  
        total_assets_list = []  
        total_liabilities_list = []  
        net_worth_list = []  
        tax_paid_list = []  
        five29_balance_list = []  
        roth_balance_list = []  

        # RMD balances  
        primary_ira = ira_balance  
        primary_401k = four01k_403b_balance  
        partner_ira = partner_ira_balance if partner_exists else 0.0  
        partner_401k = partner_four01k_403b_balance if partner_exists else 0.0  

        # 529 and Roth
        five29_balance = five29_plan_balance
        roth_balance = 0.0  # Starts at 0, conversions add to it  

        # Simulation loop  
        for year in range(simulation_years):  
            current_year = start_year + year  
            years.append(current_year)  
            ages.append(current_age)  

            deltas = family_cashflows.get(current_year, {"expense_delta": 0.0, "inflow_delta": 0.0})  
            annual_income = initial_annual_income * (1 + inflation_rate / 100) ** year + deltas["inflow_delta"]  
            annual_expenses = initial_annual_expenses * (1 + inflation_rate / 100) ** year + deltas["expense_delta"]  
            event_delta = deltas["expense_delta"] - deltas["inflow_delta"]  

            # RMD calculation  
            rmd_prim = 0  
            if current_age >= 73:  
                primary_rmd_balance = primary_ira + primary_401k  
                rmd_factor = rmd_factors.get(current_age, 6.4)  
                rmd_prim = primary_rmd_balance / rmd_factor  
                primary_ira = max(0, primary_ira - rmd_prim / 2) if primary_401k else max(0, primary_ira - rmd_prim)  
                primary_401k = max(0, primary_401k - rmd_prim / 2) if primary_ira else max(0, primary_401k - rmd_prim)  
            rmd_part = 0  
            if partner_exists and current_partner_age >= 73:  
                partner_rmd_balance = partner_ira + partner_401k  
                rmd_factor = rmd_factors.get(current_partner_age, 6.4)  
                rmd_part = partner_rmd_balance / rmd_factor  
                partner_ira = max(0, partner_ira - rmd_part / 2) if partner_401k else max(0, partner_ira - rmd_part)  
                partner_401k = max(0, partner_401k - rmd_part / 2) if partner_ira else max(0, partner_401k - rmd_part)  
            total_rmd_before = rmd_prim + rmd_part  
            total_net_rmd = total_rmd_before * (1 - tax_rate / 100)  

            # Net cash flow  
            net_flow = annual_expenses - annual_income - total_net_rmd  
            net_draw = max(0, net_flow)  

            # Savings growth  
            savings_open_value = current_savings  
            savings_growth_value = current_savings * (investment_return_rate / 100)  
            savings_before_draw_value = current_savings + savings_growth_value + monthly_surplus * 12  
            cash_used_from_savings = min(savings_before_draw_value, net_draw)  
            current_savings = max(0, savings_before_draw_value - net_draw)  

            # Assets appreciation  
            current_primary_home *= 1.03  
            current_secondary_home *= 1.03  

            # Liabilities reduction  
            current_liabilities = max(0.0, current_liabilities * 0.95)  

            combined_other_assets_current = combined_other_assets_total * (1 + inflation_rate / 100) ** year  
            total_assets_now = current_savings + current_primary_home + current_secondary_home + combined_other_assets_current  
            current_net_worth = total_assets_now - current_liabilities  

            # Add to lists  
            total_incomes.append(annual_income)  
            total_expenses_list.append(annual_expenses)  
            event_deltas.append(event_delta)  
            net_draws.append(net_draw)  
            rmd_primary.append(rmd_prim)  
            rmd_partner.append(rmd_part)  
            total_rmd_before_tax.append(total_rmd_before)  
            net_rmd_used_list.append(total_net_rmd)  
            cash_used_from_savings_list.append(cash_used_from_savings)  
            savings_open.append(savings_open_value)  
            savings_growth.append(savings_growth_value)  
            savings_before_draw.append(savings_before_draw_value)  
            savings_end.append(current_savings)  
            primary_home_values.append(current_primary_home)  
            secondary_home_values.append(current_secondary_home)  
            total_assets_list.append(total_assets_now)  
            total_liabilities_list.append(current_liabilities)  
            net_worth_list.append(current_net_worth)  
            tax_paid_list.append(0)  # Placeholder, update with tax logic  
            five29_balance_list.append(0)  # Placeholder  
            roth_balance_list.append(0)  # Placeholder  

            current_age += 1  
            if partner_exists:  
                current_partner_age += 1  

        df = pd.DataFrame({  
            "Year": years, "Age": ages, "Total Income": total_incomes, "Total Expenses": total_expenses_list,  
            "Event Delta": event_deltas, "Net Draw": net_draws, "RMD Primary": rmd_primary, "RMD Partner": rmd_partner,  
            "Total RMD Before Tax": total_rmd_before_tax, "Net RMD Used": net_rmd_used_list,  
            "Cash Used from Savings": cash_used_from_savings_list, "Savings Open": savings_open,  
            "Savings Growth": savings_growth, "Savings Before Draw": savings_before_draw, "Savings End": savings_end,  
            "Primary Home Value": primary_home_values, "Secondary Home Value": secondary_home_values,  
            "Total Assets": total_assets_list, "Total Liabilities": total_liabilities_list, "Net Worth": net_worth_list  
        })  

        # Monte Carlo  
        monte_carlo_results = None  
        if mc_iterations > 0:  
            monte_carlo_results = run_monte_carlo(total_income, total_expenses, investment_return_rate, inflation_rate, simulation_years, mc_iterations, combined_financial_assets, family_cashflows)  

        # Goal achievement  
        goal_achievement = {}  
        for goal, data in goal_costs.items():  
            year_index = data['year'] - start_year  
            if 0 <= year_index < simulation_years:  
                actual = savings_end[year_index]  
                achieved = actual >= data['amount']  
                goal_achievement[goal] = {'target': data['amount'], 'year': data['year'], 'actual': actual, 'achieved': achieved}  
            else:  
                goal_achievement[goal] = {'target': data['amount'], 'year': data['year'], 'actual': 0, 'achieved': False}  

        # Health metrics  
        emergency_fund_months = combined_financial_assets / total_expenses if total_expenses > 0 else 0  
        debt_to_income = combined_total_liabilities / total_income if total_income > 0 else 0  
        savings_rate = monthly_surplus / total_income if total_income > 0 else 0  
        health_score = financial_utils.calculate_health_score(emergency_fund_months, debt_to_income, savings_rate, savings_end[-1] > 0 if savings_end else False)  

        return {  
            "df": df,  
            "years_solvent": sum(1 for s in savings_end if s > 0),  
            "final_savings": savings_end[-1] if savings_end else 0,  
            "final_net_worth": net_worth_list[-1] if net_worth_list else 0,  
            "emergency_fund_months": emergency_fund_months,  
            "debt_to_income": debt_to_income,  
            "savings_rate": savings_rate,  
            "health_score": health_score,  
            "goal_achievement": goal_achievement,  
            "monte_carlo_results": monte_carlo_results,  
            "events": family_cashflows,  
            "total_incomes": total_incomes,  
            "total_rmd": total_rmd_before_tax  # Assuming for Sankey  
        }  
    except Exception as e:  
        st.error(f"Simulation error: {str(e)}")  
        return None  

def run_monte_carlo(total_income, total_expenses, investment_return_rate, inflation_rate, simulation_years, mc_iterations, combined_financial_assets, family_cashflows):  
    start_year = date.today().year  
    mc_paths = []  
    for _ in range(mc_iterations):  
        current_savings = combined_financial_assets  
        path = []  
        for year in range(simulation_years):  
            current_year = start_year + year  
            deltas = family_cashflows.get(current_year, {"expense_delta": 0.0, "inflow_delta": 0.0})  
            ann_return = np.random.normal(investment_return_rate / 100, 0.05)  
            ann_infl = np.random.normal(inflation_rate / 100, 0.01)  
            ann_income = (total_income * 12) * (1 + ann_infl) ** year + deltas["inflow_delta"]  
            ann_exp = (total_expenses * 12) * (1 + ann_infl) ** year + deltas["expense_delta"]  
            net_flow = ann_exp - ann_income  
            current_savings = current_savings * (1 + ann_return) - max(0, net_flow)  
            path.append(max(0, current_savings))  
        mc_paths.append(path)  
    mc_df = pd.DataFrame(mc_paths, columns=range(start_year, start_year + simulation_years))  
    success_rate = (mc_df.iloc[-1] > 0).mean() * 100 if not mc_df.empty else 0  
    return {"mc_df": mc_df, "success_rate": success_rate}  