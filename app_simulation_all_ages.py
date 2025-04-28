import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
from openai import OpenAI

# Title
st.title("Retirement Simulation App")

# Scenario Management
st.header("🗂️ Scenario Management")
scenario_file = "saved_scenarios.json"

# Load existing scenarios
if os.path.exists(scenario_file):
    with open(scenario_file, "r") as f:
        saved_scenarios = json.load(f)
else:
    saved_scenarios = {}

# Scenario selector
scenario_name = st.selectbox("Select Scenario:", ["New Scenario"] + list(saved_scenarios.keys()))
if scenario_name != "New Scenario":
    inputs = saved_scenarios[scenario_name]
else:
    inputs = {}

# Clear saved data and session state
if st.button("Clear Saved Data and Session State"):
    if os.path.exists(scenario_file):
        os.remove(scenario_file)
    st.session_state.clear()
    st.success("All saved data and session state cleared!")
    st.rerun()

# Preferences
st.header("🧹 Preferences")
input_style = st.radio("Input Style:", ["Detailed Breakdown", "Gross Totals"], index=0 if inputs.get("input_style", "Detailed Breakdown") == "Detailed Breakdown" else 1)

# Primary User Age
st.header("👤 Primary User Information")
age_group = st.selectbox("Age Group:", ["25-55", "55-70", "70+"], index=0 if inputs.get("age_group", "25-55") == "25-55" else (1 if inputs.get("age_group") == "55-70" else 2))
default_age = inputs.get("age", 40 if age_group == "25-55" else 60 if age_group == "55-70" else 76)
age = st.number_input("Starting Age:", min_value=25, max_value=110, value=default_age)

# Partner Information
st.header("👥 Partner Information")
partner_name = st.text_input("Partner's Name:", value=inputs.get("partner_name", ""))
partner_age = st.number_input("Partner's Age:", min_value=25, max_value=110, value=inputs.get("partner_age", age))
partner_ira_balance = st.number_input("Partner's IRA Balance:", value=inputs.get("partner_ira_balance", 0.0))
partner_four01k_403b_balance = st.number_input("Partner's 401k/403b Balance:", value=inputs.get("partner_four01k_403b_balance", 0.0))
partner_taxable_investment_accounts = st.number_input("Partner's Taxable Investment Accounts:", value=inputs.get("partner_taxable_investment_accounts", 0.0))
partner_other_assets = st.number_input("Partner's Other Assets (Savings, Vehicles, Collectibles):", value=inputs.get("partner_other_assets", 0.0))
partner_liabilities = st.number_input("Partner's Liabilities (Mortgage, Loans, Credit Card Debt):", value=inputs.get("partner_liabilities", 0.0))

