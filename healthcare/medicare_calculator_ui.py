"""
Medicare IRMAA Calculator - User Interface
==========================================
Streamlit UI for Medicare IRMAA premium calculator with Roth conversion analyzer.

Author: ForeCash Development Team
Last Updated: October 22, 2025
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Import our calculation modules
from healthcare.medicare_irmaa_calculator import MedicareIRMAACalculator
from healthcare.medicare_data import (
    get_medicare_cost_summary,
    STATE_PART_D_PREMIUMS,
    project_part_b_premium,
    MEDICARE_INFLATION_RATES
)
from healthcare.healthcare_disclaimers import (
    show_medicare_irmaa_disclaimer,
    show_roth_conversion_disclaimer,
    require_healthcare_disclaimer_acknowledgment
)


def format_currency(amount):
    """Format number as currency"""
    return f"${amount:,.2f}"


def format_large_currency(amount):
    """Format large number as currency"""
    return f"${amount:,.0f}"


def create_irmaa_bracket_chart(calculator, filing_status="single"):
    """Create visual chart of IRMAA brackets"""
    brackets = calculator.get_all_brackets_summary(filing_status)

    # Prepare data for chart
    bracket_names = [b["bracket_name"] for b in brackets]
    income_ranges = [b["income_range"] for b in brackets]
    annual_costs = [float(b["total_annual"].replace("$", "").replace(",", "")) for b in brackets]

    # Create bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=bracket_names,
        y=annual_costs,
        text=[f"${cost:,.0f}/yr" for cost in annual_costs],
        textposition='auto',
        marker_color=['#2E7D32', '#558B2F', '#FFA726', '#F57C00', '#E53935', '#B71C1C'],
        hovertemplate='<b>%{x}</b><br>Income: %{customdata}<br>Annual Cost: $%{y:,.0f}<extra></extra>',
        customdata=income_ranges
    ))

    fig.update_layout(
        title=f"Medicare Annual Costs by IRMAA Bracket ({filing_status.title()})",
        xaxis_title="IRMAA Bracket",
        yaxis_title="Total Annual Medicare Cost (Part B + D)",
        height=400,
        showlegend=False,
        hovermode='x unified'
    )

    return fig


def create_projection_chart(projections):
    """Create multi-year premium projection chart"""
    df = pd.DataFrame(projections)

    fig = go.Figure()

    # Add total annual cost
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['total_annual'],
        mode='lines+markers',
        name='Total Annual Cost',
        line=dict(color='#1976D2', width=3),
        marker=dict(size=8),
        hovertemplate='Year %{x}<br>Total: $%{y:,.0f}<extra></extra>'
    ))

    # Add IRMAA bracket annotations
    for idx, row in df.iterrows():
        if idx == 0 or df.iloc[idx-1]['irmaa_bracket'] != row['irmaa_bracket']:
            fig.add_annotation(
                x=row['year'],
                y=row['total_annual'],
                text=row['irmaa_bracket'],
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#666",
                ax=0,
                ay=-40
            )

    fig.update_layout(
        title="Medicare Premium Projection (20-Year Outlook)",
        xaxis_title="Year",
        yaxis_title="Annual Medicare Cost",
        height=500,
        hovermode='x unified'
    )

    return fig


def create_roth_conversion_comparison_chart(impact_data):
    """Create comparison chart for Roth conversion impact"""
    categories = ['Current', 'With Conversion']
    annual_premiums = [
        impact_data['current_annual_premium'],
        impact_data['new_annual_premium']
    ]

    colors = ['#2E7D32', '#E53935'] if impact_data['bracket_changed'] else ['#2E7D32', '#558B2F']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=categories,
        y=annual_premiums,
        text=[f"${p:,.0f}/yr" for p in annual_premiums],
        textposition='auto',
        marker_color=colors,
        hovertemplate='<b>%{x}</b><br>Annual Premium: $%{y:,.0f}<extra></extra>'
    ))

    # Add annotation showing increase
    fig.add_annotation(
        x=1,
        y=impact_data['new_annual_premium'],
        text=f"↑ ${impact_data['annual_increase']:,.0f}/year",
        showarrow=False,
        yshift=20,
        font=dict(size=14, color='red')
    )

    fig.update_layout(
        title="Medicare Cost Impact of Roth Conversion",
        yaxis_title="Annual Medicare Premium",
        height=400,
        showlegend=False
    )

    return fig


def show_calculator_page():
    """Main Medicare IRMAA Calculator page"""

    st.title("🏥 Medicare IRMAA Calculator")

    # Show disclaimer
    show_medicare_irmaa_disclaimer()

    st.markdown("---")

    # Initialize calculator
    calculator = MedicareIRMAACalculator()

    # Sidebar inputs
    st.sidebar.header("📋 Your Information")

    # Filing status
    filing_status = st.sidebar.selectbox(
        "Filing Status",
        ["single", "married"],
        format_func=lambda x: "Single" if x == "single" else "Married Filing Jointly"
    )

    # Current age
    current_age = st.sidebar.number_input(
        "Current Age",
        min_value=50,
        max_value=100,
        value=65,
        help="Your current age (Medicare starts at 65)"
    )

    st.sidebar.markdown("---")
    st.sidebar.header("💰 Income Information")

    # Income input method
    income_method = st.sidebar.radio(
        "How would you like to enter income?",
        ["Simple (AGI + Tax-Exempt Interest)", "Detailed (Retirement Income Sources)"]
    )

    if income_method == "Simple (AGI + Tax-Exempt Interest)":
        # Simple MAGI input
        agi = st.sidebar.number_input(
            "Adjusted Gross Income (AGI)",
            min_value=0,
            max_value=10000000,
            value=100000,
            step=5000,
            help="Line 11 from Form 1040"
        )

        tax_exempt = st.sidebar.number_input(
            "Tax-Exempt Interest",
            min_value=0,
            max_value=1000000,
            value=0,
            step=1000,
            help="Municipal bond interest (Line 2a from Form 1040)"
        )

        magi = calculator.calculate_magi_simple(agi, tax_exempt)

    else:
        # Detailed retirement income
        st.sidebar.markdown("**Income Sources:**")

        social_security = st.sidebar.number_input(
            "Social Security (taxable portion)",
            min_value=0,
            max_value=100000,
            value=30000,
            step=1000
        )

        pension = st.sidebar.number_input(
            "Pension/Annuity Income",
            min_value=0,
            max_value=500000,
            value=0,
            step=5000
        )

        ira_withdrawals = st.sidebar.number_input(
            "IRA/401k Withdrawals",
            min_value=0,
            max_value=500000,
            value=40000,
            step=5000
        )

        investment_income = st.sidebar.number_input(
            "Investment Income (dividends, interest)",
            min_value=0,
            max_value=500000,
            value=20000,
            step=5000
        )

        capital_gains = st.sidebar.number_input(
            "Capital Gains",
            min_value=0,
            max_value=1000000,
            value=0,
            step=10000
        )

        tax_exempt = st.sidebar.number_input(
            "Tax-Exempt Interest (Municipal bonds)",
            min_value=0,
            max_value=200000,
            value=0,
            step=1000,
            help="This COUNTS toward MAGI for IRMAA!"
        )

        magi = calculator.calculate_magi_from_retirement_income(
            social_security=social_security,
            pension=pension,
            ira_withdrawals=ira_withdrawals,
            investment_income=investment_income,
            capital_gains=capital_gains,
            tax_exempt_interest=tax_exempt
        )

    # Calculate premiums
    result = calculator.calculate_premiums(magi, filing_status)

    # Main content area
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Your MAGI",
            format_large_currency(magi),
            help="Modified Adjusted Gross Income for IRMAA"
        )

    with col2:
        st.metric(
            "IRMAA Bracket",
            result.irmaa_bracket,
            help="Your income bracket for Medicare surcharges"
        )

    with col3:
        st.metric(
            "Monthly Medicare Cost",
            format_currency(result.total_monthly),
            help="Total Part B + Part D premiums"
        )

    st.markdown("---")

    # Detailed breakdown
    st.subheader("📊 Premium Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Part B (Medical Insurance):**")
        breakdown_df = pd.DataFrame({
            "Component": ["Base Premium", "IRMAA Surcharge", "Total Part B"],
            "Monthly": [
                format_currency(result.base_part_b),
                format_currency(result.part_b_surcharge),
                format_currency(result.total_part_b)
            ],
            "Annual": [
                format_currency(result.base_part_b * 12),
                format_currency(result.part_b_surcharge * 12),
                format_currency(result.total_part_b * 12)
            ]
        })
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Part D (Prescription Drugs):**")
        part_d_df = pd.DataFrame({
            "Component": ["Base Premium", "IRMAA Surcharge", "Total Part D"],
            "Monthly": [
                format_currency(result.base_part_d),
                format_currency(result.part_d_surcharge),
                format_currency(result.total_part_d)
            ],
            "Annual": [
                format_currency(result.base_part_d * 12),
                format_currency(result.part_d_surcharge * 12),
                format_currency(result.total_part_d * 12)
            ]
        })
        st.dataframe(part_d_df, use_container_width=True, hide_index=True)

    # Total summary
    st.info(f"**💰 TOTAL ANNUAL MEDICARE COST: {format_currency(result.total_annual)}**")

    if result.part_b_surcharge > 0:
        standard_annual = (calculator.BASE_PART_B_PREMIUM + calculator.BASE_PART_D_PREMIUM) * 12
        extra_cost = result.total_annual - standard_annual
        st.warning(f"⚠️ You're paying **{format_currency(extra_cost)}** extra per year due to IRMAA!")

    st.markdown("---")

    # IRMAA bracket comparison chart
    st.subheader("📊 All IRMAA Brackets Comparison")
    bracket_chart = create_irmaa_bracket_chart(calculator, filing_status)
    st.plotly_chart(bracket_chart, use_container_width=True)

    # Show bracket table
    with st.expander("📋 View Detailed Bracket Table"):
        brackets_df = pd.DataFrame(calculator.get_all_brackets_summary(filing_status))
        st.dataframe(brackets_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Multi-year projection
    st.subheader("📈 20-Year Medicare Cost Projection")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("**Projection Assumptions:**")

        inflation_rate = st.slider(
            "Premium Inflation Rate",
            min_value=0.0,
            max_value=0.10,
            value=0.05,
            step=0.01,
            format="%.1f%%",
            help="Historical average: 5-6% per year"
        )

        income_growth = st.slider(
            "Annual Income Growth",
            min_value=-0.05,
            max_value=0.10,
            value=0.02,
            step=0.01,
            format="%.1f%%",
            help="Expected annual change in your income"
        )

    # Generate projections
    current_year = datetime.now().year
    magi_by_year = {}
    for i in range(25):  # 25 years to account for 2-year lookback
        year = current_year + i
        projected_magi = magi * ((1 + income_growth) ** i)
        magi_by_year[year] = projected_magi

    projections = calculator.project_premiums_multi_year(
        starting_year=current_year,
        magi_by_year=magi_by_year,
        filing_status=filing_status,
        inflation_rate=inflation_rate
    )

    # Show projection chart
    with col1:
        projection_chart = create_projection_chart(projections[:20])  # Show 20 years
        st.plotly_chart(projection_chart, use_container_width=True)

    # Summary statistics
    total_20_year = sum(p['total_annual'] for p in projections[:20])
    average_annual = total_20_year / 20

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("20-Year Total Cost", format_large_currency(total_20_year))
    with col2:
        st.metric("Average Annual Cost", format_large_currency(average_annual))
    with col3:
        final_year_cost = projections[19]['total_annual']
        increase_pct = ((final_year_cost / result.total_annual) - 1) * 100
        st.metric("Year 20 Cost", format_large_currency(final_year_cost), f"+{increase_pct:.0f}%")

    st.markdown("---")

    # Roth conversion impact analyzer
    st.subheader("💡 Roth Conversion Impact Analyzer")

    show_roth_conversion_disclaimer()

    st.markdown("""
    **Important:** Roth conversions count as taxable income and can push you into higher
    IRMAA brackets for **2 years** due to Medicare's lookback period.
    """)

    col1, col2 = st.columns([1, 1])

    with col1:
        conversion_amount = st.number_input(
            "Roth Conversion Amount",
            min_value=0,
            max_value=1000000,
            value=50000,
            step=10000,
            help="Amount you're considering converting from Traditional IRA to Roth"
        )

        if st.button("Calculate Conversion Impact", type="primary"):
            impact = calculator.calculate_roth_conversion_impact(
                current_magi=magi,
                conversion_amount=conversion_amount,
                filing_status=filing_status
            )

            st.session_state['conversion_impact'] = impact

    with col2:
        if 'conversion_impact' in st.session_state:
            impact = st.session_state['conversion_impact']

            st.markdown("**Impact Summary:**")

            if impact['bracket_changed']:
                st.error(f"⚠️ **BRACKET CHANGE!** {impact['current_bracket']} → {impact['new_bracket']}")
            else:
                st.success(f"✅ No bracket change (stays in {impact['current_bracket']})")

            st.metric(
                "Medicare Cost Increase",
                format_currency(impact['monthly_increase']) + "/month",
                format_currency(impact['annual_increase']) + "/year"
            )

            st.metric(
                "2-Year Total Impact",
                format_currency(impact['two_year_total_cost']),
                help="Medicare uses 2-year lookback, so IRMAA impact lasts 2 years"
            )

            st.info(f"""
            **New MAGI:** {format_large_currency(impact['new_magi'])}
            **Conversion Amount:** {format_large_currency(impact['conversion_amount'])}
            """)

            # Show comparison chart
            comparison_chart = create_roth_conversion_comparison_chart(impact)
            st.plotly_chart(comparison_chart, use_container_width=True)

            st.warning("""
            ⚠️ **Remember:** This shows ONLY the Medicare impact. You must also consider:
            - Federal and state income taxes on the conversion
            - Effect on Social Security taxation
            - Impact on other benefits (ACA subsidies, etc.)
            - Long-term Roth benefits vs. short-term costs

            **Always consult a tax professional before executing Roth conversions!**
            """)


def main():
    """Main entry point"""
    # Require disclaimer acknowledgment
    require_healthcare_disclaimer_acknowledgment()

    # Show calculator
    show_calculator_page()


if __name__ == "__main__":
    main()
