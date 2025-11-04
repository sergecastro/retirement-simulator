"""
Medicare Charts & Visualizations
=================================
Comprehensive charting library for Medicare cost visualizations including
IRMAA brackets, multi-year projections, state comparisons, and scenario analysis.

Author: Family Forecast Development Team
Last Updated: October 22, 2025
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict
import streamlit as st


# =============================================================================
# COLOR SCHEMES
# =============================================================================

IRMAA_COLORS = {
    "standard": "#2E7D32",      # Green - no IRMAA
    "bracket_1": "#558B2F",     # Light green
    "bracket_2": "#FFA726",     # Orange
    "bracket_3": "#F57C00",     # Dark orange
    "bracket_4": "#E53935",     # Red
    "bracket_5": "#B71C1C",     # Dark red
}

CHART_COLORS = {
    "primary": "#1976D2",
    "secondary": "#424242",
    "success": "#2E7D32",
    "warning": "#F57C00",
    "danger": "#E53935",
    "info": "#0288D1",
}


# =============================================================================
# IRMAA BRACKET VISUALIZATIONS
# =============================================================================

def create_irmaa_waterfall_chart(current_premium, standard_premium, breakdown):
    """
    Create waterfall chart showing premium buildup from standard to IRMAA-adjusted

    Args:
        current_premium: Total current premium
        standard_premium: Standard premium without IRMAA
        breakdown: Dictionary with part_b_surcharge and part_d_surcharge

    Returns:
        plotly figure
    """
    fig = go.Figure(go.Waterfall(
        name="Premium Breakdown",
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Standard<br>Premium", "Part B<br>IRMAA", "Part D<br>IRMAA", "Total<br>Cost"],
        textposition="outside",
        text=[
            f"${standard_premium:.2f}",
            f"+${breakdown['part_b_surcharge']:.2f}",
            f"+${breakdown['part_d_surcharge']:.2f}",
            f"${current_premium:.2f}"
        ],
        y=[
            standard_premium,
            breakdown['part_b_surcharge'],
            breakdown['part_d_surcharge'],
            0
        ],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": CHART_COLORS["danger"]}},
        increasing={"marker": {"color": CHART_COLORS["warning"]}},
        totals={"marker": {"color": CHART_COLORS["primary"]}}
    ))

    fig.update_layout(
        title="How IRMAA Increases Your Medicare Premiums",
        yaxis_title="Monthly Premium ($)",
        showlegend=False,
        height=400
    )

    return fig


def create_irmaa_bracket_heatmap(calculator, filing_status="single"):
    """
    Create heatmap showing IRMAA costs across income levels

    Args:
        calculator: MedicareIRMAACalculator instance
        filing_status: "single" or "married"

    Returns:
        plotly figure
    """
    # Generate income range
    if filing_status == "single":
        income_range = list(range(50000, 600001, 25000))
    else:
        income_range = list(range(100000, 800001, 50000))

    # Calculate premiums for each income level
    data = []
    for income in income_range:
        result = calculator.calculate_premiums(income, filing_status)
        data.append({
            "Income": f"${income:,}",
            "Monthly": result.total_monthly,
            "Annual": result.total_annual,
            "Bracket": result.irmaa_bracket
        })

    df = pd.DataFrame(data)

    # Create heatmap
    fig = px.bar(
        df,
        x="Income",
        y="Annual",
        color="Annual",
        color_continuous_scale="RdYlGn_r",
        text="Annual",
        hover_data={"Bracket": True, "Monthly": True},
        labels={"Annual": "Annual Cost ($)", "Income": "MAGI"}
    )

    fig.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    )

    fig.update_layout(
        title=f"Medicare Costs Across Income Levels ({filing_status.title()})",
        xaxis_title="Modified Adjusted Gross Income (MAGI)",
        yaxis_title="Annual Medicare Cost",
        height=500,
        showlegend=False
    )

    return fig


def create_bracket_threshold_chart(calculator, filing_status="single"):
    """
    Create chart highlighting IRMAA bracket thresholds (the "cliffs")

    Args:
        calculator: MedicareIRMAACalculator instance
        filing_status: "single" or "married"

    Returns:
        plotly figure
    """
    brackets = calculator.IRMAA_BRACKETS_2025

    # Prepare data
    thresholds = []
    premiums = []
    colors = []

    for i, bracket in enumerate(brackets[:-1]):  # Exclude last (infinite) bracket
        if filing_status == "single":
            threshold = bracket.single_max
        else:
            threshold = bracket.married_max

        # Calculate premium at this threshold
        result = calculator.calculate_premiums(threshold, filing_status)

        thresholds.append(f"${threshold:,}")
        premiums.append(result.total_monthly)
        colors.append(list(IRMAA_COLORS.values())[i])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=thresholds,
        y=premiums,
        mode='lines+markers',
        marker=dict(
            size=12,
            color=colors,
            line=dict(width=2, color='white')
        ),
        line=dict(color='gray', width=2, dash='dash'),
        text=[f"${p:.2f}/mo" for p in premiums],
        textposition="top center",
        hovertemplate='Income Threshold: %{x}<br>Monthly Premium: $%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=f"IRMAA Bracket Thresholds - The Premium 'Cliffs' ({filing_status.title()})",
        xaxis_title="Income Threshold",
        yaxis_title="Monthly Medicare Premium",
        height=450,
        showlegend=False,
        annotations=[
            dict(
                x=0.5,
                y=-0.15,
                xref='paper',
                yref='paper',
                text="⚠️ Small income increases at thresholds can cause large premium jumps!",
                showarrow=False,
                font=dict(size=12, color="red")
            )
        ]
    )

    return fig


# =============================================================================
# MULTI-YEAR PROJECTIONS
# =============================================================================

def create_stacked_area_projection(projections):
    """
    Create stacked area chart showing base premium vs IRMAA surcharge over time

    Args:
        projections: List of projection dictionaries from calculator

    Returns:
        plotly figure
    """
    df = pd.DataFrame(projections)

    fig = go.Figure()

    # Base premium (Part B + Part D)
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['base_part_b'] + df['total_part_d'] - df['part_d_surcharge'],
        mode='lines',
        name='Base Premium',
        fill='tozeroy',
        line=dict(color=CHART_COLORS["success"], width=2),
        hovertemplate='Year: %{x}<br>Base Premium: $%{y:,.2f}<extra></extra>'
    ))

    # IRMAA surcharges
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['part_b_surcharge'] + df['part_d_surcharge'],
        mode='lines',
        name='IRMAA Surcharge',
        fill='tonexty',
        line=dict(color=CHART_COLORS["danger"], width=2),
        hovertemplate='Year: %{x}<br>IRMAA Surcharge: $%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title="Medicare Cost Breakdown Over Time",
        xaxis_title="Year",
        yaxis_title="Annual Cost ($)",
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_cumulative_cost_chart(projections):
    """
    Create chart showing cumulative Medicare costs over time

    Args:
        projections: List of projection dictionaries

    Returns:
        plotly figure
    """
    df = pd.DataFrame(projections)
    df['cumulative_cost'] = df['total_annual'].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['cumulative_cost'],
        mode='lines',
        fill='tozeroy',
        line=dict(color=CHART_COLORS["primary"], width=3),
        hovertemplate='Year: %{x}<br>Total Spent: $%{y:,.0f}<extra></extra>'
    ))

    # Add milestone markers
    milestones = [100000, 200000, 300000, 400000, 500000]
    for milestone in milestones:
        milestone_year = df[df['cumulative_cost'] >= milestone].iloc[0] if len(df[df['cumulative_cost'] >= milestone]) > 0 else None
        if milestone_year is not None:
            fig.add_annotation(
                x=milestone_year['year'],
                y=milestone_year['cumulative_cost'],
                text=f"${milestone:,}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=CHART_COLORS["warning"],
                ax=-40,
                ay=-40
            )

    fig.update_layout(
        title="Cumulative Medicare Costs Over Retirement",
        xaxis_title="Year",
        yaxis_title="Total Medicare Costs Paid ($)",
        height=450
    )

    return fig


def create_year_over_year_change_chart(projections):
    """
    Create chart showing year-over-year cost changes

    Args:
        projections: List of projection dictionaries

    Returns:
        plotly figure
    """
    df = pd.DataFrame(projections)
    df['yoy_change'] = df['total_annual'].pct_change() * 100
    df['yoy_dollar_change'] = df['total_annual'].diff()

    fig = go.Figure()

    # Bar chart of dollar changes
    colors = [CHART_COLORS["success"] if x < 5 else CHART_COLORS["warning"] if x < 10 else CHART_COLORS["danger"]
              for x in df['yoy_change'].fillna(0)]

    fig.add_trace(go.Bar(
        x=df['year'][1:],  # Skip first year (no comparison)
        y=df['yoy_dollar_change'][1:],
        marker_color=colors[1:],
        text=[f"${x:,.0f}" for x in df['yoy_dollar_change'][1:]],
        textposition='outside',
        hovertemplate='Year: %{x}<br>Increase: $%{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title="Year-Over-Year Medicare Cost Increases",
        xaxis_title="Year",
        yaxis_title="Annual Increase ($)",
        height=400,
        showlegend=False
    )

    return fig


# =============================================================================
# ROTH CONVERSION ANALYSIS
# =============================================================================

def create_roth_conversion_multi_scenario_chart(calculator, current_magi, filing_status, conversion_amounts):
    """
    Create chart comparing multiple Roth conversion scenarios

    Args:
        calculator: MedicareIRMAACalculator instance
        current_magi: Current MAGI without conversion
        filing_status: "single" or "married"
        conversion_amounts: List of conversion amounts to compare

    Returns:
        plotly figure
    """
    scenarios = []

    for amount in conversion_amounts:
        impact = calculator.calculate_roth_conversion_impact(
            current_magi=current_magi,
            conversion_amount=amount,
            filing_status=filing_status
        )
        scenarios.append({
            "Conversion": f"${amount:,}",
            "2-Year Cost": impact['two_year_total_cost'],
            "New Bracket": impact['new_bracket'],
            "Bracket Changed": impact['bracket_changed']
        })

    df = pd.DataFrame(scenarios)

    fig = go.Figure()

    colors = [CHART_COLORS["danger"] if x else CHART_COLORS["success"] for x in df["Bracket Changed"]]

    fig.add_trace(go.Bar(
        x=df["Conversion"],
        y=df["2-Year Cost"],
        marker_color=colors,
        text=[f"${x:,.0f}" for x in df["2-Year Cost"]],
        textposition='outside',
        hovertemplate='Conversion: %{x}<br>2-Year Medicare Cost: $%{y:,.0f}<br>Bracket: %{customdata}<extra></extra>',
        customdata=df["New Bracket"]
    ))

    fig.update_layout(
        title="Medicare Impact of Different Roth Conversion Amounts",
        xaxis_title="Roth Conversion Amount",
        yaxis_title="2-Year Medicare Cost Increase ($)",
        height=450,
        showlegend=False
    )

    return fig


def create_conversion_breakeven_chart(calculator, current_magi, filing_status, max_conversion=200000):
    """
    Create chart showing Medicare cost vs conversion amount (find sweet spots)

    Args:
        calculator: MedicareIRMAACalculator instance
        current_magi: Current MAGI
        filing_status: "single" or "married"
        max_conversion: Maximum conversion to analyze

    Returns:
        plotly figure
    """
    conversion_amounts = list(range(0, max_conversion + 1, 10000))
    costs = []
    brackets = []

    for amount in conversion_amounts:
        impact = calculator.calculate_roth_conversion_impact(
            current_magi=current_magi,
            conversion_amount=amount,
            filing_status=filing_status
        )
        costs.append(impact['two_year_total_cost'])
        brackets.append(impact['new_bracket'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=conversion_amounts,
        y=costs,
        mode='lines+markers',
        line=dict(color=CHART_COLORS["primary"], width=3),
        marker=dict(size=6),
        hovertemplate='Conversion: $%{x:,}<br>2-Yr Medicare Cost: $%{y:,}<extra></extra>'
    ))

    # Highlight bracket changes (the "cliffs")
    for i in range(1, len(brackets)):
        if brackets[i] != brackets[i-1]:
            fig.add_vline(
                x=conversion_amounts[i],
                line_dash="dash",
                line_color="red",
                annotation_text=f"Bracket Change",
                annotation_position="top"
            )

    fig.update_layout(
        title="Find the Sweet Spots: Medicare Cost vs Roth Conversion Amount",
        xaxis_title="Roth Conversion Amount ($)",
        yaxis_title="2-Year Medicare Cost Increase ($)",
        height=500,
        annotations=[
            dict(
                x=0.5,
                y=-0.15,
                xref='paper',
                yref='paper',
                text="⚠️ Vertical jumps = IRMAA bracket changes. Convert just below to maximize efficiency!",
                showarrow=False,
                font=dict(size=11, color="red")
            )
        ]
    )

    return fig


# =============================================================================
# STATE COMPARISON CHARTS
# =============================================================================

def create_state_comparison_chart(states_data):
    """
    Create comparison chart of Medicare costs across states

    Args:
        states_data: List of dicts with state, part_d_premium, medigap_premium

    Returns:
        plotly figure
    """
    df = pd.DataFrame(states_data)

    fig = go.Figure()

    # Part D premiums
    fig.add_trace(go.Bar(
        name='Part D Premium',
        x=df['state'],
        y=df['part_d_premium'],
        marker_color=CHART_COLORS["info"],
        text=[f"${x:.0f}" for x in df['part_d_premium']],
        textposition='auto'
    ))

    # Medigap premiums
    fig.add_trace(go.Bar(
        name='Medigap Plan G',
        x=df['state'],
        y=df['medigap_premium'],
        marker_color=CHART_COLORS["secondary"],
        text=[f"${x:.0f}" for x in df['medigap_premium']],
        textposition='auto'
    ))

    fig.update_layout(
        title="Medicare Supplemental Costs by State",
        xaxis_title="State",
        yaxis_title="Monthly Premium ($)",
        barmode='group',
        height=450,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


# =============================================================================
# SUMMARY DASHBOARD CHARTS
# =============================================================================

def create_medicare_cost_gauge(current_cost, max_cost=10000):
    """
    Create gauge chart showing current Medicare costs vs typical range

    Args:
        current_cost: Current annual cost
        max_cost: Maximum for gauge scale

    Returns:
        plotly figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_cost,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Annual Medicare Cost"},
        delta={'reference': 3000, 'suffix': " vs Standard"},
        gauge={
            'axis': {'range': [None, max_cost]},
            'bar': {'color': CHART_COLORS["primary"]},
            'steps': [
                {'range': [0, 3000], 'color': CHART_COLORS["success"]},
                {'range': [3000, 6000], 'color': CHART_COLORS["warning"]},
                {'range': [6000, max_cost], 'color': CHART_COLORS["danger"]}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 8000
            }
        }
    ))

    fig.update_layout(height=300)

    return fig


