# visualization/charts_advanced.py - FIXED: Monte Carlo shows percentiles with correct axes
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
from datetime import date


# ============================================================
# HELPER: Register chart data for Claude explanation system
# ============================================================
def register_chart_data(chart_id, title, fig, data_summary):
    """
    Register chart data for Claude explanation system.

    Args:
        chart_id: Unique identifier for this chart
        title: Human-readable title
        fig: Plotly figure object
        data_summary: Dictionary with key metrics/summary data
    """
    if '__chart_registry__' not in st.session_state:
        st.session_state.__chart_registry__ = {}

    # Convert Plotly figure to JSON (this is the KEY step!)
    plotly_json = fig.to_json()

    st.session_state.__chart_registry__[chart_id] = {
        'title': title,
        'data': {
            'plotly_spec': json.loads(plotly_json),  # Full Plotly figure spec
            'summary': data_summary  # Additional context
        }
    }

    print(f"[Chart Registry] Registered: {chart_id} with {len(fig.data)} traces")

def show_sankey(results):
    # Add help button for this chart
    from utils.chart_tooltips import add_chart_help_button
    add_chart_help_button("sankey_diagram")

    st.subheader("💰 Cash Flow Analysis (Sankey Diagram)")
    df = results.get('df', pd.DataFrame())
    if df.empty:
        st.warning("No data for Sankey")
        return
    
    # Use standardized columns with underscores
    total_income = df['Total_Income'].sum()
    total_expenses = df['Total_Expenses'].sum()
    total_taxes = df.get('Taxes_Paid', pd.Series([0])).sum()
    total_savings = df['Savings_End'].iloc[-1] - df['Savings_End'].iloc[0]
    total_rmd = df.get('Total_RMD', pd.Series([0])).sum()
    inheritance_total = df.get('Inheritance_Inflow', pd.Series([0])).sum()
    college_total = df.get('College_Expenses', pd.Series([0])).sum()
    
    labels = ["Primary Income", "RMD Income", "Inheritance", "Total Available", "Taxes", "Living Expenses", "College Expenses", "Net Savings"]
    sources = [0, 1, 2, 3, 3, 3, 3]
    targets = [3, 3, 3, 4, 5, 6, 7]
    values = [total_income, total_rmd, inheritance_total, total_taxes, total_expenses, college_total, max(0, total_savings)]
    
    # Filter out zero values
    filtered_sources = []
    filtered_targets = []
    filtered_values = []
    for i in range(len(values)):
        if values[i] > 0:
            filtered_sources.append(sources[i])
            filtered_targets.append(targets[i])
            filtered_values.append(values[i])
    
    if filtered_values:
        fig = go.Figure(go.Sankey(
            node=dict(
                label=labels,
                pad=15,
                thickness=20
            ),
            link=dict(
                source=filtered_sources,
                target=filtered_targets,
                value=filtered_values
            )
        ))
        fig.update_layout(title="Cash Flow Sankey Diagram", height=500)

        # Register chart data for Claude explanations
        data_summary = {
            "chart_type": "sankey_cash_flow",
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "total_taxes": float(total_taxes),
            "total_savings": float(total_savings),
            "total_rmd": float(total_rmd),
            "inheritance_total": float(inheritance_total),
            "college_total": float(college_total),
            "net_savings_rate": float(total_savings / total_income * 100) if total_income > 0 else 0,
            "major_flows": [
                {"from": "Primary Income", "to": "Total Available", "amount": float(total_income)},
                {"from": "Total Available", "to": "Taxes", "amount": float(total_taxes)},
                {"from": "Total Available", "to": "Living Expenses", "amount": float(total_expenses)},
                {"from": "Total Available", "to": "Net Savings", "amount": float(max(0, total_savings))}
            ]
        }

        register_chart_data(
            chart_id="sankey_cash_flow",
            title="Cash Flow Sankey Diagram",
            fig=fig,
            data_summary=data_summary
        )

        # Inject chart data as JavaScript
        chart_data_json = json.dumps({
            'chart_id': 'sankey_cash_flow',
            'title': 'Cash Flow Sankey Diagram',
            'data_summary': data_summary
        })

        st.components.v1.html(f"""
        <script>
        if (!window.parent.__CHART_DATA_REGISTRY__) {{
            window.parent.__CHART_DATA_REGISTRY__ = {{}};
        }}
        window.parent.__CHART_DATA_REGISTRY__['sankey_cash_flow'] = {chart_data_json};
        console.log('[ChartRegistry] Registered sankey_cash_flow:', window.parent.__CHART_DATA_REGISTRY__['sankey_cash_flow']);
        </script>
        """, height=0)

        st.plotly_chart(fig, use_container_width=True, key="sankey_chart")
    else:
        st.info("Insufficient data for Sankey diagram")

