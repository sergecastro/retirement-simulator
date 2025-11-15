# timeline.py - FIXED: Proper detailed table display + CSV download
import streamlit as st
import plotly.graph_objects as go
from datetime import date
import pandas as pd

def show_timeline(results, user_data, family_data):
    """Display family financial timeline with major events"""
    # Add help button for this chart
    from utils.chart_tooltips import add_chart_help_button
    add_chart_help_button("family_timeline")

    st.subheader("📅 Family Financial Timeline")
    
    events = []
    current_year = date.today().year
    
    # RMD
    if user_data['age'] < 73:
        rmd_year = current_year + (73 - user_data['age'])
        events.append({'Year': rmd_year, 'Event': 'User RMD Starts', 'Type': 'Milestone', 'Amount': 0})
    
    if user_data.get('partner_exists') and user_data.get('partner_age', 0) < 73:
        partner_rmd_year = current_year + (73 - user_data.get('partner_age', 0))
        events.append({'Year': partner_rmd_year, 'Event': 'Partner RMD Starts', 'Type': 'Milestone', 'Amount': 0})
    
    # Social Security
    if user_data['age'] < 67:
        ss_year = current_year + (67 - user_data['age'])
        events.append({'Year': ss_year, 'Event': 'Full Social Security', 'Type': 'Milestone', 'Amount': 0})
    
    # Children college
    if family_data and 'children' in family_data:
        for child in family_data['children']:
            if child.get('Name', '').strip() and child.get('College Plan', 'None') != 'None':
                college_year = child.get('Birth Year', current_year) + 18
                events.append({'Year': college_year, 'Event': f"{child['Name']} College Start", 'Type': 'Education', 'Amount': -50000})
    
    # Inheritances
    if family_data and 'inheritances' in family_data:
        for inh in family_data['inheritances']:
            if inh.get('Amount', 0) > 0:
                events.append({'Year': inh.get('Year', current_year), 'Event': f"Inheritance", 'Type': 'Inheritance', 'Amount': inh['Amount']})
    
    if events:
        events_df = pd.DataFrame(sorted(events, key=lambda x: x['Year']))
        color_map = {'Milestone': 'blue', 'Education': 'red', 'Inheritance': 'green', 'Debt': 'orange'}
        
        fig = go.Figure()
        for event_type in events_df['Type'].unique():
            type_data = events_df[events_df['Type'] == event_type]
            fig.add_trace(go.Scatter(
                x=type_data['Year'], 
                y=type_data['Event'], 
                mode='markers+text', 
                marker=dict(size=15, color=color_map.get(event_type, 'gray')), 
                text=[f"${amt:,.0f}" if amt != 0 else "" for amt in type_data['Amount']], 
                name=event_type
            ))
        
        fig.update_layout(title="Family Timeline", xaxis_title="Year", yaxis_title="Events", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📋 Event Details"):
            st.dataframe(events_df, use_container_width=True)
    else:
        st.info("Add family events to see timeline.")

def show_goal_gauges(results):
    """Display goal achievement gauges"""
    # Add help button for this visualization
    from utils.chart_tooltips import add_chart_help_button
    add_chart_help_button("goal_achievement_gauges")

    st.subheader("🎯 Goal Achievement Gauges")

    goal_data = results.get('goal_achievement', {})
    if not goal_data:
        st.info("No goals configured")
        return
    
    cols = st.columns(min(3, len(goal_data)))
    
    for idx, (goal, data) in enumerate(goal_data.items()):
        with cols[idx % 3]:
            progress_pct = (data['actual'] / data['target'] * 100) if data['target'] > 0 else 0
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=progress_pct,
                title={'text': goal},
                delta={'reference': 100},
                gauge={
                    'axis': {'range': [0, 120]},
                    'bar': {'color': "green" if data['achieved'] else "red"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 100], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 100
                    }
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption(f"Target: ${data['target']:,.0f} by {data['year']}")
            st.caption(f"Actual: ${data['actual']:,.0f}")

def show_detailed_projection_table(results):
    """
    Display the detailed year-by-year projection table with all calculations
    This is the 40+ column spreadsheet that shows the complete financial picture
    """
    st.header("📊 Detailed Year-by-Year Financial Projection")
    
    if 'df' not in results or results['df'] is None or results['df'].empty:
        st.warning("⚠️ No detailed projection data available. Run simulation first.")
        return
    
    df = results['df']
    
    # Info message
    st.info(f"📈 Showing {len(df)} years of detailed projections with {len(df.columns)} data columns")
    
    # Format currency columns for display
    currency_cols = [col for col in df.columns if col not in ['Year', 'User_Age', 'Partner_Age', 'Goal_Progress']]
    
    # Create formatted dataframe for display
    display_df = df.copy()
    for col in currency_cols:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    
    # Display with formatting
    st.dataframe(
        display_df,
        use_container_width=True,
        height=600
    )
    
    # Key insights
    with st.expander("🔍 Key Insights from Projection"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Years Until Savings Depleted", 
                     sum(1 for s in df['Savings_End'] if s > 0),
                     help="Number of years with positive savings")
            
            first_negative = next((i for i, s in enumerate(df['Savings_End']) if s <= 0), None)
            if first_negative:
                st.warning(f"⚠️ Savings depleted in year {df['Year'].iloc[first_negative]}")
            else:
                st.success("✅ Savings remain positive throughout projection")
        
        with col2:
            total_rmd = df['Total_RMD'].sum()
            st.metric("Total RMD Over Period", f"${total_rmd:,.0f}")
            
            total_inheritance = df['Inheritance_Inflow'].sum()
            if total_inheritance > 0:
                st.metric("Total Inheritances", f"${total_inheritance:,.0f}")
        
        with col3:
            total_college = df['College_Expenses'].sum()
            if total_college > 0:
                st.metric("Total College Costs", f"${total_college:,.0f}")
            
            peak_net_worth = df['Net_Worth'].max()
            st.metric("Peak Net Worth", f"${peak_net_worth:,.0f}")
    
    # Column explanations
    with st.expander("📖 Column Definitions"):
        st.markdown("""
        **Basic Information:**
        - **Year**: Calendar year
        - **User_Age**: Your age in that year
        - **Partner_Age**: Partner's age in that year (0 if no partner)
        
        **Income Components:**
        - **Salary_Wages**: Employment income
        - **Rental_Income**: Income from rental properties
        - **Investment_Income**: Dividends, interest, capital gains
        - **Social_Security**: Social Security benefits
        - **Pension_Income**: Pension payments
        - **Other_Income**: Other income sources
        - **Base_Income_Subtotal**: Sum of above income sources
        
        **RMD (Required Minimum Distributions):**
        - **User_RMD**: Your RMD from retirement accounts (starts age 73)
        - **Partner_RMD**: Partner's RMD (starts age 73)
        - **Total_RMD**: Combined RMD for both
        
        **Total Income:**
        - **Total_Income**: Base Income + Total RMD
        
        **Expense Components:**
        - **Housing_Expenses**: Rent/mortgage, HOA fees
        - **Utilities**: Electric, gas, water, internet
        - **Groceries**: Food and household items
        - **Transportation**: Car payments, gas, maintenance
        - **Healthcare**: Medical costs not covered by insurance
        - **Insurance**: All insurance premiums
        - **Entertainment**: Subscriptions, hobbies, activities
        - **Travel**: Vacation and travel expenses
        - **Other_Expenses**: Clothing, personal care, charitable donations
        - **Base_Expenses_Subtotal**: Sum of above expenses
        
        **Special Cash Flows:**
        - **College_Expenses**: Annual college costs for children
        - **Inheritance_Inflow**: One-time inheritance received
        - **Total_Expenses**: Base Expenses + College Expenses
        
        **Net Calculations:**
        - **Taxes_Paid**: Income tax paid
        - **Net_Income_Before_Special**: Total Income - Total Expenses - Taxes
        - **Net_Income_After_Special**: Net Before + Inheritances
        
        **Savings & Assets:**
        - **Savings_Start**: Savings at beginning of year
        - **Investment_Return**: Return on investments
        - **Savings_End**: Savings at end of year
        - **Total_Assets**: Savings + Real Estate + Other Assets
        - **Total_Liabilities**: All debts and loans
        - **Net_Worth**: Total Assets - Total Liabilities
        
        **Goals:**
        - **Goal_Progress**: Progress toward financial goals (ratio)
        """)

def show_download_options(results):
    """Provide download options for results"""
    st.header("📥 Export & Download")
    
    if 'df' not in results or results['df'] is None or results['df'].empty:
        st.warning("No data to export")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Detailed Projection CSV")
        csv = results['df'].to_csv(index=False)
        st.download_button(
            label="📊 Download Full Projection (CSV)",
            data=csv,
            file_name=f"financial_projection_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.caption(f"Contains {len(results['df'])} years × {len(results['df'].columns)} columns")
    
    with col2:
        st.subheader("📄 Executive Summary")
        summary = f"""FINANCIAL PROJECTION SUMMARY
Generated: {date.today().strftime('%B %d, %Y')}
{'='*50}

FINAL RESULTS (End of Projection):
  Final Savings: ${results.get('final_savings', 0):,.2f}
  Final Net Worth: ${results.get('final_net_worth', 0):,.2f}
  Years Solvent: {results.get('years_solvent', 0)} years
  
FINANCIAL HEALTH METRICS:
  Emergency Fund: {results.get('emergency_fund_months', 0):.1f} months
  Debt-to-Income Ratio: {results.get('debt_to_income', 0):.2f}
  Savings Rate: {results.get('savings_rate', 0)*100:.1f}%
  Overall Health Score: {results.get('health_score', 0)}/100

GOAL ACHIEVEMENT:
"""
        for goal, data in results.get('goal_achievement', {}).items():
            status = "✅ ACHIEVED" if data['achieved'] else "❌ NOT MET"
            summary += f"  {goal}: {status}\n"
            summary += f"    Target: ${data['target']:,.0f} by {data['year']}\n"
            summary += f"    Actual: ${data['actual']:,.0f}\n\n"
        
        st.download_button(
            label="📄 Download Summary (TXT)",
            data=summary,
            file_name=f"financial_summary_{date.today()}.txt",
            mime="text/plain",
            use_container_width=True
        )
        st.caption("Executive summary of key results")
    
    # Additional export option - Excel format (if openpyxl available)
    st.subheader("💾 Additional Export Options")
    
    try:
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            results['df'].to_excel(writer, sheet_name='Projection', index=False)
        
        st.download_button(
            label="📊 Download as Excel (XLSX)",
            data=buffer.getvalue(),
            file_name=f"financial_projection_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except ImportError:
        st.info("💡 Install openpyxl to enable Excel export: `pip install openpyxl`")