"""
Healthcare Cost Projector - Main Hub
====================================
Main navigation page for all healthcare planning tools including Medicare IRMAA
calculator, Medigap vs Medicare Advantage comparison, and Long-Term Care analysis.

Author: ForeCash Development Team
Last Updated: October 22, 2025
"""

import streamlit as st
from datetime import datetime

# Import disclaimers
from healthcare.healthcare_disclaimers import (
    show_primary_healthcare_disclaimer,
    show_all_healthcare_disclaimers,
    require_healthcare_disclaimer_acknowledgment,
    get_disclaimer_metadata
)

# Import calculator modules
from healthcare.medicare_irmaa_calculator import MedicareIRMAACalculator
from healthcare.medicare_data import (
    HISTORICAL_PART_B_PREMIUMS,
    get_medicare_cost_summary,
    STATE_PART_D_PREMIUMS
)


def show_welcome_section():
    """Display welcome and overview section"""
    st.title("🏥 Healthcare Cost Projector")
    st.markdown("### Plan for Healthcare Costs in Retirement")

    st.markdown("""
    Healthcare is one of the **largest expenses** in retirement. This tool helps you:

    - 💰 **Calculate Medicare premiums** including IRMAA surcharges based on your income
    - 📊 **Project healthcare costs** over 20-30 years with inflation
    - 💡 **Analyze Roth conversion impacts** on Medicare premiums
    - 🏥 **Compare coverage options** (Medigap vs Medicare Advantage)
    - 🏥 **Plan for long-term care** costs and funding strategies

    ---
    """)

    # Show key statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Average Retiree",
            "$7,000/yr",
            help="Average annual healthcare costs for retirees"
        )

    with col2:
        st.metric(
            "With IRMAA",
            "$10,000+/yr",
            help="Costs for higher-income retirees with IRMAA surcharges"
        )

    with col3:
        st.metric(
            "20-Year Total",
            "$150K-300K",
            help="Typical total healthcare costs over retirement"
        )

    with col4:
        st.metric(
            "Inflation Rate",
            "5-6%/yr",
            help="Historical healthcare cost inflation"
        )

    st.markdown("---")


