# visualization.py - Visualization Components
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

def display_key_metrics(results, sim_years):
    """Display key performance metrics"""
    st.header("📊 Key Performance Metrics")
    
    final_savings = results.get('final_savings', 0)
    final_net_worth = results.get('final_net_worth', final_savings)
    years_positive = results.get('years_solvent', results.get('years_positive', 0))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Final Savings", f"${final_savings:,.0f}")
    with col2:
        st.metric("Final Net Worth", f"${final_net_worth:,.0f}")
    with col3:
        st.metric("Years Solvent", f"{years_positive}/{sim_years}")
    with col4:
        success_rate = (years_positive / sim_years) * 100 if sim_years > 0 else 0
        st.metric("Success Rate", f"{success_rate:.0f}%")

def show_trajectories(results):
    """Show main financial trajectories"""
    st.subheader("📈 Financial Trajectories")
    
    df = results.get('df', pd.DataFrame())
    if df.empty:
        st.warning("No trajectory data available")
        return
    
    # Create multi-line chart
    fig = go.Figure()
    
    # Fix: Get actual data arrays, not just column names
    if 'Year' in df.columns:
        year_data = df['Year']
    else:
        year_data = df.index
    
    # Try different column names for compatibility
    savings_col = next((col for col in ['Savings End', 'Savings', 'Balance'] if col in df.columns), None)
    income_col = next((col for col in ['Total Income', 'Income'] if col in df.columns), None)
    expense_col = next((col for col in ['Total Expenses', 'Expenses'] if col in df.columns), None)
    
    if savings_col:
        fig.add_trace(go.Scatter(
            x=year_data, y=df[savings_col],
            mode='lines', name='Savings Balance',
            line=dict(color='blue', width=3)
        ))
    
    if income_col:
        fig.add_trace(go.Scatter(
            x=year_data, y=df[income_col],
            mode='lines', name='Annual Income',
            line=dict(color='green', width=2)
        ))
    
    if expense_col:
        fig.add_trace(go.Scatter(
            x=year_data, y=df[expense_col],
            mode='lines', name='Annual Expenses',
            line=dict(color='red', width=2, dash='dash')
        ))
    
    # Add net worth if available
    if 'Net Worth' in df.columns:
        fig.add_trace(go.Scatter(
            x=year_data, y=df['Net Worth'],
            mode='lines', name='Net Worth',
            line=dict(color='purple', width=2),
            yaxis='y2'
        ))
    
    fig.update_layout(
        title="Comprehensive Financial Trajectory",
        xaxis_title="Year",
        yaxis_title="Amount ($)",
        yaxis2=dict(title='Net Worth ($)', overlaying='y', side='right'),
        hovermode='x unified',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show data table
    with st.expander("📊 View Detailed Data"):
        st.dataframe(df.style.format("{:,.0f}"))

def show_monte_carlo(results):
    """Display Monte Carlo simulation results"""
    st.subheader("🎲 Monte Carlo Probability Analysis")
    
    mc_results = results.get('monte_carlo_results', {})
    if not mc_results:
        st.info("Monte Carlo simulation not run. Enable it in parameters.")
        return
    
    # Get Monte Carlo data
    mc_df = mc_results.get('mc_df', pd.DataFrame())
    success_rate = mc_results.get('success_rate', 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Success rate gauge
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = success_rate,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Success Probability (%)"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Final balance distribution
        if 'final_balances' in mc_results:
            final_balances = mc_results['final_balances']
        elif not mc_df.empty:
            final_balances = mc_df.iloc[-1].values
        else:
            final_balances = []
        
        if len(final_balances) > 0:
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=final_balances,
                nbinsx=50,
                name='Final Balance Distribution',
                marker_color='royalblue'
            ))
            fig_hist.update_layout(
                title="Final Balance Distribution",
                xaxis_title="Final Balance ($)",
                yaxis_title="Frequency",
                height=300
            )
            st.plotly_chart(fig_hist, use_container_width=True)
    
    # Fan chart
    if not mc_df.empty and len(mc_df.columns) > 1:
        st.markdown("**Monte Carlo Projection Fan Chart**")
        
        # Calculate percentiles
        try:
            p10 = mc_df.quantile(0.1, axis=0)
            p25 = mc_df.quantile(0.25, axis=0)
            p50 = mc_df.quantile(0.5, axis=0)
            p75 = mc_df.quantile(0.75, axis=0)
            p90 = mc_df.quantile(0.9, axis=0)
            
            fig_fan = go.Figure()
            
            # Add confidence bands
            fig_fan.add_trace(go.Scatter(
                x=list(mc_df.columns), y=p90,
                fill=None, mode='lines', line_color='rgba(0,100,80,0)',
                showlegend=False
            ))
            fig_fan.add_trace(go.Scatter(
                x=list(mc_df.columns), y=p10,
                fill='tonexty', mode='lines', line_color='rgba(0,100,80,0)',
                name='80% Confidence Interval',
                fillcolor='rgba(0,100,80,0.2)'
            ))
            fig_fan.add_trace(go.Scatter(
                x=list(mc_df.columns), y=p75,
                fill=None, mode='lines', line_color='rgba(0,100,80,0)',
                showlegend=False
            ))
            fig_fan.add_trace(go.Scatter(
                x=list(mc_df.columns), y=p25,
                fill='tonexty', mode='lines', line_color='rgba(0,100,80,0)',
                name='50% Confidence Interval',
                fillcolor='rgba(0,100,80,0.3)'
            ))
            fig_fan.add_trace(go.Scatter(
                x=list(mc_df.columns), y=p50,
                mode='lines', name='Median Outcome',
                line=dict(color='royalblue', width=3)
            ))
            
            fig_fan.update_layout(
                title="Monte Carlo Confidence Intervals",
                xaxis_title="Year",
                yaxis_title="Savings Balance ($)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_fan, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create fan chart: {str(e)}")

