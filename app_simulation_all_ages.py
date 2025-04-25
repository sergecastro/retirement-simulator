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

# Age
st.header("👤 Age")
age_group = st.selectbox("Age Group:", ["25-55", "55-70", "70+"], index=0 if inputs.get("age_group", "25-55") == "25-55" else (1 if inputs.get("age_group") == "55-70" else 2))
default_age = inputs.get("age", 40 if age_group == "25-55" else 60 if age_group == "55-70" else 76)
age = st.number_input("Starting Age:", min_value=25, max_value=110, value=default_age)

# Validate age against age group
if age_group == "25-55" and (age < 25 or age > 55):
    st.error("Starting Age must be between 25 and 55 for the 25-55 age group.")
    st.stop()
elif age_group == "55-70" and (age < 55 or age > 70):
    st.error("Starting Age must be between 55 and 70 for the 55-70 age group.")
    st.stop()
elif age_group == "70+" and age < 70:
    st.error("Starting Age must be 70 or higher for the 70+ age group.")
    st.stop()

# Income & Expenses (Monthly)
st.header("💵 Income & Expenses (Monthly)")
if input_style == "Detailed Breakdown":
    st.subheader("Income Sources (Monthly)")
    salary_income = st.number_input("Salary/Wages (Monthly):", value=inputs.get("salary_income", 0.0))
    self_employment_income = st.number_input("Self-Employment Income (Monthly):", value=inputs.get("self_employment_income", 0.0))
    rental_income = st.number_input("Rental Income (Monthly):", value=inputs.get("rental_income", 0.0))
    investment_income = st.number_input("Investment Income (Monthly):", value=inputs.get("investment_income", 0.0))
    pension_income = st.number_input("Pension Income (Monthly):", value=inputs.get("pension_income", 0.0))
    social_security = st.number_input("Social Security (Monthly):", value=inputs.get("social_security", 0.0))
    annuity_income = st.number_input("Annuity Income (Monthly):", value=inputs.get("annuity_income", 0.0))
    part_time_income = st.number_input("Part-Time/Retirement Job Income (Monthly):", value=inputs.get("part_time_income", 0.0))
    passive_income = st.number_input("Passive Income (Monthly):", value=inputs.get("passive_income", 0.0))
    government_assistance = st.number_input("Government Assistance (Monthly):", value=inputs.get("government_assistance", 0.0))
    alimony_child_support_received = st.number_input("Alimony/Child Support Received (Monthly):", value=inputs.get("alimony_child_support_received", 0.0))
    family_support_gifts = st.number_input("Family Support/Gifts (Monthly):", value=inputs.get("family_support_gifts", 0.0))
    inheritance_gains = st.number_input("Inheritance/One-Time Gains (Monthly):", value=inputs.get("inheritance_gains", 0.0))
    scholarships_grants = st.number_input("Scholarships/Grants (Monthly):", value=inputs.get("scholarships_grants", 0.0))
    other_income = st.number_input("Other Income (Monthly):", value=inputs.get("other_income", 0.0))

    total_income_monthly = (
        salary_income + self_employment_income + rental_income + investment_income +
        pension_income + social_security + annuity_income + part_time_income +
        passive_income + government_assistance + alimony_child_support_received +
        family_support_gifts + inheritance_gains + scholarships_grants + other_income
    )
    st.write(f"**Total Income (Monthly):** ${total_income_monthly:,.2f}")
    total_income = total_income_monthly * 12

    st.subheader("Expenses (Monthly)")
    housing_costs = st.number_input("Housing Costs (Monthly):", value=inputs.get("housing_costs", 0.0))
    utilities = st.number_input("Utilities (Monthly):", value=inputs.get("utilities", 0.0))
    groceries_food = st.number_input("Groceries/Food (Monthly):", value=inputs.get("groceries_food", 0.0))
    dining_out = st.number_input("Dining Out (Monthly):", value=inputs.get("dining_out", 0.0))
    transportation = st.number_input("Transportation (Monthly):", value=inputs.get("transportation", 0.0))
    healthcare_costs = st.number_input("Healthcare Costs (Monthly):", value=inputs.get("healthcare_costs", 0.0))
    insurance_premiums = st.number_input("Insurance Premiums (Monthly):", value=inputs.get("insurance_premiums", 0.0))
    education_expenses = st.number_input("Education Expenses (Monthly):", value=inputs.get("education_expenses", 0.0))
    childcare_dependent_care = st.number_input("Childcare/Dependent Care (Monthly):", value=inputs.get("childcare_dependent_care", 0.0))
    entertainment_leisure = st.number_input("Entertainment/Leisure (Monthly):", value=inputs.get("entertainment_leisure", 0.0))
    clothing_personal_care = st.number_input("Clothing/Personal Care (Monthly):", value=inputs.get("clothing_personal_care", 0.0))
    charitable_donations = st.number_input("Charitable Donations (Monthly):", value=inputs.get("charitable_donations", 0.0))
    student_loan_payments = st.number_input("Student Loan Payments (Monthly):", value=inputs.get("student_loan_payments", 0.0))
    alimony_child_support_paid = st.number_input("Alimony/Child Support Paid (Monthly):", value=inputs.get("alimony_child_support_paid", 0.0))
    travel_vacation = st.number_input("Travel/Vacation (Monthly):", value=inputs.get("travel_vacation", 0.0))
    hobbies_special_interests = st.number_input("Hobbies/Special Interests (Monthly):", value=inputs.get("hobbies_special_interests", 0.0))
    pet_care = st.number_input("Pet Care (Monthly):", value=inputs.get("pet_care", 0.0))
    home_maintenance = st.number_input("Home Maintenance (Monthly):", value=inputs.get("home_maintenance", 0.0))
    professional_services = st.number_input("Professional Services (Monthly):", value=inputs.get("professional_services", 0.0))
    fitness_wellness = st.number_input("Fitness/Wellness (Monthly):", value=inputs.get("fitness_wellness", 0.0))
    gifts_celebrations = st.number_input("Gifts/Celebrations (Monthly):", value=inputs.get("gifts_celebrations", 0.0))
    savings_contributions = st.number_input("Savings Contributions (Monthly):", value=inputs.get("savings_contributions", 0.0))
    miscellaneous_expenses = st.number_input("Miscellaneous Expenses (Monthly):", value=inputs.get("miscellaneous_expenses", 0.0))

    total_expenses_monthly = (
        housing_costs + utilities + groceries_food + dining_out + transportation +
        healthcare_costs + insurance_premiums + education_expenses + childcare_dependent_care +
        entertainment_leisure + clothing_personal_care + charitable_donations +
        student_loan_payments + alimony_child_support_paid + travel_vacation +
        hobbies_special_interests + pet_care + home_maintenance + professional_services +
        fitness_wellness + gifts_celebrations + savings_contributions + miscellaneous_expenses
    )
    st.write(f"**Total Expenses (Monthly):** ${total_expenses_monthly:,.2f}")
    total_expenses = total_expenses_monthly * 12
