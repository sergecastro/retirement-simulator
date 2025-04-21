import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 🔐 Simple Password Gate ---
st.sidebar.markdown("### 🔐 Secure Access")
password = st.sidebar.text_input("Enter password", type="password")

if password != "letmein":
    st.warning("Please enter the correct password to use the app.")
    st.stop()

st.info("👋 Welcome! Please enter your own numbers below to simulate your retirement plan. This app does not include preset personal data.")

# --- Formatting helper ---
def usd(x):
    return f"${x:,.0f}"

# --- Sidebar Controls ---
st.sidebar.header("Retirement Simulation Inputs")
start_year = st.sidebar.number_input("Start Year", value=2025, key="start_year")
years = st.sidebar.slider("Number of Years", 10, 40, 20, key="years")
age_first_start = st.sidebar.number_input("First Person Age at Start", value=70, key="age_first")
age_second_start = st.sidebar.number_input("Second Person Age at Start (enter 0 to ignore)", value=0, key="age_second")
monthly_expenses = st.sidebar.number_input("Monthly Living Expenses", value=0, key="monthly_expenses")
insurance_annual = st.sidebar.number_input("Yearly Premium Life Insurance", value=0, key="insurance_annual")
inflation_rate = st.sidebar.slider("Inflation Rate", 0.0, 0.1, 0.025, key="inflation_rate")
insurance_growth = st.sidebar.slider("Insurance Growth Rate", 0.0, 0.1, 0.025, key="insurance_growth")
ss_first = st.sidebar.number_input("First Person SS Monthly", value=0, key="ss_first")
ss_second = st.sidebar.number_input("Second Person SS Monthly", value=0, key="ss_second")
ss_cola = st.sidebar.slider("Social Security COLA", 0.0, 0.1, 0.025, key="ss_cola")
rent_income = st.sidebar.number_input("Monthly Rental Income", value=0, key="rent_income")
rent_growth = st.sidebar.slider("Rental Income Growth", 0.0, 0.1, 0.02, key="rent_growth")
income_tax_rate = st.sidebar.slider("Income Tax Rate", 0.0, 0.5, 0.25, key="income_tax_rate")
rmd_tax_rate = st.sidebar.slider("RMD Tax Rate", 0.0, 0.5, 0.25, key="rmd_tax_rate")
ira_start = st.sidebar.number_input("Starting IRA Balance", value=0, key="ira_start")
ira_growth_rate = st.sidebar.slider("IRA Growth Rate", 0.0, 0.2, 0.05, key="ira_growth_rate")
savings_start = st.sidebar.number_input("Starting Regular Savings", value=0, key="savings_start")
savings_growth_rate = st.sidebar.slider("Savings Growth Rate", 0.0, 0.2, 0.05, key="savings_growth_rate")

# --- IRS RMD Divisors ---
irs_divisors = {
    73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1,
    80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2,
    87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8
}

# --- SIMULATION ---
years_range = list(range(start_year, start_year + years))
ages_first = list(range(age_first_start, age_first_start + years))
ages_second = list(range(age_second_start, age_second_start + years)) if age_second_start > 0 else ["N/A"] * years
ira = ira_start
savings = savings_start
results = []
ira_depleted_year = None
savings_depleted_year = None
first_shortfall_year = None
total_drawdown = 0

for i, year in enumerate(years_range):
    age = ages_first[i]
    age_2 = ages_second[i]
    expenses = monthly_expenses * 12 * (1 + inflation_rate) ** i
    insurance = insurance_annual * (1 + insurance_growth) ** i
    total_expenses = expenses + insurance

    ss_s = ss_first * 12 * (1 + ss_cola) ** i
    ss_j = ss_second * 12 * (1 + ss_cola) ** i if age_second_start > 0 else 0
    rent = rent_income * 12 * (1 + rent_growth) ** i
    earned_income = ss_s + ss_j + rent
    income_tax = earned_income * income_tax_rate
    net_income = earned_income - income_tax

    rmd_ira = ira / irs_divisors[age] if age in irs_divisors and ira > 0 else 0
    rmd_savings = 0 if ira > 0 else savings / irs_divisors[age] if age in irs_divisors else 0

    ira -= rmd_ira
    savings -= rmd_savings

    ira_growth_amt = ira * ira_growth_rate
    savings_growth_amt = savings * savings_growth_rate

    ira += ira_growth_amt
    savings += savings_growth_amt

    total_rmd = rmd_ira + rmd_savings
    rmd_tax = total_rmd * rmd_tax_rate
    net_rmd = total_rmd - rmd_tax

    total_cash_available = net_income + net_rmd
    shortfall = max(0, total_expenses - total_cash_available)

    ira_used = min(ira, shortfall)
    ira -= ira_used
    remaining_shortfall = shortfall - ira_used
    savings_used = min(savings, remaining_shortfall)
    savings -= savings_used

    total_used = ira_used + savings_used
    total_drawdown += total_used

    if ira_depleted_year is None and ira <= 1:
        ira_depleted_year = year
    if savings_depleted_year is None and savings <= 1:
        savings_depleted_year = year
    if first_shortfall_year is None and shortfall > 0:
        first_shortfall_year = year

    results.append({
        "Year": year,
        "Age - First Person": age,
        "Age - Second Person": age_2,
        "Monthly Expenses": round(expenses, 2),
        "Insurance Premium": round(insurance, 2),
        "Total Expenses": round(total_expenses, 2),
        "Earned Income": round(earned_income, 2),
        "Income Tax": round(income_tax, 2),
        "Net Income": round(net_income, 2),
        "RMD from IRA": round(rmd_ira, 2),
        "RMD from Savings": round(rmd_savings, 2),
        "RMD Tax": round(rmd_tax, 2),
        "Net RMD": round(net_rmd, 2),
        "Total Cash Available": round(total_cash_available, 2),
        "Shortfall": round(shortfall, 2),
        "Used from IRA": round(ira_used, 2),
        "Used from Savings": round(savings_used, 2),
        "IRA Balance": round(ira, 2),
        "Savings Balance": round(savings, 2),
        "Total Drawdown": round(total_used, 2)
    })

# --- Dashboard ---
df = pd.DataFrame(results)
st.subheader("📌 Simulation Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Final IRA Balance", usd(df['IRA Balance'].iloc[-1]))
col2.metric("Final Savings Balance", usd(df['Savings Balance'].iloc[-1]))
col3.metric("Total Drawdown", usd(total_drawdown))

if ira_depleted_year:
    st.warning(f"⚠️ IRA depleted in {ira_depleted_year}")
if savings_depleted_year:
    st.warning(f"❌ Savings depleted in {savings_depleted_year}")
if first_shortfall_year:
    st.info(f"📉 First shortfall occurred in {first_shortfall_year}")

# --- Data Table ---
formatted_df = df.copy()
currency_cols = [
    "Monthly Expenses", "Insurance Premium", "Total Expenses", "Earned Income",
    "Income Tax", "Net Income", "RMD from IRA", "RMD from Savings", "RMD Tax",
    "Net RMD", "Total Cash Available", "Shortfall", "Used from IRA",
    "Used from Savings", "IRA Balance", "Savings Balance", "Total Drawdown"
]
for col in currency_cols:
    formatted_df[col] = formatted_df[col].apply(usd)

st.subheader("📋 Year-by-Year Data Table")
st.dataframe(formatted_df, use_container_width=True)

# --- Download Button ---
st.download_button("📥 Download CSV", data=df.to_csv(index=False), file_name="retirement_projection.csv", mime="text/csv")
