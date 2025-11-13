"""
Scenario Studio Page
Self-contained scenario creation and side-by-side comparison
"""

import streamlit as st
from utils.comparison_scenarios import get_comparisons_for_plan, load_comparison_scenario
from utils.snapshot_manager import get_current_snapshot


def render_scenario_studio_page():
    """Render the Scenario Studio page - Full self-contained experience"""

    # Page header with quick rerun button for testing
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.markdown("# 🎬 Scenario Studio")
        st.markdown("**Create, simulate, and compare multiple retirement strategies**")
    with col_header2:
        st.markdown("### ")  # Spacing
        if st.button("🔄 Reload Page", key="quick_rerun_button", help="Refresh to see latest code changes", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Get current base plan
    try:
        current_snapshot = get_current_snapshot()
        if not current_snapshot:
            st.warning("⚠️ Please complete the INTAKE questionnaire first to create a base plan.")
            if st.button("📝 Go to INTAKE"):
                st.session_state['current_mode'] = 'INTAKE'
                st.rerun()
            return

        # Get the current snapshot ID from the index
        from utils.snapshot_manager import get_snapshots_index
        index = get_snapshots_index()
        base_plan_id = index.get('current_snapshot_id')

        if not base_plan_id:
            st.error("❌ No current snapshot ID found. Please save a snapshot in INTAKE mode first.")
            if st.button("📝 Go to INTAKE"):
                st.session_state['current_mode'] = 'INTAKE'
                st.rerun()
            return

        # Extract user info from snapshot data (snapshot uses 'input_' prefix)
        user_name = current_snapshot.get('input_user_name', 'User')

        st.success(f"✅ Base Plan: **{user_name}** (ID: {base_plan_id[:8]}...)")

    except Exception as e:
        st.error(f"❌ Error loading base plan: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return

    # =============================================================================
    # SECTION 1: CREATE NEW SCENARIO
    # =============================================================================

    st.markdown("---")
    st.markdown("### 🎨 Create New Scenario")
    st.markdown("**Adjust any parameters below to explore different retirement strategies**")

    with st.form(key="create_scenario_form"):

        # Scenario name - PROMINENT & MANDATORY
        st.markdown("#### 📝 Scenario Name (Required)")
        st.markdown("**Give this scenario a unique, memorable name before adjusting parameters**")

        scenario_name = st.text_input(
            "Enter scenario name:",
            placeholder="e.g., High Income Strategy, Early Retirement at 60, Conservative Plan",
            help="⚠️ REQUIRED: You must enter a scenario name to run the simulation",
            label_visibility="collapsed"
        )

        # Show warning if name is empty (visual cue)
        if not scenario_name or scenario_name.strip() == "":
            st.warning("⚠️ **Please enter a scenario name above before running the simulation**")
        else:
            st.success(f"✅ Scenario name set: **{scenario_name}**")

        # Get all base plan values from current_snapshot for defaults
        # The snapshot stores raw input values with 'input_' prefix
        snapshot_data = current_snapshot.get('data', current_snapshot)

        # Helper function to safely get values with defaults
        def get_value(key, default=0):
            """Get value from snapshot, handling both with and without input_ prefix"""
            # Try with input_ prefix first
            if f'input_{key}' in snapshot_data:
                return snapshot_data[f'input_{key}']
            # Try without prefix
            if key in snapshot_data:
                return snapshot_data[key]
            # Return default
            return default

        st.markdown("---")

        # =============================================================================
        # INCOME & EXPENSES
        # =============================================================================
        st.markdown("#### 💰 Income & Expenses")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Income Sources**")

            adj_salary_wages = st.number_input(
                "Annual Salary/Wages",
                min_value=0,
                max_value=10000000,
                value=int(get_value('salary_wages', 100000)),
                step=5000,
                help="Employment income"
            )

            adj_social_security = st.number_input(
                "Annual Social Security",
                min_value=0,
                max_value=100000,
                value=int(get_value('social_security_income', 0)),
                step=1000,
                help="Expected Social Security benefits"
            )

            adj_pension = st.number_input(
                "Annual Pension",
                min_value=0,
                max_value=500000,
                value=int(get_value('pension_income', 0)),
                step=1000,
                help="Pension income"
            )

            adj_investment_income = st.number_input(
                "Annual Investment Income",
                min_value=0,
                max_value=1000000,
                value=int(get_value('investment_income', 0)),
                step=1000,
                help="Dividends, interest, rental income"
            )

            adj_other_income = st.number_input(
                "Other Annual Income",
                min_value=0,
                max_value=1000000,
                value=int(get_value('other_income', 0)),
                step=1000,
                help="Other income sources"
            )

        with col2:
            st.markdown("**Expense Categories**")

            adj_housing_expenses = st.number_input(
                "Annual Housing Expenses",
                min_value=0,
                max_value=500000,
                value=int(get_value('housing_expenses', 24000)),
                step=1000,
                help="Rent/mortgage, maintenance, utilities"
            )

            adj_healthcare_expenses = st.number_input(
                "Annual Healthcare Expenses",
                min_value=0,
                max_value=100000,
                value=int(get_value('healthcare_expenses', 6000)),
                step=500,
                help="Medical, insurance, prescriptions"
            )

            adj_groceries = st.number_input(
                "Annual Groceries",
                min_value=0,
                max_value=50000,
                value=int(get_value('groceries_expenses', 7200)),
                step=500,
                help="Food and household supplies"
            )

            adj_transportation = st.number_input(
                "Annual Transportation",
                min_value=0,
                max_value=50000,
                value=int(get_value('transportation_expenses', 4800)),
                step=500,
                help="Car, gas, insurance, public transit"
            )

            adj_other_expenses = st.number_input(
                "Other Annual Expenses",
                min_value=0,
                max_value=200000,
                value=int(get_value('other_expenses', 12000)),
                step=500,
                help="Entertainment, travel, misc"
            )

        st.markdown("---")

        # =============================================================================
        # RETIREMENT TIMING
        # =============================================================================
        st.markdown("#### 🎯 Retirement Timing & Life Planning")

        col3, col4, col5 = st.columns(3)

        with col3:
            adj_age = st.number_input(
                "Current Age",
                min_value=18,
                max_value=100,
                value=int(get_value('age', 45)),
                step=1,
                help="Your current age"
            )

            adj_retirement_age = st.slider(
                "Planned Retirement Age",
                min_value=50,
                max_value=80,
                value=int(get_value('retirement_age', 65)),
                step=1,
                help="Age you plan to retire"
            )

        with col4:
            adj_life_expectancy = st.slider(
                "Life Expectancy",
                min_value=75,
                max_value=105,
                value=int(get_value('life_expectancy', 90)),
                step=1,
                help="Planning horizon"
            )

            adj_ss_claiming_age = st.slider(
                "Social Security Claiming Age",
                min_value=62,
                max_value=70,
                value=int(get_value('ss_claiming_age', 67)),
                step=1,
                help="Age to start Social Security"
            )

        with col5:
            adj_partner_exists = st.checkbox(
                "Partner/Spouse?",
                value=bool(get_value('partner_exists', False)),
                help="Include partner in planning"
            )

            if adj_partner_exists:
                adj_partner_age = st.number_input(
                    "Partner's Age",
                    min_value=18,
                    max_value=100,
                    value=int(get_value('partner_age', 45)),
                    step=1
                )
            else:
                adj_partner_age = None

        st.markdown("---")

        # =============================================================================
        # INVESTMENT STRATEGY
        # =============================================================================
        st.markdown("#### 📈 Investment Strategy & Returns")

        col6, col7 = st.columns(2)

        with col6:
            adj_return_rate = st.slider(
                "Expected Annual Return Rate",
                min_value=0.0,
                max_value=0.20,
                value=float(get_value('return_rate', 0.07)),
                step=0.005,
                format="%.2f%%",
                help="Average annual investment return (before inflation)"
            )

            adj_stocks_allocation = st.slider(
                "Stocks Allocation %",
                min_value=0,
                max_value=100,
                value=int(get_value('stocks_allocation', 60)),
                step=5,
                format="%d%%",
                help="Percentage allocated to stocks/equity"
            )

            adj_bonds_allocation = st.slider(
                "Bonds Allocation %",
                min_value=0,
                max_value=100,
                value=int(get_value('bonds_allocation', 40)),
                step=5,
                format="%d%%",
                help="Percentage allocated to bonds/fixed income"
            )

        with col7:
            adj_inflation_rate = st.slider(
                "Expected Inflation Rate",
                min_value=0.0,
                max_value=0.10,
                value=float(get_value('inflation_rate', 0.03)),
                step=0.005,
                format="%.2f%%",
                help="Average annual inflation rate"
            )

            # Allocation warning
            total_allocation = adj_stocks_allocation + adj_bonds_allocation
            if total_allocation != 100:
                st.warning(f"⚠️ Allocation total: {total_allocation}% (should be 100%)")
            else:
                st.success(f"✅ Allocation total: {total_allocation}%")

        st.markdown("---")

        # =============================================================================
        # ACCOUNT BALANCES
        # =============================================================================
        st.markdown("#### 💼 Current Account Balances")

        col8, col9, col10 = st.columns(3)

        with col8:
            st.markdown("**Tax-Advantaged**")

            adj_ira_balance = st.number_input(
                "Traditional IRA Balance",
                min_value=0,
                max_value=50000000,
                value=int(get_value('ira_balance', 0)),
                step=10000,
                help="Traditional IRA accounts"
            )

            adj_401k_balance = st.number_input(
                "401(k)/403(b) Balance",
                min_value=0,
                max_value=50000000,
                value=int(get_value('four01k_403b_balance', 0)),
                step=10000,
                help="Employer retirement accounts"
            )

        with col9:
            st.markdown("**Tax-Free**")

            adj_roth_balance = st.number_input(
                "Roth IRA Balance",
                min_value=0,
                max_value=50000000,
                value=int(get_value('roth_balance', 0)),
                step=10000,
                help="Roth IRA accounts"
            )

            adj_hsa_balance = st.number_input(
                "HSA Balance",
                min_value=0,
                max_value=1000000,
                value=int(get_value('hsa_balance', 0)),
                step=1000,
                help="Health Savings Account"
            )

        with col10:
            st.markdown("**Taxable**")

            adj_taxable_accounts = st.number_input(
                "Taxable Investment Accounts",
                min_value=0,
                max_value=100000000,
                value=int(get_value('taxable_investment_accounts', 0)),
                step=10000,
                help="Brokerage accounts"
            )

            adj_savings = st.number_input(
                "High-Yield Savings",
                min_value=0,
                max_value=10000000,
                value=int(get_value('high_yield_savings_account', 0)),
                step=5000,
                help="Cash savings accounts"
            )

        # Partner accounts (if applicable)
        if adj_partner_exists:
            st.markdown("---")
            st.markdown("**Partner's Accounts**")

            col11, col12, col13 = st.columns(3)

            with col11:
                adj_partner_ira = st.number_input(
                    "Partner's IRA Balance",
                    min_value=0,
                    max_value=50000000,
                    value=int(get_value('partner_ira_balance', 0)),
                    step=10000
                )

            with col12:
                adj_partner_401k = st.number_input(
                    "Partner's 401(k) Balance",
                    min_value=0,
                    max_value=50000000,
                    value=int(get_value('partner_four01k_403b_balance', 0)),
                    step=10000
                )

            with col13:
                st.write("")  # Spacing
        else:
            adj_partner_ira = 0
            adj_partner_401k = 0

        st.markdown("---")

        # =============================================================================
        # REAL ESTATE & ASSETS
        # =============================================================================
        st.markdown("#### 🏠 Real Estate & Other Assets")

        col14, col15 = st.columns(2)

        with col14:
            adj_home_value = st.number_input(
                "Primary Residence Value",
                min_value=0,
                max_value=50000000,
                value=int(get_value('primary_residence_value', 0)),
                step=25000,
                help="Current market value of home"
            )

            adj_mortgage_balance = st.number_input(
                "Mortgage Balance",
                min_value=0,
                max_value=10000000,
                value=int(get_value('mortgage_balance', 0)),
                step=10000,
                help="Remaining mortgage principal"
            )

            adj_vehicles_value = st.number_input(
                "Vehicles Value",
                min_value=0,
                max_value=1000000,
                value=int(get_value('vehicles_value', 0)),
                step=5000,
                help="Total value of vehicles"
            )

        with col15:
            adj_other_assets = st.number_input(
                "Other Assets",
                min_value=0,
                max_value=100000000,
                value=int(get_value('other_assets', 0)),
                step=10000,
                help="Business, rental property, collectibles, etc."
            )

            adj_other_liabilities = st.number_input(
                "Other Debts/Liabilities",
                min_value=0,
                max_value=10000000,
                value=int(get_value('other_liabilities', 0)),
                step=5000,
                help="Credit cards, loans, etc."
            )

        st.markdown("---")

        # =============================================================================
        # FORM SUBMIT
        # =============================================================================

        col_submit1, col_submit2 = st.columns([3, 1])

        with col_submit1:
            st.markdown("**Ready to simulate this scenario?**")
            st.markdown("Click below to run the retirement simulation with these adjusted parameters.")

        with col_submit2:
            run_scenario = st.form_submit_button(
                "🔍 Run This Scenario",
                type="primary",
                use_container_width=True
            )

    # =============================================================================
    # HANDLE FORM SUBMISSION
    # =============================================================================

    if run_scenario:
        if not scenario_name or scenario_name.strip() == "":
            st.error("⚠️ **Please enter a scenario name** before running the simulation.")
        else:
            # =============================================================================
            # RUN SIMULATION
            # =============================================================================

            st.markdown("---")
            st.markdown("### 🔍 Running Simulation...")

            with st.spinner(f"Calculating '{scenario_name}' retirement trajectory..."):
                try:
                    from simulation_core import run_simulation

                    # Calculate total income and expenses
                    total_income = (adj_salary_wages + adj_social_security +
                                  adj_pension + adj_investment_income + adj_other_income)

                    total_expenses = (adj_housing_expenses + adj_healthcare_expenses +
                                    adj_groceries + adj_transportation + adj_other_expenses)

                    # Calculate liquid assets (retirement accounts + taxable + savings)
                    liquid_assets = (adj_ira_balance + adj_401k_balance + adj_roth_balance +
                                   adj_hsa_balance + adj_taxable_accounts + adj_savings +
                                   adj_partner_ira + adj_partner_401k)

                    # Calculate total liabilities
                    total_liabilities = adj_mortgage_balance + adj_other_liabilities

                    # Calculate simulation years (from current age to life expectancy)
                    simulation_years = adj_life_expectancy - adj_age

                    # Monthly surplus
                    monthly_surplus = (total_income - total_expenses) / 12

                    # Run the simulation!
                    results = run_simulation(
                        age=adj_age,
                        partner_exists=adj_partner_exists,
                        partner_age=adj_partner_age if adj_partner_exists else adj_age,
                        total_income=total_income,
                        total_expenses=total_expenses,
                        combined_financial_assets=liquid_assets,
                        primary_residence_value=adj_home_value,
                        secondary_residence_value=0,  # Not captured in form yet
                        combined_other_assets_total=adj_other_assets + adj_vehicles_value,
                        total_liabilities_local=total_liabilities,
                        partner_liabilities=0,
                        tax_rate=22.0,  # Default tax rate
                        inflation_rate=adj_inflation_rate * 100,  # Convert to percentage
                        investment_return_rate=adj_return_rate * 100,  # Convert to percentage
                        simulation_years=simulation_years,
                        mc_iterations=0,  # No Monte Carlo for quick preview
                        goal_costs={},
                        college_inflation_pct=4.0,
                        base_public_in=20000,
                        base_public_out=40000,
                        base_private=60000,
                        ira_balance=adj_ira_balance,
                        four01k_403b_balance=adj_401k_balance,
                        partner_ira_balance=adj_partner_ira,
                        partner_four01k_403b_balance=adj_partner_401k,
                        monthly_surplus=monthly_surplus,
                        combined_total_liabilities=total_liabilities
                    )

                    if results:
                        st.success(f"✅ **Simulation complete for '{scenario_name}'!**")

                        # =============================================================================
                        # RESULTS PREVIEW
                        # =============================================================================

                        st.markdown("---")
                        st.markdown("### 📊 Results Preview")

                        # Key metrics in columns
                        col_r1, col_r2, col_r3 = st.columns(3)

                        with col_r1:
                            final_savings = results.get('final_savings', 0)
                            st.metric(
                                "Final Savings",
                                f"${final_savings:,.0f}",
                                help="Projected savings at life expectancy"
                            )

                        with col_r2:
                            years_solvent = results.get('years_solvent', 0)
                            st.metric(
                                "Years Solvent",
                                f"{years_solvent} years",
                                help="How many years your money lasts"
                            )

                        with col_r3:
                            final_net_worth = results.get('final_net_worth', 0)
                            st.metric(
                                "Final Net Worth",
                                f"${final_net_worth:,.0f}",
                                help="Total net worth at end"
                            )

                        # Additional metrics
                        col_r4, col_r5, col_r6 = st.columns(3)

                        with col_r4:
                            health_score = results.get('health_score', 0)
                            st.metric(
                                "Financial Health Score",
                                f"{health_score}/100",
                                help="Overall financial health rating"
                            )

                        with col_r5:
                            savings_rate = results.get('savings_rate', 0)
                            st.metric(
                                "Savings Rate",
                                f"{savings_rate:.1f}%",
                                help="Percentage of income saved"
                            )

                        with col_r6:
                            emergency_months = results.get('emergency_fund_months', 0)
                            st.metric(
                                "Emergency Fund",
                                f"{emergency_months:.1f} months",
                                help="Months of expenses covered"
                            )

                        # Store results for comparison and saving
                        st.session_state['pending_scenario'] = {
                            'name': scenario_name,
                            'base_plan_id': base_plan_id,
                            'adjustments': {
                                # Income
                                'salary_wages': adj_salary_wages,
                                'social_security_income': adj_social_security,
                                'pension_income': adj_pension,
                                'investment_income': adj_investment_income,
                                'other_income': adj_other_income,

                                # Expenses
                                'housing_expenses': adj_housing_expenses,
                                'healthcare_expenses': adj_healthcare_expenses,
                                'groceries_expenses': adj_groceries,
                                'transportation_expenses': adj_transportation,
                                'other_expenses': adj_other_expenses,

                                # Timing
                                'age': adj_age,
                                'retirement_age': adj_retirement_age,
                                'life_expectancy': adj_life_expectancy,
                                'ss_claiming_age': adj_ss_claiming_age,
                                'partner_exists': adj_partner_exists,
                                'partner_age': adj_partner_age,

                                # Investment
                                'return_rate': adj_return_rate,
                                'inflation_rate': adj_inflation_rate,
                                'stocks_allocation': adj_stocks_allocation,
                                'bonds_allocation': adj_bonds_allocation,

                                # Accounts
                                'ira_balance': adj_ira_balance,
                                'four01k_403b_balance': adj_401k_balance,
                                'roth_balance': adj_roth_balance,
                                'hsa_balance': adj_hsa_balance,
                                'taxable_investment_accounts': adj_taxable_accounts,
                                'high_yield_savings_account': adj_savings,
                                'partner_ira_balance': adj_partner_ira,
                                'partner_four01k_403b_balance': adj_partner_401k,

                                # Real Estate
                                'primary_residence_value': adj_home_value,
                                'mortgage_balance': adj_mortgage_balance,
                                'vehicles_value': adj_vehicles_value,
                                'other_assets': adj_other_assets,
                                'other_liabilities': adj_other_liabilities,
                            },
                            'simulation_results': results
                        }

                        # Save button moved outside form block for reliability
                        st.markdown("---")
                        st.info("✅ **Simulation complete!** Scroll down to save this scenario.")

                    else:
                        st.error("❌ Simulation failed. Please check your parameters.")

                except Exception as e:
                    st.error(f"❌ Error running simulation: {str(e)}")
                    import traceback
                    with st.expander("🐛 Show error details"):
                        st.code(traceback.format_exc())

    # =============================================================================
    # SECTION 1.5: SAVE PENDING SCENARIO (OUTSIDE FORM BLOCK)
    # =============================================================================

    # Check if there's a pending scenario to save (moved outside form submission)
    if 'pending_scenario' in st.session_state and st.session_state.get('pending_scenario'):
        pending = st.session_state['pending_scenario']

        st.markdown("---")
        st.markdown("---")
        st.markdown("### 💾 Save This Scenario")
        st.markdown(f"**Scenario:** {pending['name']}")
        st.markdown("This scenario has been simulated. Click below to save it permanently.")

            col_save1, col_save2, col_save3 = st.columns([1, 2, 1])

            with col_save2:
                # Unique key based on scenario name
                save_button_key = f"save_btn_{pending['name'].replace(' ', '_')}"

                if st.button(
                    "💾 Save Scenario",
                    type="primary",
                    use_container_width=True,
                    key=save_button_key
                ):
                    from utils.comparison_scenarios import save_comparison_scenario

                    try:
                        print(f"[SCENARIO STUDIO] 🔴 Save button clicked! Scenario: {pending['name']}")

                        # Prepare simulation results - convert DataFrame to dict for JSON serialization
                        sim_results = pending.get('simulation_results', {})
                        serializable_results = {}

                        for key, value in sim_results.items():
                            # Check if it's a DataFrame
                            if hasattr(value, 'to_dict'):
                                # Convert DataFrame to dict (orient='list' is most compact)
                                serializable_results[key] = {
                                    '_type': 'dataframe',
                                    'data': value.to_dict(orient='list')
                                }
                            else:
                                # Keep as-is for other types
                                serializable_results[key] = value

                        print(f"[SCENARIO STUDIO] Serialized {len(serializable_results)} result keys")

                        comparison_id = save_comparison_scenario(
                            base_plan_id=pending['base_plan_id'],
                            name=pending['name'],
                            description=f"Created in Scenario Studio",
                            adjustments=pending['adjustments'],
                            simulation_results=serializable_results
                        )

                        if comparison_id:
                            print(f"[SCENARIO STUDIO] ✅ Save successful! ID: {comparison_id}")

                            # 🎈 CELEBRATION!
                            st.balloons()

                            # Clear pending scenario
                            del st.session_state['pending_scenario']

                            # Show success inline (NO RERUN!)
                            st.success(f"✅ **Saved!** Scenario '{pending['name']}' (ID: {comparison_id[:8]}...)")
                            st.info("🔄 **Reload the page manually** to see it in your saved scenarios list below.")
                        else:
                            st.error("❌ Save failed - no comparison ID returned")
                            print(f"[SCENARIO STUDIO] ❌ No ID returned")

                    except Exception as e:
                        st.error(f"❌ Error saving: {str(e)}")
                        print(f"[SCENARIO STUDIO] ❌ Error: {e}")
                        import traceback
                        traceback.print_exc()

    # =============================================================================
    # SECTION 2: SAVED SCENARIOS (List)
    # =============================================================================

    st.markdown("---")
    st.markdown("---")
    st.markdown("### 📊 Your Saved Scenarios")

    # Get saved comparisons
    comparisons = get_comparisons_for_plan(base_plan_id)

    if len(comparisons) == 0:
        st.info("💡 **No saved scenarios yet!** Create and save your first scenario above.")

    elif len(comparisons) == 1:
        st.info(f"✅ **Found 1 saved scenario.** Create at least one more to enable side-by-side comparison.")
        st.markdown("**Saved Scenarios:**")
        for comp in comparisons:
            st.markdown(f"- {comp['name']} (Created: {comp['created_at'][:10]})")

    else:
        # 2+ scenarios - SHOW COMPARISON TABLE!
        st.success(f"📊 **Found {len(comparisons)} saved scenarios!**")

        st.markdown("---")
        st.markdown("### 🔀 Compare Scenarios Side-by-Side")

        # Multi-select for scenarios to compare
        scenario_names = [comp['name'] for comp in comparisons]

        selected_names = st.multiselect(
            "Select 2-4 scenarios to compare:",
            options=scenario_names,
            default=scenario_names[:min(3, len(scenario_names))],  # Auto-select first 3
            max_selections=4,
            help="Choose which scenarios you want to compare"
        )

        if len(selected_names) >= 2:
            st.markdown(f"**Comparing {len(selected_names)} scenarios...**")

            # Load full data for selected scenarios
            selected_comparisons = [comp for comp in comparisons if comp['name'] in selected_names]

            # Load detailed data for each
            from utils.comparison_scenarios import load_comparison_scenario
            detailed_scenarios = []

            for comp in selected_comparisons:
                detailed = load_comparison_scenario(comp['id'])
                if detailed:
                    detailed_scenarios.append(detailed)

            if len(detailed_scenarios) >= 2:
                # Build comparison table
                import pandas as pd

                comparison_data = []

                # Row 1: Scenario Name
                comparison_data.append({
                    'Metric': '📝 Scenario Name',
                    **{f'Scenario {i+1}': s['name'] for i, s in enumerate(detailed_scenarios)}
                })

                # Section: Key Results
                comparison_data.append({
                    'Metric': '─── 📊 KEY RESULTS ───',
                    **{f'Scenario {i+1}': '' for i in range(len(detailed_scenarios))}
                })

                # Get simulation results (if available)
                for metric_key, metric_label in [
                    ('final_savings', '💰 Final Savings'),
                    ('final_net_worth', '💎 Final Net Worth'),
                    ('years_solvent', '⏳ Years Solvent'),
                    ('health_score', '❤️ Health Score'),
                    ('savings_rate', '📈 Savings Rate'),
                ]:
                    row = {'Metric': metric_label}
                    for i, s in enumerate(detailed_scenarios):
                        sim_results = s.get('simulation_results', {})
                        value = sim_results.get(metric_key, 'N/A')

                        # Format the value
                        if value == 'N/A':
                            formatted = 'N/A'
                        elif metric_key in ['final_savings', 'final_net_worth']:
                            formatted = f"${value:,.0f}"
                        elif metric_key == 'years_solvent':
                            formatted = f"{value} years"
                        elif metric_key == 'health_score':
                            formatted = f"{value}/100"
                        elif metric_key == 'savings_rate':
                            formatted = f"{value:.1f}%"
                        else:
                            formatted = str(value)

                        row[f'Scenario {i+1}'] = formatted

                    comparison_data.append(row)

                # Section: Income & Expenses
                comparison_data.append({
                    'Metric': '─── 💰 INCOME & EXPENSES ───',
                    **{f'Scenario {i+1}': '' for i in range(len(detailed_scenarios))}
                })

                for adj_key, adj_label in [
                    ('salary_wages', '💵 Salary/Wages'),
                    ('social_security_income', '🏛️ Social Security'),
                    ('pension_income', '🎖️ Pension'),
                    ('housing_expenses', '🏠 Housing'),
                    ('healthcare_expenses', '⚕️ Healthcare'),
                ]:
                    row = {'Metric': adj_label}
                    for i, s in enumerate(detailed_scenarios):
                        adjustments = s.get('adjustments', {})
                        value = adjustments.get(adj_key, 'N/A')
                        row[f'Scenario {i+1}'] = f"${value:,.0f}" if value != 'N/A' else 'N/A'
                    comparison_data.append(row)

                # Section: Investment Strategy
                comparison_data.append({
                    'Metric': '─── 📈 INVESTMENT STRATEGY ───',
                    **{f'Scenario {i+1}': '' for i in range(len(detailed_scenarios))}
                })

                for adj_key, adj_label in [
                    ('return_rate', '📊 Return Rate'),
                    ('inflation_rate', '📉 Inflation Rate'),
                    ('stocks_allocation', '📈 Stocks %'),
                    ('bonds_allocation', '🔒 Bonds %'),
                ]:
                    row = {'Metric': adj_label}
                    for i, s in enumerate(detailed_scenarios):
                        adjustments = s.get('adjustments', {})
                        value = adjustments.get(adj_key, 'N/A')

                        if value != 'N/A':
                            if 'rate' in adj_key:
                                formatted = f"{value * 100:.1f}%"
                            elif 'allocation' in adj_key:
                                formatted = f"{value}%"
                            else:
                                formatted = str(value)
                        else:
                            formatted = 'N/A'

                        row[f'Scenario {i+1}'] = formatted
                    comparison_data.append(row)

                # Create DataFrame and display
                df = pd.DataFrame(comparison_data)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    height=600
                )

                st.success("✅ Comparison complete! Scroll to see all metrics.")

            else:
                st.warning("⚠️ Could not load detailed data for selected scenarios.")

        elif len(selected_names) == 1:
            st.info("💡 Select at least 2 scenarios to see the comparison table.")
        else:
            st.info("💡 Select 2-4 scenarios above to compare them side-by-side.")

    st.markdown("---")
    st.markdown("*🎬 Scenario Studio - Create, simulate, and compare retirement strategies*")