else:
    total_income_monthly = st.number_input("Total Income (Monthly):", value=inputs.get("income_monthly", 0.0))
    st.write(f"**Total Income (Monthly):** ${total_income_monthly:,.2f}")
    total_income = total_income_monthly * 12
    total_expenses_monthly = st.number_input("Total Expenses (Monthly):", value=inputs.get("expenses_monthly", 0.0))
    st.write(f"**Total Expenses (Monthly):** ${total_expenses_monthly:,.2f}")
    total_expenses = total_expenses_monthly * 12

# Assets & Liabilities
st.header("💰 Assets & Liabilities")
st.subheader("Assets")
primary_residence_value = st.number_input("Primary Residence Value:", value=inputs.get("primary_residence_value", 0.0))
secondary_residence_value = st.number_input("Secondary Residence Value:", value=inputs.get("secondary_residence_value", 0.0))
ira_balance = st.number_input("IRA Balance:", value=inputs.get("ira_balance", 0.0))
four01k_403b_balance = st.number_input("401k/403b Balance:", value=inputs.get("four01k_403b_balance", 0.0))
taxable_investment_accounts = st.number_input("Taxable Investment Accounts:", value=inputs.get("taxable_investment_accounts", 0.0))
pension_fund_value = st.number_input("Pension Fund Value:", value=inputs.get("pension_fund_value", 0.0))
life_insurance_cash_value = st.number_input("Life Insurance Cash Value:", value=inputs.get("life_insurance_cash_value", 0.0))
high_yield_savings_account = st.number_input("High-Yield Savings Account:", value=inputs.get("high_yield_savings_account", 0.0))
hsa_balance = st.number_input("HSA Balance:", value=inputs.get("hsa_balance", 0.0))
five29_plan_balance = st.number_input("529 Plan Balance:", value=inputs.get("five29_plan_balance", 0.0))
vehicles_value = st.number_input("Vehicles Value:", value=inputs.get("vehicles_value", 0.0))
jewelry_collectibles_value = st.number_input("Jewelry/Collectibles Value:", value=inputs.get("jewelry_collectibles_value", 0.0))
business_ownership_value = st.number_input("Business Ownership Value:", value=inputs.get("business_ownership_value", 0.0))
cryptocurrency_holdings = st.number_input("Cryptocurrency Holdings:", value=inputs.get("cryptocurrency_holdings", 0.0))
other_assets = st.number_input("Other Assets:", value=inputs.get("other_assets", 0.0))

total_assets = (
    primary_residence_value + secondary_residence_value + ira_balance +
    four01k_403b_balance + taxable_investment_accounts + pension_fund_value +
    life_insurance_cash_value + high_yield_savings_account + hsa_balance +
    five29_plan_balance + vehicles_value + jewelry_collectibles_value +
    business_ownership_value + cryptocurrency_holdings + other_assets
)
st.write(f"**Total Assets:** ${total_assets:,.2f}")

