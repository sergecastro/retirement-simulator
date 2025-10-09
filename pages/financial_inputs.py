# pages/financial_inputs.py - COMPLETE with RELIABLE Goals (individual fields)
import streamlit as st
from datetime import date
from financial_utils import (
    calculate_total_income, calculate_total_expenses, 
    calculate_liquid_assets, calculate_total_liabilities,
    parse_goal_costs
)
import pandas as pd

def collect_financial_data():
    """Collect financial data with reliable goals input"""
    
    partner_exists = st.session_state.get('input_partner_exists', False)
    
    # Income section
    st.header("💰 Monthly Income")
    col1, col2 = st.columns(2)
    
    with col1:
        salary_wages = st.number_input(
            "Salary/Wages:", 
            value=float(st.session_state.get('input_salary_wages', 0.0)),
            key="input_salary_wages"
        )
        self_employment = st.number_input(
            "Self-Employment:", 
            value=float(st.session_state.get('input_self_employment_income', 0.0)),
            key="input_self_employment_income"
        )
        rental_income = st.number_input(
            "Rental Income:", 
            value=float(st.session_state.get('input_rental_income', 0.0)),
            key="input_rental_income"
        )
        investment_income = st.number_input(
            "Investment Income:", 
            value=float(st.session_state.get('input_investment_income', 0.0)),
            key="input_investment_income"
        )
    
    with col2:
        social_security = st.number_input(
            "Social Security:", 
            value=float(st.session_state.get('input_social_security_income', 0.0)),
            key="input_social_security_income"
        )
        pension_income = st.number_input(
            "Pension Income:", 
            value=float(st.session_state.get('input_pension_income', 0.0)),
            key="input_pension_income"
        )
        other_income = st.number_input(
            "Other Income:", 
            value=float(st.session_state.get('input_other_income', 0.0)),
            key="input_other_income"
        )
    
    total_income = calculate_total_income(
        salary_wages, self_employment, rental_income, 
        investment_income, social_security, pension_income, other_income
    )
    st.session_state['input_total_income'] = total_income
    
    # Expenses section
    st.header("💸 Monthly Expenses")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        housing = st.number_input(
            "Housing:", 
            value=float(st.session_state.get('input_housing_expenses', 0.0)),
            key="input_housing_expenses"
        )
        utilities = st.number_input(
            "Utilities:", 
            value=float(st.session_state.get('input_utilities_expenses', 0.0)),
            key="input_utilities_expenses"
        )
        groceries = st.number_input(
            "Groceries:", 
            value=float(st.session_state.get('input_groceries_expenses', 0.0)),
            key="input_groceries_expenses"
        )
        transportation = st.number_input(
            "Transportation:", 
            value=float(st.session_state.get('input_transportation_expenses', 0.0)),
            key="input_transportation_expenses"
        )
        healthcare = st.number_input(
            "Healthcare:", 
            value=float(st.session_state.get('input_healthcare_expenses', 0.0)),
            key="input_healthcare_expenses"
        )
    
    with col2:
        insurance = st.number_input(
            "Insurance:", 
            value=float(st.session_state.get('input_insurance_expenses', 0.0)),
            key="input_insurance_expenses"
        )
        property_tax = st.number_input(
            "Property Tax:", 
            value=float(st.session_state.get('input_property_tax_expenses', 0.0)),
            key="input_property_tax_expenses"
        )
        entertainment = st.number_input(
            "Entertainment:", 
            value=float(st.session_state.get('input_entertainment_expenses', 0.0)),
            key="input_entertainment_expenses"
        )
        restaurants = st.number_input(
            "Restaurants:", 
            value=float(st.session_state.get('input_restaurant_expenses', 0.0)),
            key="input_restaurant_expenses"
        )
        travel = st.number_input(
            "Travel:", 
            value=float(st.session_state.get('input_travel_expenses', 0.0)),
            key="input_travel_expenses"
        )
    
    with col3:
        education = st.number_input(
            "Education:", 
            value=float(st.session_state.get('input_education_expenses', 0.0)),
            key="input_education_expenses"
        )
        childcare = st.number_input(
            "Childcare:", 
            value=float(st.session_state.get('input_childcare_expenses', 0.0)),
            key="input_childcare_expenses"
        )
        clothing = st.number_input(
            "Clothing:", 
            value=float(st.session_state.get('input_clothing_expenses', 0.0)),
            key="input_clothing_expenses"
        )
        charitable = st.number_input(
            "Charitable:", 
            value=float(st.session_state.get('input_charitable_donations', 0.0)),
            key="input_charitable_donations"
        )
        miscellaneous = st.number_input(
            "Miscellaneous:", 
            value=float(st.session_state.get('input_miscellaneous_expenses', 0.0)),
            key="input_miscellaneous_expenses"
        )
        other_expenses = st.number_input(
            "Other Expenses:", 
            value=float(st.session_state.get('input_other_expenses', 0.0)),
            key="input_other_expenses"
        )
    
    total_expenses = calculate_total_expenses(
        housing, utilities, groceries, transportation, healthcare,
        insurance, property_tax, entertainment, restaurants, travel,
        education, childcare, clothing, charitable, miscellaneous, other_expenses
    )
    st.session_state['input_total_expenses'] = total_expenses
    
    # Assets section
    st.header("🏦 Assets")
    
    st.subheader("🏠 Real Estate")
    col1, col2 = st.columns(2)
    with col1:
        primary_residence = st.number_input(
            "Primary Residence Value:", 
            value=float(st.session_state.get('input_primary_residence_value', 0.0)),
            key="input_primary_residence_value",
            help="Current market value of your primary home"
        )
    with col2:
        secondary_residence = st.number_input(
            "Secondary Residence Value:", 
            value=float(st.session_state.get('input_secondary_residence_value', 0.0)),
            key="input_secondary_residence_value",
            help="Vacation home, rental property, etc."
        )
    
    st.subheader("💼 Your Retirement Accounts")
    col1, col2 = st.columns(2)
    with col1:
        ira_balance = st.number_input(
            "Your IRA Balance:", 
            value=float(st.session_state.get('input_ira_balance', 0.0)),
            key="input_ira_balance",
            help="Traditional IRA, Roth IRA, SEP IRA"
        )
        four01k_balance = st.number_input(
            "Your 401k/403b Balance:", 
            value=float(st.session_state.get('input_four01k_403b_balance', 0.0)),
            key="input_four01k_403b_balance",
            help="Employer-sponsored retirement plans"
        )
    with col2:
        pension_value = st.number_input(
            "Pension Fund Value:", 
            value=float(st.session_state.get('input_pension_fund_value', 0.0)),
            key="input_pension_fund_value",
            help="Current value of pension benefits"
        )
        st.metric("Your Total Retirement", f"${ira_balance + four01k_balance + pension_value:,.0f}")
    
    partner_ira_balance = 0
    partner_four01k_balance = 0
    
    if partner_exists:
        st.markdown("---")
        st.subheader("👥 Partner Retirement Accounts")
        st.info("Partner detected - enter retirement account balances for RMD calculations")
        
        col1, col2 = st.columns(2)
        with col1:
            partner_ira_balance = st.number_input(
                "Partner IRA Balance:", 
                value=float(st.session_state.get('input_partner_ira_balance', 0.0)),
                key="input_partner_ira_balance",
                help="Partner's IRA accounts"
            )
            partner_four01k_balance = st.number_input(
                "Partner 401k/403b Balance:", 
                value=float(st.session_state.get('input_partner_four01k_403b_balance', 0.0)),
                key="input_partner_four01k_403b_balance",
                help="Partner's 401k/403b"
            )
        with col2:
            st.metric("Partner Total Retirement", f"${partner_ira_balance + partner_four01k_balance:,.0f}")
            st.metric("Combined Retirement", f"${ira_balance + four01k_balance + partner_ira_balance + partner_four01k_balance:,.0f}")
            
            partner_age = st.session_state.get('input_partner_age', 65)
            if partner_age < 73:
                years_until_rmd = 73 - partner_age
                st.caption(f"Partner RMD starts in {years_until_rmd} years (age 73)")
            else:
                st.caption("Partner is currently taking RMDs")
    else:
        st.session_state['input_partner_ira_balance'] = 0
        st.session_state['input_partner_four01k_balance'] = 0
    
    st.subheader("💵 Liquid Assets")
    col1, col2 = st.columns(2)
    with col1:
        taxable_investments = st.number_input(
            "Taxable Investment Accounts:", 
            value=float(st.session_state.get('input_taxable_investment_accounts', 0.0)),
            key="input_taxable_investment_accounts",
            help="Brokerage accounts, stocks, bonds"
        )
        savings_account = st.number_input(
            "High-Yield Savings:", 
            value=float(st.session_state.get('input_high_yield_savings_account', 0.0)),
            key="input_high_yield_savings_account",
            help="Savings accounts, CDs, money market"
        )
    with col2:
        hsa_balance = st.number_input(
            "HSA Balance:", 
            value=float(st.session_state.get('input_hsa_balance', 0.0)),
            key="input_hsa_balance",
            help="Health Savings Account"
        )
        five29_balance = st.number_input(
            "529 Plan Balance:", 
            value=float(st.session_state.get('input_five29_plan_balance', 0.0)),
            key="input_five29_plan_balance",
            help="College savings plans"
        )
    
    st.subheader("🎨 Other Assets")
    col1, col2, col3 = st.columns(3)
    with col1:
        vehicles = st.number_input(
            "Vehicles Value:", 
            value=float(st.session_state.get('input_vehicles_value', 0.0)),
            key="input_vehicles_value"
        )
    with col2:
        jewelry = st.number_input(
            "Jewelry/Collectibles:", 
            value=float(st.session_state.get('input_jewelry_collectibles_value', 0.0)),
            key="input_jewelry_collectibles_value"
        )
    with col3:
        crypto = st.number_input(
            "Cryptocurrency:", 
            value=float(st.session_state.get('input_cryptocurrency_holdings', 0.0)),
            key="input_cryptocurrency_holdings"
        )
    
    liquid_assets = (taxable_investments + savings_account + hsa_balance + 
                    ira_balance + four01k_balance + pension_value +
                    partner_ira_balance + partner_four01k_balance)
    
    # Liabilities section
    st.header("💳 Liabilities")
    col1, col2 = st.columns(2)
    
    with col1:
        primary_mortgage = st.number_input(
            "Primary Mortgage Balance:", 
            value=float(st.session_state.get('input_primary_residence_mortgage', 0.0)),
            key="input_primary_residence_mortgage"
        )
        secondary_mortgage = st.number_input(
            "Secondary Mortgage Balance:", 
            value=float(st.session_state.get('input_secondary_residence_mortgage', 0.0)),
            key="input_secondary_residence_mortgage"
        )
        auto_loans = st.number_input(
            "Auto Loans:", 
            value=float(st.session_state.get('input_auto_loans', 0.0)),
            key="input_auto_loans"
        )
    
    with col2:
        student_loans = st.number_input(
            "Student Loans:", 
            value=float(st.session_state.get('input_student_loans', 0.0)),
            key="input_student_loans"
        )
        credit_cards = st.number_input(
            "Credit Card Debt:", 
            value=float(st.session_state.get('input_credit_card_debt', 0.0)),
            key="input_credit_card_debt"
        )
        personal_loans = st.number_input(
            "Personal Loans:", 
            value=float(st.session_state.get('input_personal_loans', 0.0)),
            key="input_personal_loans"
        )
    
    total_liabilities = calculate_total_liabilities(
        primary_mortgage, secondary_mortgage, auto_loans,
        student_loans, credit_cards, personal_loans
    )
    
    monthly_surplus = total_income - total_expenses
    
    # Summary display
    st.markdown("---")
    st.subheader("📊 Financial Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Monthly Income", f"${total_income:,.0f}")
        st.metric("Total Monthly Expenses", f"${total_expenses:,.0f}")
    with col2:
        st.metric("Monthly Surplus", f"${monthly_surplus:,.0f}", 
                 delta_color="normal" if monthly_surplus >= 0 else "inverse")
        st.metric("Liquid Assets", f"${liquid_assets:,.0f}")
    with col3:
        st.metric("Total Liabilities", f"${total_liabilities:,.0f}")
        net_worth = liquid_assets + primary_residence + secondary_residence + vehicles + jewelry + crypto - total_liabilities
        st.metric("Estimated Net Worth", f"${net_worth:,.0f}")
    
    # ============================================
    # RELIABLE GOALS SECTION - Individual Input Fields
    # ============================================
    st.header("🎯 Financial Goals")
    
    # Initialize goals list
    if 'goals_list' not in st.session_state:
        st.session_state['goals_list'] = []
    
    # Add goal button
    if st.button("➕ Add New Goal", key="add_goal_reliable"):
        st.session_state['goals_list'].append({
            'goal': '',
            'amount': 0.0,
            'year': date.today().year + 10
        })
        st.rerun()
    
    if len(st.session_state['goals_list']) == 0:
        st.info("Click 'Add New Goal' to start tracking financial milestones")
        goal_costs = {}
    else:
        st.write(f"**Currently tracking {len(st.session_state['goals_list'])} goal(s)**")
        
        # Display each goal as individual input fields
        goal_costs = {}
        goals_to_remove = []
        
        for idx, goal_data in enumerate(st.session_state['goals_list']):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    goal_name = st.text_input(
                        "Goal Name:",
                        value=goal_data.get('goal', ''),
                        key=f"goal_name_{idx}",
                        placeholder="e.g., Retirement Fund, Down Payment"
                    )
                    st.session_state['goals_list'][idx]['goal'] = goal_name
                
                with col2:
                    goal_amount = st.number_input(
                        "Target Amount ($):",
                        value=float(goal_data.get('amount', 0.0)),
                        min_value=0.0,
                        step=1000.0,
                        format="%.0f",
                        key=f"goal_amount_{idx}"
                    )
                    st.session_state['goals_list'][idx]['amount'] = goal_amount
                
                with col3:
                    default_year = date.today().year + 10
                    year_value = goal_data.get('year', default_year)
                    year = int(year_value) if year_value is not None else default_year
                    goal_year = st.number_input(
                        "Target Year:",
                        value=year,
                        min_value=date.today().year,
                        max_value=date.today().year + 50,
                        step=1,
                        key=f"goal_year_{idx}"
                    )
                    st.session_state['goals_list'][idx]['year'] = goal_year
                
                with col4:
                    st.write("")
                    st.write("")
                    if st.button("🗑️", key=f"delete_goal_{idx}", help="Delete this goal"):
                        goals_to_remove.append(idx)
                        st.rerun()
                
                # Add to goal_costs if valid
                if goal_name.strip() and goal_amount > 0:
                    goal_costs[goal_name] = {
                        'year': int(goal_year),
                        'amount': float(goal_amount)
                    }
                
                st.markdown("---")
        
        # Remove deleted goals
        for idx in reversed(goals_to_remove):
            st.session_state['goals_list'].pop(idx)
        
        # Show summary
        valid_goals = len(goal_costs)
        if valid_goals > 0:
            st.success(f"{valid_goals} goal(s) configured and ready for simulation")
            
            with st.expander("Goals Summary"):
                for goal_name, goal_data in goal_costs.items():
                    years_away = goal_data['year'] - date.today().year
                    st.write(f"**{goal_name}**")
                    st.write(f"  Target: ${goal_data['amount']:,.0f} by {goal_data['year']} ({years_away} years)")
        else:
            st.warning("Fill in goal names and amounts for simulation")
    
    # Return all data
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'liquid_assets': liquid_assets,
        'primary_residence_value': primary_residence,
        'secondary_residence_value': secondary_residence,
        'total_liabilities': total_liabilities,
        'monthly_surplus': monthly_surplus,
        'ira_balance': ira_balance,
        'four01k_403b_balance': four01k_balance,
        'partner_ira_balance': partner_ira_balance,
        'partner_four01k_403b_balance': partner_four01k_balance,
        'other_assets': vehicles + jewelry + crypto,
        'goal_costs': goal_costs,
        'partner_liabilities': 0
    }