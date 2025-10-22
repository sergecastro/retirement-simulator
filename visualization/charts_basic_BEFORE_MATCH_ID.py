# charts_basic.py - Updated for hidden div approach
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from financial_utils import display_health_dashboard
from streamlit_explain_api import plotly_chart_with_explain  # Import the new function

def show_trajectories(results):
    st.subheader("📈 Financial Trajectories")
    if 'df' not in results or results['df'].empty:
        st.warning("No data for trajectories")
        return
    
    df = results['df']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Savings_End'], mode='lines', name='Savings'))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Net_Worth'], mode='lines', name='Net Worth'))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Total_Income'], mode='lines', name='Income'))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Total_Expenses'], mode='lines', name='Expenses'))
    
    fig.update_layout(title="Financial Projections", xaxis_title="Year", yaxis_title="Amount ($)")
    
    # Extract data summary for explanation
    data_summary = {
        'years': df['Year'].tolist(),
        'savings': df['Savings_End'].tolist(),
        'net_worth': df['Net_Worth'].tolist(),
        'income': df['Total_Income'].tolist(),
        'expenses': df['Total_Expenses'].tolist()
    }
    
    # Use the new function instead of st.plotly_chart
    plotly_chart_with_explain(
        fig=fig,
        chart_id="financial_trajectories",
        title="Financial Trajectories",
        data_summary=data_summary
    )

def show_health_dashboard(liquid_assets, total_expenses, total_income, total_liabilities, results):
    # Calculate args for display_health_dashboard (4 args)
    emergency_months = liquid_assets / total_expenses if total_expenses > 0 else 0
    dti = total_liabilities / total_income if total_income > 0 else 0
    savings_rate = (total_income - total_expenses) / total_income if total_income > 0 else 0
    health_score = results['health_score']
    
    display_health_dashboard(emergency_months, dti, savings_rate, health_score)