st.subheader("Liabilities")
primary_residence_mortgage = st.number_input("Primary Residence Mortgage:", value=inputs.get("primary_residence_mortgage", 0.0))
secondary_residence_mortgage = st.number_input("Secondary Residence Mortgage:", value=inputs.get("secondary_residence_mortgage", 0.0))
auto_loans = st.number_input("Auto Loans:", value=inputs.get("auto_loans", 0.0))
student_loans = st.number_input("Student Loans:", value=inputs.get("student_loans", 0.0))
credit_card_debt = st.number_input("Credit Card Debt:", value=inputs.get("credit_card_debt", 0.0))
personal_loans = st.number_input("Personal Loans:", value=inputs.get("personal_loans", 0.0))
business_loans = st.number_input("Business Loans:", value=inputs.get("business_loans", 0.0))
other_liabilities = st.number_input("Other Liabilities:", value=inputs.get("other_liabilities", 0.0))

# Simulation Settings
st.header("⚙️ Simulation Settings")
income_tax_rate = st.number_input("Income Tax Rate:", value=inputs.get("income_tax_rate", 0.25))
rmd_tax_rate = st.number_input("RMD Tax Rate:", value=inputs.get("rmd_tax_rate", 0.25))
inflation_rate = st.number_input("Inflation Rate:", value=inputs.get("inflation_rate", 0.025))
growth_rate = st.number_input("Asset Growth Rate:", value=inputs.get("growth_rate", 0.05))
home_appreciation = st.number_input("Home Appreciation:", value=inputs.get("home_appreciation", 0.03))
ss_cola = st.number_input("Social Security COLA:", value=inputs.get("ss_cola", 0.025))
rent_growth = st.number_input("Rental Growth:", value=inputs.get("rent_growth", 0.02))
sim_years = st.number_input("Years to Simulate:", min_value=1, max_value=50, value=inputs.get("sim_years", 35))

# OpenAI API Key Input
st.header("🤖 OpenAI Financial Assessment")
openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")
use_openai = st.checkbox("Enable OpenAI Assessment", value=False)

# Monte Carlo Settings
st.header("🎲 Monte Carlo Simulation")
run_monte_carlo = st.checkbox("Run Monte Carlo Simulation", value=False)
num_iterations = 1000  # Number of Monte Carlo iterations

# Save scenario button
st.header("💾 Save Scenario")
save_option = st.radio("Save Option:", ["Create New Scenario", "Update Existing Scenario"], index=0)
if save_option == "Create New Scenario":
    new_scenario_name = st.text_input("Save as Scenario (enter name):", "")
else:
    new_scenario_name = st.selectbox("Select Scenario to Update:", list(saved_scenarios.keys()))

if st.button("Save Scenario") and new_scenario_name:
    saved_inputs = {
        "age": age,
        "age_group": age_group,
        "income_monthly": total_income_monthly,
        "expenses_monthly": total_expenses_monthly,
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
        "salary_income": salary_income,
        "self_employment_income": self_employment_income,
        "rental_income": rental_income,
        "investment_income": investment_income,
        "pension_income": pension_income,
        "social_security": social_security,
        "annuity_income": annuity_income,
        "part_time_income": part_time_income,
        "passive_income": passive_income,
        "government_assistance": government_assistance,
        "alimony_child_support_received": alimony_child_support_received,
        "family_support_gifts": family_support_gifts,
        "inheritance_gains": inheritance_gains,
        "scholarships_grants": scholarships_grants,
        "other_income": other_income,
        "housing_costs": housing_costs,
        "utilities": utilities,
        "groceries_food": groceries_food,
        "dining_out": dining_out,
        "transportation": transportation,
        "healthcare_costs": healthcare_costs,
        "insurance_premiums": insurance_premiums,
        "education_expenses": education_expenses,
        "childcare_dependent_care": childcare_dependent_care,
        "entertainment_leisure": entertainment_leisure,
        "clothing_personal_care": clothing_personal_care,
        "charitable_donations": charitable_donations,
        "student_loan_payments": student_loan_payments,
        "alimony_child_support_paid": alimony_child_support_paid,
        "travel_vacation": travel_vacation,
        "hobbies_special_interests": hobbies_special_interests,
        "pet_care": pet_care,
        "home_maintenance": home_maintenance,
        "professional_services": professional_services,
        "fitness_wellness": fitness_wellness,
        "gifts_celebrations": gifts_celebrations,
        "savings_contributions": savings_contributions,
        "miscellaneous_expenses": miscellaneous_expenses,
        "input_style": input_style,
        "income_tax_rate": income_tax_rate,
        "rmd_tax_rate": rmd_tax_rate,
        "inflation_rate": inflation_rate,
        "growth_rate": growth_rate,
        "home_appreciation": home_appreciation,
        "ss_cola": ss_cola,
        "rent_growth": rent_growth,
        "sim_years": sim_years
    }
    saved_scenarios[new_scenario_name] = saved_inputs
    with open(scenario_file, "w") as f:
        json.dump(saved_scenarios, f)
    st.success(f"Scenario '{new_scenario_name}' saved successfully!")
    st.rerun()