def show_quick_facts():
    """Display quick facts about Medicare and healthcare costs"""
    st.subheader("📋 Quick Medicare Facts")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Medicare Basics:**
        - **Part A (Hospital):** Usually free if you worked 10+ years
        - **Part B (Doctor visits):** ~$175/month standard premium (2025)
        - **Part D (Prescriptions):** ~$55/month average (varies by plan)
        - **Enrollment:** Starts at age 65 (strict deadlines!)

        **IRMAA (Income Surcharges):**
        - Based on your income from **2 years ago**
        - 5 income brackets with increasing surcharges
        - Single: Starts at $106K MAGI (2025)
        - Married: Starts at $212K MAGI (2025)
        """)

    with col2:
        st.markdown("""
        **Additional Coverage Options:**
        - **Medigap (Supplement):** Covers gaps in Original Medicare
        - **Medicare Advantage (Part C):** All-in-one alternative to Original Medicare
        - **Both have pros/cons** based on your needs

        **Important Considerations:**
        - Roth conversions count as income → Can trigger IRMAA!
        - Tax-exempt interest counts for IRMAA (but not regular taxes)
        - Life-changing events may allow IRMAA appeals
        - Plans and costs change every year
        """)

    st.markdown("---")


def show_calculator_cards():
    """Display cards for each calculator/tool"""
    st.subheader("🛠️ Healthcare Planning Tools")

    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            st.markdown("### 💰 Medicare IRMAA Calculator")
            st.markdown("""
            Calculate your exact Medicare premiums including IRMAA surcharges.

            **Features:**
            - ✅ Calculate premiums based on your income
            - ✅ See which IRMAA bracket you're in
            - ✅ 20-year cost projections
            - ✅ Roth conversion impact analyzer
            - ✅ State-by-state comparisons

            **Best for:**
            - Planning retirement income withdrawals
            - Optimizing Roth conversions
            - Understanding Medicare costs
            """)

            if st.button("Open Medicare IRMAA Calculator →", key="medicare_calc", type="primary"):
                st.session_state['healthcare_page'] = 'medicare_calculator'
                st.rerun()

    with col2:
        with st.container():
            st.markdown("### 🏥 Medigap vs Medicare Advantage")
            st.markdown("""
            Compare Medigap (Supplement) and Medicare Advantage plans.

            **Features:**
            - ✅ Side-by-side plan comparison
            - ✅ Cost calculator based on usage
            - ✅ Decision helper tool
            - ✅ Long-term cost projections

            **Best for:**
            - Choosing coverage at 65
            - Evaluating plan switches
            - Understanding trade-offs

            ⚠️ *Coming Soon!*
            """)

            if st.button("Compare Plans →", key="medigap_compare", disabled=True):
                st.session_state['healthcare_page'] = 'medigap_comparison'
                st.rerun()

    st.markdown("---")

    # Second row
    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            st.markdown("### 🏥 Long-Term Care Cost Planner")
            st.markdown("""
            Estimate long-term care costs and compare funding strategies.

            **Features:**
            - ✅ Regional LTC cost estimates
            - ✅ Probability analysis (will I need care?)
            - ✅ Monte Carlo simulations
            - ✅ Compare: Self-insure vs Insurance vs Medicaid

            **Best for:**
            - LTC insurance decisions
            - Asset protection planning
            - Medicaid planning

            ⚠️ *Coming Soon!*
            """)

            if st.button("Plan for LTC →", key="ltc_planner", disabled=True):
                st.session_state['healthcare_page'] = 'ltc_planner'
                st.rerun()

    with col2:
        with st.container():
            st.markdown("### 📊 Complete Healthcare Budget")
            st.markdown("""
            Comprehensive healthcare cost projection for retirement.

            **Includes:**
            - ✅ Medicare premiums (with IRMAA)
            - ✅ Supplemental insurance
            - ✅ Out-of-pocket expenses
            - ✅ Dental, vision, hearing
            - ✅ Long-term care reserves

            **Best for:**
            - Complete retirement budget
            - Monte Carlo simulations
            - Comprehensive planning

            ⚠️ *Coming Soon!*
            """)

            if st.button("Build Healthcare Budget →", key="complete_budget", disabled=True):
                st.session_state['healthcare_page'] = 'complete_budget'
                st.rerun()


def show_educational_resources():
    """Display educational resources and links"""
    st.subheader("📖 Educational Resources")

    with st.expander("🎓 Learn About Medicare", expanded=False):
        st.markdown("""
        **Official Resources:**
        - **[Medicare.gov](https://www.medicare.gov)** - Official Medicare website
        - **[Medicare Plan Finder](https://www.medicare.gov/plan-compare/)** - Compare plans in your area
        - **[SHIP (State Health Insurance Assistance Program)](https://www.shiphelp.org/)** - Free Medicare counseling
        - **[Social Security](https://www.ssa.gov/medicare/)** - Medicare enrollment info

        **Key Topics:**
        - Medicare enrollment periods and deadlines
        - Understanding Parts A, B, C, D
        - Choosing between Original Medicare and Medicare Advantage
        - Medigap plan types (A, B, C, D, F, G, K, L, M, N)
        - Prescription drug coverage (Part D)
        - Costs, premiums, and out-of-pocket expenses
        """)

    with st.expander("💰 Understanding IRMAA", expanded=False):
        st.markdown("""
        **What is IRMAA?**
        Income-Related Monthly Adjustment Amount (IRMAA) is an additional charge for Medicare
        Part B and Part D if your income exceeds certain thresholds.

        **Key Facts:**
        - Based on MAGI (Modified Adjusted Gross Income) from **2 years prior**
        - 5 income brackets with increasing surcharges
        - Applies to both Part B and Part D
        - Tax-exempt interest (muni bonds) COUNTS toward IRMAA
        - Life-changing events may qualify for appeals

        **2025 IRMAA Brackets (Single):**
        - ≤ $106,000: No IRMAA (standard premium)
        - $106,001 - $133,000: +$69.90/month Part B
        - $133,001 - $167,000: +$174.70/month Part B
        - $167,001 - $200,000: +$279.50/month Part B
        - $200,001 - $500,000: +$384.30/month Part B
        - > $500,000: +$419.30/month Part B (maximum)

        **Planning Strategies:**
        - Time income carefully (2-year lookback creates planning window)
        - Consider Roth conversions in low-income years
        - Watch for IRMAA "cliffs" (small income increase = big premium jump)
        - Appeal if you have qualifying life events
        """)

    with st.expander("🏥 Medigap vs Medicare Advantage", expanded=False):
        st.markdown("""
        **Two Different Approaches:**

        **Medigap (Medicare Supplement Insurance):**
        - Works WITH Original Medicare
        - Covers "gaps" (deductibles, coinsurance)
        - See ANY doctor who accepts Medicare
        - More predictable costs (higher premiums, lower out-of-pocket)
        - Best for: Frequent travelers, those who want provider flexibility

        **Medicare Advantage (Part C):**
        - REPLACES Original Medicare
        - All-in-one plan (includes Part D usually)
        - Provider networks (HMO/PPO)
        - Lower premiums, higher out-of-pocket when you use care
        - Best for: Healthy individuals, those who stay local

        **Decision Factors:**
        - Your health status and expected healthcare usage
        - Budget (can you afford higher premiums vs. risk of high out-of-pocket?)
        - Travel frequency (Medigap better for travelers)
        - Preferred doctors (in-network for Advantage?)
        - Medications (check formularies!)
        """)

    with st.expander("🏥 Long-Term Care Planning", expanded=False):
        st.markdown("""
        **LTC Statistics:**
        - ~70% of people over 65 will need some form of long-term care
        - Average duration: 3.5 years (but 20% need 5+ years)
        - Women typically need more care than men
        - Costs: $8,000-12,000/month for nursing home

        **Funding Options:**

        **1. Self-Insure:**
        - Need $200K-500K+ in liquid assets
        - Risk: One extended stay can deplete savings

        **2. Traditional LTC Insurance:**
        - Age limits (typically max 75-80 to purchase)
        - Medical underwriting required
        - Premiums can increase
        - Use-it-or-lose-it

        **3. Hybrid Life/LTC Policies:**
        - Combination product
        - Death benefit if LTC not needed
        - More expensive upfront

        **4. Medicaid:**
        - For low-income individuals
        - 5-year lookback period
        - Asset spend-down required
        - Requires elder law attorney guidance

        **When to Plan:**
        - LTC insurance: Buy in 50s-early 60s (before health issues)
        - Medicaid planning: Start 5+ years before potential need
        - Self-insure: Build assets throughout working years
        """)


def show_cost_trends():
    """Display historical Medicare cost trends"""
    st.subheader("📈 Historical Medicare Cost Trends")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Part B Premium History:**")

        history_data = []
        for year, premium in sorted(HISTORICAL_PART_B_PREMIUMS.items()):
            history_data.append({"Year": year, "Monthly Premium": f"${premium:.2f}"})

        import pandas as pd
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Calculate average increase
        years = sorted(HISTORICAL_PART_B_PREMIUMS.keys())
        first_year_premium = HISTORICAL_PART_B_PREMIUMS[years[0]]
        last_year_premium = HISTORICAL_PART_B_PREMIUMS[years[-1]]
        total_increase = ((last_year_premium / first_year_premium) - 1) * 100
        avg_annual = total_increase / (years[-1] - years[0])

        st.info(f"📊 Average annual increase ({years[0]}-{years[-1]}): **{avg_annual:.1f}%**")

    with col2:
        st.markdown("**Key Observations:**")
        st.markdown("""
        - Medicare premiums have increased **5-6% annually** on average
        - Large jump in 2022 due to controversial Aduhelm drug coverage
        - IRMAA brackets adjust annually for inflation
        - Part D premiums vary more by plan selection
        - Healthcare inflation typically exceeds general inflation

        **Planning Implications:**
        - Budget for 5-6% annual healthcare cost increases
        - Review plans annually during open enrollment
        - Consider inflation in multi-year projections
        - Healthcare is often the #1 or #2 expense in retirement
        """)


def show_important_disclaimers():
    """Show disclaimers section"""
    st.markdown("---")
    st.subheader("⚖️ Important Legal Information")

    show_all_healthcare_disclaimers()

    # Version info
    metadata = get_disclaimer_metadata()
    st.caption(f"Disclaimer Version: {metadata['version']} | Last Updated: {metadata['last_updated']}")


def main():
    """Main healthcare hub page"""

    # Require disclaimer acknowledgment
    require_healthcare_disclaimer_acknowledgment()

    # Check if user selected a specific tool
    if 'healthcare_page' in st.session_state and st.session_state['healthcare_page'] == 'medicare_calculator':
        # Import and show Medicare calculator
        from healthcare.medicare_calculator_ui import show_calculator_page

        # Add back button
        if st.button("← Back to Healthcare Hub"):
            st.session_state['healthcare_page'] = 'hub'
            st.rerun()

        show_calculator_page()
        return

    # Show main hub page
    show_welcome_section()

    # Quick facts
    show_quick_facts()

    # Calculator cards
    show_calculator_cards()

    # Educational resources
    show_educational_resources()

    # Cost trends
    show_cost_trends()

    # Disclaimers
    show_important_disclaimers()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>ForeCash Healthcare Cost Projector</strong></p>
    <p>Educational planning tool for retirement healthcare costs</p>
    <p style='font-size: 0.9em;'>Always consult qualified professionals before making healthcare or financial decisions</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
