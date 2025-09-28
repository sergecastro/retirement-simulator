# ui_components.py - User Interface Components with Enhanced Scenario Management
import streamlit as st
import pandas as pd
import json
import os
from datetime import date

def setup_sidebar(is_trusted_user):
    """Setup sidebar with feature toggles"""
    st.sidebar.header("🚀 Advanced Features")
    
    features = {}
    
    # Financial Health Dashboard
    st.sidebar.markdown("**📊 Financial Health Dashboard**")
    features['show_health_dashboard'] = st.sidebar.checkbox("Financial Health Scoring", value=True)
    features['show_risk_analysis'] = st.sidebar.checkbox("Risk Analysis Matrix", value=True)
    
    # Interactive Planning
    st.sidebar.markdown("**🗓️ Interactive Timeline & Planning**")
    features['show_timeline'] = st.sidebar.checkbox("Interactive Family Timeline", value=True)
    features['show_scenario_comparison'] = st.sidebar.checkbox("Scenario Comparison Tool", value=True)
    features['show_family_events'] = st.sidebar.checkbox("Family Events Planning", value=True)
    
    # Visual Analytics
    st.sidebar.markdown("**📈 Visual Analytics Lab**")
    features['show_trajectories'] = st.sidebar.checkbox("Financial Trajectories", value=True)
    features['show_sankey'] = st.sidebar.checkbox("Cash-Flow Sankey", value=True)
    features['show_goals'] = st.sidebar.checkbox("Goal-Funding Gauges", value=True)
    features['show_calendar'] = st.sidebar.checkbox("Monthly Heatmap", value=False)
    
    # Advanced Simulations
    st.sidebar.markdown("**🎲 Advanced Simulations**")
    features['show_monte_carlo'] = st.sidebar.checkbox("Monte Carlo Analysis", value=True)
    features['show_stress_tests'] = st.sidebar.checkbox("Stress Testing", value=False)
    
    # AI Features (trusted users only)
    if is_trusted_user:
        st.sidebar.markdown("**🤖 AI Features**")
        features['show_ai_advisor'] = st.sidebar.checkbox("AI Financial Advisor", value=True)
        features['show_auto_optimization'] = st.sidebar.checkbox("Auto-Optimization", value=False)
    
    return features

def load_scenarios(filename="family_scenarios.json"):
    """Load scenarios from file"""
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            st.warning(f"Error loading scenarios: {e}")
            return {}
    return {}

