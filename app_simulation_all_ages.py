import os
import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI

# --- Load API Key ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("OpenAI API key not found. Please set it in Streamlit secrets.")
    st.stop()

# --- Clear Session State for All Sliders at the Very Top ---
SLIDER_KEYS = ["income_tax_rate", "rmd_tax_rate", "growth_rate", "home_appreciation", 
               "inflation_rate", "ss_cola", "rent_growth", "sim_years"]
for key in SLIDER_KEYS:
    if key in st.session_state:
        del st.session_state[key]
DEFAULT_VALUES = {
    "income_tax_rate": 0.25,
    "rmd_tax_rate": 0.25,
    "growth_rate": 0.05,
    "home_appreciation": 0.03,
    "inflation_rate": 0.025,
    "ss_cola": 0.025,
    "rent_growth": 0.02,
    "sim_years": 14
}
for key, default in DEFAULT_VALUES.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Page Config ---
st.set_page_config(page_title="Retirement Simulation (All Ages)", layout="wide")
def usd(x): return f"${x:,.0f}"

# --- Saved Inputs ---
SAVE_FILE = "my_saved_inputs_all_ages.json"
saved = {}
try:
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            temp_saved = json.load(f)
        for key, val in temp_saved.items():
            if isinstance(val, (int, float)):
                saved[key] = float(val)
except (json.JSONDecodeError, IOError):
    saved = {}

# --- Add a Button to Clear Session State and JSON File ---
if st.button("Clear Saved Data and Session State"):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump({}, f)
    except IOError as e:
        st.error(f"Error clearing saved data: {e}")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    for key, default in DEFAULT_VALUES.items():
        st.session_state[key] = default
    st.success("Session state and saved data cleared!")
    st.rerun()

# --- Preferences ---
st.markdown("### 🧹 Preferences")
col1, col2 = st.columns([5, 1])
use_saved = col2.checkbox("Use Saved Inputs", value=False)
save_inputs = st.checkbox("Save Inputs for Next Time")
if use_saved:
    st.info("Note: Loaded values may not match the default age group. Please verify your age group selection.")

# --- Title & Mode Switch ---
st.title("🎯 Retirement Simulation (All Ages)")
mode = st.radio("Input Style:", ["Detailed Breakdown", "Gross Totals"], horizontal=True)
inputs = {}

# --- Input Helpers ---
def smart_input(label, key, default_value, min_value=0.0):
    if not isinstance(default_value, (int, float)):
        default_value = min_value
    if use_saved and key in saved:
        default_value = float(saved.get(key, default_value))
    val = st.number_input(label, min_value=float(min_value), value=float(default_value), step=100.0, key=key, format="%.0f")
    saved[key] = val
    return val

def smart_slider(label, key, min_val, max_val, default_value, step):
    if not isinstance(default_value, (int, float)):
        default_value = min_val
    if use_saved and key in saved:
        saved_val = saved.get(key, default_value)
        if isinstance(saved_val, (int, float)):
            default_value = float(saved_val)
        else:
            default_value = min_val
    val = st.slider(label, min_val, max_val, float(default_value), step=step, key=key)
    saved[key] = val
    return val

# --- Determine Age Group from Saved Age ---
default_age_group = "25-55"
if use_saved and "age" in saved:
    saved_age = saved["age"]
    if 25 <= saved_age <= 55:
        default_age_group = "25-55"
    elif 56 <= saved_age <= 69:
        default_age_group = "56-69"
    else:
        default_age_group = "70+"

# --- Tabs for Inputs ---
tab1, tab2, tab3 = st.tabs(["👤 Age", "💵 Income & Expenses", "💰 Assets & Liabilities"])

with tab1:
    age_group = st.selectbox("Age Group:", ["25-55", "56-69", "70+"], index=["25-55", "56-69", "70+"].index(default_age_group))
    if age_group == "25-55":
        age = smart_input("🎂 Age", "age", 40, min_value=25)
    elif age_group == "56-69":
        age = smart_input("🎂 Age", "age", 68, min_value=56)
    else:
        age = smart_input("🎂 Age", "age", 76, min_value=70)

