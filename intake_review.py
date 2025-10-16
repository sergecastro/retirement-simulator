# intake_review.py - Advanced pages for Family Retirement Intake
# Pages 4-7: Assets, Liabilities, Family Events, Review & Export
import streamlit as st
import pandas as pd
import json

# ---------- small helpers (types + currency sanitizing) ----------
def _to_float(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        if isinstance(x, str):
            x = x.replace("$", "").replace(",", "").strip()
            return float(x) if x else default
        return float(x)
    except Exception:
        return default

def _to_int_or_none(x):
    try:
        if x is None or x == "":
            return None
        if isinstance(x, str):
            x = x.strip()
        return int(float(x))
    except Exception:
        return None

def _ensure_columns(df: pd.DataFrame, columns_with_dtype):
    """
    Ensure DataFrame has given columns. columns_with_dtype is list of tuples: (name, dtype)
    dtype can be 'Int64', 'float', 'str', or 'bool'.
    """
    if df is None or df.empty:
        cols = {}
        for name, dtype in columns_with_dtype:
            if dtype == "Int64":
                cols[name] = pd.Series(dtype="Int64")
            elif dtype == "float":
                cols[name] = pd.Series(dtype="float")
            elif dtype == "bool":
                cols[name] = pd.Series(dtype="boolean")
            else:
                cols[name] = pd.Series(dtype="object")
        return pd.DataFrame(cols)
    # add missing columns
    for name, dtype in columns_with_dtype:
        if name not in df.columns:
            if dtype == "Int64":
                df[name] = pd.Series([None] * len(df), dtype="Int64")
            elif dtype == "float":
                df[name] = pd.Series([None] * len(df), dtype="float")
            elif dtype == "bool":
                df[name] = pd.Series([None] * len(df), dtype="boolean")
            else:
                df[name] = ""
    return df

def show_assets_page(existing, save_payload, go_to_page):
    """Page 4: Assets & Accounts"""
    st.header("💎 Assets & Accounts")
    st.caption("Enter current balances for all your accounts and assets")
    
    # Retirement Accounts
    st.subheader("🦠 Retirement Accounts")
    ira = st.number_input(
        "Your IRA Balance",
        min_value=0.0,
        value=float(existing.get("input_ira_balance", 0.0)),
        step=1000.0,
        help="Traditional IRA balance"
    )
    
    k401 = st.number_input(
        "Your 401k/403b Balance",
        min_value=0.0,
        value=float(existing.get("input_four01k_403b_balance", 0.0)),
        step=1000.0,
        help="Current 401k or 403b balance"
    )
    
    # Partner accounts (if couple)
    partner_exists = existing.get("input_partner_exists", False)
    if partner_exists:
        st.caption("Partner Retirement Accounts")
        partner_ira = st.number_input(
            "Partner IRA Balance",
            min_value=0.0,
            value=float(existing.get("input_partner_ira_balance", 0.0)),
            step=1000.0
        )
        partner_k401 = st.number_input(
            "Partner 401k/403b Balance",
            min_value=0.0,
            value=float(existing.get("input_partner_four01k_403b_balance", 0.0)),
            step=1000.0
        )
    else:
        partner_ira = 0.0
        partner_k401 = 0.0
    
    # Savings & Investments
    st.subheader("💰 Savings & Investments")
    taxable = st.number_input(
        "Taxable Investment Accounts",
        min_value=0.0,
        value=float(existing.get("input_taxable_investment_accounts", 0.0)),
        step=1000.0,
        help="Brokerage accounts, mutual funds"
    )
    
    savings = st.number_input(
        "High-Yield Savings Account",
        min_value=0.0,
        value=float(existing.get("input_high_yield_savings_account", 0.0)),
        step=1000.0,
        help="Emergency fund, savings accounts"
    )
    
    hsa = st.number_input(
        "HSA Balance",
        min_value=0.0,
        value=float(existing.get("input_hsa_balance", 0.0)),
        step=500.0,
        help="Health Savings Account"
    )
    
    plan529 = st.number_input(
        "529 Plan Balance",
        min_value=0.0,
        value=float(existing.get("input_five29_plan_balance", 0.0)),
        step=500.0,
        help="Education savings plan"
    )
    
    # Real Estate
    st.subheader("🏡 Real Estate")
    primary_home = st.number_input(
        "Primary Residence Value",
        min_value=0.0,
        value=float(existing.get("input_primary_residence_value", 0.0)),
        step=10000.0,
        help="Current market value of your home"
    )
    
    secondary_home = st.number_input(
        "Secondary Residence Value",
        min_value=0.0,
        value=float(existing.get("input_secondary_residence_value", 0.0)),
        step=10000.0,
        help="Vacation home, rental property value"
    )
    
    # Other Assets
    st.subheader("🚗 Other Assets")
    vehicles = st.number_input(
        "Vehicles Value",
        min_value=0.0,
        value=float(existing.get("input_vehicles_value", 0.0)),
        step=1000.0,
        help="Cars, boats, RVs - current market value"
    )
    
    jewelry = st.number_input(
        "Jewelry & Collectibles",
        min_value=0.0,
        value=float(existing.get("input_jewelry_collectibles_value", 0.0)),
        step=500.0,
        help="Valuable jewelry, art, collectibles"
    )
    
    business = st.number_input(
        "Business Ownership Value",
        min_value=0.0,
        value=float(existing.get("input_business_ownership_value", 0.0)),
        step=5000.0,
        help="Your stake in a business"
    )
    
    crypto = st.number_input(
        "Cryptocurrency Holdings",
        min_value=0.0,
        value=float(existing.get("input_cryptocurrency_holdings", 0.0)),
        step=500.0,
        help="Bitcoin, Ethereum, etc. - current value"
    )
    
    other_assets = st.number_input(
        "Other Assets",
        min_value=0.0,
        value=float(existing.get("input_other_assets", 0.0)),
        step=500.0,
        help="Any other valuable assets"
    )
    
    # Calculate total
    total_assets = (ira + k401 + partner_ira + partner_k401 + taxable + savings + 
                   hsa + plan529 + primary_home + secondary_home + vehicles + 
                   jewelry + business + crypto + other_assets)
    
    st.divider()
    st.metric("Total Assets", f"${total_assets:,.2f}")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Expenses", use_container_width=True):
            go_to_page('expenses')
    with col3:
        if st.button("Next: Liabilities →", type="primary", use_container_width=True):
            # Save asset data
            data = existing.copy()
            data["input_ira_balance"] = float(ira)
            data["input_four01k_403b_balance"] = float(k401)
            data["input_partner_ira_balance"] = float(partner_ira)
            data["input_partner_four01k_403b_balance"] = float(partner_k401)
            data["input_taxable_investment_accounts"] = float(taxable)
            data["input_high_yield_savings_account"] = float(savings)
            data["input_hsa_balance"] = float(hsa)
            data["input_five29_plan_balance"] = float(plan529)
            data["input_primary_residence_value"] = float(primary_home)
            data["input_secondary_residence_value"] = float(secondary_home)
            data["input_vehicles_value"] = float(vehicles)
            data["input_jewelry_collectibles_value"] = float(jewelry)
            data["input_business_ownership_value"] = float(business)
            data["input_cryptocurrency_holdings"] = float(crypto)
            data["input_other_assets"] = float(other_assets)
            save_payload(data)
            go_to_page('liabilities')


def show_liabilities_page(existing, save_payload, go_to_page):
    """Page 5: Liabilities & Debts"""
    st.header("💳 Liabilities & Debts")
    st.caption("Enter outstanding balances (leave at $0 if you don't have these)")
    
    mortgage = st.number_input(
        "Mortgage Balance",
        min_value=0.0,
        value=float(existing.get("input_mortgage_balance", 0.0)),
        step=5000.0,
        help="Remaining mortgage principal"
    )
    
    auto_loan = st.number_input(
        "Auto Loans",
        min_value=0.0,
        value=float(existing.get("input_auto_loan_balance", 0.0)),
        step=500.0,
        help="Car loans, leases"
    )
    
    student_loan = st.number_input(
        "Student Loans",
        min_value=0.0,
        value=float(existing.get("input_student_loan_balance", 0.0)),
        step=500.0,
        help="Education debt"
    )
    
    credit_card = st.number_input(
        "Credit Card Debt",
        min_value=0.0,
        value=float(existing.get("input_credit_card_debt", 0.0)),
        step=100.0,
        help="Outstanding credit card balances"
    )
    
    other_debt = st.number_input(
        "Other Liabilities",
        min_value=0.0,
        value=float(existing.get("input_other_liabilities", 0.0)),
        step=500.0,
        help="Personal loans, HELOCs, other debts"
    )
    
    total_liabilities = mortgage + auto_loan + student_loan + credit_card + other_debt
    
    st.divider()
    st.metric("Total Liabilities", f"${total_liabilities:,.2f}")
    
    # Calculate net worth preview
    total_assets = sum([
        existing.get("input_ira_balance", 0.0),
        existing.get("input_four01k_403b_balance", 0.0),
        existing.get("input_partner_ira_balance", 0.0),
        existing.get("input_partner_four01k_403b_balance", 0.0),
        existing.get("input_taxable_investment_accounts", 0.0),
        existing.get("input_high_yield_savings_account", 0.0),
        existing.get("input_hsa_balance", 0.0),
        existing.get("input_five29_plan_balance", 0.0),
        existing.get("input_primary_residence_value", 0.0),
        existing.get("input_secondary_residence_value", 0.0),
        existing.get("input_vehicles_value", 0.0),
        existing.get("input_jewelry_collectibles_value", 0.0),
        existing.get("input_business_ownership_value", 0.0),
        existing.get("input_cryptocurrency_holdings", 0.0),
        existing.get("input_other_assets", 0.0)
    ])
    
    if total_assets > 0:
        net_worth = total_assets - total_liabilities
        st.metric("Estimated Net Worth", f"${net_worth:,.2f}")
        if net_worth < 0:
            st.warning("⚠️ Your liabilities exceed your assets. This is important to address.")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Assets", use_container_width=True):
            go_to_page('assets')
    with col3:
        if st.button("Next: Family Events →", type="primary", use_container_width=True):
            # Save liability data
            data = existing.copy()
            data["input_mortgage_balance"] = float(mortgage)
            data["input_auto_loan_balance"] = float(auto_loan)
            data["input_student_loan_balance"] = float(student_loan)
            data["input_credit_card_debt"] = float(credit_card)
            data["input_other_liabilities"] = float(other_debt)
            save_payload(data)
            go_to_page('family')


def show_family_page(existing, save_payload, go_to_page):
    """Page 6: Family Events (Children & Inheritances)"""
    st.header("👨‍👩‍👧‍👦 Family Events (Optional)")
    st.caption("Add children, college plans, and expected inheritances - skip if not applicable")
    
    # ============================================
    # CHILDREN SECTION (columns match simulator)
    # ============================================
    st.subheader("Children & College Plans")
    st.caption("Add rows for each child. Use calendar Birth Year.")
    if 'temp_children' not in st.session_state:
        # Accept any legacy keys; store canonical columns
        legacy_children = existing.get("children_list", existing.get("children_rows", [])) or []
        st.session_state.temp_children = []
        for r in legacy_children:
            st.session_state.temp_children.append({
                "Name": r.get("Name") or r.get("name", ""),
                "Birth Year": _to_int_or_none(r.get("Birth Year") or r.get("birth_year")),
                "College Plan": r.get("College Plan") or r.get("college_plan", "None"),
                "Scholarship %": _to_int_or_none(r.get("Scholarship %") or r.get("scholarship_pct") or 0),
                "Use 529 First?": bool(r.get("Use 529 First?") if "Use 529 First?" in r else r.get("use_529_first", True)),
                "Start Age": _to_int_or_none(r.get("Start Age") or r.get("start_age") or 18),
                "Years": _to_int_or_none(r.get("Years") or r.get("years") or 4),
            })
    children_df = pd.DataFrame(st.session_state.temp_children)
    children_df = _ensure_columns(children_df, [
        ("Name","str"),("Birth Year","Int64"),("College Plan","str"),
        ("Scholarship %","Int64"),("Use 529 First?","bool"),
        ("Start Age","Int64"),("Years","Int64")
    ])

    st.info("💡 **HOW TO USE:** After entering each value, press ENTER to save. Then move to next cell.")
    edited_children = st.data_editor(
        children_df,
        num_rows="dynamic",
        use_container_width=True,
        key="children_editor",
        column_config={
            "Name": st.column_config.TextColumn("Child Name", required=True),
            "Birth Year": st.column_config.NumberColumn("Birth Year", min_value=1900, max_value=2045, step=1, help="Child's birth year (1900-2045)"),
            "College Plan": st.column_config.SelectboxColumn(
                "College Plan",
                options=["None","Public In-State","Public Out-of-State","Private Nonprofit"]
            ),
            "Scholarship %": st.column_config.NumberColumn("Scholarship %", min_value=0, max_value=100, step=5),
            "Use 529 First?": st.column_config.CheckboxColumn("Use 529 First?"),
            "Start Age": st.column_config.NumberColumn("Start Age", min_value=0, max_value=30, step=1),
            "Years": st.column_config.NumberColumn("Years", min_value=0, max_value=10, step=1),
        },
    )
    # normalize dtypes before persisting
    if not edited_children.empty:
        edited_children["Birth Year"] = pd.to_numeric(edited_children["Birth Year"], errors="coerce").astype("Int64")
        edited_children["Scholarship %"] = pd.to_numeric(edited_children["Scholarship %"], errors="coerce").astype("Int64")
        edited_children["Start Age"] = pd.to_numeric(edited_children["Start Age"], errors="coerce").astype("Int64")
        edited_children["Years"] = pd.to_numeric(edited_children["Years"], errors="coerce").astype("Int64")
    st.session_state.temp_children = edited_children.to_dict("records") if not edited_children.empty else []

    st.divider()

    # ============================================
    # INHERITANCES SECTION (columns match simulator)
    # ============================================
    st.subheader("Expected Inheritances")
    st.caption("Enter calendar Year and Amount. (The simulator uses Year rather than 'Age at receipt'.)")
    if 'temp_inherit' not in st.session_state:
        legacy_inherit = existing.get("inheritance_list", existing.get("inherit_rows", [])) or []
        st.session_state.temp_inherit = []
        for r in legacy_inherit:
            st.session_state.temp_inherit.append({
                "Year": _to_int_or_none(r.get("Year") or r.get("year")),
                "Amount": _to_float(r.get("Amount") or r.get("amount") or 0.0),
                "Taxable?": bool(r.get("Taxable?") if "Taxable?" in r else r.get("taxable", False)),
            })
    inherit_df = pd.DataFrame(st.session_state.temp_inherit)
    inherit_df = _ensure_columns(inherit_df, [("Year","Int64"),("Amount","float"),("Taxable?","bool")])
    st.info("💡 **HOW TO USE:** After entering each value, press ENTER to save. Then move to next cell.")

    edited_inherit = st.data_editor(
        inherit_df,
        num_rows="dynamic",
        use_container_width=True,
        key="inherit_editor",
        column_config={
            "Year": st.column_config.NumberColumn("Year", min_value=2020, max_value=2075, step=1, help="Year of expected inheritance (2020-2075)"),
            "Amount": st.column_config.NumberColumn("Amount ($)", min_value=0, step=1000, format="$%.0f"),
            "Taxable?": st.column_config.CheckboxColumn("Taxable?"),
        },
    )
    if not edited_inherit.empty:
        edited_inherit["Year"] = pd.to_numeric(edited_inherit["Year"], errors="coerce").astype("Int64")
        # Allow users to type $… strings; convert when present
        edited_inherit["Amount"] = edited_inherit["Amount"].apply(_to_float)
    st.session_state.temp_inherit = edited_inherit.to_dict("records") if not edited_inherit.empty else []

    st.divider()

    # ============================================
    # FINANCIAL GOALS SECTION (persists while typing)
    # ============================================
    st.subheader("🎯 Financial Goals")
    st.caption("Major financial milestones you're planning for")
    if 'temp_goals' not in st.session_state:
        # accept both 'goals_list' and 'goals_data'
        st.session_state.temp_goals = existing.get("goals_list", existing.get("goals_data", [])) or []
    goals_df = pd.DataFrame(st.session_state.temp_goals)
    goals_df = _ensure_columns(goals_df, [("goal","str"),("amount","float"),("year","Int64")])
    st.info("💡 **HOW TO USE:** After entering each value, press ENTER to save. Then move to next cell.")

    edited_goals = st.data_editor(
        goals_df,
        num_rows="dynamic",
        use_container_width=True,
        key="goals_editor",
        column_config={
            "goal": st.column_config.TextColumn("Goal Name", required=True, help="e.g., Retirement Fund, Down Payment, World Travel"),
            "amount": st.column_config.NumberColumn("Target Amount", min_value=0, step=1000, format="$%.0f"),
            "year": st.column_config.NumberColumn("Target Year", min_value=2020, max_value=2075, step=1),
        },
    )
    if not edited_goals.empty:
        edited_goals["amount"] = edited_goals["amount"].apply(_to_float)
        edited_goals["year"] = pd.to_numeric(edited_goals["year"], errors="coerce").astype("Int64")
    st.session_state.temp_goals = edited_goals.to_dict('records') if not edited_goals.empty else []

    st.divider()

    # ============================================
    # CUSTOM EXPENSES SECTION (NEW!)
    # ============================================
    st.subheader("📝 Custom Monthly Expenses")
    st.caption("Add any special monthly expenses not covered in standard categories (e.g., Autism School Costs, Special Therapy)")
    
    if 'temp_custom_expenses' not in st.session_state:
        # Load from existing JSON if available
        st.session_state.temp_custom_expenses = existing.get("custom_expenses", [])
    
    custom_df = pd.DataFrame(st.session_state.temp_custom_expenses)
    custom_df = _ensure_columns(custom_df, [("Name","str"),("Monthly Amount","float"),("Category","str")])
    
    st.info("💡 **HOW TO USE:** After entering each value, press ENTER to save. Then move to next cell.")
    
    edited_custom = st.data_editor(
        custom_df,
        num_rows="dynamic",
        use_container_width=True,
        key="custom_expenses_editor",
        column_config={
            "Name": st.column_config.TextColumn("Expense Name", required=True, help="e.g., Autism School Costs, Special Therapy"),
            "Monthly Amount": st.column_config.NumberColumn("Monthly Amount ($)", min_value=0, step=50, format="$%.2f"),
            "Category": st.column_config.SelectboxColumn(
                "Category",
                options=["Education", "Healthcare", "Special Needs", "Childcare", "Other"],
                help="Category for organizing expenses"
            ),
        },
    )
    
    if not edited_custom.empty:
        edited_custom["Monthly Amount"] = edited_custom["Monthly Amount"].apply(_to_float)
    st.session_state.temp_custom_expenses = edited_custom.to_dict("records") if not edited_custom.empty else []
    
    # Show total of custom expenses
    if st.session_state.temp_custom_expenses:
        total_custom = sum(item.get("Monthly Amount", 0) for item in st.session_state.temp_custom_expenses)
        st.success(f"📊 Total Custom Monthly Expenses: ${total_custom:,.2f}")

    st.info("ℹ️ These fields are completely optional. Leave blank if not applicable.")

    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Liabilities", use_container_width=True):
            go_to_page('liabilities')
    with col3:
        if st.button("Next: Review →", type="primary", use_container_width=True):
            # Save family data using temp arrays (already up-to-date while typing)
            data = existing.copy()
            data["children_list"] = st.session_state.get("temp_children", [])
            data["inheritance_list"] = st.session_state.get("temp_inherit", [])
            data["goals_list"] = st.session_state.get("temp_goals", [])
            data["custom_expenses"] = st.session_state.get("temp_custom_expenses", [])

            # Backward compatibility keys
            data["children_rows"] = data["children_list"]
            data["inherit_rows"] = data["inheritance_list"]
            data["goals_data"] = data["goals_list"]
            data["custom_expenses_list"] = data["custom_expenses"]

            save_payload(data)
            go_to_page('review')
        
        
def show_review_page(existing, shared_path, go_to_page):
    # Always reload the latest JSON so the review reflects recent edits
    try:
        with open(shared_path, "r", encoding="utf-8") as _f:
            latest = json.load(_f)
        existing = latest if isinstance(latest, dict) else existing
    except Exception:
        pass

    """Page 7: Review & Export"""
    st.header("📋 Review & Complete Your Intake")
    st.caption("Review all your information before exporting to the simulator")
    
    # Profile Summary
    st.subheader("👤 Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Your Age", existing.get("input_age", "N/A"))
    with col2:
        if existing.get("input_partner_exists"):
            partner_name = existing.get("input_partner_name", "Partner")
            partner_age = existing.get("input_partner_age", "N/A")
            st.metric(f"{partner_name}'s Age", partner_age)
        else:
            st.metric("Planning Mode", "Single")
    
    if st.button("✏️ Edit Profile", key="edit_profile", use_container_width=True):
        go_to_page('profile')
    
    # Income & Expenses Summary
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💰 Monthly Income")
        total_income = existing.get("input_total_income", 0.0)
        st.metric("Total", f"${total_income:,.2f}")
        if st.button("✏️ Edit Income", key="edit_income", use_container_width=True):
            go_to_page('income')
    
    with col2:
        st.subheader("🏠 Monthly Expenses")
        total_expenses = existing.get("input_total_expenses", 0.0)
        st.metric("Total", f"${total_expenses:,.2f}")
        if st.button("✏️ Edit Expenses", key="edit_expenses", use_container_width=True):
            go_to_page('expenses')
    
    # Surplus/Deficit
    surplus = total_income - total_expenses
    if surplus >= 0:
        st.success(f"✅ Monthly Surplus: ${surplus:,.2f}")
    else:
        st.error(f"⚠️ Monthly Deficit: ${abs(surplus):,.2f}")
    
    st.divider()
    
    # Assets & Liabilities Summary
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💎 Total Assets")
        total_assets = sum([
            existing.get("input_ira_balance", 0.0),
            existing.get("input_four01k_403b_balance", 0.0),
            existing.get("input_partner_ira_balance", 0.0),
            existing.get("input_partner_four01k_403b_balance", 0.0),
            existing.get("input_taxable_investment_accounts", 0.0),
            existing.get("input_high_yield_savings_account", 0.0),
            existing.get("input_hsa_balance", 0.0),
            existing.get("input_five29_plan_balance", 0.0),
            existing.get("input_primary_residence_value", 0.0),
            existing.get("input_secondary_residence_value", 0.0),
            existing.get("input_vehicles_value", 0.0),
            existing.get("input_jewelry_collectibles_value", 0.0),
            existing.get("input_business_ownership_value", 0.0),
            existing.get("input_cryptocurrency_holdings", 0.0),
            existing.get("input_other_assets", 0.0)
        ])
        st.metric("Assets", f"${total_assets:,.2f}")
        if st.button("✏️ Edit Assets", key="edit_assets", use_container_width=True):
            go_to_page('assets')
    
    with col2:
        st.subheader("💳 Total Liabilities")
        total_liabilities = sum([
            existing.get("input_mortgage_balance", 0.0),
            existing.get("input_auto_loan_balance", 0.0),
            existing.get("input_student_loan_balance", 0.0),
            existing.get("input_credit_card_debt", 0.0),
            existing.get("input_other_liabilities", 0.0)
        ])
        st.metric("Liabilities", f"${total_liabilities:,.2f}")
        if st.button("✏️ Edit Liabilities", key="edit_liabilities", use_container_width=True):
            go_to_page('liabilities')
    
    # Net Worth
    net_worth = total_assets - total_liabilities
    st.metric("💰 Estimated Net Worth", f"${net_worth:,.2f}")
    
    st.divider()
    
    # Family Events Summary
    st.subheader("👨‍👩‍👧‍👦 Family Events")
    children_count = len(existing.get("children_rows", existing.get("children_list", [])))
    inherit_count = len(existing.get("inherit_rows", existing.get("inheritance_list", [])))
    custom_count = len(existing.get("custom_expenses", []))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Children", children_count)
    with col2:
        st.metric("Inheritances", inherit_count)
    with col3:
        st.metric("Custom Expenses", custom_count)
    
    if st.button("✏️ Edit Family Events", key="edit_family", use_container_width=True):
        go_to_page('family')
    
    # Show custom expenses if any
    if custom_count > 0:
        with st.expander("📝 Custom Monthly Expenses Details"):
            custom_expenses = existing.get("custom_expenses", [])
            for item in custom_expenses:
                st.write(f"• **{item.get('Name', 'N/A')}**: ${item.get('Monthly Amount', 0):,.2f} ({item.get('Category', 'N/A')})")
            total_custom = sum(item.get("Monthly Amount", 0) for item in custom_expenses)
            st.success(f"**Total Custom Expenses: ${total_custom:,.2f}/month**")
    
    # Final Export Section
    st.divider()
    st.subheader("🎉 Ready to Complete!")
    st.info("**Click below to export all your data to the Retirement Simulator**")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("← Back to Family", use_container_width=True):
            go_to_page('family')
    with col2:
        if st.button("✅ COMPLETE & EXPORT TO SIMULATOR", type="primary", use_container_width=True):
            st.success(f"✅ Successfully saved to:\n`{shared_path}`")
            st.balloons()
            st.markdown("### 🎯 Next Steps:")
            st.markdown("1. Open your **Retirement Simulator** app")
            st.markdown("2. In the sidebar, find **'🔥 Import from Intake App'**")
            st.markdown("3. Click **'Load from path'**")
            st.markdown("4. Review the populated fields")
            st.markdown("5. Click **'Run Simulation'** to see your retirement projection!")
            st.info("💡 **Tip:** Save as a new scenario in the simulator to preserve this data for future reference")