def save_scenarios(scenarios_dict, filename="family_scenarios.json"):
    """Save scenarios to file"""
    try:
        # Create backup
        if os.path.exists(filename):
            backup_file = filename.replace('.json', '_backup.json')
            with open(filename, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
        
        # Save new data
        with open(filename, "w") as f:
            json.dump(scenarios_dict, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving scenarios: {e}")
        return False

def get_current_scenario_data():
    """Extract current form data into scenario format"""
    scenario_data = {}
    
    # Get all basic input values from session state
    for key, value in st.session_state.items():
        if key.startswith('input_'):
            field_name = key.replace('input_', '')
            scenario_data[field_name] = value
    
    # CAPTURE ALL THE NEW EXPENSE FIELDS - THIS WAS MISSING!
    expense_fields = [
        'housing_expenses', 'utilities', 'food_expenses', 'transportation',
        'healthcare', 'insurance', 'entertainment', 'dining_out', 
        'clothing', 'personal_care', 'subscriptions', 'other_expenses'
    ]
    
    for field in expense_fields:
        if f'input_{field}' in st.session_state:
            scenario_data[field] = st.session_state[f'input_{field}']
    
    # CAPTURE ALL MORTGAGE FIELDS - THIS WAS MISSING!
    mortgage_fields = ['mortgage_balance', 'mortgage_payment', 'mortgage_rate', 'mortgage_years']
    for field in mortgage_fields:
        if f'input_{field}' in st.session_state:
            scenario_data[field] = st.session_state[f'input_{field}']
    
    # CAPTURE COMPLEX DATA STRUCTURES
    # Children's college data
    if 'children_editor' in st.session_state and st.session_state.children_editor is not None:
        try:
            children_data = st.session_state.children_editor.to_dict(orient='records')
            scenario_data['children_data'] = children_data
        except:
            scenario_data['children_data'] = []
    
    # Inheritance events data  
    if 'inheritance_editor' in st.session_state and st.session_state.inheritance_editor is not None:
        try:
            inheritance_data = st.session_state.inheritance_editor.to_dict(orient='records')
            scenario_data['inheritance_data'] = inheritance_data
        except:
            scenario_data['inheritance_data'] = []
    
    # Goals data
    if 'goals_editor' in st.session_state and st.session_state.goals_editor is not None:
        try:
            goals_data = st.session_state.goals_editor.to_dict(orient='records')
            scenario_data['goals_data'] = goals_data
        except:
            scenario_data['goals_data'] = []
    
    return scenario_data

def load_scenario_into_session(scenario_data):
    """Load scenario data into session state"""
    # Load basic input fields INCLUDING new expense and mortgage fields
    for key, value in scenario_data.items():
        if key not in ['children_data', 'inheritance_data', 'goals_data']:  # Skip complex data
            st.session_state[f"input_{key}"] = value
    
    # RESTORE COMPLEX DATA STRUCTURES
    # Children's college data
    if 'children_data' in scenario_data and scenario_data['children_data']:
        try:
            children_df = pd.DataFrame(scenario_data['children_data'])
            # Ensure all required columns exist
            required_cols = ['Name', 'Birth Year', 'College Plan', 'Start Age', 'Years', 'Scholarship %', 'Use 529 First']
            for col in required_cols:
                if col not in children_df.columns:
                    if col == 'Name':
                        children_df[col] = ""
                    elif col in ['Birth Year', 'Start Age', 'Years']:
                        children_df[col] = 2010 if col == 'Birth Year' else (18 if col == 'Start Age' else 4)
                    elif col == 'College Plan':
                        children_df[col] = "None"
                    elif col == 'Scholarship %':
                        children_df[col] = 0.0
                    elif col == 'Use 529 First':
                        children_df[col] = True
            st.session_state['children_editor'] = children_df
        except Exception as e:
            st.warning(f"Error loading children data: {e}")
    
    # Inheritance data
    if 'inheritance_data' in scenario_data and scenario_data['inheritance_data']:
        try:
            inheritance_df = pd.DataFrame(scenario_data['inheritance_data'])
            # Ensure required columns
            required_cols = ['Year', 'Amount', 'Description']
            for col in required_cols:
                if col not in inheritance_df.columns:
                    if col == 'Year':
                        inheritance_df[col] = date.today().year + 10
                    elif col == 'Amount':
                        inheritance_df[col] = 0.0
                    else:
                        inheritance_df[col] = ""
            st.session_state['inheritance_editor'] = inheritance_df
        except Exception as e:
            st.warning(f"Error loading inheritance data: {e}")
    
    # Goals data
    if 'goals_data' in scenario_data and scenario_data['goals_data']:
        try:
            goals_df = pd.DataFrame(scenario_data['goals_data'])
            # Ensure required columns
            required_cols = ['Goal Name', 'Target Amount', 'Target Year', 'Priority', 'Notes']
            for col in required_cols:
                if col not in goals_df.columns:
                    if col == 'Goal Name':
                        goals_df[col] = ""
                    elif col == 'Target Amount':
                        goals_df[col] = 0.0
                    elif col == 'Target Year':
                        goals_df[col] = date.today().year + 10
                    elif col == 'Priority':
                        goals_df[col] = "High"
                    else:
                        goals_df[col] = ""
            st.session_state['goals_editor'] = goals_df
        except Exception as e:
            st.warning(f"Error loading goals data: {e}")

def manage_scenarios(is_trusted_user):
    """Enhanced scenario loading and saving with SAFE data protection"""
    st.header("📂 Scenario Management")
    
    # CRITICAL: Use different files for different user types to prevent data loss
    if is_trusted_user:
        scenario_file = "family_scenarios.json"  # Your personal data
        st.info("🔐 TRUSTED MODE: Loading your personal retirement scenarios")
    else:
        scenario_file = "demo_scenarios.json"  # Demo data only
        st.info("📌 DEMO MODE: Using demo scenarios only")
    
    # SAFE LOADING: Load scenarios with proper fallback
    if is_trusted_user:
        # For trusted users: Load from file OR use embedded backup
        if os.path.exists(scenario_file):
            try:
                with open(scenario_file, "r") as f:
                    saved_scenarios = json.load(f)
                st.success(f"✅ Loaded personal scenarios from {scenario_file}")
            except Exception as e:
                st.error(f"Error loading {scenario_file}: {e}")
                # SAFE FALLBACK: Use your original embedded data
                saved_scenarios = get_trusted_user_fallback_scenarios()
                st.warning("⚠️ Using embedded backup scenarios due to file error")
        else:
            # File doesn't exist - use your original embedded data
            saved_scenarios = get_trusted_user_fallback_scenarios()
            st.info(f"📂 {scenario_file} not found. Using embedded personal scenarios.")
            # Optionally save the embedded scenarios to file
            if st.button("💾 Save Embedded Scenarios to File"):
                if save_scenarios(saved_scenarios, scenario_file):
                    st.success(f"✅ Saved embedded scenarios to {scenario_file}")
    else:
        # For demo users: Always use embedded demo scenarios (never touch your file)
        saved_scenarios = get_demo_user_scenarios()
    
    # Scenario selection and management interface
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        scenario_names = list(saved_scenarios.keys()) + ["🆕 Create New Scenario"]
        selected_scenario = st.selectbox("📁 Select Scenario:", scenario_names)
    
    # Load selected scenario
    if selected_scenario != "🆕 Create New Scenario" and selected_scenario in saved_scenarios:
        if st.button("📂 Load Selected", key="load_scenario"):
            scenario_data = saved_scenarios[selected_scenario]
            load_scenario_into_session(scenario_data)
            st.success(f"✅ Loaded: {selected_scenario}")
            st.rerun()
    
    # SAFE SAVE: Only allow trusted users to modify personal scenarios
    if is_trusted_user:
        with col2:
            if st.button("💾 Save Current", key="save_current"):
                current_data = get_current_scenario_data()
                if current_data:
                    if selected_scenario == "🆕 Create New Scenario":
                        save_name = f"Scenario_{date.today().strftime('%m-%d-%Y')}_{len(saved_scenarios)+1}"
                    else:
                        save_name = selected_scenario
                    
                    saved_scenarios[save_name] = current_data
                    if save_scenarios(saved_scenarios, scenario_file):
                        st.success(f"✅ Saved: {save_name}")
                        st.rerun()
                else:
                    st.warning("⚠️ No data to save")
        
        with col3:
            new_scenario_name = st.text_input("💾 Save As:", placeholder="My_Scenario_Name", key="new_scenario_name")
            if st.button("💾 Save As", key="save_as"):
                if new_scenario_name.strip():
                    current_data = get_current_scenario_data()
                    if current_data:
                        saved_scenarios[new_scenario_name.strip()] = current_data
                        if save_scenarios(saved_scenarios, scenario_file):
                            st.success(f"✅ Saved as: {new_scenario_name}")
                            st.rerun()
                    else:
                        st.warning("⚠️ No data to save")
                else:
                    st.warning("⚠️ Enter scenario name")
        
        with col4:
            if st.button("🗑️ Delete", key="delete_scenario"):
                if selected_scenario != "🆕 Create New Scenario" and selected_scenario in saved_scenarios:
                    del saved_scenarios[selected_scenario]
                    if save_scenarios(saved_scenarios, scenario_file):
                        st.success(f"🗑️ Deleted: {selected_scenario}")
                        st.rerun()
    else:
        st.info("💾 Demo mode: Scenario saving disabled to protect personal data")
    
    # Show scenario info
    if selected_scenario != "🆕 Create New Scenario" and selected_scenario in saved_scenarios:
        with st.expander("📋 Scenario Details"):
            scenario_data = saved_scenarios[selected_scenario]
            # Show key values only, not full JSON
            st.write(f"**Age:** {scenario_data.get('age', 'N/A')}")
            st.write(f"**Partner:** {scenario_data.get('partner_name', 'None')}")
            st.write(f"**Total Income:** ${scenario_data.get('total_income', 0):,.2f}")
            st.write(f"**Primary Residence:** ${scenario_data.get('primary_residence_value', 0):,.2f}")
            st.write(f"**IRA Balance:** ${scenario_data.get('ira_balance', 0):,.2f}")
    
    return saved_scenarios.get(selected_scenario, {})

def get_trusted_user_fallback_scenarios():
    """Your original 70+ retirement scenario data"""
    return {
        "70+ Retirement Scenario (Private)": {
            "input_style": "Detailed Breakdown",
            "age_group": "70+",
            "age": 76,
            "partner_name": "Judith",
            "partner_exists": True,
            "partner_age": 74,
            "partner_ira_balance": 0.0,
            "partner_four01k_403b_balance": 0.0,
            "partner_taxable_investment_accounts": 0.0,
            "partner_other_assets": 0.0,
            "partner_liabilities": 0.0,
            "salary_wages": 0.0,
            "self_employment_income": 0.0,
            "rental_income": 2000.0,
            "investment_income": 0.0,
            "social_security_income": 3600.0,
            "pension_income": 6000.0,
            "other_income": 0.0,
            "total_income": 11600.0,
            "housing_expenses": 700.0,
            "utilities_expenses": 1000.0,
            "groceries_expenses": 2000.0,
            "transportation_expenses": 1500.0,
            "healthcare_expenses": 150.0,
            "insurance_expenses": 700.0,
            "real_estate_insurance_expenses": 1300.0,
            "property_tax_expenses": 1850.0,
            "entertainment_expenses": 50.0,
            "restaurant_expenses": 500.0,
            "travel_expenses": 300.0,
            "education_expenses": 0.0,
            "childcare_expenses": 0.0,
            "clothing_expenses": 100.0,
            "charitable_donations": 0.0,
            "miscellaneous_expenses": 0.0,
            "other_expenses": 1000.0,
            "total_expenses": 11150.0,
            "primary_residence_value": 2700000.0,
            "secondary_residence_value": 1700000.0,
            "ira_balance": 400000.0,
            "four01k_403b_balance": 0.0,
            "taxable_investment_accounts": 0.0,
            "pension_fund_value": 1400000.0,
            "life_insurance_cash_value": 0.0,
            "high_yield_savings_account": 0.0,
            "hsa_balance": 0.0,
            "five29_plan_balance": 0.0,
            "vehicles_value": 0.0,
            "jewelry_collectibles_value": 0.0,
            "business_ownership_value": 0.0,
            "cryptocurrency_holdings": 0.0,
            "other_assets": 0.0,
            "primary_residence_mortgage": 0.0,
            "secondary_residence_mortgage": 0.0,
            "auto_loans": 0.0,
            "student_loans": 0.0,
            "credit_card_debt": 0.0,
            "personal_loans": 0.0,
            "business_loans": 0.0,
            "other_liabilities": 0.0,
            "tax_rate": 25.0,
            "inflation_rate": 2.5,
            "investment_return_rate": 5.0,
            "simulation_years": 14
        }
    }

def get_demo_user_scenarios():
    """Demo scenarios for public users"""
    return {
        "Demo Scenario": {
            "age": 35,
            "partner_name": "",
            "total_income": 5000.0,
            "total_expenses": 4400.0,
            "ira_balance": 50000.0,
            "four01k_403b_balance": 75000.0,
            "primary_residence_value": 400000.0,
            "primary_residence_mortgage": 300000.0
        }
    }


def collect_user_inputs():
    """Collect basic user information"""
    st.header("👤 User Information")
    
    age = st.number_input(
        "Your Age:",
        min_value=18,
        max_value=110,
        value=st.session_state.get("input_age", 35),
        key="input_age"
    )
    
    partner_name = st.text_input(
        "Partner's Name (leave blank if none):",
        value=st.session_state.get("input_partner_name", ""),
        key="input_partner_name"
    )
    
    partner_exists = bool(partner_name.strip())
    
    partner_age = None
    if partner_exists:
        partner_age = st.number_input(
            f"{partner_name}'s Age:",
            min_value=18,
            max_value=110,
            value=st.session_state.get("input_partner_age", 35),
            key="input_partner_age"
        )
    
    return {
        'age': age,
        'partner_name': partner_name,
        'partner_exists': partner_exists,
        'partner_age': partner_age if partner_age else age
    }

def collect_financial_data():
    """Collect financial information"""
    st.header("💰 Financial Information")
    
    # INCOME SECTION - Organized and Compact
    with st.expander("📈 Monthly Income Sources", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            salary = st.number_input("Salary/Wages:", value=st.session_state.get("input_salary_wages", 0.0), key="input_salary_wages")
            rental = st.number_input("Rental Income:", value=st.session_state.get("input_rental_income", 0.0), key="input_rental_income")
        with col2:
            ss = st.number_input("Social Security:", value=st.session_state.get("input_social_security_income", 0.0), key="input_social_security_income")
            pension = st.number_input("Pension:", value=st.session_state.get("input_pension_income", 0.0), key="input_pension_income")
        with col3:
            investment = st.number_input("Investment Income:", value=st.session_state.get("input_investment_income", 0.0), key="input_investment_income")
            other = st.number_input("Other Income:", value=st.session_state.get("input_other_income", 0.0), key="input_other_income")
        
        total_income = salary + rental + ss + pension + investment + other
        st.markdown(f"**💚 TOTAL MONTHLY INCOME: ${total_income:,.2f}**")
    
    # DETAILED EXPENSES SECTION - Restored Multiple Fields
    with st.expander("📉 Monthly Expense Breakdown", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            housing = st.number_input("Housing/Rent:", value=st.session_state.get("input_housing_expenses", 0.0), key="input_housing_expenses")
            utilities = st.number_input("Utilities:", value=st.session_state.get("input_utilities", 0.0), key="input_utilities")
            food = st.number_input("Food/Groceries:", value=st.session_state.get("input_food_expenses", 0.0), key="input_food_expenses")
            transportation = st.number_input("Transportation:", value=st.session_state.get("input_transportation", 0.0), key="input_transportation")
        with col2:
            healthcare = st.number_input("Healthcare/Medical:", value=st.session_state.get("input_healthcare", 0.0), key="input_healthcare")
            insurance = st.number_input("Insurance:", value=st.session_state.get("input_insurance", 0.0), key="input_insurance")
            entertainment = st.number_input("Entertainment:", value=st.session_state.get("input_entertainment", 0.0), key="input_entertainment")
            dining = st.number_input("Dining Out:", value=st.session_state.get("input_dining_out", 0.0), key="input_dining_out")
        with col3:
            clothing = st.number_input("Clothing:", value=st.session_state.get("input_clothing", 0.0), key="input_clothing")
            personal_care = st.number_input("Personal Care:", value=st.session_state.get("input_personal_care", 0.0), key="input_personal_care")
            subscriptions = st.number_input("Subscriptions/Memberships:", value=st.session_state.get("input_subscriptions", 0.0), key="input_subscriptions")
            other_expenses = st.number_input("Other Expenses:", value=st.session_state.get("input_other_expenses", 0.0), key="input_other_expenses")
        
        total_expenses = housing + utilities + food + transportation + healthcare + insurance + entertainment + dining + clothing + personal_care + subscriptions + other_expenses
        st.markdown(f"**🔴 TOTAL MONTHLY EXPENSES: ${total_expenses:,.2f}**")
        st.markdown(f"**🎯 MONTHLY SURPLUS: ${total_income - total_expenses:,.2f}**")
    
    # ASSETS SECTION - Organized by Type
    with st.expander("💎 Assets Portfolio", expanded=True):
        st.markdown("**🏠 Real Estate**")
        col1, col2 = st.columns(2)
        with col1:
            primary_home = st.number_input("Primary Residence:", value=st.session_state.get("input_primary_residence_value", 0.0), key="input_primary_residence_value")
        with col2:
            secondary_home = st.number_input("Secondary Residence:", value=st.session_state.get("input_secondary_residence_value", 0.0), key="input_secondary_residence_value")
        
        st.markdown("**🏦 Retirement Accounts**")
        col1, col2 = st.columns(2)
        with col1:
            ira = st.number_input("IRA Balance:", value=st.session_state.get("input_ira_balance", 0.0), key="input_ira_balance")
            four01k = st.number_input("401k Balance:", value=st.session_state.get("input_four01k_403b_balance", 0.0), key="input_four01k_403b_balance")
        with col2:
            partner_ira = st.number_input("Partner IRA:", value=st.session_state.get("input_partner_ira_balance", 0.0), key="input_partner_ira_balance")
            partner_401k = st.number_input("Partner 401k:", value=st.session_state.get("input_partner_four01k_403b_balance", 0.0), key="input_partner_four01k_403b_balance")
        
        st.markdown("**💰 Liquid Assets**")
        col1, col2 = st.columns(2)
        with col1:
            taxable = st.number_input("Taxable Investments:", value=st.session_state.get("input_taxable_investment_accounts", 0.0), key="input_taxable_investment_accounts")
            savings = st.number_input("Savings Account:", value=st.session_state.get("input_high_yield_savings_account", 0.0), key="input_high_yield_savings_account")
        with col2:
            partner_taxable = st.number_input("Partner Taxable Investments:", value=st.session_state.get("input_partner_taxable_investment_accounts", 0.0), key="input_partner_taxable_investment_accounts")
            other_assets = st.number_input("Other Assets:", value=st.session_state.get("input_other_assets", 0.0), key="input_other_assets")
        
        st.markdown("**📊 Special Assets**")
        col1, col2 = st.columns(2)
        with col1:
            pension_value = st.number_input("Pension Value:", value=st.session_state.get("input_pension_fund_value", 0.0), key="input_pension_fund_value")
        with col2:
            life_insurance = st.number_input("Life Insurance Cash Value:", value=st.session_state.get("input_life_insurance_cash_value", 0.0), key="input_life_insurance_cash_value")
        
        total_assets = primary_home + secondary_home + ira + four01k + partner_ira + partner_401k + taxable + savings + partner_taxable + other_assets + pension_value + life_insurance
        st.markdown(f"**💚 TOTAL ASSETS: ${total_assets:,.2f}**")
    
    # LIABILITIES SECTION
    with st.expander("📉 Liabilities & Debt", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            mortgage = st.number_input("Primary Mortgage Balance:", value=st.session_state.get("input_primary_residence_mortgage", 0.0), key="input_primary_residence_mortgage")
            auto = st.number_input("Auto Loans:", value=st.session_state.get("input_auto_loans", 0.0), key="input_auto_loans")
        with col2:
            student = st.number_input("Student Loans:", value=st.session_state.get("input_student_loans", 0.0), key="input_student_loans")
            credit = st.number_input("Credit Card Debt:", value=st.session_state.get("input_credit_card_debt", 0.0), key="input_credit_card_debt")
        
        total_liabilities = mortgage + auto + student + credit
        st.markdown(f"**🔴 TOTAL LIABILITIES: ${total_liabilities:,.2f}**")
        st.markdown(f"**🎯 NET WORTH: ${total_assets - total_liabilities:,.2f}**")
    
    # MORTGAGE INTEGRATION MODULE - More Compact
    with st.expander("🏠 Detailed Mortgage Analysis", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            mortgage_balance = st.number_input("Current Loan Balance:", value=st.session_state.get("input_mortgage_balance", 0.0), key="input_mortgage_balance")
            mortgage_payment = st.number_input("Monthly Payment:", value=st.session_state.get("input_mortgage_payment", 0.0), key="input_mortgage_payment")
        with col2:
            mortgage_rate = st.number_input("Interest Rate (%):", value=st.session_state.get("input_mortgage_rate", 4.5), key="input_mortgage_rate")
            mortgage_years = st.number_input("Years Remaining:", value=st.session_state.get("input_mortgage_years", 25), key="input_mortgage_years")
        
        # Calculate and show mortgage info more compactly
        if mortgage_balance > 0 and mortgage_rate > 0:
            monthly_rate = mortgage_rate / 100 / 12
            total_payments = mortgage_years * 12
            if monthly_rate > 0:
                calculated_payment = mortgage_balance * (monthly_rate * (1 + monthly_rate)**total_payments) / ((1 + monthly_rate)**total_payments - 1)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Calculated Payment", f"${calculated_payment:,.2f}")
                with col2:
                    total_interest = calculated_payment * total_payments - mortgage_balance
                    st.metric("Total Interest", f"${total_interest:,.0f}")
    
    # Goals Collection - Made more prominent
    goals_data = collect_financial_goals()
    
    # Calculate totals for return
    liquid_assets = ira + four01k + taxable + savings + partner_ira + partner_401k + partner_taxable
    
    # Include mortgage details in return
    mortgage_details = {
        'balance': st.session_state.get("input_mortgage_balance", mortgage),
        'payment': st.session_state.get("input_mortgage_payment", 0.0),
        'rate': st.session_state.get("input_mortgage_rate", 4.5),
        'years_remaining': st.session_state.get("input_mortgage_years", 25)
    }
    
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'monthly_surplus': total_income - total_expenses,
        'primary_residence_value': primary_home,
        'secondary_residence_value': secondary_home,
        'ira_balance': ira,
        'four01k_403b_balance': four01k,
        'taxable_investment_accounts': taxable,
        'high_yield_savings_account': savings,
        'pension_fund_value': pension_value,
        'life_insurance_cash_value': life_insurance,
        'partner_ira_balance': partner_ira,
        'partner_four01k_403b_balance': partner_401k,
        'partner_taxable_investment_accounts': partner_taxable,
        'total_liabilities': total_liabilities,
        'total_assets': total_assets,
        'liquid_assets': liquid_assets,
        'mortgage_details': mortgage_details,
        'goal_costs': goals_data
    }

def collect_financial_goals():
    """Collect financial goals information"""
    st.header("🎯 Financial Goals")
    
    st.markdown("""
    **Define specific financial targets with amounts and timelines.**
    Examples: Retirement Fund, Emergency Fund, Home Down Payment, Children's Education, etc.
    """)
    
    goals_data = st.data_editor(
        pd.DataFrame([{
            "Goal Name": "", 
            "Target Amount": 0.0,
            "Target Year": date.today().year + 10,
            "Priority": "High",
            "Notes": ""
        }]),
        num_rows="dynamic",
        key="goals_editor",
        column_config={
            "Target Amount": st.column_config.NumberColumn(
                "Target Amount ($)",
                min_value=0.0,
                step=1000.0,
                format="$%.0f"
            ),
            "Target Year": st.column_config.NumberColumn(
                "Target Year",
                min_value=date.today().year,
                max_value=date.today().year + 50,
                step=1
            ),
            "Priority": st.column_config.SelectboxColumn(
                "Priority",
                options=["High", "Medium", "Low"],
                required=True,
            ),
            "Notes": st.column_config.TextColumn(
                "Notes",
                max_chars=100
            )
        }
    )
    
    # Convert to goal_costs format for compatibility
    goal_costs = {}
    for goal in goals_data.to_dict(orient='records'):
        if goal.get('Goal Name') and goal.get('Target Amount', 0) > 0:
            goal_costs[goal['Goal Name']] = {
                'target': goal['Target Amount'],
                'year': goal.get('Target Year', date.today().year + 10),
                'priority': goal.get('Priority', 'Medium'),
                'notes': goal.get('Notes', '')
            }

    return goal_costs

def collect_family_events():
    """Collect family event data"""
    st.header("👨‍👩‍👧‍👦 Family Events")
    
    # Children data
    st.subheader("🎓 Children & Education")
    
    # Explain College Plan options
    with st.expander("ℹ️ College Plan Options Explained"):
        st.markdown("""
        **College Plan Choices:**
        - **None** → No college expenses planned
        - **Public In-State** → State university (resident tuition)
        - **Public Out-of-State** → State university (non-resident tuition)  
        - **Private** → Private university (highest cost)
        
        **Other Fields:**
        - **Start Age:** When they start college (usually 18)
        - **Years:** Duration of studies (usually 4)
        - **Scholarship %:** Percentage covered by scholarships (0-100%)
        - **Use 529 First:** Whether to use 529 education savings first
        """)
    
    # Create template with dropdown options
    college_options = ["None", "Public In-State", "Public Out-of-State", "Private"]
    
    children_data = st.data_editor(
        pd.DataFrame([{
            "Name": "", 
            "Birth Year": date.today().year - 5, 
            "College Plan": "None",
            "Start Age": 18,
            "Years": 4,
            "Scholarship %": 0.0,
            "Use 529 First": True
        }]),
        num_rows="dynamic",
        key="children_editor",
        column_config={
            "College Plan": st.column_config.SelectboxColumn(
                "College Plan",
                options=college_options,
                required=True,
            ),
            "Scholarship %": st.column_config.NumberColumn(
                "Scholarship %",
                min_value=0.0,
                max_value=100.0,
                step=5.0,
                format="%.1f%%"
            )
        }
    )
    
    # College costs
    col1, col2 = st.columns(2)
    with col1:
        college_inflation = st.number_input("College Inflation Rate (%):", value=4.0)
        public_in = st.number_input("Public In-State Annual Cost:", value=20000.0)
    with col2:
        public_out = st.number_input("Public Out-of-State Annual Cost:", value=40000.0)
        private = st.number_input("Private College Annual Cost:", value=60000.0)
    
    # Inheritance Events
    st.subheader("💰 Inheritance Events")
    inheritance_data = st.data_editor(
        pd.DataFrame([{"Year": date.today().year + 10, "Amount": 0.0, "Description": ""}]),
        num_rows="dynamic",
        key="inheritance_editor",
        column_config={
            "Amount": st.column_config.NumberColumn(
                "Amount ($)",
                min_value=0.0,
                step=1000.0,
                format="$%.0f"
            ),
            "Year": st.column_config.NumberColumn(
                "Year",
                min_value=date.today().year,
                max_value=date.today().year + 50,
                step=1
            )
        }
    )
    
    return {
        'children': children_data.to_dict(orient='records'),
        'inheritances': inheritance_data.to_dict(orient='records'),
        'college_inflation_pct': college_inflation,
        'base_public_in': public_in,
        'base_public_out': public_out,
        'base_private': private
    }

def get_simulation_parameters(show_monte_carlo):
    """Get simulation parameters"""
    st.header("⚙️ Simulation Parameters")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tax_rate = st.number_input("Tax Rate (%):", value=st.session_state.get("input_tax_rate", 22.0), key="input_tax_rate")
        inflation_rate = st.number_input("Inflation (%):", value=st.session_state.get("input_inflation_rate", 3.0), key="input_inflation_rate")
    with col2:
        return_rate = st.number_input("Return Rate (%):", value=st.session_state.get("input_investment_return_rate", 7.0), key="input_investment_return_rate")
        years = st.number_input("Years:", value=st.session_state.get("input_simulation_years", 30), key="input_simulation_years")
    with col3:
        if show_monte_carlo:
            mc_iters = st.number_input("Monte Carlo Iterations:", value=1000, min_value=0, max_value=10000, step=100)
        else:
            mc_iters = 0
    
    return {
        'tax_rate': tax_rate,
        'inflation_rate': inflation_rate,
        'investment_return_rate': return_rate,
        'simulation_years': years,
        'mc_iterations': mc_iters
    }