# Income & Expenses (Monthly)
st.header("💵 Income & Expenses (Monthly)")
if input_style == "Detailed Breakdown":
    st.subheader("Income")
    salary_wages = st.number_input("Salary/Wages:", value=inputs.get("salary_wages", 0.0))
    self_employment_income = st.number_input("Self-Employment Income:", value=inputs.get("self_employment_income", 0.0))
    rental_income = st.number_input("Rental Income:", value=inputs.get("rental_income", 0.0))
    investment_income = st.number_input("Investment Income:", value=inputs.get("investment_income", 0.0))
    social_security_income = st.number_input("Social Security Income:", value=inputs.get("social_security_income", 0.0))
    pension_income = st.number_input("Pension Income:", value=inputs.get("pension_income", 0.0))
    other_income = st.number_input("Other Income:", value=inputs.get("other_income", 0.0))

    total_income = salary_wages + self_employment_income + rental_income + investment_income + social_security_income + pension_income + other_income
    st.write(f"Total Income (Monthly): ${total_income:,.2f}")

    st.subheader("Expenses")
    housing_expenses = st.number_input("Housing Expenses (Rent, Mortgage, Maintenance, Excluding Insurance):", value=inputs.get("housing_expenses", 0.0))
    utilities_expenses = st.number_input("Utilities Expenses (Electricity, Gas, Water, Telephone):", value=inputs.get("utilities_expenses", 0.0))
    groceries_expenses = st.number_input("Groceries Expenses:", value=inputs.get("groceries_expenses", 0.0))
    transportation_expenses = st.number_input("Transportation Expenses (Car Gas, Insurance, Maintenance):", value=inputs.get("transportation_expenses", 0.0))
    healthcare_expenses = st.number_input("Healthcare Expenses (Medical Bills, Prescriptions):", value=inputs.get("healthcare_expenses", 0.0))
    insurance_expenses = st.number_input("Insurance Expenses (Health, Life Insurance):", value=inputs.get("insurance_expenses", 0.0))
    real_estate_insurance_expenses = st.number_input("Real Estate Insurance Expenses (Homeowners, Renters Insurance):", value=inputs.get("real_estate_insurance_expenses", 0.0))
    property_tax_expenses = st.number_input("Property Tax Expenses:", value=inputs.get("property_tax_expenses", 0.0))
    entertainment_expenses = st.number_input("Entertainment Expenses (Movies, Concerts, Subscriptions):", value=inputs.get("entertainment_expenses", 0.0))
    restaurant_expenses = st.number_input("Restaurant Expenses:", value=inputs.get("restaurant_expenses", 0.0))
    travel_expenses = st.number_input("Travel Expenses (Vacations, Flights, Hotels):", value=inputs.get("travel_expenses", 0.0))
    education_expenses = st.number_input("Education Expenses (Tuition, Books, Courses):", value=inputs.get("education_expenses", 0.0))
    childcare_expenses = st.number_input("Childcare Expenses:", value=inputs.get("childcare_expenses", 0.0))
    clothing_expenses = st.number_input("Clothing Expenses:", value=inputs.get("clothing_expenses", 0.0))
    charitable_donations = st.number_input("Charitable Donations:", value=inputs.get("charitable_donations", 0.0))
    miscellaneous_expenses = st.number_input("Miscellaneous Expenses (Unexpected Costs, Gifts):", value=inputs.get("miscellaneous_expenses", 0.0))
    other_expenses = st.number_input("Other Expenses:", value=inputs.get("other_expenses", 0.0))

    total_expenses = (housing_expenses + utilities_expenses + groceries_expenses + transportation_expenses +
                      healthcare_expenses + insurance_expenses + real_estate_insurance_expenses + property_tax_expenses +
                      entertainment_expenses + restaurant_expenses + travel_expenses + education_expenses +
                      childcare_expenses + clothing_expenses + charitable_donations + miscellaneous_expenses + other_expenses)
    st.write(f"Total Expenses (Monthly): ${total_expenses:,.2f}")
else:
    total_income = st.number_input("Total Income (Monthly):", value=inputs.get("total_income", 0.0))
    st.write(f"Total Income (Monthly): ${total_income:,.2f}")
    total_expenses = st.number_input("Total Expenses (Monthly):", value=inputs.get("total_expenses", 0.0))
    st.write(f"Total Expenses (Monthly): ${total_expenses:,.2f}")