with tab2:
    if mode == "Gross Totals":
        col1, col2 = st.columns(2)
        with col1:
            inputs["total_income"] = smart_input("💵 Monthly Income", "total_income", 5652)
        with col2:
            inputs["total_expenses"] = smart_input("💸 Monthly Expenses", "total_expenses", 16452)
        st.markdown(f"**Total Monthly Income:** {usd(inputs['total_income'])} | **Total Monthly Expenses:** {usd(inputs['total_expenses'])}")
    else:
        # Income Section
        with st.expander("💵 Income (Monthly, Pre-Tax)", expanded=True):
            st.markdown("**Work & Business Income**")
            col1, col2 = st.columns(2)
            with col1:
                inputs["salary"] = smart_input("💼 Salary", "salary", 0)
                inputs["side_gigs"] = smart_input("🚀 Side Gigs", "side_gigs", 0)
            with col2:
                inputs["business_income"] = smart_input("🏢 Business", "business_income", 0)
                inputs["investment_income"] = smart_input("📈 Investments", "investment_income", 0)
            
            st.markdown("**Retirement & Other Income**")
            col1, col2 = st.columns(2)
            with col1:
                inputs["social_security"] = smart_input("🧃 Social Security", "social_security", 3662 if age_group != "25-55" else 0)
                inputs["rental_income"] = smart_input("🏨 Rental", "rental_income", 2000)
            with col2:
                inputs["other_income"] = smart_input("💰 Other", "other_income", 0)
            
            inputs["total_income"] = sum([inputs["salary"], inputs["side_gigs"], inputs["investment_income"],
                                         inputs["business_income"], inputs["social_security"], inputs["rental_income"],
                                         inputs["other_income"]])
            st.markdown(f"**Total Monthly Income:** {usd(inputs['total_income'])}")

        # Expenses Section
        with st.expander("💸 Expenses (Monthly, Pre-Tax)", expanded=True):
            st.markdown("**Housing & Living Costs**")
            col1, col2 = st.columns(2)
            with col1:
                inputs["mortgage_rent"] = smart_input("🏠 Mortgage/Rent", "mortgage_rent", 0)
                inputs["utilities"] = smart_input("💡 Utilities", "utilities", 0)
            with col2:
                inputs["groceries"] = smart_input("🍎 Groceries", "groceries", 0)
                inputs["entertainment"] = smart_input("🎭 Entertainment", "entertainment", 0)
            
            st.markdown("**Transportation & Healthcare**")
            col1, col2 = st.columns(2)
            with col1:
                inputs["transportation"] = smart_input("🚗 Transportation", "transportation", 0)
                inputs["healthcare"] = smart_input("🩺 Healthcare", "healthcare", 0)
            with col2:
                inputs["education"] = smart_input("📚 Education", "education", 0)
            
            st.markdown("**Insurance & Debt**")
            col1, col2 = st.columns(2)
            with col1:
                inputs["insurance"] = smart_input("🛡️ Insurance", "insurance", 4355)
                inputs["debt_payments"] = smart_input("💳 Debt", "debt_payments", 0)
            with col2:
                inputs["other_expenses"] = smart_input("💸 Other", "other_expenses", 12097)
            
            inputs["total_expenses"] = sum([inputs["mortgage_rent"], inputs["utilities"], inputs["groceries"],
                                          inputs["transportation"], inputs["healthcare"], inputs["education"],
                                          inputs["entertainment"], inputs["insurance"], inputs["debt_payments"],
                                          inputs["other_expenses"]])
            st.markdown(f"**Total Monthly Expenses:** {usd(inputs['total_expenses'])}")

