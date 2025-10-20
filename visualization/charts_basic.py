# charts_basic.py - FIXED: Proper data registration for Claude chart explanations
# This version sends the FULL Plotly figure spec to Claude so it can analyze actual data

import streamlit as st
import plotly.graph_objects as go
import json
from financial_utils import display_health_dashboard


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


# ============================================================
# FIXED: show_trajectories with data registration
# ============================================================
def show_trajectories(results):
    st.subheader("📈 Financial Trajectories")
    if 'df' not in results or results['df'].empty:
        st.warning("No data for trajectories")
        return

    df = results['df']

    # DEBUG: Show data summary to diagnose flat line issue
    with st.expander("🔍 Debug: Data Summary (click to expand)", expanded=False):
        st.write(f"**Years**: {df['Year'].min()} to {df['Year'].max()}")
        st.write(f"**Savings Range**: ${df['Savings_End'].min():,.0f} to ${df['Savings_End'].max():,.0f}")
        st.write(f"**Net Worth Range**: ${df['Net_Worth'].min():,.0f} to ${df['Net_Worth'].max():,.0f}")
        st.write(f"**Income Range**: ${df['Total_Income'].min():,.0f} to ${df['Total_Income'].max():,.0f}")
        st.write(f"**Expenses Range**: ${df['Total_Expenses'].min():,.0f} to ${df['Total_Expenses'].max():,.0f}")
        st.write("**First 3 rows:**")
        st.dataframe(df[['Year', 'Savings_End', 'Net_Worth', 'Total_Income', 'Total_Expenses']].head(3))
        st.write("**Last 3 rows:**")
        st.dataframe(df[['Year', 'Savings_End', 'Net_Worth', 'Total_Income', 'Total_Expenses']].tail(3))

    # Build the Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Savings_End'], mode='lines', name='Savings'))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Net_Worth'], mode='lines', name='Net Worth'))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Total_Income'], mode='lines', name='Income'))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Total_Expenses'], mode='lines', name='Expenses'))
    
    fig.update_layout(
        title="Financial Projections",
        xaxis_title="Year",
        yaxis_title="Amount ($)",
        hovermode='x unified'
    )
    
    # CRITICAL: Register the chart data for Claude
    data_summary = {
        "start_year": int(df['Year'].min()),
        "end_year": int(df['Year'].max()),
        "starting_savings": float(df['Savings_End'].iloc[0]),
        "ending_savings": float(df['Savings_End'].iloc[-1]),
        "peak_savings": float(df['Savings_End'].max()),
        "peak_savings_year": int(df.loc[df['Savings_End'].idxmax(), 'Year']),
        "starting_net_worth": float(df['Net_Worth'].iloc[0]),
        "ending_net_worth": float(df['Net_Worth'].iloc[-1]),
        "avg_annual_income": float(df['Total_Income'].mean()),
        "avg_annual_expenses": float(df['Total_Expenses'].mean()),
    }
    
    register_chart_data(
        chart_id="financial_trajectories",
        title="Financial Projections",
        fig=fig,
        data_summary=data_summary
    )

    # Inject chart data as JavaScript for the explain system to access
    import json
    chart_data_json = json.dumps({
        'chart_id': 'financial_trajectories',
        'title': 'Financial Projections',
        'data_summary': data_summary
    })

    st.components.v1.html(f"""
    <script>
    if (!window.parent.__CHART_DATA_REGISTRY__) {{
        window.parent.__CHART_DATA_REGISTRY__ = {{}};
    }}
    window.parent.__CHART_DATA_REGISTRY__['financial_trajectories'] = {chart_data_json};
    console.log('[ChartRegistry] Registered financial_trajectories:', window.parent.__CHART_DATA_REGISTRY__['financial_trajectories']);
    </script>
    """, height=0)

    # Display the chart
    st.plotly_chart(fig, use_container_width=True, key="financial_trajectories_chart")


# ============================================================
# show_health_dashboard (no changes needed)
# ============================================================
def show_health_dashboard(liquid_assets, total_expenses, total_income, total_liabilities, results):
    emergency_months = liquid_assets / total_expenses if total_expenses > 0 else 0
    dti = total_liabilities / total_income if total_income > 0 else 0
    savings_rate = (total_income - total_expenses) / total_income if total_income > 0 else 0
    health_score = results['health_score']
    
    display_health_dashboard(emergency_months, dti, savings_rate, health_score)