# Assets & Liabilities (Primary User)
st.header("💰 Assets & Liabilities (Primary User)")
st.subheader("Assets")
primary_residence_value = st.number_input("Primary Residence Value:", value=inputs.get("primary_residence_value", 0.0))
secondary_residence_value = st.number_input("Secondary Residence Value:", value=inputs.get("secondary_residence_value", 0.0))
ira_balance = st.number_input("IRA Balance (Shared):", value=inputs.get("ira_balance", 0.0))
four01k_403b_balance = st.number_input("401k/403b Balance (Shared):", value=inputs.get("four01k_403b_balance", 0.0))
taxable_investment_accounts = st.number_input("Taxable Investment Accounts:", value=inputs.get("taxable_investment_accounts", 0.0))
pension_fund_value = st.number_input("Pension Fund Value (Savings from Employer Pension Plans, Shared):", value=inputs.get("pension_fund_value", 0.0))
life_insurance_cash_value = st.number_input("Life Insurance Cash Value:", value=inputs.get("life_insurance_cash_value", 0.0))
high_yield_savings_account = st.number_input("High-Yield Savings Account:", value=inputs.get("high_yield_savings_account", 0.0))
hsa_balance = st.number_input("HSA Balance (Health Savings Account):", value=inputs.get("hsa_balance", 0.0))
five29_plan_balance = st.number_input("529 Plan Balance (Education Savings):", value=inputs.get("five29_plan_balance", 0.0))
vehicles_value = st.number_input("Vehicles Value:", value=inputs.get("vehicles_value", 0.0))
jewelry_collectibles_value = st.number_input("Jewelry/Collectibles Value:", value=inputs.get("jewelry_collectibles_value", 0.0))
business_ownership_value = st.number_input("Business Ownership Value:", value=inputs.get("business_ownership_value", 0.0))
cryptocurrency_holdings = st.number_input("Cryptocurrency Holdings:", value=inputs.get("cryptocurrency_holdings", 0.0))
other_assets = st.number_input("Other Assets (Savings, Other Investments):", value=inputs.get("other_assets", 0.0))

st.subheader("Liabilities")
primary_residence_mortgage = st.number_input("Primary Residence Mortgage:", value=inputs.get("primary_residence_mortgage", 0.0))
secondary_residence_mortgage = st.number_input("Secondary Residence Mortgage:", value=inputs.get("secondary_residence_mortgage", 0.0))
auto_loans = st.number_input("Auto Loans:", value=inputs.get("auto_loans", 0.0))
student_loans = st.number_input("Student Loans:", value=inputs.get("student_loans", 0.0))
credit_card_debt = st.number_input("Credit Card Debt:", value=inputs.get("credit_card_debt", 0.0))
personal_loans = st.number_input("Personal Loans:", value=inputs.get("personal_loans", 0.0))
business_loans = st.number_input("Business Loans:", value=inputs.get("business_loans", 0.0))
other_liabilities = st.number_input("Other Liabilities (Other Debts):", value=inputs.get("other_liabilities", 0.0))

# Simulation Settings
st.header("⚙️ Simulation Settings")
tax_rate = st.number_input("Tax Rate (%):", value=inputs.get("tax_rate", 25.0))
inflation_rate = st.number_input("Inflation Rate (%):", value=inputs.get("inflation_rate", 2.5))
investment_return_rate = st.number_input("Investment Return Rate (%):", value=inputs.get("investment_return_rate", 5.0))
simulation_years = st.number_input("Simulation Years:", value=inputs.get("simulation_years", 35))

# OpenAI API Key Input
st.header("🤖 OpenAI Financial Assessment")
# Retrieve API key from secrets
openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
if not openai_api_key:
    st.error("OpenAI API Key not found in secrets. Please configure it in Streamlit Community Cloud.")
    st.stop()
use_openai = st.checkbox("Enable OpenAI Assessment", value=False)

# Monte Carlo Settings
st.header("🎲 Monte Carlo Simulation")
run_monte_carlo = st.checkbox("Run Monte Carlo Simulation", value=False)
num_iterations = 1000  # Number of Monte Carlo iterations

# RMD Divisors (for both primary user and partner)
rmd_divisors = {
    73: 26.5, 74: 25.6, 75: 24.7, 76: 23.8, 77: 22.9, 78: 22.0, 79: 21.1,
    80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2,
    87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1,
    94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4
}

