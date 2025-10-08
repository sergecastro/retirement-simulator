# intake_review.py - Advanced pages for Family Retirement Intake
# Pages 4-7: Assets, Liabilities, Family Events, Review & Export
import streamlit as st
import pandas as pd

def show_assets_page(existing, save_payload, go_to_page):
    """Page 4: Assets & Accounts"""
    st.header("💎 Assets & Accounts")
    st.caption("Enter current balances for all your accounts and assets")
    
    # Retirement Accounts
    st.subheader("🏦 Retirement Accounts")
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
    
    # Children section
    st.subheader("Children & College Plans")
    st.caption("Add rows for each child")
    
    if 'temp_children' not in st.session_state:
        st.session_state.temp_children = existing.get("children_rows", [])
    
    children_df = pd.DataFrame(st.session_state.temp_children) if st.session_state.temp_children else pd.DataFrame(columns=["name", "age", "support_end_age"])
    
    edited_children = st.data_editor(
        children_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "name": st.column_config.TextColumn("Child Name", required=True, help="First name or nickname"),
            "age": st.column_config.NumberColumn("Current Age", min_value=0, max_value=50, step=1, help="How old is this child now?"),
            "support_end_age": st.column_config.NumberColumn("Support Until Age", min_value=0, max_value=30, step=1, help="Age when financial support ends (0 = no support)")
        }
    )
    
    # Inheritances section
    st.subheader("Expected Inheritances")
    st.caption("Money you expect to receive in the future")
    
    if 'temp_inherit' not in st.session_state:
        st.session_state.temp_inherit = existing.get("inherit_rows", [])
    
    inherit_df = pd.DataFrame(st.session_state.temp_inherit) if st.session_state.temp_inherit else pd.DataFrame(columns=["recipient", "amount", "age"])
    
    edited_inherit = st.data_editor(
        inherit_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "recipient": st.column_config.TextColumn("Recipient/Description", required=True, help="Who receives it or from whom"),
            "amount": st.column_config.NumberColumn("Amount ($)", min_value=0, step=1000, format="$%.0f", help="Expected inheritance amount"),
            "age": st.column_config.NumberColumn("Your Age When Received", min_value=0, max_value=120, step=1, help="How old will YOU be?")
        }
    )
    
    st.info("ℹ️ These fields are completely optional. Leave blank if not applicable.")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Liabilities", use_container_width=True):
            go_to_page('liabilities')
    with col3:
        if st.button("Next: Review →", type="primary", use_container_width=True):
            # Save family data
            data = existing.copy()
            data["children_rows"] = edited_children.to_dict('records') if not edited_children.empty else []
            data["inherit_rows"] = edited_inherit.to_dict('records') if not edited_inherit.empty else []
            save_payload(data)
            go_to_page('review')


def show_review_page(existing, shared_path, go_to_page):
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
    children_count = len(existing.get("children_rows", []))
    inherit_count = len(existing.get("inherit_rows", []))
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Children", children_count)
    with col2:
        st.metric("Inheritances", inherit_count)
    if st.button("✏️ Edit Family Events", key="edit_family", use_container_width=True):
        go_to_page('family')
    
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
            st.markdown("2. In the sidebar, find **'📥 Import from Intake App'**")
            st.markdown("3. Click **'Load from path'**")
            st.markdown("4. Review the populated fields")
            st.markdown("5. Click **'Run Simulation'** to see your retirement projection!")
            st.info("💡 **Tip:** Save as a new scenario in the simulator to preserve this data for future reference")