def create_cost_breakdown_pie(result):
    """
    Create pie chart of Medicare cost breakdown

    Args:
        result: MedicarePremiun object from calculator

    Returns:
        plotly figure
    """
    labels = ['Part B Base', 'Part B IRMAA', 'Part D Base', 'Part D IRMAA']
    values = [
        result.base_part_b * 12,
        result.part_b_surcharge * 12,
        result.base_part_d * 12,
        result.part_d_surcharge * 12
    ]

    colors = [CHART_COLORS["success"], CHART_COLORS["danger"],
              CHART_COLORS["info"], CHART_COLORS["warning"]]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent',
        hovertemplate='%{label}<br>$%{value:,.0f}/year<br>%{percent}<extra></extra>'
    )])

    fig.update_layout(
        title="Annual Medicare Cost Breakdown",
        height=400
    )

    return fig


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("✅ MEDICARE CHARTS MODULE")
    print("=" * 70)
    print("\nChart Functions Available:")
    print("  📊 IRMAA bracket visualizations (waterfall, heatmap, thresholds)")
    print("  📈 Multi-year projections (stacked area, cumulative, YoY changes)")
    print("  💡 Roth conversion analysis (multi-scenario, breakeven finder)")
    print("  🗺️  State comparisons")
    print("  📊 Summary dashboards (gauges, pie charts)")
    print("\n✅ Ready for integration!")
    print("=" * 70)