def show_sankey(results):
    """Display cash flow Sankey diagram"""
    st.subheader("💰 Cash Flow Analysis (Sankey Diagram)")
    
    # Get income and expense data
    total_income = sum(results.get('total_incomes', [results.get('annual_income', 0) * 10]))
    total_expenses = sum(results.get('total_expenses_list', [results.get('annual_expenses', 0) * 10]))
    total_taxes = total_income * 0.22  # Estimate
    total_savings = total_income - total_expenses - total_taxes
    
    # Ensure non-negative values
    total_income = max(0, total_income)
    total_expenses = max(0, total_expenses) 
    total_taxes = max(0, total_taxes)
    total_savings = max(0, total_savings)
    
    # Create Sankey
    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = ["Income", "Taxes", "Expenses", "Savings", "Investments"],
            color = ["green", "red", "orange", "blue", "purple"]
        ),
        link = dict(
            source = [0, 0, 0, 3],
            target = [1, 2, 3, 4],
            value = [total_taxes, total_expenses, total_savings, total_savings * 0.8]
        )
    )])
    
    fig.update_layout(title="Lifetime Cash Flow Visualization", height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_goal_gauges(results):
    """Display goal achievement gauges"""
    st.subheader("🎯 Goal Achievement Analysis")
    
    goals = results.get('goal_achievement', {})
    if not goals:
        st.info("No goals defined. Add goals in the input section.")
        return
    
    cols = st.columns(min(3, len(goals)))
    for idx, (goal_name, goal_data) in enumerate(goals.items()):
        if idx >= 3:
            break
        
        target = goal_data.get('target', 100000)
        actual = goal_data.get('actual', results.get('final_savings', 0))
        achieved = actual / target * 100 if target > 0 else 0
        
        with cols[idx]:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = achieved,
                title = {'text': goal_name},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 150]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 100], 'color': "yellow"},
                        {'range': [100, 150], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 100
                    }
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

def show_health_dashboard(results, financial_data):
    """Display financial health metrics"""
    st.subheader("🏥 Financial Health Dashboard")
    
    # Calculate health metrics
    emergency_months = financial_data['liquid_assets'] / (financial_data['total_expenses'] * 12) * 12 if financial_data['total_expenses'] > 0 else 0
    debt_to_income = financial_data['total_liabilities'] / (financial_data['total_income'] * 12) if financial_data['total_income'] > 0 else 0
    savings_rate = financial_data['monthly_surplus'] / financial_data['total_income'] if financial_data['total_income'] > 0 else 0
    
    # Calculate health score
    health_score = 0
    if emergency_months >= 6: health_score += 30
    elif emergency_months >= 3: health_score += 20
    if debt_to_income <= 0.36: health_score += 30
    elif debt_to_income <= 0.5: health_score += 20
    if savings_rate >= 0.2: health_score += 20
    elif savings_rate >= 0.1: health_score += 10
    if results.get('final_savings', 0) > 0: health_score += 20
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Emergency Fund", f"{emergency_months:.1f} months")
    with col2:
        st.metric("Debt-to-Income", f"{debt_to_income:.1%}")
    with col3:
        st.metric("Savings Rate", f"{savings_rate:.1%}")
    with col4:
        color = "🟢" if health_score >= 70 else "🟡" if health_score >= 50 else "🔴"
        st.metric("Health Score", f"{color} {health_score}/100")

