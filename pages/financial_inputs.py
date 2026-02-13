# pages/financial_inputs.py - COMPLETE with RELIABLE Goals (individual fields) + CUSTOM EXPENSES
import streamlit as st
from datetime import date
from financial_utils import (
    calculate_total_income, calculate_total_expenses,
    calculate_liquid_assets, calculate_total_liabilities,
    parse_goal_costs
)
import pandas as pd


def _init_float(key: str, default: float = 0.0):
    """Initialize session_state float field if missing or None"""
    if key not in st.session_state or st.session_state[key] is None:
        st.session_state[key] = default


def _display_currency(label, value, help_text=None):
    """Display a currency value as formatted text instead of a disabled input.
    Readable on all devices including mobile Safari with accessibility settings."""
    val = float(value) if value is not None else 0.0
    formatted = f"${val:,.0f}" if val >= 0 else f"-${abs(val):,.0f}"
    if help_text:
        st.markdown(f"**{label}:** &nbsp; `{formatted}` &nbsp; <small style='color:#888;'>{help_text}</small>", unsafe_allow_html=True)
    else:
        st.markdown(f"**{label}:** &nbsp; `{formatted}`", unsafe_allow_html=True)


def collect_financial_data():
    """Collect financial data with reliable goals input"""

    partner_exists = st.session_state.get('input_partner_exists', False)

    # Income section
    st.header("💰 Monthly Income")

    # Prominent note about before-tax income
    st.info("📝 **Important:** Enter all income amounts **BEFORE TAXES**. The app will calculate federal and state taxes for you.")

    # Initialize ALL income fields before widgets (avoid value/key conflict)
    _init_float('input_salary_wages')
    _init_float('input_self_employment_income')
    _init_float('input_rental_income')
    _init_float('input_investment_income')
    _init_float('input_social_security_income')
    _init_float('input_pension_income')
    _init_float('input_other_income')

    col1, col2 = st.columns(2)

    with col1:
        salary_wages = st.session_state.get('input_salary_wages', 0.0)
        _display_currency("Monthly Salary/Wages (Before Taxes)", salary_wages)

        self_employment = st.session_state.get('input_self_employment_income', 0.0)
        _display_currency("Monthly Self-Employment Income", self_employment)

        rental_income = st.session_state.get('input_rental_income', 0.0)
        _display_currency("Monthly Rental Income", rental_income)

        investment_income = st.session_state.get('input_investment_income', 0.0)
        _display_currency("Monthly Investment Income (Before Taxes)", investment_income)

    with col2:
        social_security = st.session_state.get('input_social_security_income', 0.0)
        _display_currency("Monthly Social Security (Before Taxes)", social_security)

        pension_income = st.session_state.get('input_pension_income', 0.0)
        _display_currency("Monthly Pension (Before Taxes)", pension_income)

        other_income = st.session_state.get('input_other_income', 0.0)
        _display_currency("Monthly Other Income", other_income)

    total_income = calculate_total_income(
        salary_wages, self_employment, rental_income,
        investment_income, social_security, pension_income, other_income
    )
    st.session_state['input_total_income'] = total_income

    # Expenses section
    st.header("💸 Monthly Expenses")

    # Initialize ALL expense fields before widgets
    _init_float('input_housing_expenses')
    _init_float('input_utilities_expenses')
    _init_float('input_groceries_expenses')
    _init_float('input_transportation_expenses')
    _init_float('input_healthcare_expenses')
    _init_float('input_insurance_expenses')
    _init_float('input_property_tax_expenses')
    _init_float('input_entertainment_expenses')
    _init_float('input_restaurant_expenses')
    _init_float('input_travel_expenses')
    _init_float('input_education_expenses')
    _init_float('input_childcare_expenses')
    _init_float('input_clothing_expenses')
    _init_float('input_charitable_donations')
    _init_float('input_miscellaneous_expenses')
    _init_float('input_other_expenses')

    col1, col2, col3 = st.columns(3)

    with col1:
        housing = st.session_state.get('input_housing_expenses', 0.0)
        _display_currency("Housing", housing)

        utilities = st.session_state.get('input_utilities_expenses', 0.0)
        _display_currency("Utilities", utilities)

        groceries = st.session_state.get('input_groceries_expenses', 0.0)
        _display_currency("Groceries", groceries)

        transportation = st.session_state.get('input_transportation_expenses', 0.0)
        _display_currency("Transportation", transportation)

        healthcare = st.session_state.get('input_healthcare_expenses', 0.0)
        _display_currency("Healthcare", healthcare)

    with col2:
        insurance = st.session_state.get('input_insurance_expenses', 0.0)
        _display_currency("Insurance", insurance)

        property_tax = st.session_state.get('input_property_tax_expenses', 0.0)
        _display_currency("Property Tax", property_tax)

        entertainment = st.session_state.get('input_entertainment_expenses', 0.0)
        _display_currency("Entertainment", entertainment)

        restaurants = st.session_state.get('input_restaurant_expenses', 0.0)
        _display_currency("Restaurants", restaurants)

        travel = st.session_state.get('input_travel_expenses', 0.0)
        _display_currency("Travel", travel)

    with col3:
        education = st.session_state.get('input_education_expenses', 0.0)
        _display_currency("Education", education)

        childcare = st.session_state.get('input_childcare_expenses', 0.0)
        _display_currency("Childcare", childcare)

        clothing = st.session_state.get('input_clothing_expenses', 0.0)
        _display_currency("Clothing", clothing)

        charitable = st.session_state.get('input_charitable_donations', 0.0)
        _display_currency("Charitable", charitable)

        miscellaneous = st.session_state.get('input_miscellaneous_expenses', 0.0)
        _display_currency("Miscellaneous", miscellaneous)

        other_expenses = st.session_state.get('input_other_expenses', 0.0)
        _display_currency("Other Expenses", other_expenses)

    # ============================================
    # CUSTOM INCOME SECTION (NEW!)
    # ============================================
    st.markdown("---")
    st.subheader("💰 Custom Income Sources")

    # Get custom income from session state (loaded from intake app)
    custom_income_display = st.session_state.get('custom_income', [])

    if custom_income_display:
        st.info(f"ℹ️ {len(custom_income_display)} custom income source(s) imported from intake app")

        # Display custom income in a nice format
        for idx, income in enumerate(custom_income_display):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{income.get('Name', 'N/A')}**")
            with col2:
                st.write(f"${income.get('Monthly Amount', 0):,.2f}/month")
            with col3:
                st.write(f"*{income.get('Category', 'N/A')}*")

        # Calculate total custom income
        custom_income_display_total = sum(inc.get('Monthly Amount', 0) for inc in custom_income_display)
        st.success(f"📊 **Total Custom Income: ${custom_income_display_total:,.2f}/month**")
    else:
        st.caption("No custom income sources defined. You can add them in the intake app.")

    # ============================================
    # CUSTOM EXPENSES SECTION (NEW!)
    # ============================================
    st.markdown("---")
    st.subheader("📝 Custom Monthly Expenses")

    # Get custom expenses from session state (loaded from intake JSON)
    custom_expenses = st.session_state.get('custom_expenses', [])

    if custom_expenses:
        st.info(f"ℹ️ {len(custom_expenses)} custom expense(s) imported from intake app")

        # Display custom expenses in a nice format
        for idx, expense in enumerate(custom_expenses):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{expense.get('Name', 'N/A')}**")
            with col2:
                st.write(f"${expense.get('Monthly Amount', 0):,.2f}/month")
            with col3:
                st.write(f"*{expense.get('Category', 'N/A')}*")

        # Calculate total custom expenses
        custom_expenses_total = sum(expense.get('Monthly Amount', 0) for expense in custom_expenses)
        st.success(f"📊 **Total Custom Expenses: ${custom_expenses_total:,.2f}/month**")
    else:
        st.caption("No custom expenses defined. You can add them in the intake app.")
        custom_expenses_total = 0.0

    # ============================================
    # CALCULATE TOTAL EXPENSES (including custom)
    # ============================================
    base_expenses = calculate_total_expenses(
        housing, utilities, groceries, transportation, healthcare,
        insurance, property_tax, entertainment, restaurants, travel,
        education, childcare, clothing, charitable, miscellaneous, other_expenses
    )

    total_expenses = base_expenses + custom_expenses_total
    st.session_state['input_total_expenses'] = total_expenses

    # Assets section
    st.header("🦠 Assets")

    # Initialize ALL asset fields before widgets
    _init_float('input_primary_residence_value')
    _init_float('input_secondary_residence_value')
    _init_float('input_ira_balance')
    _init_float('input_four01k_403b_balance')
    _init_float('input_pension_fund_value')
    _init_float('input_partner_ira_balance')
    _init_float('input_partner_four01k_403b_balance')
    _init_float('input_taxable_investment_accounts')
    _init_float('input_high_yield_savings_account')
    _init_float('input_hsa_balance')
    _init_float('input_five29_plan_balance')
    _init_float('input_vehicles_value')
    _init_float('input_jewelry_collectibles_value')
    _init_float('input_cryptocurrency_holdings')

    st.subheader("🏠 Real Estate")
    col1, col2 = st.columns(2)
    with col1:
        primary_residence = st.session_state.get('input_primary_residence_value', 0.0)
        _display_currency("Primary Residence Value", primary_residence)
    with col2:
        secondary_residence = st.session_state.get('input_secondary_residence_value', 0.0)
        _display_currency("Secondary Residence Value", secondary_residence)

    st.subheader("💼 Your Retirement Accounts")
    col1, col2 = st.columns(2)
    with col1:
        ira_balance = st.session_state.get('input_ira_balance', 0.0)
        _display_currency("Your IRA Balance", ira_balance)

        four01k_balance = st.session_state.get('input_four01k_403b_balance', 0.0)
        _display_currency("Your 401k/403b Balance", four01k_balance)
    with col2:
        pension_value = st.session_state.get('input_pension_fund_value', 0.0)
        _display_currency("Pension Fund Value", pension_value)

        st.metric("Your Total Retirement", f"${ira_balance + four01k_balance + pension_value:,.0f}")

    partner_ira_balance = 0
    partner_four01k_balance = 0

    if partner_exists:
        st.markdown("---")
        st.subheader("💥 Partner Retirement Accounts")
        st.info("Partner detected - enter retirement account balances for RMD calculations")

        col1, col2 = st.columns(2)
        with col1:
            partner_ira_balance = st.session_state.get('input_partner_ira_balance', 0.0)
            _display_currency("Partner IRA Balance", partner_ira_balance)

            partner_four01k_balance = st.session_state.get('input_partner_four01k_403b_balance', 0.0)
            _display_currency("Partner 401k/403b Balance", partner_four01k_balance)
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
        taxable_investments = st.session_state.get('input_taxable_investment_accounts', 0.0)
        _display_currency("Taxable Investment Accounts", taxable_investments)

        savings_account = st.session_state.get('input_high_yield_savings_account', 0.0)
        _display_currency("High-Yield Savings", savings_account)
    with col2:
        hsa_balance = st.session_state.get('input_hsa_balance', 0.0)
        _display_currency("HSA Balance", hsa_balance)

        five29_balance = st.session_state.get('input_five29_plan_balance', 0.0)
        _display_currency("529 Plan Balance", five29_balance)

    st.subheader("🎨 Other Assets")
    col1, col2, col3 = st.columns(3)
    with col1:
        vehicles = st.session_state.get('input_vehicles_value', 0.0)
        _display_currency("Vehicles Value", vehicles)
    with col2:
        jewelry = st.session_state.get('input_jewelry_collectibles_value', 0.0)
        _display_currency("Jewelry/Collectibles", jewelry)
    with col3:
        crypto = st.session_state.get('input_cryptocurrency_holdings', 0.0)
        _display_currency("Cryptocurrency", crypto)

    liquid_assets = (taxable_investments + savings_account + hsa_balance +
                    ira_balance + four01k_balance + pension_value +
                    partner_ira_balance + partner_four01k_balance)

    # Liabilities section
    st.header("💳 Liabilities")

    # Initialize ALL liability fields before widgets
    _init_float('input_mortgage_balance')
    _init_float('input_secondary_residence_mortgage')
    _init_float('input_auto_loan_balance')
    _init_float('input_student_loan_balance')
    _init_float('input_credit_card_debt')
    _init_float('input_other_liabilities')

    col1, col2 = st.columns(2)

    with col1:
        primary_mortgage = st.session_state.get('input_mortgage_balance', 0.0)
        _display_currency("Primary Mortgage Balance", primary_mortgage)

        secondary_mortgage = st.session_state.get('input_secondary_residence_mortgage', 0.0)
        _display_currency("Secondary Mortgage Balance", secondary_mortgage)

        auto_loans = st.session_state.get('input_auto_loan_balance', 0.0)
        _display_currency("Auto Loans", auto_loans)

    with col2:
        student_loans = st.session_state.get('input_student_loan_balance', 0.0)
        _display_currency("Student Loans", student_loans)

        credit_cards = st.session_state.get('input_credit_card_debt', 0.0)
        _display_currency("Credit Card Debt", credit_cards)

        personal_loans = st.session_state.get('input_other_liabilities', 0.0)
        _display_currency("Personal Loans", personal_loans)

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

    # Show custom expenses impact on surplus
    if custom_expenses_total > 0:
        st.info(f"ℹ️ Custom expenses (${custom_expenses_total:,.2f}/month) are included in your total expenses and surplus calculation")

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
                        placeholder="e.g., Retirement Fund, Down Payment",
                        disabled=True,
                        help="📝 Edit in INTAKE mode"
                    )
                    st.session_state['goals_list'][idx]['goal'] = goal_name

                with col2:
                    goal_amount = st.number_input(
                        "Target Amount ($):",
                        value=float(goal_data.get('amount', 0.0)),
                        min_value=0.0,
                        step=1000.0,
                        format="%.0f",
                        key=f"goal_amount_{idx}",
                        disabled=True,
                        help="📝 Edit in INTAKE mode"
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
                        max_value=2100,
                        step=1,
                        key=f"goal_year_{idx}",
                        disabled=True,
                        help="📝 Edit in INTAKE mode"
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

    # Get custom income from session state
    custom_income = st.session_state.get('custom_income', [])
    custom_income_total = sum(item.get('Monthly Amount', 0) for item in custom_income) if custom_income else 0.0

    # DEBUG: Check custom income calculation
    if custom_income:
        print(f"[FINANCIAL_INPUTS DEBUG] custom_income list has {len(custom_income)} items")
        for idx, item in enumerate(custom_income):
            print(f"  Item {idx}: {item.get('Name', 'N/A')} = ${item.get('Monthly Amount', 0):,.2f}/month")
        print(f"[FINANCIAL_INPUTS DEBUG] custom_income_total (MONTHLY) = ${custom_income_total:,.2f}")

    # Return all data (including custom expenses AND custom income)
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
        'partner_liabilities': 0,
        'custom_expenses': custom_expenses,
        'custom_expenses_total': custom_expenses_total,
        'custom_income': custom_income,
        'custom_income_total': custom_income_total
    }
