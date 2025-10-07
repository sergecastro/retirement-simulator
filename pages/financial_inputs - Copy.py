# pages/financial_inputs.py - COMPLETE FILE
import streamlit as st
from datetime import date
from financial_utils import (
    calculate_total_income, calculate_total_expenses, 
    calculate_liquid_assets, calculate_total_liabilities,
    parse_goal_costs
)
import pandas as pd

def collect_financial_data():
    """Collect financial data with proper session state integration"""
    
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
    
    # Assets section
    st.header("🏦 Assets")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Real Estate")
        primary_residence = st.number_input(
            "Primary Residence:", 
            value=float(st.session_state.get('input_primary_residence_value', 0.0)),
            key="input_primary_residence_value"
        )
        secondary_residence = st.number_input(
            "Secondary Residence:", 
            value=float(st.session_state.get('input_secondary_residence_value', 0.0)),
            key="input_secondary_residence_value"
        )
        
        st.subheader("Retirement Accounts")
        ira_balance = st.number_input(
            "IRA Balance:", 
            value=float(st.session_state.get('input_ira_balance', 0.0)),
            key="input_ira_balance"
        )
        four01k_balance = st.number_input(
            "401k/403b Balance:", 
            value=float(st.session_state.get('input_four01k_403b_balance', 0.0)),
            key="input_four01k_403b_balance"
        )
        pension_value = st.number_input(
            "Pension Fund Value:", 
            value=float(st.session_state.get('input_pension_fund_value', 0.0)),
            key="input_pension_fund_value"
        )
    
    with col2:
        st.subheader("Liquid Assets")
        taxable_investments = st.number_input(
            "Taxable Investments:", 
            value=float(st.session_state.get('input_taxable_investment_accounts', 0.0)),
            key="input_taxable_investment_accounts"
        )
        savings_account = st.number_input(
            "High-Yield Savings:", 
            value=float(st.session_state.get('input_high_yield_savings_account', 0.0)),
            key="input_high_yield_savings_account"
        )
        hsa_balance = st.number_input(
            "HSA Balance:", 
            value=float(st.session_state.get('input_hsa_balance', 0.0)),
            key="input_hsa_balance"
        )
        
        st.subheader("Other Assets")
        vehicles = st.number_input(
            "Vehicles Value:", 
            value=float(st.session_state.get('input_vehicles_value', 0.0)),
            key="input_vehicles_value"
        )
        jewelry = st.number_input(
            "Jewelry/Collectibles:", 
            value=float(st.session_state.get('input_jewelry_collectibles_value', 0.0)),
            key="input_jewelry_collectibles_value"
        )
        crypto = st.number_input(
            "Cryptocurrency:", 
            value=float(st.session_state.get('input_cryptocurrency_holdings', 0.0)),
            key="input_cryptocurrency_holdings"
        )
    
    # Calculate liquid assets
    liquid_assets = calculate_liquid_assets(
        taxable_investments, savings_account, hsa_balance,
        ira_balance, four01k_balance, pension_value
    )
    
    # Liabilities section
    st.header("💳 Liabilities")
    col1, col2 = st.columns(2)
    
    with col1:
        primary_mortgage = st.number_input(
            "Primary Mortgage:", 
            value=float(st.session_state.get('input_primary_residence_mortgage', 0.0)),
            key="input_primary_residence_mortgage"
        )
        secondary_mortgage = st.number_input(
            "Secondary Mortgage:", 
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
    
    # Calculate monthly surplus
    monthly_surplus = total_income - total_expenses
    
    # Summary display
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
        net_worth = liquid_assets + primary_residence + secondary_residence - total_liabilities
        st.metric("Estimated Net Worth", f"${net_worth:,.0f}")
    
    # FIXED: Enhanced Financial Goals section
    st.header("🎯 Financial Goals")

    # Initialize goals data if not exists
    if 'goals_data' not in st.session_state:
        st.session_state['goals_data'] = [
            {"Goal": "", "Target $": 0.0, "Target Year": 2030},
            {"Goal": "", "Target $": 0.0, "Target Year": 2030},
            {"Goal": "", "Target $": 0.0, "Target Year": 2030}
        ]

    # Create DataFrame
    goals_df = pd.DataFrame(st.session_state['goals_data'])

    # Data editor with proper configuration
    updated_goals_df = st.data_editor(
        goals_df,
        column_config={
            "Goal": st.column_config.TextColumn(
                "Goal Name", 
                help="What are you saving for?",
                width="medium",
                required=False
            ),
            "Target $": st.column_config.NumberColumn(
                "Target Amount", 
                help="How much money do you need?",
                format="$%.0f",
                min_value=0.0,
                step=1000.0,
                required=False
            ),
            "Target Year": st.column_config.NumberColumn(
                "Target Year", 
                help="What year to achieve this goal?",
                format="%d",
                min_value=date.today().year,
                max_value=date.today().year + 50,
                step=1,
                required=False
            )
        },
        num_rows="dynamic",
        use_container_width=True,
        key="enhanced_goals_editor",
        hide_index=True
    )

    # Update session state
    st.session_state['goals_data'] = updated_goals_df.to_dict('records')

    # Parse goals
    goal_costs = {}
    valid_goals = []

    for _, row in updated_goals_df.iterrows():
        goal_name = str(row.get('Goal', '')).strip()
        target_amount = row.get('Target $', 0)
        target_year = row.get('Target Year', date.today().year + 10)
        
        if goal_name and pd.notna(target_amount) and target_amount > 0:
            goal_costs[goal_name] = {
                'year': int(target_year), 
                'amount': float(target_amount)
            }
            valid_goals.append({
                'name': goal_name,
                'amount': target_amount,
                'year': int(target_year)
            })

    # Show analysis if goals exist
    if valid_goals:
        st.subheader("📊 Goals Analysis")
        
        total_goal_amount = sum(goal['amount'] for goal in valid_goals)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Goal Amount", f"${total_goal_amount:,.0f}")
        with col2:
            st.metric("Number of Goals", len(valid_goals))
        with col3:
            avg_years = sum(goal['year'] - date.today().year for goal in valid_goals) / len(valid_goals)
            st.metric("Avg Years to Goals", f"{avg_years:.1f}")
        
        st.subheader("💰 Monthly Savings Required")
        for goal in valid_goals:
            years_to_goal = max(1, goal['year'] - date.today().year)
            monthly_needed = goal['amount'] / (years_to_goal * 12)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(goal['name'], f"${goal['amount']:,.0f}")
            with col2:
                st.metric("Target Year", goal['year'])
            with col3:
                st.metric("Years Left", years_to_goal)
            with col4:
                st.metric("Monthly Needed", f"${monthly_needed:,.0f}")
                if monthly_needed <= monthly_surplus:
                    st.success("✅ Achievable")
                else:
                    st.error("❌ Needs adjustment")
    else:
        st.info("💡 Add financial goals above to see savings recommendations!")
    
    # Return statement
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
        'other_assets': vehicles + jewelry + crypto,
        'goal_costs': goal_costs
    }