with tab3:
    # Assets
    with st.expander("📈 Assets", expanded=True):
        st.markdown("**Financial Assets**")
        col1, col2 = st.columns(2)
        with col1:
            inputs["ira_balance"] = smart_input("📦 IRA/401(k)", "ira_balance", 1850000)
            inputs["savings_balance"] = smart_input("🏦 Savings", "savings_balance", 25000)
        with col2:
            inputs["other_investments"] = smart_input("📈 Other Investments", "other_investments", 0)
        
        st.markdown("**Property & Vehicles**")
        col1, col2 = st.columns(2)
        with col1:
            inputs["home_value"] = smart_input("🏡 Home Value", "home_value", 500000)
        with col2:
            inputs["car_value"] = smart_input("🚗 Car Value", "car_value", 20000)
        
        inputs["total_assets"] = sum([inputs["ira_balance"], inputs["savings_balance"], inputs["home_value"],
                                    inputs["car_value"], inputs["other_investments"]])
        st.markdown(f"**Total Assets:** {usd(inputs['total_assets'])}")

    # Liabilities
    with st.expander("📉 Liabilities", expanded=True):
        st.markdown("**Housing & Education Debt**")
        col1, col2 = st.columns(2)
        with col1:
            inputs["mortgage_balance"] = smart_input("🏠 Mortgage", "mortgage_balance", 200000)
        with col2:
            inputs["student_loans"] = smart_input("📚 Student Loans", "student_loans", 0)
        
        st.markdown("**Other Debt**")
        col1, col2 = st.columns(2)
        with col1:
            inputs["credit_card_debt"] = smart_input("💳 Credit Card", "credit_card_debt", 0)
            inputs["car_loans"] = smart_input("🚗 Car Loans", "car_loans", 0)
        with col2:
            inputs["other_debt"] = smart_input("💸 Other Debt", "other_debt", 0)
        
        inputs["total_liabilities"] = sum([inputs["mortgage_balance"], inputs["student_loans"],
                                           inputs["credit_card_debt"], inputs["car_loans"], inputs["other_debt"]])
        st.markdown(f"**Total Liabilities:** {usd(inputs['total_liabilities'])}")
        
        st.markdown("**Equity**")
        inputs["net_home_equity"] = inputs["home_value"] - inputs["mortgage_balance"]
        inputs["net_car_equity"] = inputs["car_value"] - inputs["car_loans"]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Net Home Equity:** {usd(inputs['net_home_equity'])}")
        with col2:
            st.markdown(f"**Net Car Equity:** {usd(inputs['net_car_equity'])}")