def show_monte_carlo(results):
    """
    FIXED: Display Monte Carlo simulation with percentile bands instead of all paths
    Shows 10th, 50th (median), and 90th percentiles with proper year labels
    """
    # Add help button for this chart
    from utils.chart_tooltips import add_chart_help_button
    add_chart_help_button("monte_carlo_simulation")

    st.subheader("🎲 Monte Carlo Simulation Analysis")
    
    if 'monte_carlo_results' not in results:
        st.warning("No Monte Carlo data available. Enable Monte Carlo in simulation parameters.")
        return
    
    mc_results = results['monte_carlo_results']
    mc_df = mc_results.get('mc_df')
    success_rate = mc_results.get('success_rate', 0)
    
    if mc_df is None or mc_df.empty:
        st.warning("Monte Carlo simulation produced no data")
        return
    
    # Get dimensions
    num_years = len(mc_df)
    num_iterations = len(mc_df.columns)
    
    # CRITICAL FIX: Create proper year labels (not iteration indices)
    start_year = date.today().year
    years = list(range(start_year, start_year + num_years))
    
    # Calculate percentiles across all simulations for each year
    percentile_10 = []
    percentile_50 = []  # Median
    percentile_90 = []
    
    for year_idx in range(num_years):
        # Get all simulation values for this year
        year_values = mc_df.iloc[year_idx].values
        
        # Calculate percentiles
        percentile_10.append(np.percentile(year_values, 10))
        percentile_50.append(np.percentile(year_values, 50))
        percentile_90.append(np.percentile(year_values, 90))
    
    # Create figure with percentile bands
    fig = go.Figure()
    
    # Add 90th percentile (optimistic scenario)
    fig.add_trace(go.Scatter(
        x=years,
        y=percentile_90,
        mode='lines',
        name='90th Percentile (Optimistic)',
        line=dict(color='lightgreen', width=2),
        fill=None
    ))
    
    # Add 50th percentile (median/expected scenario)
    fig.add_trace(go.Scatter(
        x=years,
        y=percentile_50,
        mode='lines',
        name='50th Percentile (Median)',
        line=dict(color='blue', width=3),
        fill='tonexty',  # Fill area between this and previous trace
        fillcolor='rgba(144, 238, 144, 0.2)'
    ))
    
    # Add 10th percentile (pessimistic scenario)
    fig.add_trace(go.Scatter(
        x=years,
        y=percentile_10,
        mode='lines',
        name='10th Percentile (Pessimistic)',
        line=dict(color='lightcoral', width=2),
        fill='tonexty',  # Fill area between this and previous trace
        fillcolor='rgba(173, 216, 230, 0.2)'
    ))
    
    # Update layout with proper labels
    fig.update_layout(
        title=f"Monte Carlo Simulation: {num_iterations} Scenarios Analyzed",
        xaxis_title="Year",
        yaxis_title="Projected Savings ($)",
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickformat="$,.0f")

    # Register chart data for Claude explanations
    data_summary = {
        "chart_type": "monte_carlo_simulation",
        "num_iterations": int(num_iterations),
        "num_years": int(num_years),
        "start_year": int(years[0]),
        "end_year": int(years[-1]),
        "success_rate": float(success_rate),
        "median_final_savings": float(percentile_50[-1]),
        "optimistic_final_savings": float(percentile_90[-1]),
        "pessimistic_final_savings": float(percentile_10[-1]),
        "probability_positive": float((mc_df.iloc[-1].values > 0).sum() / num_iterations * 100),
        "probability_above_1m": float((mc_df.iloc[-1].values > 1_000_000).sum() / num_iterations * 100),
        "probability_above_5m": float((mc_df.iloc[-1].values > 5_000_000).sum() / num_iterations * 100),
    }

    register_chart_data(
        chart_id="monte_carlo_simulation",
        title=f"Monte Carlo Simulation: {num_iterations} Scenarios",
        fig=fig,
        data_summary=data_summary
    )

    # Inject chart data as JavaScript
    chart_data_json = json.dumps({
        'chart_id': 'monte_carlo_simulation',
        'title': f"Monte Carlo Simulation: {num_iterations} Scenarios",
        'data_summary': data_summary
    })

    st.components.v1.html(f"""
    <script>
    if (!window.parent.__CHART_DATA_REGISTRY__) {{
        window.parent.__CHART_DATA_REGISTRY__ = {{}};
    }}
    window.parent.__CHART_DATA_REGISTRY__['monte_carlo_simulation'] = {chart_data_json};
    console.log('[ChartRegistry] Registered monte_carlo_simulation:', window.parent.__CHART_DATA_REGISTRY__['monte_carlo_simulation']);
    </script>
    """, height=0)

    st.plotly_chart(fig, use_container_width=True, key="monte_carlo_chart")
    
    # Display key statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            help="Percentage of scenarios where savings remain positive"
        )
    
    with col2:
        final_median = percentile_50[-1]
        st.metric(
            "Median Final Savings",
            f"${final_median:,.0f}",
            help="Expected outcome (50th percentile)"
        )
    
    with col3:
        final_optimistic = percentile_90[-1]
        st.metric(
            "Optimistic Outcome",
            f"${final_optimistic:,.0f}",
            help="90th percentile scenario"
        )
    
    with col4:
        final_pessimistic = percentile_10[-1]
        st.metric(
            "Pessimistic Outcome",
            f"${final_pessimistic:,.0f}",
            help="10th percentile scenario"
        )
    
    # Additional analysis
    with st.expander("📊 Detailed Monte Carlo Analysis"):
        st.write(f"**Simulation Parameters:**")
        st.write(f"- Number of scenarios simulated: {num_iterations:,}")
        st.write(f"- Time horizon: {num_years} years ({years[0]} - {years[-1]})")
        st.write(f"- Success rate: {success_rate:.1f}% of scenarios remain solvent")
        
        st.write(f"\n**Outcome Distribution:**")
        st.write(f"- Best case (90th percentile): ${percentile_90[-1]:,.0f}")
        st.write(f"- Expected (median): ${percentile_50[-1]:,.0f}")
        st.write(f"- Worst case (10th percentile): ${percentile_10[-1]:,.0f}")
        st.write(f"- Range: ${percentile_90[-1] - percentile_10[-1]:,.0f}")
        
        # Calculate probability of achieving certain thresholds
        final_values = mc_df.iloc[-1].values
        prob_positive = (final_values > 0).sum() / num_iterations * 100
        prob_1m = (final_values > 1_000_000).sum() / num_iterations * 100
        prob_5m = (final_values > 5_000_000).sum() / num_iterations * 100
        
        st.write(f"\n**Probability of Outcomes:**")
        st.write(f"- Remaining solvent (>$0): {prob_positive:.1f}%")
        st.write(f"- Savings above $1M: {prob_1m:.1f}%")
        st.write(f"- Savings above $5M: {prob_5m:.1f}%")
        
        # Show year-by-year percentile data
        st.write(f"\n**Year-by-Year Percentile Analysis:**")
        analysis_df = pd.DataFrame({
            'Year': years,
            '10th Percentile': [f"${x:,.0f}" for x in percentile_10],
            'Median (50th)': [f"${x:,.0f}" for x in percentile_50],
            '90th Percentile': [f"${x:,.0f}" for x in percentile_90]
        })
        st.dataframe(analysis_df, use_container_width=True)