# Save Scenario
st.header("💾 Save Scenario")
new_scenario_name = st.text_input("Scenario Name:", value=scenario_name if scenario_name != "New Scenario" else "")
if st.button("Save Scenario") and new_scenario_name:
    inputs = {
        "input_style": input_style,
        "age_group": age_group,
        "age": age,
        "partner_name": partner_name,
        "partner_age": partner_age,
        "partner_ira_balance": partner_ira_balance,
        "partner_four01k_403b_balance": partner_four01k_403b_balance,
        "partner_taxable_investment_accounts": partner_taxable_investment_accounts,
        "partner_other_assets": partner_other_assets,
        "partner_liabilities": partner_liabilities,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "primary_residence_value": primary_residence_value,
        "secondary_residence_value": secondary_residence_value,
        "ira_balance": ira_balance,
        "four01k_403b_balance": four01k_403b_balance,
        "taxable_investment_accounts": taxable_investment_accounts,
        "pension_fund_value": pension_fund_value,
        "life_insurance_cash_value": life_insurance_cash_value,
        "high_yield_savings_account": high_yield_savings_account,
        "hsa_balance": hsa_balance,
        "five29_plan_balance": five29_plan_balance,
        "vehicles_value": vehicles_value,
        "jewelry_collectibles_value": jewelry_collectibles_value,
        "business_ownership_value": business_ownership_value,
        "cryptocurrency_holdings": cryptocurrency_holdings,
        "other_assets": other_assets,
        "primary_residence_mortgage": primary_residence_mortgage,
        "secondary_residence_mortgage": secondary_residence_mortgage,
        "auto_loans": auto_loans,
        "student_loans": student_loans,
        "credit_card_debt": credit_card_debt,
        "personal_loans": personal_loans,
        "business_loans": business_loans,
        "other_liabilities": other_liabilities,
        "tax_rate": tax_rate,
        "inflation_rate": inflation_rate,
        "investment_return_rate": investment_return_rate,
        "simulation_years": simulation_years
    }
    if input_style == "Detailed Breakdown":
        inputs.update({
            "salary_wages": salary_wages,
            "self_employment_income": self_employment_income,
            "rental_income": rental_income,
            "investment_income": investment_income,
            "social_security_income": social_security_income,
            "pension_income": pension_income,
            "other_income": other_income,
            "housing_expenses": housing_expenses,
            "utilities_expenses": utilities_expenses,
            "groceries_expenses": groceries_expenses,
            "transportation_expenses": transportation_expenses,
            "healthcare_expenses": healthcare_expenses,
            "insurance_expenses": insurance_expenses,
            "real_estate_insurance_expenses": real_estate_insurance_expenses,
            "property_tax_expenses": property_tax_expenses,
            "entertainment_expenses": entertainment_expenses,
            "restaurant_expenses": restaurant_expenses,
            "travel_expenses": travel_expenses,
            "education_expenses": education_expenses,
            "childcare_expenses": childcare_expenses,
            "clothing_expenses": clothing_expenses,
            "charitable_donations": charitable_donations,
            "miscellaneous_expenses": miscellaneous_expenses,
            "other_expenses": other_expenses
        })
    saved_scenarios[new_scenario_name] = inputs
    with open(scenario_file, "w") as f:
        json.dump(saved_scenarios, f)
    st.success(f"Scenario '{new_scenario_name}' saved successfully!")
    st.rerun()