# RMD Divisors
rmd_divisors = {
    73: 26.5, 74: 25.6, 75: 24.7, 76: 23.8, 77: 22.9, 78: 22.0, 79: 21.1,
    80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2,
    87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1,
    94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4
}

# Simulation Logic
st.header("📊 Simulation Results")
if st.button("Run Simulation"):
    # Initialize variables
    financial_assets = (
        ira_balance + four01k_403b_balance + taxable_investment_accounts +
        high_yield_savings_account + hsa_balance + five29_plan_balance +
        life_insurance_cash_value + cryptocurrency_holdings
    )
    other_assets_total = vehicles_value + jewelry_collectibles_value + business_ownership_value + other_assets
    primary_home_value = primary_residence_value
    secondary_home_value = secondary_residence_value
    total_liabilities = (
        primary_residence_mortgage + secondary_residence_mortgage + auto_loans +
        student_loans + credit_card_debt + personal_loans + business_loans + other_liabilities
    )

    # Monte Carlo Simulation
    if run_monte_carlo:
        st.subheader("Monte Carlo Simulation Results")
        all_results = []
        for iteration in range(num_iterations):
            results = []
            current_financial_assets = financial_assets
            current_other_assets = other_assets_total
            current_primary_home_value = primary_home_value
            current_secondary_home_value = secondary_home_value
            current_total_liabilities = total_liabilities

            current_rental_income = rental_income if input_style == "Detailed Breakdown" else 0.0
            current_social_security = social_security if input_style == "Detailed Breakdown" else 0.0
            current_salary_income = salary_income if input_style == "Detailed Breakdown" else 0.0
            current_self_employment_income = self_employment_income if input_style == "Detailed Breakdown" else 0.0
            current_investment_income = investment_income if input_style == "Detailed Breakdown" else 0.0
            current_pension_income = pension_income if input_style == "Detailed Breakdown" else 0.0
            current_annuity_income = annuity_income if input_style == "Detailed Breakdown" else 0.0
            current_part_time_income = part_time_income if input_style == "Detailed Breakdown" else 0.0
            current_passive_income = passive_income if input_style == "Detailed Breakdown" else 0.0
            current_government_assistance = government_assistance if input_style == "Detailed Breakdown" else 0.0
            current_alimony_child_support_received = alimony_child_support_received if input_style == "Detailed Breakdown" else 0.0
            current_family_support_gifts = family_support_gifts if input_style == "Detailed Breakdown" else 0.0
            current_inheritance_gains = inheritance_gains if input_style == "Detailed Breakdown" else 0.0
            current_scholarships_grants = scholarships_grants if input_style == "Detailed Breakdown" else 0.0
            current_other_income = other_income if input_style == "Detailed Breakdown" else 0.0

            current_housing_costs = housing_costs if input_style == "Detailed Breakdown" else 0.0
            current_utilities = utilities if input_style == "Detailed Breakdown" else 0.0
            current_groceries_food = groceries_food if input_style == "Detailed Breakdown" else 0.0
            current_dining_out = dining_out if input_style == "Detailed Breakdown" else 0.0
            current_transportation = transportation if input_style == "Detailed Breakdown" else 0.0
            current_healthcare_costs = healthcare_costs if input_style == "Detailed Breakdown" else 0.0
            current_insurance_premiums = insurance_premiums if input_style == "Detailed Breakdown" else 0.0
            current_education_expenses = education_expenses if input_style == "Detailed Breakdown" else 0.0
            current_childcare_dependent_care = childcare_dependent_care if input_style == "Detailed Breakdown" else 0.0
            current_entertainment_leisure = entertainment_leisure if input_style == "Detailed Breakdown" else 0.0
            current_clothing_personal_care = clothing_personal_care if input_style == "Detailed Breakdown" else 0.0
            current_charitable_donations = charitable_donations if input_style == "Detailed Breakdown" else 0.0
            current_student_loan_payments = student_loan_payments if input_style == "Detailed Breakdown" else 0.0
            current_alimony_child_support_paid = alimony_child_support_paid if input_style == "Detailed Breakdown" else 0.0
            current_travel_vacation = travel_vacation if input_style == "Detailed Breakdown" else 0.0
            current_hobbies_special_interests = hobbies_special_interests if input_style == "Detailed Breakdown" else 0.0
            current_pet_care = pet_care if input_style == "Detailed Breakdown" else 0.0
            current_home_maintenance = home_maintenance if input_style == "Detailed Breakdown" else 0.0
            current_professional_services = professional_services if input_style == "Detailed Breakdown" else 0.0
            current_fitness_wellness = fitness_wellness if input_style == "Detailed Breakdown" else 0.0
            current_gifts_celebrations = gifts_celebrations if input_style == "Detailed Breakdown" else 0.0
            current_savings_contributions = savings_contributions if input_style == "Detailed Breakdown" else 0.0
            current_miscellaneous_expenses = miscellaneous_expenses if input_style == "Detailed Breakdown" else 0.0

            # Generate random rates for this iteration
            sim_growth_rates = np.random.normal(growth_rate, 0.02, sim_years)
            sim_inflation_rates = np.random.normal(inflation_rate, 0.005, sim_years)
            sim_home_appreciations = np.random.normal(home_appreciation, 0.01, sim_years)

            for year_idx, year in enumerate(range(2025, 2025 + sim_years)):
                current_age = age + (year - 2025)
                # Income
                if input_style == "Detailed Breakdown":
                    current_rental_income *= (1 + rent_growth)
                    current_social_security *= (1 + ss_cola)
                    current_salary_income *= (1 + sim_inflation_rates[year_idx])
                    current_self_employment_income *= (1 + sim_inflation_rates[year_idx])
                    current_investment_income *= (1 + sim_inflation_rates[year_idx])
                    current_pension_income *= (1 + sim_inflation_rates[year_idx])
                    current_annuity_income *= (1 + sim_inflation_rates[year_idx])
                    current_part_time_income *= (1 + sim_inflation_rates[year_idx])
                    current_passive_income *= (1 + sim_inflation_rates[year_idx])
                    current_government_assistance *= (1 + sim_inflation_rates[year_idx])
                    current_alimony_child_support_received *= (1 + sim_inflation_rates[year_idx])
                    current_family_support_gifts *= (1 + sim_inflation_rates[year_idx])
                    current_inheritance_gains *= (1 + sim_inflation_rates[year_idx])
                    current_scholarships_grants *= (1 + sim_inflation_rates[year_idx])
                    current_other_income *= (1 + sim_inflation_rates[year_idx])

                    total_income_monthly = (
                        current_salary_income + current_self_employment_income + current_rental_income +
                        current_investment_income + current_pension_income + current_social_security +
                        current_annuity_income + current_part_time_income + current_passive_income +
                        current_government_assistance + current_alimony_child_support_received +
                        current_family_support_gifts + current_inheritance_gains + current_scholarships_grants +
                        current_other_income
                    )
                    total_income = total_income_monthly * 12
                else:
                    total_income *= (1 + sim_inflation_rates[year_idx])

                net_total_income = total_income * (1 - income_tax_rate)

                # Expenses
                if input_style == "Detailed Breakdown":
                    current_housing_costs *= (1 + sim_inflation_rates[year_idx])
                    current_utilities *= (1 + sim_inflation_rates[year_idx])
                    current_groceries_food *= (1 + sim_inflation_rates[year_idx])
                    current_dining_out *= (1 + sim_inflation_rates[year_idx])
                    current_transportation *= (1 + sim_inflation_rates[year_idx])
                    current_healthcare_costs *= (1 + sim_inflation_rates[year_idx])
                    current_insurance_premiums *= (1 + sim_inflation_rates[year_idx])
                    current_education_expenses *= (1 + sim_inflation_rates[year_idx])
                    current_childcare_dependent_care *= (1 + sim_inflation_rates[year_idx])
                    current_entertainment_leisure *= (1 + sim_inflation_rates[year_idx])
                    current_clothing_personal_care *= (1 + sim_inflation_rates[year_idx])
                    current_charitable_donations *= (1 + sim_inflation_rates[year_idx])
                    current_student_loan_payments *= (1 + sim_inflation_rates[year_idx])
                    current_alimony_child_support_paid *= (1 + sim_inflation_rates[year_idx])
                    current_travel_vacation *= (1 + sim_inflation_rates[year_idx])
                    current_hobbies_special_interests *= (1 + sim_inflation_rates[year_idx])
                    current_pet_care *= (1 + sim_inflation_rates[year_idx])
                    current_home_maintenance *= (1 + sim_inflation_rates[year_idx])
                    current_professional_services *= (1 + sim_inflation_rates[year_idx])
                    current_fitness_wellness *= (1 + sim_inflation_rates[year_idx])
                    current_gifts_celebrations *= (1 + sim_inflation_rates[year_idx])
                    current_savings_contributions *= (1 + sim_inflation_rates[year_idx])
                    current_miscellaneous_expenses *= (1 + sim_inflation_rates[year_idx])

                    total_expenses_monthly = (
                        current_housing_costs + current_utilities + current_groceries_food + current_dining_out +
                        current_transportation + current_healthcare_costs + current_insurance_premiums +
                        current_education_expenses + current_childcare_dependent_care + current_entertainment_leisure +
                        current_clothing_personal_care + current_charitable_donations + current_student_loan_payments +
                        current_alimony_child_support_paid + current_travel_vacation + current_hobbies_special_interests +
                        current_pet_care + current_home_maintenance + current_professional_services +
                        current_fitness_wellness + current_gifts_celebrations + current_savings_contributions +
                        current_miscellaneous_expenses
                    )
                    total_expenses = total_expenses_monthly * 12
                else:
                    total_expenses *= (1 + sim_inflation_rates[year_idx])

                net_draw = total_expenses - net_total_income

                # RMD
                rmd = 0.0
                if current_age in rmd_divisors:
                    rmd = current_financial_assets / rmd_divisors[current_age]
                net_rmd = rmd * (1 - rmd_tax_rate)
                cash_from_savings = max(0, net_draw - net_rmd)
                if cash_from_savings > 0:
                    rmd_used = rmd
                    net_rmd_used = net_rmd
                else:
                    rmd_used = net_draw / (1 - rmd_tax_rate)
                    net_rmd_used = net_draw
                    cash_from_savings = 0.0

                # Financial Assets
                financial_assets_open = current_financial_assets
                financial_assets_growth = financial_assets_open * sim_growth_rates[year_idx]
                financial_assets_before_draw = financial_assets_open + financial_assets_growth
                current_financial_assets = financial_assets_before_draw - cash_from_savings - rmd_used

                # Real Estate
                current_primary_home_value *= (1 + sim_home_appreciations[year_idx])
                current_secondary_home_value *= (1 + sim_home_appreciations[year_idx])

                # Net Worth
                total_assets = (
                    current_financial_assets + current_primary_home_value + current_secondary_home_value +
                    current_other_assets + pension_fund_value
                )
                net_worth = total_assets - current_total_liabilities

                results.append({
                    "Year": year,
                    "Age": current_age,
                    "Total Income": round(total_income, 2),
                    "Net Total Income": round(net_total_income, 2),
                    "Total Expenses": round(total_expenses, 2),
                    "Net Draw": round(net_draw, 2),
                    "RMD Used": round(rmd_used, 2),
                    "Net RMD Used": round(net_rmd_used, 2),
                    "Cash from Savings": round(cash_from_savings, 2),
                    "Financial Assets Open": round(financial_assets_open, 2),
                    "Financial Assets Growth": round(financial_assets_growth, 2),
                    "Financial Assets Before Draw": round(financial_assets_before_draw, 2),
                    "Financial Assets End": round(current_financial_assets, 2),
                    "Primary Home Value": round(current_primary_home_value, 2),
                    "Secondary Home Value": round(current_secondary_home_value, 2),
                    "Total Assets": round(total_assets, 2),
                    "Total Liabilities": round(current_total_liabilities, 2),
                    "Net Worth": round(net_worth, 2)
                })
            all_results.append(pd.DataFrame(results))

        # Aggregate Monte Carlo Results
        years = list(range(2025, 2025 + sim_years))
        net_worths = np.zeros((num_iterations, sim_years))
        financial_assets_ends = np.zeros((num_iterations, sim_years))

        for i, df in enumerate(all_results):
            net_worths[i, :] = df["Net Worth"].values
            financial_assets_ends[i, :] = df["Financial Assets End"].values

        # Calculate statistics
        median_net_worth = np.median(net_worths, axis=0)
        percentile_10_net_worth = np.percentile(net_worths, 10, axis=0)
        percentile_90_net_worth = np.percentile(net_worths, 90, axis=0)
        prob_bankruptcy = np.mean(financial_assets_ends < 0, axis=0) * 100

        # Display Monte Carlo Results
        monte_carlo_df = pd.DataFrame({
            "Year": years,
            "Median Net Worth": median_net_worth,
            "10th Percentile Net Worth": percentile_10_net_worth,
            "90th Percentile Net Worth": percentile_90_net_worth,
            "Probability of Bankruptcy (%)": prob_bankruptcy
        })
        st.write("Monte Carlo Summary (1,000 Iterations)")
        st.dataframe(monte_carlo_df)

        # Plot Net Worth Range
        fig, ax = plt.subplots()
        ax.plot(years, median_net_worth, label="Median Net Worth", color="blue")
        ax.fill_between(years, percentile_10_net_worth, percentile_90_net_worth, color="blue", alpha=0.2, label="10th-90th Percentile")
        ax.set_xlabel("Year")
        ax.set_ylabel("Net Worth ($)")
        ax.set_title("Monte Carlo Net Worth Projection")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        # Use the median scenario for OpenAI assessment
        median_idx = np.argmin(np.abs(net_worths[:, -1] - median_net_worth[-1]))
        df = all_results[median_idx]
    else:
        # Single Deterministic Simulation
        results = []
        current_financial_assets = financial_assets
        current_other_assets = other_assets_total
        current_primary_home_value = primary_home_value
        current_secondary_home_value = secondary_home_value
        current_total_liabilities = total_liabilities

        current_rental_income = rental_income if input_style == "Detailed Breakdown" else 0.0
        current_social_security = social_security if input_style == "Detailed Breakdown" else 0.0
        current_salary_income = salary_income if input_style == "Detailed Breakdown" else 0.0
        current_self_employment_income = self_employment_income if input_style == "Detailed Breakdown" else 0.0
        current_investment_income = investment_income if input_style == "Detailed Breakdown" else 0.0
        current_pension_income = pension_income if input_style == "Detailed Breakdown" else 0.0
        current_annuity_income = annuity_income if input_style == "Detailed Breakdown" else 0.0
        current_part_time_income = part_time_income if input_style == "Detailed Breakdown" else 0.0
        current_passive_income = passive_income if input_style == "Detailed Breakdown" else 0.0
        current_government_assistance = government_assistance if input_style == "Detailed Breakdown" else 0.0
        current_alimony_child_support_received = alimony_child_support_received if input_style == "Detailed Breakdown" else 0.0
        current_family_support_gifts = family_support_gifts if input_style == "Detailed Breakdown" else 0.0
        current_inheritance_gains = inheritance_gains if input_style == "Detailed Breakdown" else 0.0
        current_scholarships_grants = scholarships_grants if input_style == "Detailed Breakdown" else 0.0
        current_other_income = other_income if input_style == "Detailed Breakdown" else 0.0

        current_housing_costs = housing_costs if input_style == "Detailed Breakdown" else 0.0
        current_utilities = utilities if input_style == "Detailed Breakdown" else 0.0
        current_groceries_food = groceries_food if input_style == "Detailed Breakdown" else 0.0
        current_dining_out = dining_out if input_style == "Detailed Breakdown" else 0.0
        current_transportation = transportation if input_style == "Detailed Breakdown" else 0.0
        current_healthcare_costs = healthcare_costs if input_style == "Detailed Breakdown" else 0.0
        current_insurance_premiums = insurance_premiums if input_style == "Detailed Breakdown" else 0.0
        current_education_expenses = education_expenses if input_style == "Detailed Breakdown" else 0.0
        current_childcare_dependent_care = childcare_dependent_care if input_style == "Detailed Breakdown" else 0.0
        current_entertainment_leisure = entertainment_leisure if input_style == "Detailed Breakdown" else 0.0
        current_clothing_personal_care = clothing_personal_care if input_style == "Detailed Breakdown" else 0.0
        current_charitable_donations = charitable_donations if input_style == "Detailed Breakdown" else 0.0
        current_student_loan_payments = student_loan_payments if input_style == "Detailed Breakdown" else 0.0
        current_alimony_child_support_paid = alimony_child_support_paid if input_style == "Detailed Breakdown" else 0.0
        current_travel_vacation = travel_vacation if input_style == "Detailed Breakdown" else 0.0
        current_hobbies_special_interests = hobbies_special_interests if input_style == "Detailed Breakdown" else 0.0
        current_pet_care = pet_care if input_style == "Detailed Breakdown" else 0.0
        current_home_maintenance = home_maintenance if input_style == "Detailed Breakdown" else 0.0
        current_professional_services = professional_services if input_style == "Detailed Breakdown" else 0.0
        current_fitness_wellness = fitness_wellness if input_style == "Detailed Breakdown" else 0.0
        current_gifts_celebrations = gifts_celebrations if input_style == "Detailed Breakdown" else 0.0
        current_savings_contributions = savings_contributions if input_style == "Detailed Breakdown" else 0.0
        current_miscellaneous_expenses = miscellaneous_expenses if input_style == "Detailed Breakdown" else 0.0

        for year in range(2025, 2025 + sim_years):
            current_age = age + (year - 2025)
            # Income
            if input_style == "Detailed Breakdown":
                current_rental_income *= (1 + rent_growth)
                current_social_security *= (1 + ss_cola)
                current_salary_income *= (1 + inflation_rate)
                current_self_employment_income *= (1 + inflation_rate)
                current_investment_income *= (1 + inflation_rate)
                current_pension_income *= (1 + inflation_rate)
                current_annuity_income *= (1 + inflation_rate)
                current_part_time_income *= (1 + inflation_rate)
                current_passive_income *= (1 + inflation_rate)
                current_government_assistance *= (1 + inflation_rate)
                current_alimony_child_support_received *= (1 + inflation_rate)
                current_family_support_gifts *= (1 + inflation_rate)
                current_inheritance_gains *= (1 + inflation_rate)
                current_scholarships_grants *= (1 + inflation_rate)
                current_other_income *= (1 + inflation_rate)

                total_income_monthly = (
                    current_salary_income + current_self_employment_income + current_rental_income +
                    current_investment_income + current_pension_income + current_social_security +
                    current_annuity_income + current_part_time_income + current_passive_income +
                    current_government_assistance + current_alimony_child_support_received +
                    current_family_support_gifts + current_inheritance_gains + current_scholarships_grants +
                    current_other_income
                )
                total_income = total_income_monthly * 12
            else:
                total_income *= (1 + inflation_rate)

            net_total_income = total_income * (1 - income_tax_rate)

            # Expenses
            if input_style == "Detailed Breakdown":
                current_housing_costs *= (1 + inflation_rate)
                current_utilities *= (1 + inflation_rate)
                current_groceries_food *= (1 + inflation_rate)
                current_dining_out *= (1 + inflation_rate)
                current_transportation *= (1 + inflation_rate)
                current_healthcare_costs *= (1 + inflation_rate)
                current_insurance_premiums *= (1 + inflation_rate)
                current_education_expenses *= (1 + inflation_rate)
                current_childcare_dependent_care *= (1 + inflation_rate)
                current_entertainment_leisure *= (1 + inflation_rate)
                current_clothing_personal_care *= (1 + inflation_rate)
                current_charitable_donations *= (1 + inflation_rate)
                current_student_loan_payments *= (1 + inflation_rate)
                current_alimony_child_support_paid *= (1 + inflation_rate)
                current_travel_vacation *= (1 + inflation_rate)
                current_hobbies_special_interests *= (1 + inflation_rate)
                current_pet_care *= (1 + inflation_rate)
                current_home_maintenance *= (1 + inflation_rate)
                current_professional_services *= (1 + inflation_rate)
                current_fitness_wellness *= (1 + inflation_rate)
                current_gifts_celebrations *= (1 + inflation_rate)
                current_savings_contributions *= (1 + inflation_rate)
                current_miscellaneous_expenses *= (1 + inflation_rate)

                total_expenses_monthly = (
                    current_housing_costs + current_utilities + current_groceries_food + current_dining_out +
                    current_transportation + current_healthcare_costs + current_insurance_premiums +
                    current_education_expenses + current_childcare_dependent_care + current_entertainment_leisure +
                    current_clothing_personal_care + current_charitable_donations + current_student_loan_payments +
                    current_alimony_child_support_paid + current_travel_vacation + current_hobbies_special_interests +
                    current_pet_care + current_home_maintenance + current_professional_services +
                    current_fitness_wellness + current_gifts_celebrations + current_savings_contributions +
                    current_miscellaneous_expenses
                )
                total_expenses = total_expenses_monthly * 12
            else:
                total_expenses *= (1 + inflation_rate)

            net_draw = total_expenses - net_total_income

            # RMD
            rmd = 0.0
            if current_age in rmd_divisors:
                rmd = current_financial_assets / rmd_divisors[current_age]
            net_rmd = rmd * (1 - rmd_tax_rate)
            cash_from_savings = max(0, net_draw - net_rmd)
            if cash_from_savings > 0:
                rmd_used = rmd
                net_rmd_used = net_rmd
            else:
                rmd_used = net_draw / (1 - rmd_tax_rate)
                net_rmd_used = net_draw
                cash_from_savings = 0.0

            # Financial Assets
            financial_assets_open = current_financial_assets
            financial_assets_growth = financial_assets_open * growth_rate
            financial_assets_before_draw = financial_assets_open + financial_assets_growth
            current_financial_assets = financial_assets_before_draw - cash_from_savings - rmd_used

            # Real Estate
            current_primary_home_value *= (1 + home_appreciation)
            current_secondary_home_value *= (1 + home_appreciation)

            # Net Worth
            total_assets = (
                current_financial_assets + current_primary_home_value + current_secondary_home_value +
                current_other_assets + pension_fund_value
            )
            net_worth = total_assets - current_total_liabilities

            results.append({
                "Year": year,
                "Age": current_age,
                "Total Income": round(total_income, 2),
                "Net Total Income": round(net_total_income, 2),
                "Total Expenses": round(total_expenses, 2),
                "Net Draw": round(net_draw, 2),
                "RMD Used": round(rmd_used, 2),
                "Net RMD Used": round(net_rmd_used, 2),
                "Cash from Savings": round(cash_from_savings, 2),
                "Financial Assets Open": round(financial_assets_open, 2),
                "Financial Assets Growth": round(financial_assets_growth, 2),
                "Financial Assets Before Draw": round(financial_assets_before_draw, 2),
                "Financial Assets End": round(current_financial_assets, 2),
                "Primary Home Value": round(current_primary_home_value, 2),
                "Secondary Home Value": round(current_secondary_home_value, 2),
                "Total Assets": round(total_assets, 2),
                "Total Liabilities": round(current_total_liabilities, 2),
                "Net Worth": round(net_worth, 2)
            })
        df = pd.DataFrame(results)
        st.write("Year-by-Year Data (Deterministic)")
        st.dataframe(df)

    # Download CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="simulation_all_ages.csv",
        mime="text/csv"
    )

    # OpenAI Assessment
    if use_openai and openai_api_key:
        try:
            client = OpenAI(api_key=openai_api_key)
            df_str = df.to_string()
            prompt = (
                "You are a financial advisor. Below is a retirement simulation for a person starting at age " + str(age) +
                ". The simulation includes year-by-year data on income, expenses, savings, home value, and net worth.\n\n" +
                df_str + "\n\n" +
                "Please provide a detailed financial assessment. Include:\n" +
                "- Whether their savings will last through the simulation period.\n" +
                "- Key risks or concerns (e.g., high expenses, low income).\n" +
                "- Recommendations to improve their financial outlook (e.g., reduce expenses, increase income, adjust investments).\n" +
                "- Any other insights or advice."
            )
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial advisor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            assessment = response.choices[0].message.content
            st.subheader("OpenAI Financial Assessment")
            st.write(assessment)
        except Exception as e:
            st.error(f"Error with OpenAI API: {str(e)}")
            st.write("Please check your API key or ensure you have access to the OpenAI API.")