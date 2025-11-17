"""
Roth Conversion Sweet Spot Calculator
======================================
Find your optimal Roth conversion amount to minimize lifetime taxes.
"""

import streamlit as st
import pandas as pd
from utils.roth_calculations import (
    calculate_roth_sweet_spot,
    generate_conversion_timeline,
    get_bracket_recommendations
)


def show_roth_calculator():
    """
    Main Roth Conversion Calculator page.
    """
    st.title("💰 Roth Conversion Sweet Spot Calculator")
    st.markdown("**Find your optimal conversion amount to minimize lifetime taxes**")

    # COMING SOON BANNER
    st.info("""
    💡 **PREVIEW FEATURE:** This is a simplified calculator for launch.

    The **full Tax Optimization Dashboard** (with multi-year strategies,
    withdrawal optimization, and IRMAA planning) launches **December 2nd**
    for Founding Members. Lock in your lifetime discount today!
    """)

    # Educational disclaimer
    st.warning("""
    ⚠️ **EDUCATIONAL TOOL** - This calculator provides estimates based on simplified assumptions.
    Actual tax savings depend on your complete financial picture. **Consult a tax professional**
    before implementing any Roth conversion strategy.
    """)

    # Navigation
    col_nav1, col_nav2 = st.columns([1, 3])
    with col_nav1:
        if st.button("↩️ Back to Analysis", key="back_to_analysis"):
            st.session_state.current_mode = "Analysis"
            st.session_state.mode_selected = True
            st.rerun()

    st.markdown("---")

    # =============================================================================
    # INPUT SECTION - Pre-filled from INTAKE
    # =============================================================================
    st.markdown("### 📋 Your Current Situation")
    st.caption("*Pre-filled from your INTAKE data - adjust as needed*")

    col1, col2 = st.columns(2)

    with col1:
        # Get defaults from session state (INTAKE data)
        default_age = st.session_state.get('input_age', 55)
        default_ira = st.session_state.get('input_ira_balance', 0) + st.session_state.get('input_four01k_403b_balance', 0)
        default_roth = st.session_state.get('input_roth_balance', 0)

        current_age = st.number_input(
            "Your current age",
            min_value=40,
            max_value=72,
            value=default_age,
            step=1,
            help="Roth conversions are most valuable between ages 55-72",
            key="roth_current_age"
        )

        trad_ira_balance = st.number_input(
            "Traditional IRA/401k balance ($)",
            min_value=0,
            max_value=10_000_000,
            value=int(default_ira),
            step=10_000,
            help="Total of all tax-deferred retirement accounts",
            key="roth_trad_balance"
        )

        roth_balance = st.number_input(
            "Current Roth balance ($)",
            min_value=0,
            max_value=10_000_000,
            value=int(default_roth),
            step=10_000,
            help="Current Roth IRA/401k balance (already tax-free)",
            key="roth_current_balance"
        )

    with col2:
        # Get income defaults
        default_income = st.session_state.get('input_salary_wages', 75000)
        partner_exists = st.session_state.get('input_partner_exists', False)

        # Estimate taxable income (simplified)
        taxable_income_estimate = default_income * 0.85  # Rough AGI estimate

        current_income = st.number_input(
            "Current annual taxable income ($)",
            min_value=0,
            max_value=1_000_000,
            value=int(taxable_income_estimate),
            step=5_000,
            help="Your AGI (Adjusted Gross Income) - income after deductions",
            key="roth_current_income"
        )

        filing_status = st.radio(
            "Filing status",
            options=["Married Filing Jointly", "Single"],
            index=0 if partner_exists else 1,
            key="roth_filing_status",
            help="This affects tax bracket thresholds"
        )

        filing_code = "married" if "Married" in filing_status else "single"

    st.markdown("---")
    st.markdown("### 🎯 Your Conversion Strategy")

    col3, col4 = st.columns(2)

    with col3:
        # Get bracket recommendations
        recommendations = get_bracket_recommendations(current_income, filing_code)

        target_bracket = st.radio(
            "Target tax bracket to stay within:",
            options=["22%", "24%", "12%"],
            index=0,
            key="roth_target_bracket",
            help="Convert enough to 'fill up' this bracket each year"
        )

        # Show recommendation for selected bracket
        for rec in recommendations:
            if rec["bracket"] == target_bracket:
                st.caption(f"📊 **{rec['recommendation']}**")
                st.caption(f"Best for: {rec['best_for']}")
                st.caption(f"Bracket ceiling: ${rec['max_income']:,}")
                break

    with col4:
        conversion_start = st.number_input(
            "Start conversions at age",
            min_value=current_age,
            max_value=72,
            value=max(current_age, 60),
            step=1,
            help="When to begin Roth conversions",
            key="roth_start_age"
        )

        conversion_end = st.number_input(
            "Stop conversions at age",
            min_value=conversion_start + 1,
            max_value=73,
            value=72,
            step=1,
            help="Stop before RMDs start at 73",
            key="roth_end_age"
        )

        # Warning if window is too short
        if conversion_end - conversion_start < 3:
            st.warning("⚠️ Short conversion window. Consider starting earlier for more tax savings.")

    # =============================================================================
    # CALCULATE RESULTS
    # =============================================================================
    st.markdown("---")

    results = calculate_roth_sweet_spot(
        current_age=current_age,
        trad_ira_balance=trad_ira_balance,
        roth_balance=roth_balance,
        current_taxable_income=current_income,
        target_bracket=target_bracket,
        conversion_start_age=conversion_start,
        conversion_end_age=conversion_end,
        filing_status=filing_code
    )

    # =============================================================================
    # BIG NUMBER DISPLAY (Hero Metrics)
    # =============================================================================
    st.markdown("## 🎯 Your Optimal Roth Conversion Strategy")

    # Main recommendation
    if results["annual_conversion_amount"] > 0:
        st.success(f"""
        ### Convert **${results['annual_conversion_amount']:,.0f} per year**
        ### from age **{results['start_age']}** to **{results['end_age']}**
        """)
    else:
        st.error("⚠️ Your current income already exceeds the target bracket ceiling. Consider a lower bracket or reducing current income first.")

    # Key metrics
    col_m1, col_m2, col_m3 = st.columns(3)

    with col_m1:
        st.metric(
            "Total to Convert",
            f"${results['total_converted']:,.0f}",
            help=f"Over {results['conversion_years']} years"
        )
        st.caption(f"{results['conversion_percentage']:.0f}% of your Traditional IRA")

    with col_m2:
        st.metric(
            "Tax Paid Now",
            f"${results['tax_paid_now']:,.0f}",
            help=f"At {results['target_bracket']} rate ({results['target_rate']*100:.0f}%)"
        )
        st.caption(f"Spread over {results['conversion_years']} years")

    with col_m3:
        st.metric(
            "💰 Lifetime Tax Savings",
            f"${results['lifetime_tax_savings']:,.0f}",
            delta=f"+${results['lifetime_tax_savings']:,.0f}",
            delta_color="normal",
            help="Tax avoided by converting now vs paying RMDs later"
        )
        st.caption("Compared to no conversion")

    # Additional benefits
    if results['irmaa_savings_estimate'] > 0:
        st.info(f"💊 **BONUS:** Potential Medicare IRMAA savings of **${results['irmaa_savings_estimate']:,.0f}** by keeping income below thresholds in retirement.")

    # RMD impact
    if results['rmd_reduction_at_73'] > 0:
        st.success(f"📉 **RMD Reduction:** Your Required Minimum Distribution at age 73 would be reduced by **${results['rmd_reduction_at_73']:,.0f}/year**")

    # =============================================================================
    # PLAIN ENGLISH EXPLANATION
    # =============================================================================
    st.markdown("---")
    st.markdown("### 📖 What This Means (Plain English)")

    st.markdown(f"""
    **Your Strategy:**

    By converting **${results['annual_conversion_amount']:,.0f}** each year from age {results['start_age']} to {results['end_age']},
    you'll stay within the **{results['target_bracket']}** tax bracket (top of bracket: ${results['bracket_ceiling']:,}).

    **Tax Impact:**

    - You'll pay **${results['tax_paid_now']:,.0f}** in conversion taxes now (at {results['target_rate']*100:.0f}% rate)
    - Without conversion, you'd pay **${results['tax_if_no_conversion']:,.0f}** in RMD taxes later (at 24% rate)
    - **Net lifetime savings: ${results['lifetime_tax_savings']:,.0f}** 🎉

    **Why This Works:**

    1. **Tax bracket arbitrage** - Pay 22% now instead of 24%+ later
    2. **RMD reduction** - Less in Traditional = smaller required withdrawals
    3. **Tax-free growth** - Roth grows tax-free forever (no RMDs!)
    4. **IRMAA avoidance** - Lower income in retirement = lower Medicare premiums

    **Important:** After conversion, you'll have **${results['remaining_traditional']:,.0f}** remaining in Traditional IRA
    (subject to RMDs starting at age 73).
    """)

    # =============================================================================
    # VISUALIZATION - Simple Bar Chart
    # =============================================================================
    st.markdown("---")
    st.markdown("### 📊 Tax Comparison: Convert Now vs. Pay Later")

    try:
        import plotly.graph_objects as go

        fig = go.Figure()

        # Bar 1: Tax if no conversion
        fig.add_trace(go.Bar(
            name="Tax if NO Conversion",
            x=["Without Conversion", "With Conversion"],
            y=[results['tax_if_no_conversion'], 0],
            marker_color='#FF6B6B',
            text=[f"${results['tax_if_no_conversion']:,.0f}", ""],
            textposition='outside'
        ))

        # Bar 2: Tax with conversion
        fig.add_trace(go.Bar(
            name="Tax WITH Conversion",
            x=["Without Conversion", "With Conversion"],
            y=[0, results['tax_paid_now']],
            marker_color='#4ECDC4',
            text=["", f"${results['tax_paid_now']:,.0f}"],
            textposition='outside'
        ))

        fig.update_layout(
            title=f"Total Tax on ${results['total_converted']:,.0f}",
            yaxis_title="Total Tax Paid ($)",
            yaxis_tickformat='$,.0f',
            barmode='stack',
            showlegend=True,
            height=400,
            annotations=[
                dict(
                    x=1,
                    y=results['tax_paid_now'] + results['lifetime_tax_savings'] * 0.3,
                    text=f"SAVINGS: ${results['lifetime_tax_savings']:,.0f}",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-40,
                    font=dict(size=16, color='green')
                )
            ]
        )

        st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        st.warning("📊 Install Plotly for interactive charts: `pip install plotly`")

        # Fallback text display
        st.markdown(f"""
        **Tax Comparison:**
        - Without conversion: **${results['tax_if_no_conversion']:,.0f}** (24% on RMDs)
        - With conversion: **${results['tax_paid_now']:,.0f}** ({results['target_bracket']} now)
        - **SAVINGS: ${results['lifetime_tax_savings']:,.0f}** ✅
        """)

    # =============================================================================
    # YEAR-BY-YEAR BREAKDOWN (Optional Detail)
    # =============================================================================
    with st.expander("📅 Year-by-Year Conversion Timeline", expanded=False):
        timeline = generate_conversion_timeline(
            current_age=current_age,
            trad_ira_balance=trad_ira_balance,
            annual_conversion=results['annual_conversion_amount'],
            conversion_start_age=conversion_start,
            conversion_end_age=conversion_end
        )

        df_timeline = pd.DataFrame(timeline)
        df_timeline = df_timeline.rename(columns={
            'age': 'Age',
            'year': 'Year',
            'trad_balance_start': 'Trad IRA Start',
            'conversion_amount': 'Convert',
            'trad_balance_end': 'Trad IRA End',
            'roth_balance': 'Roth Balance'
        })

        # Format currency
        for col in ['Trad IRA Start', 'Convert', 'Trad IRA End', 'Roth Balance']:
            df_timeline[col] = df_timeline[col].apply(lambda x: f"${x:,.0f}")

        st.dataframe(df_timeline, use_container_width=True, hide_index=True)

    # =============================================================================
    # ACTION BUTTON
    # =============================================================================
    st.markdown("---")
    st.markdown("### 🚀 Apply This Strategy")

    col_act1, col_act2 = st.columns(2)

    with col_act1:
        if st.button("📊 Save Strategy to My Plan", type="primary", key="save_roth_strategy"):
            # Save to session state for later use
            st.session_state['roth_strategy'] = results
            st.session_state['roth_strategy_applied'] = True
            st.success(f"""
            ✅ **Strategy Saved!**

            Your Roth conversion plan:
            - Convert ${results['annual_conversion_amount']:,.0f}/year
            - From age {results['start_age']} to {results['end_age']}
            - Estimated lifetime savings: ${results['lifetime_tax_savings']:,.0f}

            This will be reflected in your Analysis and Scenario Studio.
            """)

    with col_act2:
        # Export summary
        summary_text = f"""ROTH CONVERSION STRATEGY
========================
Generated: {st.session_state.get('input_user_name', 'User')}

STRATEGY:
- Convert ${results['annual_conversion_amount']:,.0f}/year
- From age {results['start_age']} to {results['end_age']}
- Target bracket: {results['target_bracket']}

FINANCIAL IMPACT:
- Total converted: ${results['total_converted']:,.0f}
- Tax paid now: ${results['tax_paid_now']:,.0f}
- Tax saved: ${results['lifetime_tax_savings']:,.0f}

ADDITIONAL BENEFITS:
- RMD reduction at 73: ${results['rmd_reduction_at_73']:,.0f}/year
- Remaining in Traditional: ${results['remaining_traditional']:,.0f}

IMPORTANT: Consult a tax professional before implementing.
This is educational only - not financial advice.
"""
        st.text_area(
            "📋 Copy your strategy summary:",
            value=summary_text,
            height=300,
            help="Share with your financial advisor"
        )

    # =============================================================================
    # COMING SOON TEASER
    # =============================================================================
    st.markdown("---")
    st.markdown("## 🚀 COMING SOON: FULL TAX OPTIMIZATION SUITE")
    st.markdown("### *Launching December 2nd for Founding Members*")

    st.success("""
    We're building the **most comprehensive tax planning tools** in retirement planning:

    ✅ **Multi-Year Tax Strategy** - Optimize conversions across 5-10 year windows
    ✅ **Withdrawal Sequence Optimizer** - Perfect order: taxable → deferred → Roth
    ✅ **Capital Gains Harvesting** - Maximize 0% bracket opportunities
    ✅ **QCD Planning** - Tax-free charitable giving (age 70.5+)
    ✅ **IRMAA Threshold Manager** - Stay below Medicare surcharge triggers
    ✅ **State Tax Optimization** - Multi-state retirement strategies
    ✅ **Estate Tax Planning** - Minimize taxes for your heirs

    **Plus:** Interactive year-by-year tax dashboard showing your lifetime tax savings
    """)

    st.info("""
    💎 **Join as a Founding Member** today to lock in **lifetime early-bird pricing**
    and get **first access** to these premium features.

    **Founding Member Price: $119/year for LIFE** (Regular: $199/year)

    [Contact us to reserve your spot]
    """)

    # =============================================================================
    # IMPORTANT DISCLAIMERS
    # =============================================================================
    st.markdown("---")

    with st.expander("⚠️ Important Disclaimers & Limitations", expanded=False):
        st.markdown("""
        ### Educational Tool Only

        This calculator provides **simplified estimates** based on:

        - 2025 federal tax brackets (may change annually)
        - Simplified RMD projections
        - Assumed future tax rates
        - No state tax considerations
        - No alternative minimum tax (AMT) check
        - No net investment income tax (NIIT) check

        **NOT considered:**
        - Your complete tax situation
        - State income taxes (varies 0-13%)
        - Social Security taxation impact
        - Capital gains implications
        - Healthcare costs and IRMAA
        - Estate planning considerations
        - Pro-rata rule for conversions

        **BEFORE implementing any Roth conversion strategy:**

        1. **Consult a CPA or tax professional**
        2. Review your complete tax return
        3. Consider multi-year tax projections
        4. Evaluate your estate plan
        5. Check state tax implications
        6. Consider the 5-year Roth rule

        **This tool is for educational purposes only and does not constitute financial or tax advice.**
        """)

    st.caption("💰 *Roth conversion calculations based on 2025 IRS tax brackets. Consult a tax professional for personalized advice.*")


# Allow direct execution for testing
if __name__ == "__main__":
    show_roth_calculator()