# Simulation Logic
st.header("📊 Simulation Results")
if st.button("Run Simulation"):
    # Validate age before running the simulation
    if age_group == "25-55" and (age < 25 or age > 55):
        st.error("Starting Age must be between 25 and 55 for the 25-55 age group.")
    elif age_group == "55-70" and (age < 55 or age > 70):
        st.error("Starting Age must be between 55 and 70 for the 55-70 age group.")
    elif age_group == "70+" and age < 70:
        st.error("Starting Age must be 70 or higher for the 70+ age group.")
    else:
        # Initialize variables for primary user
        financial_assets = (
            ira_balance + four01k_403b_balance + taxable_investment_accounts +
            high_yield_savings_account + hsa_balance + five29_plan_balance +
            life_insurance_cash_value + cryptocurrency_holdings + pension_fund_value  # Include pension as savings
        )
        other_assets_total = vehicles_value + jewelry_collectibles_value + business_ownership_value + other_assets
        primary_home_value = primary_residence_value
        secondary_home_value = secondary_residence_value
        total_liabilities = (
            primary_residence_mortgage + secondary_residence_mortgage + auto_loans +
            student_loans + credit_card_debt + personal_loans + business_loans + other_liabilities
        )

        # Initialize variables for partner
        partner_financial_assets = (
            partner_ira_balance + partner_four01k_403b_balance + partner_taxable_investment_accounts
        )
        partner_other_assets_total = partner_other_assets
        partner_total_liabilities = partner_liabilities

        # Combined financials
        combined_financial_assets = financial_assets + partner_financial_assets
        combined_other_assets_total = other_assets_total + partner_other_assets_total
        combined_total_liabilities = total_liabilities + partner_total_liabilities

        # Split shared retirement accounts for RMD purposes (50/50)
        total_ira = ira_balance + partner_ira_balance
        total_401k = four01k_403b_balance + partner_four01k_403b_balance
        primary_ira_for_rmd = total_ira / 2
        partner_ira_for_rmd = total_ira / 2
        primary_401k_for_rmd = total_401k / 2
        partner_401k_for_rmd = total_401k / 2

        # Deterministic Simulation
        years = list(range(2025, 2025 + simulation_years))
        ages = list(range(int(age), int(age + simulation_years)))
        total_incomes = []
        total_expenses_list = []
        net_draws = []
        rmd_pers1 = []
        rmd_pers2 = []
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

        current_savings = combined_financial_assets
        current_primary_home = primary_home_value
        current_secondary_home = secondary_home_value
        current_liabilities = combined_total_liabilities
        annual_income = total_income * 12
        annual_expenses = total_expenses * 12
        initial_annual_expenses = annual_expenses  # Store initial expenses for OpenAI assessment

        # RMD calculations
        rmd_primary = 0.0
        rmd_partner = 0.0
        for year in range(int(simulation_years)):
            current_age = age + (year)
            current_partner_age = partner_age + (year)

            # Adjust for inflation
            annual_expenses *= (1 + inflation_rate / 100)
            # Income after tax
            annual_net_income = annual_income * (1 - tax_rate / 100)
            # Net draw or contribution
            net_draw = annual_expenses - annual_net_income

            # RMD for primary user
            rmd_primary_ira = 0.0
            rmd_primary_401k = 0.0
            if current_age >= 73:
                divisor = rmd_divisors.get(current_age, rmd_divisors[100])  # Use last divisor for ages > 100
                rmd_primary_ira = primary_ira_for_rmd / divisor
                rmd_primary_401k = primary_401k_for_rmd / divisor
            rmd_primary = rmd_primary_ira + rmd_primary_401k
            net_rmd_primary = rmd_primary * (1 - tax_rate / 100)

            # RMD for partner
            rmd_partner_ira = 0.0
            rmd_partner_401k = 0.0
            if current_partner_age >= 73:
                divisor = rmd_divisors.get(current_partner_age, rmd_divisors[100])  # Use last divisor for ages > 100
                rmd_partner_ira = partner_ira_for_rmd / divisor
                rmd_partner_401k = partner_401k_for_rmd / divisor
            rmd_partner = rmd_partner_ira + rmd_partner_401k
            net_rmd_partner = rmd_partner * (1 - tax_rate / 100)

            # Total RMD before and after tax
            total_rmd_before = rmd_primary + rmd_partner
            total_net_rmd = net_rmd_primary + net_rmd_partner
            cash_used_from_savings = max(0, net_draw - total_net_rmd)

            # Apply RMD withdrawals (proportionally from shared accounts)
            if current_age >= 73:
                primary_ira_for_rmd -= rmd_primary_ira
                primary_401k_for_rmd -= rmd_primary_401k
            if current_partner_age >= 73:
                partner_ira_for_rmd -= rmd_partner_ira
                partner_401k_for_rmd -= rmd_partner_401k

            # Savings calculations
            savings_open_value = current_savings
            savings_growth_value = current_savings * (investment_return_rate / 100)
            savings_before_draw_value = current_savings + savings_growth_value
            current_savings = savings_before_draw_value - cash_used_from_savings

            # Recalculate savings after RMD
            current_savings = (
                (primary_ira_for_rmd + partner_ira_for_rmd) +  # Remaining shared IRA
                (primary_401k_for_rmd + partner_401k_for_rmd) +  # Remaining shared 401k
                taxable_investment_accounts +
                high_yield_savings_account + hsa_balance + five29_plan_balance +
                life_insurance_cash_value + cryptocurrency_holdings + pension_fund_value +
                partner_taxable_investment_accounts
            )

            # Home value growth (assumed 3% annual growth)
            current_primary_home *= 1.03
            current_secondary_home *= 1.03
            # Liabilities (assumed linear reduction for simplicity)
            current_liabilities = max(0, current_liabilities - (combined_total_liabilities / simulation_years))
            # Total assets and net worth
            total_assets = current_savings + current_primary_home + current_secondary_home + combined_other_assets_total
            current_net_worth = total_assets - current_liabilities

            # Append data for CSV
            total_incomes.append(round(annual_income, 2))
            total_expenses_list.append(round(annual_expenses, 2))
            net_draws.append(round(net_draw, 2))
            rmd_pers1.append(round(rmd_primary, 2))
            rmd_pers2.append(round(rmd_partner, 2))
            total_rmd_before_tax.append(round(total_rmd_before, 2))
            net_rmd_used_list.append(round(total_net_rmd, 2))
            cash_used_from_savings_list.append(round(cash_used_from_savings, 2))
            savings_open.append(round(savings_open_value, 2))
            savings_growth.append(round(savings_growth_value, 2))
            savings_before_draw.append(round(savings_before_draw_value, 2))
            savings_end.append(round(current_savings, 2))
            primary_home_values.append(round(current_primary_home, 2))
            secondary_home_values.append(round(current_secondary_home, 2))
            total_assets_list.append(round(total_assets, 2))
            total_liabilities_list.append(round(current_liabilities, 2))
            net_worth_list.append(round(current_net_worth, 2))

        # Create DataFrame with all columns
        df = pd.DataFrame({
            "Year": years,
            "Age": ages,
            "Total Income": total_incomes,
            "Total Expenses": total_expenses_list,
            "Net Draw": net_draws,
            "RMD (Pers1)": rmd_pers1,
            "RMD (Pers2)": rmd_pers2,
            "Total RMD Before Tax": total_rmd_before_tax,
            "Net Total RMD Used": net_rmd_used_list,
            "Cash Used from Savings": cash_used_from_savings_list,
            "Savings Open": savings_open,
            "Savings Growth": savings_growth,
            "Savings Before Draw": savings_before_draw,
            "Savings End": savings_end,
            "Primary Home Value": primary_home_values,
            "Secondary Home Value": secondary_home_values,
            "Total Assets": total_assets_list,
            "Total Liabilities": total_liabilities_list,
            "Net Worth": net_worth_list
        })

        # Display Results
        st.subheader("Simulation Results")
        st.dataframe(df)

        # Graph 1: Savings and Net Worth
        st.subheader("Savings and Net Worth Over Time")
        st.line_chart(df.set_index("Age")[["Savings End", "Net Worth"]])

        # Graph 2: Income vs. Expenses
        st.subheader("Income vs. Expenses Over Time")
        st.line_chart(df.set_index("Age")[["Total Income", "Total Expenses"]])

        if run_monte_carlo:
            st.subheader("Monte Carlo Simulation Results (Total Savings)")
            monte_carlo_savings = []
            for _ in range(num_iterations):
                mc_savings = combined_financial_assets
                mc_ira_balance = primary_ira_for_rmd
                mc_partner_ira_balance = partner_ira_for_rmd
                mc_401k_balance = primary_401k_for_rmd
                mc_partner_401k_balance = partner_401k_for_rmd
                mc_annual_expenses = total_expenses * 12  # Reset for each iteration
                mc_savings_history = []
                for year in range(int(simulation_years)):
                    current_age = age + year
                    current_partner_age = partner_age + year

                    # Introduce variability in returns and inflation
                    mc_investment_return = np.random.normal(investment_return_rate, 5) / 100  # Further increased variability
                    mc_inflation = np.random.normal(inflation_rate, 2) / 100  # Further increased variability
                    mc_annual_expenses *= (1 + mc_inflation)
                    annual_net_income_mc = annual_income * (1 - tax_rate / 100)
                    net_draw_mc = mc_annual_expenses - annual_net_income_mc

                    # RMD for Monte Carlo
                    mc_rmd_primary = 0.0
                    mc_rmd_partner = 0.0
                    if current_age >= 73:
                        divisor = rmd_divisors.get(current_age, rmd_divisors[100])
                        mc_rmd_primary_ira = mc_ira_balance / divisor
                        mc_rmd_primary_401k = mc_401k_balance / divisor
                        mc_rmd_primary = mc_rmd_primary_ira + mc_rmd_primary_401k
                        mc_ira_balance -= mc_rmd_primary_ira
                        mc_401k_balance -= mc_rmd_primary_401k
                    if current_partner_age >= 73:
                        divisor = rmd_divisors.get(current_partner_age, rmd_divisors[100])
                        mc_rmd_partner_ira = mc_partner_ira_balance / divisor
                        mc_rmd_partner_401k = mc_partner_401k_balance / divisor
                        mc_rmd_partner = mc_rmd_partner_ira + mc_rmd_partner_401k
                        mc_partner_ira_balance -= mc_rmd_partner_ira
                        mc_partner_401k_balance -= mc_rmd_partner_401k
                    mc_net_rmd = (mc_rmd_primary + mc_rmd_partner) * (1 - tax_rate / 100)
                    mc_cash_used_from_savings = max(0, net_draw_mc - mc_net_rmd)

                    mc_savings *= (1 + mc_investment_return)
                    mc_savings -= mc_cash_used_from_savings

                    # Recalculate savings for Monte Carlo (only Savings End)
                    mc_savings = (
                        mc_ira_balance + mc_401k_balance +
                        taxable_investment_accounts +
                        high_yield_savings_account + hsa_balance + five29_plan_balance +
                        life_insurance_cash_value + cryptocurrency_holdings + pension_fund_value +
                        mc_partner_ira_balance + mc_partner_401k_balance +
                        partner_taxable_investment_accounts
                    )

                    mc_savings_history.append(mc_savings)
                monte_carlo_savings.append(mc_savings_history)

            # Monte Carlo DataFrame for savings
            monte_carlo_savings_df = pd.DataFrame(monte_carlo_savings).T
            monte_carlo_savings_df.index = years

            # Calculate ranges for savings
            savings_min = monte_carlo_savings_df.min(axis=1)
            savings_max = monte_carlo_savings_df.max(axis=1)
            savings_median = monte_carlo_savings_df.median(axis=1)

            # Display numerical ranges with proper formatting
            st.markdown(f'<div style="font-family: monospace;">Monte Carlo Savings Range (Year {years[0]}): Min ${savings_min.iloc[0]:,.2f}, Max ${savings_max.iloc[0]:,.2f}, Median ${savings_median.iloc[0]:,.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family: monospace;">Monte Carlo Savings Range (Year {years[-1]}): Min ${savings_min.iloc[-1]:,.2f}, Max ${savings_max.iloc[-1]:,.2f}, Median ${savings_median.iloc[-1]:,.2f}</div>', unsafe_allow_html=True)

            # Create DataFrame for plotting ranges
            monte_carlo_range_df = pd.DataFrame({
                "Savings Min": savings_min,
                "Savings Median": savings_median,
                "Savings Max": savings_max
            }, index=years)

            # Plot with shaded ranges
            fig, ax = plt.subplots()
            ax.fill_between(years, monte_carlo_range_df["Savings Min"], monte_carlo_range_df["Savings Max"], alpha=0.3, color="blue", label="Savings Range")
            ax.plot(years, monte_carlo_range_df["Savings Median"], color="blue", label="Savings Median")
            ax.set_xlabel("Year")
            ax.set_ylabel("Savings End ($)")
            ax.legend()
            st.pyplot(fig)

        # OpenAI Financial Assessment (Moved inside the simulation block)
        if use_openai:
            client = OpenAI(api_key=openai_api_key)
            financial_summary = f"""
            User Profile:
            - Primary User Age: {age}
            - Partner's Age: {partner_age}
            - Annual Income: ${annual_income:,.2f}
            - Annual Expenses: ${initial_annual_expenses:,.2f}

            Initial Financial Position:
            - Initial Savings (Combined): ${combined_financial_assets:,.2f}
              - Shared IRA: ${total_ira:,.2f}
              - Shared 401k/403b: ${total_401k:,.2f}
              - Pension Fund: ${pension_fund_value:,.2f}
            - Total Assets (Initial): ${total_assets_list[0]:,.2f}
              - Primary Home Value: ${primary_home_values[0]:,.2f}
              - Secondary Home Value: ${secondary_home_values[0]:,.2f}
              - Other Assets (Primary + Partner): ${combined_other_assets_total:,.2f}
            - Total Liabilities (Initial): ${total_liabilities_list[0]:,.2f}
              - Primary User Liabilities: ${total_liabilities - partner_total_liabilities:,.2f}
              - Partner Liabilities: ${partner_total_liabilities:,.2f}

            Simulation Results (After {simulation_years} Years):
            - Final Savings: ${df['Savings End'].iloc[-1]:,.2f}
            - Final Net Worth: ${df['Net Worth'].iloc[-1]:,.2f}
            - Final Total Assets: ${df['Total Assets'].iloc[-1]:,.2f}
            - Final Total Liabilities: ${df['Total Liabilities'].iloc[-1]:,.2f}
            - RMD (Pers1, First Year): ${df['RMD (Pers1)'].iloc[0]:,.2f}
            - RMD (Pers2, First Year): ${df['RMD (Pers2)'].iloc[0]:,.2f}

            Trends Over Simulation Period:
            - Income vs. Expenses: Annual net draw started at ${df['Net Draw'].iloc[0]:,.2f} and ended at ${df['Net Draw'].iloc[-1]:,.2f}.
            - Savings Trend: Savings changed from ${df['Savings End'].iloc[0]:,.2f} to ${df['Savings End'].iloc[-1]:,.2f}.
            - Net Worth Trend: Net worth changed from ${df['Net Worth'].iloc[0]:,.2f} to ${df['Net Worth'].iloc[-1]:,.2f}.
            """
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial advisor with expertise in retirement planning. Provide a detailed and insightful assessment of the user's financial situation, considering their income, expenses, savings, assets, liabilities, and simulation trends. Highlight potential risks, opportunities, and recommendations for improving their retirement outlook."},
                    {"role": "user", "content": financial_summary}
                ]
            )
            st.subheader("OpenAI Financial Assessment")
            st.markdown(
                f'<div style="font-family: monospace; white-space: pre-wrap;">{response.choices[0].message.content}</div>',
                unsafe_allow_html=True
            )
            st.write("")
            st.subheader("Ask a Question About Your Financial Future or Calculations")
            st.write("You can ask questions about the future or calculation methods here:")
            # Create a form for question submission
            with st.form(key="question_form"):
                user_question = st.text_area("Enter your question (e.g., 'What happens if I reduce my expenses by 20%?' or 'How are RMDs calculated?'):", height=100, key="user_question_form")
                submit_button = st.form_submit_button(label="Submit Question")
            # Placeholder for the AI response
            response_placeholder = st.empty()
            if submit_button and user_question:
                question_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a financial advisor with expertise in retirement planning. Answer the user's question about their financial simulation or future outlook based on the provided data."},
                        {"role": "user", "content": f"Context:\n{financial_summary}\n\nQuestion:\n{user_question}"}
                    ]
                )
                response_placeholder.subheader("Response to Your Question")
                response_placeholder.markdown(
                    f'<div style="font-family: monospace; white-space: pre-wrap;">{question_response.choices[0].message.content}</div>',
                    unsafe_allow_html=True
                )

        # Download Results
        csv = df.to_csv(index=False)
        st.download_button("Download Results as CSV", csv, "retirement_simulation.csv", "text/csv")
else:
    st.write("Click 'Run Simulation' to see results.")