def show_comparison(base_results, adj_results):
    """Show scenario comparison"""
    st.subheader("📊 Scenario Comparison")
    
    # Side by side trajectories
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Base Scenario**")
        if 'df' in base_results and not base_results['df'].empty:
            df = base_results['df']
            year_col = 'Year' if 'Year' in df.columns else df.index
            savings_col = next((col for col in ['Savings End', 'Savings', 'Balance'] if col in df.columns), df.columns[0])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df[year_col] if isinstance(year_col, str) else year_col,
                y=df[savings_col],
                mode='lines',
                name='Base Scenario'
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Adjusted Scenario**")
        if adj_results and 'df' in adj_results and not adj_results['df'].empty:
            df = adj_results['df']
            year_col = 'Year' if 'Year' in df.columns else df.index
            savings_col = next((col for col in ['Savings End', 'Savings', 'Balance'] if col in df.columns), df.columns[0])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df[year_col] if isinstance(year_col, str) else year_col,
                y=df[savings_col],
                mode='lines',
                name='Adjusted Scenario'
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

def show_timeline(results, user_data, family_data):
    """Show family timeline"""
    st.subheader("📅 Family Financial Timeline")
    
    events = []
    current_year = date.today().year
    
    # Add RMD events
    if user_data['age'] < 73:
        rmd_year = current_year + (73 - user_data['age'])
        events.append({'Year': rmd_year, 'Event': 'RMD Starts', 'Type': 'Milestone', 'Amount': 0})
    
    # Add Social Security events
    if user_data['age'] < 67:
        ss_year = current_year + (67 - user_data['age'])
        events.append({'Year': ss_year, 'Event': 'Full Social Security', 'Type': 'Milestone', 'Amount': 0})
    
    # Add children college events
    if family_data and 'children' in family_data:
        for child in family_data['children']:
            if child.get('Name') and child.get('College Plan', 'None') != 'None':
                college_year = child.get('Birth Year', current_year) + 18
                college_cost = 50000  # Estimate based on plan
                events.append({
                    'Year': college_year, 
                    'Event': f"{child['Name']} - College Start", 
                    'Type': 'Education',
                    'Amount': -college_cost
                })
    
    # Add inheritance events - THIS WAS MISSING!
    if family_data and 'inheritances' in family_data:
        for inheritance in family_data['inheritances']:
            if inheritance.get('Amount', 0) > 0:
                events.append({
                    'Year': inheritance.get('Year', current_year),
                    'Event': f"Inheritance: {inheritance.get('Description', 'Estate')}",
                    'Type': 'Inheritance', 
                    'Amount': inheritance['Amount']
                })
    
    # Add mortgage payoff event if mortgage exists
    if 'mortgage_details' in results and results['mortgage_details'].get('years_remaining', 0) > 0:
        payoff_year = current_year + results['mortgage_details']['years_remaining']
        events.append({
            'Year': payoff_year,
            'Event': 'Mortgage Paid Off',
            'Type': 'Debt',
            'Amount': 0
        })
    
    if events:
        # Sort events by year
        events = sorted(events, key=lambda x: x['Year'])
        events_df = pd.DataFrame(events)
        
        # Create enhanced timeline visualization
        fig = go.Figure()
        
        # Color map for different event types
        color_map = {
            'Milestone': 'blue',
            'Education': 'red', 
            'Inheritance': 'green',
            'Debt': 'orange'
        }
        
        for event_type in events_df['Type'].unique():
            type_data = events_df[events_df['Type'] == event_type]
            fig.add_trace(go.Scatter(
                x=type_data['Year'],
                y=type_data['Event'],
                mode='markers+text',
                marker=dict(size=15, color=color_map.get(event_type, 'gray')),
                text=[f"${amt:,.0f}" if amt != 0 else "" for amt in type_data['Amount']],
                textposition="middle right",
                name=event_type
            ))
        
        fig.update_layout(
            title="Family Financial Timeline",
            xaxis_title="Year",
            yaxis_title="Events",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show event details table
        with st.expander("📋 Timeline Event Details"):
            st.dataframe(events_df)
    else:
        st.info("No timeline events to display. Add children, inheritance events, or other family events to see timeline.")

def show_download_options(results):
    """Provide download options for results"""
    st.subheader("📥 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'df' in results and not results['df'].empty:
            csv = results['df'].to_csv(index=False)
            st.download_button(
                "📊 Download Detailed Results (CSV)",
                csv,
                "retirement_projection_detailed.csv",
                "text/csv"
            )
    
    with col2:
        summary = f"""
Family Retirement Planning Summary
Generated: {date.today()}
=====================================
Final Savings: ${results.get('final_savings', 0):,.2f}
Final Net Worth: ${results.get('final_net_worth', 0):,.2f}
Years Solvent: {results.get('years_solvent', 0)}
Success Rate: {results.get('monte_carlo_results', {}).get('success_rate', 'N/A')}%
"""
        st.download_button(
            "📄 Download Summary (TXT)",
            summary,
            "retirement_summary.txt",
            "text/plain"
        )