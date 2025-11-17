"""
Social Security Optimizer Page
================================
Standalone module for SS claiming strategy optimization.
5th card in the app navigation.
"""

import streamlit as st
import pandas as pd
from datetime import date
from utils.ss_calculations import (
    calculate_benefit_at_age,
    calculate_lifetime_benefits,
    calculate_break_even_age,
    optimize_claiming_strategy,
    estimate_pia_from_income,
    generate_claiming_comparison_table,
    get_fra,
    calculate_ss_taxable_portion,
    calculate_ss_after_tax
)


def show_social_security_optimizer():
    """
    Main Social Security Optimizer page.
    """
    # Add mode selector to sidebar FIRST
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎯 Quick Mode Switch")

        mode = st.radio(
            "Choose mode:",
            options=["INTAKE", "Analysis", "Scenario Studio", "Social Security", "Healthcare"],
            index=3,  # Social Security is index 3
            key="mode_selector_ss",
            help="INTAKE: Guided questionnaire | Analysis: Advanced simulation | Scenario Studio: Compare scenarios | Social Security: Claiming optimizer | Healthcare: Cost planning"
        )

        if mode != "Social Security":
            if mode == "Scenario Studio":
                st.session_state.current_mode = "scenario_studio"
            elif mode == "Social Security":
                st.session_state.current_mode = "social_security"
            else:
                st.session_state.current_mode = mode
            st.session_state.mode_selected = True
            st.rerun()

    st.title("🏛️ Social Security Claiming Strategy")
    st.markdown("**Optimize when to claim Social Security benefits for maximum lifetime value**")

    # EDUCATIONAL DISCLAIMER - TOP OF PAGE
    st.warning("""
    ⚠️ **EDUCATIONAL PURPOSES ONLY** - This tool provides estimates based on simplified SSA rules.
    **NOT financial advice.** Actual benefits depend on your complete earnings history, which only SSA has access to.
    Always verify your benefit estimates at [ssa.gov](https://www.ssa.gov/myaccount/) before making decisions.
    """)

    # =============================================================================
    # LOAD BASE PLAN FOR DIVERGENCE TRACKING
    # =============================================================================
    from utils.snapshot_manager import get_snapshots_index, load_snapshot

    # Get current base plan
    index = get_snapshots_index()
    base_plan_id = index.get('current_snapshot_id', 'default_plan')

    # Initialize base plan values (for divergence tracking)
    can_save_scenario = False
    base_plan_data = {}

    if base_plan_id != 'default_plan' and base_plan_id:
        base_snapshot = load_snapshot(base_plan_id)
        if base_snapshot:
            base_plan_data = base_snapshot.get('snapshot_data', base_snapshot)
            can_save_scenario = True

            # Store base plan values for comparison
            st.session_state['ss_base_plan_id'] = base_plan_id

            # Life expectancy - NOT stored in snapshot, use session state or default
            base_life_exp = base_plan_data.get('input_life_expectancy',
                                               st.session_state.get('input_life_expectancy', 85))
            st.session_state['ss_base_life_exp'] = base_life_exp

            # Income - use salary from snapshot, but if 0, calculate total income
            snapshot_salary = base_plan_data.get('input_salary_wages', 0)
            if snapshot_salary > 0:
                st.session_state['ss_base_income'] = snapshot_salary
            else:
                # User may be retired (salary=0), use total income
                total_inc = base_plan_data.get('input_total_income', 0)
                if total_inc > 0:
                    st.session_state['ss_base_income'] = total_inc * 12  # Monthly to annual
                else:
                    # Fallback to session state
                    st.session_state['ss_base_income'] = st.session_state.get('input_salary_wages', 75000)

            st.session_state['ss_base_age'] = base_plan_data.get('input_age', 45)

    # Check for reset request - RESET THE ACTUAL WIDGET VALUES
    if st.session_state.get('ss_reset_to_base', False):
        # Clear the reset flag
        st.session_state['ss_reset_to_base'] = False

        # CRITICAL: Reset the actual widget keys to base plan values
        base_income = st.session_state.get('ss_base_income', 75000)
        base_life = st.session_state.get('ss_base_life_exp', 85)

        # FIX: DIRECTLY SET the widget key values (don't delete - Streamlit will use these)
        st.session_state['ss_income'] = base_income
        st.session_state['ss_life_exp'] = base_life

        # Also reset years worked to default
        st.session_state['ss_years_worked'] = 35

        st.success(f"✅ Reset to Base Plan values! Income: ${base_income:,.0f}, Life Exp: {base_life} years")
        st.rerun()  # Force immediate rerun to reflect changes

    # Navigation back to Analysis (quick button in main content)
    col_nav1, col_nav2 = st.columns([1, 3])
    with col_nav1:
        if st.button("↩️ Back to Analysis", key="back_to_analysis"):
            st.session_state.current_mode = "Analysis"
            st.session_state.mode_selected = True
            st.rerun()

    st.markdown("---")

    # =============================================================================
    # QUICK SUMMARY FROM INTAKE
    # =============================================================================
    st.markdown("### 📋 Your Current Information")

    # Get data from session state (from INTAKE)
    user_age = st.session_state.get('input_age', 45)
    user_name = st.session_state.get('input_user_name', 'You')
    life_expectancy = st.session_state.get('input_life_expectancy', 85)
    partner_exists = st.session_state.get('input_partner_exists', False)
    partner_age = st.session_state.get('input_partner_age', 45) if partner_exists else None
    partner_name = st.session_state.get('input_partner_name', 'Partner') if partner_exists else None

    # Calculate birth year from current age
    current_year = date.today().year
    user_birth_year = current_year - user_age
    partner_birth_year = current_year - partner_age if partner_age else None

    # Get income for PIA estimation
    salary_wages = st.session_state.get('input_salary_wages', 75000)

    # Store can_save flag for Tab 4
    st.session_state['ss_can_save_scenario'] = can_save_scenario

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Your Age", f"{user_age} years")
        st.caption(f"Birth Year: ~{user_birth_year}")
    with col2:
        st.metric("Life Expectancy", f"{life_expectancy} years")
        st.caption(f"Years to plan: {life_expectancy - user_age}")
    with col3:
        if partner_exists:
            st.metric("Partner Status", f"{partner_name}")
            st.caption(f"Age: {partner_age}")
        else:
            st.metric("Filing Status", "Single")
            st.caption("Individual optimization")

    # =============================================================================
    # TAB INTERFACE
    # =============================================================================
    tabs = st.tabs([
        "🎯 Your Claiming Strategy",
        "👥 Spousal Optimization" if partner_exists else "👤 Individual Strategy",
        "📊 Break-Even Analysis",
        "💾 Apply Strategy"
    ])

    # =========================================================================
    # TAB 1: YOUR CLAIMING STRATEGY
    # =========================================================================
    with tabs[0]:
        st.markdown("### 🎯 Personal Claiming Strategy")
        st.markdown("**Adjust your expected SS benefit and see how claiming age affects your lifetime benefits.**")

        # Input section
        col_input1, col_input2 = st.columns(2)

        with col_input1:
            st.markdown("#### 💰 Your Expected SS Benefit")

            # Option to enter PIA directly or estimate from income
            estimation_method = st.radio(
                "How to determine your benefit:",
                ["Estimate from income", "Enter monthly benefit directly"],
                index=0,
                key="pia_method"
            )

            if estimation_method == "Estimate from income":
                # Ensure valid default (must be >= min_value)
                # If widget key exists in session state, Streamlit will use it automatically
                # Otherwise, use base plan income for first load
                if 'ss_income' not in st.session_state:
                    # First load - initialize with base plan income
                    base_inc = st.session_state.get('ss_base_income', salary_wages)
                    default_income = max(int(base_inc), 10000) if base_inc else 75000
                else:
                    # Session state already has value - use it (Streamlit handles this automatically)
                    default_income = max(int(st.session_state['ss_income']), 10000)

                income_for_ss = st.number_input(
                    "Your highest annual income ($)",
                    min_value=10000,
                    max_value=500000,
                    value=default_income,
                    step=5000,
                    help="Your highest earning years determine your SS benefit",
                    key="ss_income"
                )

                # Show divergence indicator
                base_income = st.session_state.get('ss_base_income', salary_wages)
                if can_save_scenario and base_income > 0 and abs(income_for_ss - base_income) > 1000:
                    diff_pct = ((income_for_ss - base_income) / base_income * 100)
                    st.caption(f"⚠️ **{diff_pct:+.0f}% from base plan** (${base_income:,.0f})")
                elif can_save_scenario and base_income == 0:
                    st.caption(f"ℹ️ Base plan has $0 salary (retired?). Using ${income_for_ss:,.0f} for SS estimate.")

                years_worked = st.slider(
                    "Years of work history",
                    min_value=10,
                    max_value=45,
                    value=35,
                    help="35 years needed for full credit",
                    key="ss_years_worked"
                )
                estimated_pia = estimate_pia_from_income(income_for_ss, years_worked)
                st.info(f"📊 **Estimated monthly benefit at FRA: ${estimated_pia:,.0f}**")
                st.caption("*This is an estimate. Check your SSA statement for actual amount.*")
                user_pia = estimated_pia
            else:
                user_pia = st.number_input(
                    "Monthly benefit at Full Retirement Age ($)",
                    min_value=500,
                    max_value=5000,
                    value=2500,
                    step=100,
                    help="Find this on your SSA statement (ssa.gov)",
                    key="ss_pia_direct"
                )
                # No divergence tracking for manual entry
                income_for_ss = salary_wages  # Use base for tracking

        with col_input2:
            st.markdown("#### 📅 Claiming Age Selector")
            claiming_age = st.slider(
                "When will you claim SS benefits?",
                min_value=62,
                max_value=70,
                value=67,
                help="62 = Early (reduced) | 67 = FRA | 70 = Maximum delayed credits",
                key="ss_claiming_age"
            )

            # Show FRA info
            fra = get_fra(user_birth_year)
            if claiming_age < fra:
                st.warning(f"⚠️ Claiming **{fra - claiming_age:.1f} years early**. Benefits will be reduced.")
            elif claiming_age > fra:
                st.success(f"✅ Delaying **{claiming_age - fra:.1f} years past FRA**. Benefits will be increased!")
            else:
                st.info(f"📍 Claiming at **Full Retirement Age (FRA)**")

            # Adjust life expectancy
            # If widget key exists in session state, Streamlit uses it automatically
            # Otherwise, initialize with base plan life expectancy
            if 'ss_life_exp' not in st.session_state:
                # First load - initialize with base plan life expectancy
                default_life_exp = st.session_state.get('ss_base_life_exp', life_expectancy)
            else:
                # Session state already has value - use it (Streamlit handles this automatically)
                default_life_exp = st.session_state['ss_life_exp']

            adjusted_life_exp = st.slider(
                "Adjust life expectancy",
                min_value=70,
                max_value=100,
                value=default_life_exp,
                help="Living longer favors delayed claiming",
                key="ss_life_exp"
            )

            # Show divergence indicator
            base_life_exp = st.session_state.get('ss_base_life_exp', life_expectancy)
            if can_save_scenario and adjusted_life_exp != base_life_exp:
                diff = adjusted_life_exp - base_life_exp
                st.caption(f"⚠️ **{diff:+d} years from base plan** ({base_life_exp} years)")
            elif can_save_scenario and adjusted_life_exp == base_life_exp:
                st.caption(f"✅ Matches base plan ({base_life_exp} years)")

        # Track parameter changes for save-time warning
        param_changes = []
        if can_save_scenario:
            base_income = st.session_state.get('ss_base_income', salary_wages)
            base_life = st.session_state.get('ss_base_life_exp', life_expectancy)

            if estimation_method == "Estimate from income" and abs(income_for_ss - base_income) > 1000:
                diff_pct = ((income_for_ss - base_income) / base_income * 100) if base_income > 0 else 0
                param_changes.append({
                    'param': 'Annual Income (for SS estimate)',
                    'base': f"${base_income:,.0f}",
                    'current': f"${income_for_ss:,.0f}",
                    'diff': f"{diff_pct:+.0f}%",
                    'impact': 'Changes estimated SS benefit amount'
                })

            if adjusted_life_exp != base_life:
                diff = adjusted_life_exp - base_life
                param_changes.append({
                    'param': 'Life Expectancy',
                    'base': f"{base_life} years",
                    'current': f"{adjusted_life_exp} years",
                    'diff': f"{diff:+d} years",
                    'impact': f"Adds/removes {abs(diff)} years of simulation"
                })

        # Store for Tab 4
        st.session_state['ss_param_changes'] = param_changes
        st.session_state['ss_current_income'] = income_for_ss
        st.session_state['ss_current_life_exp'] = adjusted_life_exp
        st.session_state['ss_current_claiming_age'] = claiming_age
        st.session_state['ss_current_monthly_benefit'] = 0  # Will be set below

        # Calculate and display results
        st.markdown("---")
        st.markdown("### 📈 Your Strategy Results")

        monthly_benefit = calculate_benefit_at_age(user_pia, claiming_age, user_birth_year)
        lifetime_data = calculate_lifetime_benefits(monthly_benefit, claiming_age, adjusted_life_exp)

        # Store for Tab 4 save functionality
        st.session_state['ss_current_monthly_benefit'] = monthly_benefit

        # Key metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric(
                "Monthly Benefit",
                f"${monthly_benefit:,.0f}",
                help="Your monthly SS check"
            )
        with col_m2:
            st.metric(
                "Annual Benefit",
                f"${monthly_benefit * 12:,.0f}",
                help="Yearly total"
            )
        with col_m3:
            st.metric(
                "Lifetime Total",
                f"${lifetime_data['nominal_total']:,.0f}",
                help="Total received over lifetime (with COLA)"
            )
        with col_m4:
            st.metric(
                "Years Receiving",
                f"{lifetime_data['years_receiving']:.0f}",
                help=f"From age {claiming_age} to {adjusted_life_exp}"
            )

        # SS TAXATION CALCULATOR - NEW FEATURE!
        st.markdown("---")
        st.markdown("### 💸 Social Security Taxation Impact")
        st.info("📊 **NEW:** See how much of your SS benefits will be taxable based on your total income.")

        with st.expander("📋 Calculate Your SS Tax Liability", expanded=True):
            col_tax1, col_tax2 = st.columns(2)

            with col_tax1:
                # Get other income (non-SS income in retirement)
                other_retirement_income = st.number_input(
                    "Other retirement income (pensions, investments, etc.)",
                    min_value=0,
                    max_value=500000,
                    value=30000,
                    step=5000,
                    help="Include pension, IRA withdrawals, investment income, part-time work, etc.",
                    key="ss_other_income"
                )

                filing_status = st.selectbox(
                    "Filing status",
                    options=["Single", "Married Filing Jointly"],
                    index=1 if partner_exists else 0,
                    key="ss_filing_status",
                    help="This affects the taxation thresholds"
                )

            with col_tax2:
                federal_rate = st.slider(
                    "Your marginal federal tax rate (%)",
                    min_value=10,
                    max_value=37,
                    value=22,
                    step=2,
                    help="Common brackets: 12%, 22%, 24%, 32%",
                    key="ss_fed_rate"
                )

                state_rate = st.slider(
                    "State income tax rate (%) - 0 if exempt",
                    min_value=0.0,
                    max_value=15.0,
                    value=0.0,
                    step=0.5,
                    help="37 states don't tax SS. Check your state's rules.",
                    key="ss_state_rate"
                )

            # Calculate taxation
            annual_ss = monthly_benefit * 12
            filing_status_code = "married" if "Married" in filing_status else "single"

            taxation_result = calculate_ss_taxable_portion(
                annual_ss, other_retirement_income, filing_status_code
            )

            after_tax_result = calculate_ss_after_tax(
                annual_ss, other_retirement_income,
                federal_rate / 100, state_rate / 100,
                filing_status_code
            )

            # Display results
            st.markdown("#### 📊 Your SS Taxation Summary")

            col_res1, col_res2, col_res3, col_res4 = st.columns(4)

            with col_res1:
                st.metric(
                    "Combined Income",
                    f"${taxation_result['combined_income']:,.0f}",
                    help="Other income + 50% of SS benefits"
                )

            with col_res2:
                taxable_pct = taxation_result['taxable_percentage'] * 100
                st.metric(
                    "SS Taxable %",
                    f"{taxable_pct:.0f}%",
                    help=f"Based on {taxation_result['tax_bracket']}"
                )

            with col_res3:
                st.metric(
                    "Annual Tax on SS",
                    f"${after_tax_result['total_tax']:,.0f}",
                    help=f"Federal: ${after_tax_result['federal_tax']:,.0f}, State: ${after_tax_result['state_tax']:,.0f}"
                )

            with col_res4:
                st.metric(
                    "Net SS (After Tax)",
                    f"${after_tax_result['after_tax_ss']:,.0f}",
                    help=f"Effective tax rate: {after_tax_result['effective_tax_rate']*100:.1f}%"
                )

            # Detailed breakdown
            st.markdown(f"""
            **Tax Bracket:** {taxation_result['tax_bracket']}
            - Gross SS benefits: **${annual_ss:,.0f}/year** (${monthly_benefit:,.0f}/month)
            - Taxable portion: **${after_tax_result['taxable_ss']:,.0f}** ({taxable_pct:.0f}%)
            - Non-taxable portion: **${after_tax_result['non_taxable_ss']:,.0f}**
            - Federal tax: **${after_tax_result['federal_tax']:,.0f}**
            - State tax: **${after_tax_result['state_tax']:,.0f}**
            - **Net annual SS: ${after_tax_result['after_tax_ss']:,.0f}** (${after_tax_result['after_tax_ss']/12:,.0f}/month)
            """)

            # Warning if high taxation
            if taxable_pct >= 85:
                st.warning(f"⚠️ **85% of your SS benefits will be taxable.** Consider strategies to reduce other income or Roth conversions before claiming.")
                st.info("""
                💡 **ASK YOUR ACCOUNTANT:** Consider Roth IRA conversions BEFORE you start claiming Social Security.

                Converting traditional IRA/401k to Roth *before* SS starts can:
                - Reduce future taxable income (Roth withdrawals are tax-free)
                - Lower your "combined income" when SS begins
                - Keep more of your SS benefits tax-free
                - This strategy works best in years when your income is lower (early retirement)

                **This is a complex decision - consult a tax professional or fee-only financial advisor.**
                """)

                # Link to Roth Calculator
                if st.button("💰 Open Roth Conversion Calculator", key="open_roth_calc", type="secondary"):
                    st.session_state['show_roth_calculator'] = True
                    st.rerun()
            elif taxable_pct >= 50:
                st.info(f"ℹ️ **{taxable_pct:.0f}% of your SS is taxable.** You're in the middle bracket - some planning opportunities may exist.")
                st.caption("💡 **Tip:** Ask your accountant about Roth conversions before claiming SS to potentially reduce taxable income.")
            else:
                st.success(f"✅ **Only {taxable_pct:.0f}% taxable!** Your combined income is low enough to minimize SS taxation.")

        # COLA Information Box
        with st.expander("ℹ️ What's included in these calculations?", expanded=False):
            st.markdown("""
            **✅ Included in calculations:**
            - **COLA adjustments** (2.5% annual Cost-of-Living increases)
            - **Early claiming reductions** (5/9% per month for first 36 months early)
            - **Delayed retirement credits** (8% per year after FRA, up to age 70)
            - **Break-even analysis** (when delayed claiming "pays off")
            - **Present value calculations** (discounted to today's dollars)
            - **SS Taxation** (0%, 50%, or 85% taxable based on combined income) ✨ NEW!

            **❌ NOT included (for simplicity):**
            - Medicare premium impacts (IRMAA)
            - Earnings test if still working
            - Spousal survivor benefits after death
            - Disability considerations
            """)

        # Comparison table
        st.markdown("#### 📊 Compare All Claiming Ages")

        comparison_table = generate_claiming_comparison_table(user_pia, user_birth_year, adjusted_life_exp)

        # Convert to DataFrame for display
        df = pd.DataFrame(comparison_table)
        df = df.rename(columns={
            'claiming_age': 'Claim Age',
            'monthly_benefit': 'Monthly ($)',
            'annual_benefit': 'Annual ($)',
            'pct_of_fra': '% of FRA',
            'lifetime_total': 'Lifetime Total ($)',
            'break_even_vs_62': 'Break-Even Age'
        })

        # Format numbers
        df['Monthly ($)'] = df['Monthly ($)'].apply(lambda x: f"${x:,.0f}")
        df['Annual ($)'] = df['Annual ($)'].apply(lambda x: f"${x:,.0f}")
        df['% of FRA'] = df['% of FRA'].apply(lambda x: f"{x:.1f}%")
        df['Lifetime Total ($)'] = df['Lifetime Total ($)'].apply(lambda x: f"${x:,.0f}")
        df['Break-Even Age'] = df['Break-Even Age'].apply(lambda x: f"{x:.1f}" if x else "N/A")

        # Highlight selected age
        st.dataframe(
            df[['Claim Age', 'Monthly ($)', 'Annual ($)', '% of FRA', 'Lifetime Total ($)', 'Break-Even Age']],
            width='stretch',
            hide_index=True,
            height=350
        )

        # Highlight optimal
        optimal_strategy = optimize_claiming_strategy(user_pia, user_birth_year, adjusted_life_exp)
        optimal_age = optimal_strategy['optimal_strategy']['claiming_age']

        st.success(f"🏆 **Optimal Claiming Age: {optimal_age}** - Maximizes lifetime present value!")

        if claiming_age != optimal_age:
            diff = optimal_strategy['optimal_strategy']['lifetime_pv'] - lifetime_data['present_value']
            if diff > 0:
                st.warning(f"⚠️ Claiming at {claiming_age} instead of {optimal_age} could cost you ~${diff:,.0f} in present value.")

    # =========================================================================
    # TAB 2: SPOUSAL OPTIMIZATION
    # =========================================================================
    with tabs[1]:
        if partner_exists:
            st.markdown("### 👥 Spousal Optimization Strategy")
            st.markdown("**Coordinate claiming ages to maximize household benefits.**")

            col_you, col_partner = st.columns(2)

            with col_you:
                st.markdown(f"#### 👤 {user_name}")
                your_claim_age = st.selectbox(
                    f"{user_name}'s Claiming Age",
                    options=list(range(62, 71)),
                    index=5,  # Default 67
                    key="spousal_your_age"
                )
                your_monthly = calculate_benefit_at_age(user_pia, your_claim_age, user_birth_year)
                st.metric("Monthly Benefit", f"${your_monthly:,.0f}")

            with col_partner:
                st.markdown(f"#### 👤 {partner_name}")

                partner_income = st.number_input(
                    f"{partner_name}'s highest annual income",
                    min_value=0,
                    max_value=500000,
                    value=50000,
                    step=5000,
                    key="partner_income"
                )
                partner_pia = estimate_pia_from_income(partner_income, 35) if partner_income > 0 else 0

                partner_claim_age = st.selectbox(
                    f"{partner_name}'s Claiming Age",
                    options=list(range(62, 71)),
                    index=5,  # Default 67
                    key="spousal_partner_age"
                )

                if partner_pia > 0:
                    partner_monthly = calculate_benefit_at_age(partner_pia, partner_claim_age, partner_birth_year)
                else:
                    # Spousal benefit
                    partner_monthly = user_pia * 0.5
                    st.caption("(Spousal benefit - 50% of your FRA)")

                st.metric("Monthly Benefit", f"${partner_monthly:,.0f}")

            # Combined household benefits
            st.markdown("---")
            st.markdown("### 🏠 Combined Household Benefits")

            combined_monthly = your_monthly + partner_monthly
            combined_annual = combined_monthly * 12

            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.metric("Combined Monthly", f"${combined_monthly:,.0f}")
            with col_c2:
                st.metric("Combined Annual", f"${combined_annual:,.0f}")
            with col_c3:
                # Rough lifetime estimate
                avg_years = ((adjusted_life_exp - your_claim_age) + (adjusted_life_exp - partner_claim_age)) / 2
                st.metric("Est. Lifetime (both)", f"${combined_annual * avg_years:,.0f}")

            st.info("💡 **Tip**: Consider one spouse claiming early (for immediate income) while the other delays (for higher lifetime benefits).")

        else:
            st.markdown("### 👤 Individual Strategy")
            st.markdown("**No spouse detected. You're optimizing for single filing.**")
            st.info("ℹ️ Add a partner in INTAKE to see spousal optimization options.")

    # =========================================================================
    # TAB 3: BREAK-EVEN ANALYSIS
    # =========================================================================
    with tabs[2]:
        st.markdown("### 📊 Break-Even Analysis")
        st.markdown("**Find out when delayed claiming pays off vs early claiming.**")

        # Visual break-even chart
        try:
            import plotly.graph_objects as go

            # Generate cumulative benefit curves
            ages_to_compare = [62, 67, 70]
            colors = ['red', 'blue', 'green']
            labels = ['Age 62 (Early)', 'Age 67 (FRA)', 'Age 70 (Delayed)']

            fig = go.Figure()

            for age, color, label in zip(ages_to_compare, colors, labels):
                monthly = calculate_benefit_at_age(user_pia, age, user_birth_year)
                annual = monthly * 12

                cumulative = []
                years_list = []

                total = 0
                for current_age in range(age, adjusted_life_exp + 1):
                    if current_age > age:
                        total += annual * (1.02 ** (current_age - age - 1))  # COLA
                    cumulative.append(total)
                    years_list.append(current_age)

                fig.add_trace(go.Scatter(
                    x=years_list,
                    y=cumulative,
                    mode='lines',
                    name=label,
                    line=dict(color=color, width=3)
                ))

            # Add break-even markers
            be_67_vs_62 = calculate_break_even_age(user_pia, user_birth_year, 62, 67)
            be_70_vs_62 = calculate_break_even_age(user_pia, user_birth_year, 62, 70)

            fig.add_vline(x=be_67_vs_62, line_dash="dash", line_color="purple",
                         annotation_text=f"Break-even 67 vs 62: Age {be_67_vs_62:.0f}")
            fig.add_vline(x=be_70_vs_62, line_dash="dash", line_color="orange",
                         annotation_text=f"Break-even 70 vs 62: Age {be_70_vs_62:.0f}")

            fig.update_layout(
                title="Cumulative Lifetime Benefits by Claiming Age",
                xaxis_title="Your Age",
                yaxis_title="Cumulative Benefits ($)",
                yaxis_tickformat='$,.0f',
                height=500,
                hovermode='x unified'
            )

            st.plotly_chart(fig, width='stretch')

        except ImportError:
            st.warning("📊 Install Plotly for interactive charts: pip install plotly")

        # Break-even summary
        st.markdown("#### 🎯 Key Break-Even Points")

        be_data = []
        for delayed_age in [65, 67, 70]:
            if delayed_age > 62:
                be_age = calculate_break_even_age(user_pia, user_birth_year, 62, delayed_age)
                be_data.append({
                    'Strategy': f"Delay to {delayed_age} vs Claim at 62",
                    'Break-Even Age': f"{be_age:.0f}",
                    'Years to Wait': f"{be_age - delayed_age:.0f}",
                    'Recommendation': "✅ Favorable" if be_age < adjusted_life_exp else "⚠️ May not reach"
                })

        df_be = pd.DataFrame(be_data)
        st.dataframe(df_be, width='stretch', hide_index=True)

        if adjusted_life_exp > be_70_vs_62:
            st.success(f"🎉 **Based on your life expectancy of {adjusted_life_exp}, delaying to age 70 is projected to be beneficial!**")
        else:
            st.warning(f"⚠️ **With life expectancy of {adjusted_life_exp}, you may not reach break-even for maximum delay. Consider claiming earlier.**")

    # =========================================================================
    # TAB 4: APPLY STRATEGY
    # =========================================================================
    with tabs[3]:
        st.markdown("### 💾 Apply Your Strategy")
        st.markdown("**Save your optimized SS strategy or apply it to your retirement plan.**")

        # =================================================================
        # ORANGUTAN PREVENTION: CHECK FOR PARAMETER DIVERGENCE
        # =================================================================
        param_changes = st.session_state.get('ss_param_changes', [])
        can_save = st.session_state.get('ss_can_save_scenario', False)

        if not can_save:
            st.error("❌ **No base plan found.** Please complete INTAKE first before saving scenarios.")
            st.stop()

        # Show warning if parameters diverged from base plan
        if len(param_changes) > 0:
            st.markdown("---")
            st.error("### 🦧 SCENARIO DIVERGENCE WARNING")

            st.warning(f"""
            **You modified {len(param_changes)} parameter(s) from your Base Plan:**
            """)

            # Show each change
            for change in param_changes:
                st.markdown(f"""
                **• {change['param']}:** {change['base']} → {change['current']} ({change['diff']})
                *Impact:* {change['impact']}
                """)

            st.error("""
            ⚠️ **CRITICAL WARNING:**

            This scenario models a **DIFFERENT FINANCIAL SITUATION** than your Base Plan!

            **What this means:**
            - Comparison results will be **MISLEADING**
            - Differences come from changed assumptions, **NOT** just SS claiming age
            - Final savings differences may be **$1M+** due to these changes

            **💡 For accurate SS strategy comparison:**
            1. Click "🔄 Reset to Base Plan Values" below
            2. Keep ONLY the claiming age you selected
            3. Then save for true apples-to-apples comparison

            **OR** save anyway if you intentionally want to model different scenarios.
            """)

            # Offer reset button BEFORE save options
            col_warn1, col_warn2, col_warn3 = st.columns(3)

            with col_warn1:
                if st.button("🔄 Reset to Base Plan Values", type="primary", key="reset_to_base"):
                    st.session_state['ss_reset_to_base'] = True
                    st.rerun()

            with col_warn2:
                proceed_anyway = st.checkbox("✅ I understand the risks - proceed to save", key="proceed_with_divergence")

            with col_warn3:
                if st.button("❌ Cancel - Go Back", key="cancel_save"):
                    st.info("💡 Adjust parameters in Tab 1, then come back to save.")
                    st.stop()

            if not proceed_anyway:
                st.info("⏸️ **Waiting for your decision...** Check the box above to proceed, or reset to base plan values.")
                st.stop()

            st.success("✅ Proceeding with divergent parameters - scenario will be marked accordingly.")
            st.markdown("---")

        else:
            # No divergence - safe to save
            st.success("✅ **Parameters match your Base Plan** - safe for apples-to-apples comparison!")
            st.markdown("---")

        col_apply1, col_apply2 = st.columns(2)

        with col_apply1:
            st.markdown("#### 🎯 Save to Scenario Studio")
            st.markdown("Create a scenario with your SS claiming age baked in.")

            if st.button("📊 Create SS Strategy Scenario", type="primary", key="go_to_studio"):
                # Get values from session state (set in Tab 1)
                current_claiming_age = st.session_state.get('ss_current_claiming_age', 67)
                current_monthly_benefit = st.session_state.get('ss_current_monthly_benefit', 2500)

                # Auto-create a scenario with SS strategy
                try:
                    from utils.comparison_scenarios import save_comparison_scenario
                    from simulation_core import run_simulation
                    from utils.snapshot_manager import get_current_snapshot, get_snapshots_index

                    # Get current snapshot for base plan ID - MUST MATCH SCENARIO STUDIO!
                    index = get_snapshots_index()
                    base_plan_id = index.get('current_snapshot_id', 'default_plan')

                    if base_plan_id == 'default_plan' or not base_plan_id:
                        st.warning("⚠️ No base plan found. Please save your data in INTAKE first.")
                        st.stop()

                    # LOAD ACTUAL BASE PLAN DATA - Use same values as base plan, just add SS income
                    from utils.snapshot_manager import load_snapshot
                    base_snapshot = load_snapshot(base_plan_id)

                    if not base_snapshot:
                        st.error("❌ Could not load base plan data")
                        st.stop()

                    # Get financial data from the ACTUAL base plan (not defaults!)
                    snapshot_data = base_snapshot.get('snapshot_data', base_snapshot)

                    salary = snapshot_data.get('input_salary_wages', 75000)
                    existing_ss = snapshot_data.get('input_social_security_income', 0)
                    pension = snapshot_data.get('input_pension_income', 0)
                    inv_income = snapshot_data.get('input_investment_income', 0)
                    other_income = snapshot_data.get('input_other_income', 0)

                    housing = snapshot_data.get('input_housing_expenses', 24000)
                    healthcare = snapshot_data.get('input_healthcare_expenses', 6000)
                    groceries = snapshot_data.get('input_groceries_expenses', 7200)
                    transportation = snapshot_data.get('input_transportation_expenses', 4800)
                    other_exp = snapshot_data.get('input_other_expenses', 12000)
                    utilities = snapshot_data.get('input_utilities_expenses', 3600)
                    insurance = snapshot_data.get('input_insurance_expenses', 3600)

                    ira = snapshot_data.get('input_ira_balance', 0)
                    four01k = snapshot_data.get('input_four01k_403b_balance', 0)
                    roth = snapshot_data.get('input_roth_balance', 0)
                    hsa = snapshot_data.get('input_hsa_balance', 0)
                    partner_ira = snapshot_data.get('input_partner_ira_balance', 0)
                    partner_401k = snapshot_data.get('input_partner_four01k_403b_balance', 0)
                    taxable = snapshot_data.get('input_taxable_investment_accounts', 0)
                    cash = snapshot_data.get('input_cash_savings', 0)

                    home_value = snapshot_data.get('input_primary_residence_value', 0)
                    mortgage = snapshot_data.get('input_primary_residence_mortgage', 0)
                    secondary = snapshot_data.get('input_secondary_residence_value', 0)
                    secondary_mortgage = snapshot_data.get('input_secondary_residence_mortgage', 0)

                    return_rate = snapshot_data.get('input_return_rate', 0.07)
                    inflation_rate = snapshot_data.get('input_inflation_rate', 0.03)
                    base_life_exp = snapshot_data.get('input_life_expectancy', 85)
                    base_age = snapshot_data.get('input_age', 45)

                    # Calculate totals - REPLACE existing SS with new optimized SS income
                    ss_income = current_monthly_benefit * 12  # New optimized SS income
                    total_income = salary + ss_income + pension + inv_income + other_income
                    total_expenses = housing + healthcare + groceries + transportation + other_exp + utilities + insurance
                    liquid_assets = ira + four01k + roth + hsa + partner_ira + partner_401k + taxable + cash
                    total_liabilities = mortgage + secondary_mortgage
                    # USE BASE PLAN'S SIMULATION YEARS FOR CONSISTENCY!
                    simulation_years = base_life_exp - base_age
                    monthly_surplus = (total_income - total_expenses) / 12

                    # Show what we're using
                    st.info(f"📊 Creating scenario with: Age {base_age}, Life Exp {base_life_exp}, Sim Years: {simulation_years}")

                    # Run simulation with SS income - USE BASE PLAN AGE for consistency!
                    ss_results = run_simulation(
                        age=base_age,
                        partner_exists=partner_exists,
                        partner_age=partner_age if partner_exists else base_age,
                        total_income=total_income,
                        total_expenses=total_expenses,
                        combined_financial_assets=liquid_assets,
                        primary_residence_value=home_value,
                        secondary_residence_value=secondary,
                        combined_other_assets_total=0,
                        total_liabilities_local=total_liabilities,
                        partner_liabilities=0,
                        tax_rate=0.22,
                        inflation_rate=inflation_rate * 100,
                        investment_return_rate=return_rate * 100,
                        simulation_years=simulation_years,
                        mc_iterations=0,
                        goal_costs={},
                        college_inflation_pct=4.0,
                        base_public_in=20000,
                        base_public_out=40000,
                        base_private=60000,
                        ira_balance=ira,
                        four01k_403b_balance=four01k,
                        partner_ira_balance=partner_ira,
                        partner_four01k_403b_balance=partner_401k,
                        monthly_surplus=monthly_surplus,
                        combined_total_liabilities=total_liabilities
                    )

                    if ss_results:
                        # Serialize results for storage
                        serializable_results = {}
                        for key, value in ss_results.items():
                            if hasattr(value, 'to_dict'):
                                serializable_results[key] = {
                                    '_type': 'dataframe',
                                    'data': value.to_dict(orient='list')
                                }
                            else:
                                serializable_results[key] = value

                        # Save the scenario - include divergence info if applicable
                        has_divergence = len(param_changes) > 0
                        divergence_marker = " ⚠️" if has_divergence else ""
                        scenario_name = f"SS Claim @ Age {current_claiming_age} (${current_monthly_benefit:,.0f}/mo){divergence_marker}"

                        description = f"Social Security strategy: Claim at age {current_claiming_age} for ${current_monthly_benefit:,.0f}/month"
                        if has_divergence:
                            description += " | ⚠️ WARNING: Uses modified parameters (see parameter_divergence)"

                        scenario_id = save_comparison_scenario(
                            base_plan_id=base_plan_id,
                            name=scenario_name,
                            description=description,
                            adjustments={
                                # SS-specific adjustments
                                'social_security_income': ss_income,
                                'ss_claiming_age': current_claiming_age,
                                'ss_monthly_benefit': current_monthly_benefit,
                                'ss_annual_benefit': ss_income,
                                # CRITICAL: Save ALL input parameters for comparison debugging
                                'retirement_age': base_age + 20 if base_age < 45 else 65,  # Estimated
                                'life_expectancy': base_life_exp,
                                'simulation_years': simulation_years,
                                'annual_income': total_income,
                                'annual_expenses': total_expenses,
                                'custom_income_total': pension + inv_income + other_income,
                                'custom_expenses_total': 0,
                                'ss_income_annual': ss_income,
                                # Starting balances
                                'ira_balance': ira,
                                '401k_balance': four01k,
                                'roth_balance': roth,
                                'hsa_balance': hsa,
                                'taxable_balance': taxable + cash,
                                # Rates
                                'investment_return': return_rate * 100,
                                'inflation_rate': inflation_rate * 100,
                                'stocks_allocation': 60,  # Default assumption
                                'bonds_allocation': 40,
                                # Divergence tracking (for comparison warnings)
                                'parameter_divergence': param_changes if has_divergence else [],
                                'uses_base_plan_values': not has_divergence,
                            },
                            simulation_results=serializable_results
                        )

                        if scenario_id:
                            st.success(f"✅ **Scenario Created!** '{scenario_name}'")
                            st.info("📊 Navigating to Scenario Studio...")
                            # Auto-navigate to Studio after successful save
                            st.session_state.current_mode = "scenario_studio"
                            st.session_state.mode_selected = True
                            st.rerun()
                        else:
                            st.error("❌ Failed to save scenario")
                    else:
                        st.error("❌ Simulation failed")
                except Exception as e:
                    st.error(f"❌ Error creating scenario: {str(e)}")
                    import traceback
                    traceback.print_exc()

        with col_apply2:
            st.markdown("#### 📤 Share Your Analysis")
            st.markdown("Export or share your SS strategy with others.")

            # Get current values from session state
            current_claiming_age = st.session_state.get('ss_current_claiming_age', 67)
            current_monthly_benefit = st.session_state.get('ss_current_monthly_benefit', 2500)
            current_life_exp = st.session_state.get('ss_current_life_exp', 85)

            # Generate summary text
            summary_text = f"""Social Security Strategy Summary
================================
Name: {user_name}
Claiming Age: {current_claiming_age}
Monthly Benefit: ${current_monthly_benefit:,.0f}
Annual Benefit: ${current_monthly_benefit * 12:,.0f}
Life Expectancy: {current_life_exp}

ℹ️ Calculations include:
- COLA adjustments (2.5% annual increases)
- Early claiming reductions / Delayed credits
- Break-even analysis

⚠️ EDUCATIONAL PURPOSES ONLY
Verify at ssa.gov/myaccount"""

            st.text_area(
                "📋 Copy this summary:",
                value=summary_text,
                height=250,
                help="Select all and copy to share with spouse, advisor, etc."
            )

            st.caption("💡 Select text above and use Ctrl+C (or Cmd+C on Mac) to copy")

        st.markdown("---")
        st.markdown("### 📤 Export Data")

        # Export to CSV
        if st.button("📋 Export Full Analysis to CSV", key="ss_export_csv"):
            # Use session state values for export
            current_claiming_age = st.session_state.get('ss_current_claiming_age', 67)
            current_life_exp = st.session_state.get('ss_current_life_exp', 85)

            # We need to recalculate user_pia based on what was used
            # For now, use a reasonable default
            export_pia = st.session_state.get('ss_current_monthly_benefit', 2500)
            df_export = pd.DataFrame(generate_claiming_comparison_table(export_pia, user_birth_year, current_life_exp))
            csv_data = df_export.to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV",
                data=csv_data,
                file_name=f"ss_analysis_{user_name}_{date.today().isoformat()}.csv",
                mime="text/csv"
            )

    # Footer with comprehensive disclaimer
    st.markdown("---")

    with st.expander("📜 Important Disclaimers & Legal Information", expanded=False):
        st.markdown("""
        ### ⚠️ Educational Tool Only

        This Social Security optimization tool is provided **for educational and informational purposes only**.

        **Important Limitations:**
        - This tool uses **simplified calculations** based on publicly available SSA rules
        - Your actual benefit depends on your **complete 35-year earnings history** (AIME calculation)
        - Only the Social Security Administration has access to your official earnings record
        - Tax implications, Medicare premiums (IRMAA), and other factors are not fully modeled
        - Life expectancy is uncertain; actual results will vary

        **This is NOT:**
        - Financial advice
        - Tax advice
        - Legal advice
        - A substitute for professional consultation

        **Before making any Social Security claiming decisions:**
        1. Create a **my Social Security account** at [ssa.gov/myaccount](https://www.ssa.gov/myaccount/)
        2. Review your official **Social Security Statement**
        3. Consider consulting a **fee-only financial advisor**
        4. Understand the **tax implications** of your decision
        5. Factor in your **health, family history, and financial needs**

        **Disclaimer:** Family Forecast and its creators are not responsible for any financial decisions made based on this tool.
        Use at your own risk.
        """)

    st.caption("🏛️ *Social Security estimates based on 2025 SSA rules. Actual benefits may vary. Consult SSA.gov for official information.*")