# --- Simulation Settings ---
with st.expander("⚙️ Simulation Settings", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        income_tax_rate = smart_slider("📊 Income Tax Rate", "income_tax_rate", 0.0, 0.5, 0.25, 0.01)
        rmd_tax_rate = smart_slider("🧾 RMD Tax Rate", "rmd_tax_rate", 0.0, 0.5, 0.25, 0.01)
        inflation_rate = smart_slider("📈 Inflation Rate", "inflation_rate", 0.0, 0.1, 0.025, 0.005)
    with col2:
        growth_rate = smart_slider("📈 Asset Growth Rate", "growth_rate", 0.0, 0.2, 0.05, 0.005)
        home_appreciation = smart_slider("🏡 Home Appreciation", "home_appreciation", 0.0, 0.1, 0.03, 0.005)
        ss_cola = smart_slider("📈 SS COLA", "ss_cola", 0.0, 0.1, 0.025, 0.005)
        rent_growth = smart_slider("📈 Rental Growth", "rent_growth", 0.0, 0.1, 0.02, 0.005)
    sim_years = smart_input("🔁 Years to Simulate", "sim_years", 14, min_value=1)

# --- Save Inputs ---
if save_inputs:
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(saved, f)
        st.success("Inputs saved successfully!")
    except IOError as e:
        st.error(f"Error saving inputs: {e}")

# --- IRS Divisors ---
irs_divisors = {
    25: 59.5, 26: 58.5, 27: 57.5, 28: 56.5, 29: 55.5, 30: 54.5, 31: 53.5, 32: 52.5, 33: 51.5, 34: 50.5,
    35: 49.5, 36: 48.5, 37: 47.5, 38: 46.5, 39: 45.5, 40: 44.5, 41: 43.5, 42: 42.5, 43: 41.5, 44: 40.5,
    45: 39.5, 46: 38.5, 47: 37.5, 48: 36.5, 49: 35.5, 50: 34.5, 51: 33.5, 52: 32.5, 53: 31.5, 54: 30.5,
    55: 29.5, 56: 28.5, 57: 27.5, 58: 26.5, 59: 25.5, 60: 24.5, 61: 23.5, 62: 22.5, 63: 21.5, 64: 20.5,
    65: 19.5, 66: 18.5, 67: 17.5, 68: 16.5, 69: 15.5, 70: 27.4, 71: 26.5, 72: 25.6, 73: 24.7, 74: 23.8,
    75: 22.9, 76: 22.0, 77: 21.2, 78: 20.3, 79: 19.5, 80: 18.7, 81: 17.9, 82: 17.1, 83: 16.3, 84: 15.5,
    85: 14.8, 86: 14.1, 87: 13.4, 88: 12.7, 89: 12.0, 90: 11.4, 91: 10.8, 92: 10.2
}

# --- Simulation ---
rows = []
combined_balance = inputs["ira_balance"] + inputs["savings_balance"]
cur_ira = inputs["ira_balance"]
cur_savings = inputs["savings_balance"]
cur_home_value = inputs["home_value"]
start_year = 2025

for i in range(int(sim_years)):
    yr = start_year + i
    age_i = age + i

    # Income (convert monthly to annual)
    if mode == "Detailed Breakdown":
        salary = inputs["salary"] * 12
        side_gigs = inputs["side_gigs"] * 12
        investment_income = inputs["investment_income"] * 12
        business_income = inputs["business_income"] * 12
        ss = 0
        if age_group != "25-55" and age_i >= 62:
            ss = inputs["social_security"] * (1 + ss_cola) ** i * 12
        rent = inputs["rental_income"] * (1 + rent_growth) ** i * 12
        other_income = inputs["other_income"] * 12
        total_income = salary + side_gigs + investment_income + business_income + ss + rent + other_income
    else:
        total_income = inputs["total_income"] * 12
    net_income = total_income * (1 - income_tax_rate)

    # Expenses (convert monthly to annual)
    if mode == "Detailed Breakdown":
        mortgage_rent = inputs["mortgage_rent"] * (1 + inflation_rate) ** i * 12
        utilities = inputs["utilities"] * (1 + inflation_rate) ** i * 12
        groceries = inputs["groceries"] * (1 + inflation_rate) ** i * 12
        transportation = inputs["transportation"] * (1 + inflation_rate) ** i * 12
        healthcare = inputs["healthcare"] * (1 + inflation_rate) ** i * 12
        education = inputs["education"] * (1 + inflation_rate) ** i * 12
        entertainment = inputs["entertainment"] * (1 + inflation_rate) ** i * 12
        insurance = inputs["insurance"] * (1 + inflation_rate) ** i * 12
        debt_payments = inputs["debt_payments"] * (1 + inflation_rate) ** i * 12
        other_expenses = inputs["other_expenses"] * (1 + inflation_rate) ** i * 12
        total_expenses = (mortgage_rent + utilities + groceries + transportation + healthcare +
                         education + entertainment + insurance + debt_payments + other_expenses)
    else:
        total_expenses = inputs["total_expenses"] * (1 + inflation_rate) ** i * 12

    # RMD Calculation (only if age >= 72)
    rmd = 0
    net_rmd = 0
    if age_i >= 72:
        div = irs_divisors.get(age_i, 10.2)
        rmd = cur_ira / div if cur_ira > 0 else 0
        cur_ira -= rmd
        net_rmd = rmd * (1 - rmd_tax_rate)

    # IRA Growth
    ira_growth = cur_ira * growth_rate
    cur_ira += ira_growth

    # Update combined balance before draw
    combined_balance = cur_ira + cur_savings
    savings_growth = combined_balance * growth_rate
    combined_before = combined_balance + savings_growth

    # Drawdown from combined balance
    net_draw = total_expenses - net_income
    cash_from_savings = max(0, net_draw - net_rmd)
    combined_balance = combined_before - cash_from_savings

    # Allocate remaining balance back to IRA and savings
    if combined_balance <= 0:
        cur_ira = 0
        cur_savings = combined_balance
    else:
        ira_proportion = cur_ira / (cur_ira + cur_savings) if (cur_ira + cur_savings) > 0 else 0
        cur_ira = combined_balance * ira_proportion
        cur_savings = combined_balance * (1 - ira_proportion)

    # Update home value
    home_growth = cur_home_value * home_appreciation
    cur_home_value += home_growth

    # Calculate net worth
    total_assets = cur_ira + cur_savings + cur_home_value + inputs["car_value"] + inputs["other_investments"]
    total_liabilities = inputs["mortgage_balance"] + inputs["student_loans"] + inputs["credit_card_debt"] + inputs["car_loans"] + inputs["other_debt"]
    net_worth = total_assets - total_liabilities

    rows.append({
        "Year": yr,
        "Age": age_i,
        "Total Income": round(total_income, 2),
        "Net Total Income": round(net_income, 2),
        "Total Expenses": round(total_expenses, 2),
        "Net Draw": round(net_draw, 2),
        "RMD Used": round(rmd, 2),
        "Net RMD Used": round(net_rmd, 2),
        "Cash from Savings": round(cash_from_savings, 2),
        "Savings Open": round(combined_before - savings_growth, 2),
        "Savings Growth": round(savings_growth, 2),
        "Savings Before Draw": round(combined_before, 2),
        "Savings End": round(combined_balance, 2),
        "Home Value": round(cur_home_value, 2),
        "Net Worth": round(net_worth, 2)
    })

# --- OpenAI Functions ---
df = pd.DataFrame(rows)

def get_summary(df):
    prompt = f"Provide a concise yet detailed summary of this retirement plan, including starting savings, income, expenses, growth trends, final savings, home value, and net worth. Highlight a key insight or trend:\n{df.to_string()}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def get_smart_answer(df, question):
    prompt = f"Based on this retirement simulation data:\n{df.to_string()}\nAnswer the following question:\n{question}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

# --- Display Results ---
st.markdown("---")
st.subheader("📌 Simulation Summary")
if df.empty:
    st.error("Simulation failed to run. Please ensure 'Years to Simulate' is at least 1 and check your inputs.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Savings", usd(df['Savings End'].iloc[-1]))
    col2.metric("Final Home Value", usd(df['Home Value'].iloc[-1]))
    col3.metric("Final Net Worth", usd(df['Net Worth'].iloc[-1]))

    st.subheader("📋 Year-by-Year Data")
    st.dataframe(df.style.format({col: usd for col in df.columns if col not in ["Year", "Age"]}), use_container_width=True)

    # --- OpenAI Features ---
    st.subheader("📝 Insights & Analysis")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Summary"):
            try:
                summary = get_summary(df)
                st.markdown("#### Plan Summary")
                st.write(summary)
            except Exception as e:
                st.error(f"Error generating summary: {e}")
    with col2:
        question = st.text_input("Ask a Question:", placeholder="e.g., What’s the best strategy to increase my net worth by 2030?")
        if st.button("Get Answer"):
            if question:
                try:
                    answer = get_smart_answer(df, question)
                    st.markdown("#### Answer")
                    st.write(answer)
                except Exception as e:
                    st.error(f"Error answering question: {e}")
            else:
                st.warning("Please enter a question!")

    # --- Download Button ---
    csv = df.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, "simulation_all_ages.csv", "text/csv")

    # --- Plots ---
    st.subheader("📊 Financial Overview")
    fig, ax = plt.subplots()
    ax.plot(df["Year"], df["Savings End"], label="Savings", color="blue")
    ax.plot(df["Year"], df["Home Value"], label="Home Value", color="green")
    ax.plot(df["Year"], df["Net Worth"], label="Net Worth", color="orange")
    ax.set_xlabel("Year")
    ax.set_ylabel("Amount ($)")
    ax.legend()

    # Income vs. Expenses Chart
    st.subheader("📊 Income vs. Expenses Over Time")
    fig2, ax2 = plt.subplots()
    ax2.plot(df["Year"], df["Total Income"], label="Total Income", color="green")
    ax2.plot(df["Year"], df["Total Expenses"], label="Total Expenses", color="red")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Amount ($)")
    ax2.legend()
    st.pyplot(fig2)

    # Optimize My Plan Feature
    st.subheader("📈 Optimize Your Plan")
    if st.button("Optimize My Plan"):
        try:
            prompt = f"Based on this retirement simulation data:\n{df.to_string()}\nSuggest three specific ways to increase net worth by the end of the simulation period."
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            optimization = response.choices[0].message.content.strip()
            st.markdown("#### Optimization Suggestions")
            st.write(optimization)
        except Exception as e:
            st.error(f"Error generating optimization: {e}")
    st.pyplot(fig)

