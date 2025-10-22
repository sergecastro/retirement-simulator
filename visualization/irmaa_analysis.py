# visualization/irmaa_analysis.py - Medicare IRMAA Planning Module
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
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

    # Convert Plotly figure to JSON
    plotly_json = fig.to_json()

    st.session_state.__chart_registry__[chart_id] = {
        'title': title,
        'data': {
            'plotly_spec': json.loads(plotly_json),
            'summary': data_summary
        }
    }

    print(f"[Chart Registry] Registered: {chart_id} with {len(fig.data)} traces")

# 2025 IRMAA Income Thresholds (inflation-adjusted estimates)
IRMAA_BRACKETS_2025 = {
    'single': [
        {'min': 0, 'max': 106000, 'surcharge_monthly': 0, 'part_b_total': 174.70, 'part_d_base': 0},
        {'min': 106000, 'max': 133000, 'surcharge_monthly': 69.90, 'part_b_total': 244.60, 'part_d_base': 12.90},
        {'min': 133000, 'max': 167000, 'surcharge_monthly': 174.70, 'part_b_total': 349.40, 'part_d_base': 33.30},
        {'min': 167000, 'max': 200000, 'surcharge_monthly': 279.50, 'part_b_total': 454.20, 'part_d_base': 53.80},
        {'min': 200000, 'max': 500000, 'surcharge_monthly': 384.30, 'part_b_total': 559.00, 'part_d_base': 74.20},
        {'min': 500000, 'max': 999999999, 'surcharge_monthly': 419.30, 'part_b_total': 594.00, 'part_d_base': 81.00}
    ],
    'joint': [
        {'min': 0, 'max': 212000, 'surcharge_monthly': 0, 'part_b_total': 174.70, 'part_d_base': 0},
        {'min': 212000, 'max': 266000, 'surcharge_monthly': 69.90, 'part_b_total': 244.60, 'part_d_base': 12.90},
        {'min': 266000, 'max': 334000, 'surcharge_monthly': 174.70, 'part_b_total': 349.40, 'part_d_base': 33.30},
        {'min': 334000, 'max': 400000, 'surcharge_monthly': 279.50, 'part_b_total': 454.20, 'part_d_base': 53.80},
        {'min': 400000, 'max': 750000, 'surcharge_monthly': 384.30, 'part_b_total': 559.00, 'part_d_base': 74.20},
        {'min': 750000, 'max': 999999999, 'surcharge_monthly': 419.30, 'part_b_total': 594.00, 'part_d_base': 81.00}
    ]
}

def calculate_magi(total_income, tax_exempt_interest=0, foreign_income=0, social_security_taxable=0):
    """
    Calculate Modified Adjusted Gross Income (MAGI) for IRMAA purposes
    
    For most retirees: MAGI ≈ AGI (Adjusted Gross Income)
    MAGI = AGI + tax-exempt interest + foreign earned income + non-taxable SS benefits
    """
    # For simplicity, we'll use total income as a proxy for AGI
    # In reality, AGI = Total Income - above-the-line deductions
    magi = total_income + tax_exempt_interest + foreign_income
    return magi

def get_irmaa_bracket(magi, filing_status='joint'):
    """Determine which IRMAA bracket the MAGI falls into"""
    brackets = IRMAA_BRACKETS_2025[filing_status]
    
    for bracket in brackets:
        if bracket['min'] <= magi < bracket['max']:
            return bracket
    
    # If above all brackets, return highest
    return brackets[-1]

def calculate_annual_irmaa_cost(magi, filing_status='joint', has_partner=False):
    """Calculate total annual IRMAA surcharge for Part B and Part D"""
    bracket = get_irmaa_bracket(magi, filing_status)
    
    # Part B surcharge (12 months)
    part_b_annual = bracket['surcharge_monthly'] * 12
    
    # Part D surcharge (12 months) - average across plans
    part_d_annual = bracket['part_d_base'] * 12
    
    # Total per person
    total_per_person = part_b_annual + part_d_annual
    
    # If married filing jointly, both pay the surcharge
    if has_partner:
        return total_per_person * 2, total_per_person
    else:
        return total_per_person, total_per_person

def show_irmaa_analysis(results, user_data, sim_params):
    """
    Display Medicare IRMAA analysis with projections and recommendations
    """
    st.header("🏥 Medicare IRMAA Planning & Analysis")
    
    # Check if users are Medicare age
    current_age = user_data.get('age', 65)
    partner_age = user_data.get('partner_age', 65)
    partner_exists = user_data.get('partner_exists', False)
    
    if current_age < 65 and (not partner_exists or partner_age < 65):
        st.info("""
        **Medicare IRMAA planning will be available when you reach age 65.**
        
        IRMAA (Income-Related Monthly Adjustment Amount) are surcharges on Medicare Parts B and D 
        based on your income from 2 years prior.
        """)
        return
    
    # Get projection data
    df = results.get('df')
    if df is None or df.empty:
        st.warning("Run simulation first to see IRMAA analysis")
        return
    
    # Determine filing status
    filing_status = 'joint' if partner_exists else 'single'
    
    st.info(f"""
    **IRMAA Overview**
    
    Medicare uses your **Modified Adjusted Gross Income (MAGI)** from **2 years ago** to determine 
    if you pay higher premiums for Parts B and D.
    
    - **Your filing status:** {'Married Filing Jointly' if filing_status == 'joint' else 'Single'}
    - **2-year lookback:** Your 2025 premiums are based on 2023 income
    - **Both spouses affected:** When filing jointly, BOTH pay the same IRMAA bracket
    """)
    
    # Calculate MAGI for each year (simplified - using Total_Income as proxy)
    # In reality, would need more detailed breakdown
    df_copy = df.copy()
    
    # MAGI calculation (simplified)
    # For retirees: MAGI ≈ Total Income (wages + SS + pensions + RMDs + investment income)
    df_copy['MAGI'] = df_copy['Total_Income']
    
    # Apply 2-year lookback for IRMAA determination
    df_copy['MAGI_For_IRMAA'] = df_copy['MAGI'].shift(2).fillna(df_copy['MAGI'].iloc[0])
    
    # Calculate IRMAA bracket and costs for each year
    irmaa_brackets = []
    irmaa_annual_costs = []
    irmaa_surcharges = []
    
    for idx, row in df_copy.iterrows():
        magi_for_irmaa = row['MAGI_For_IRMAA']
        bracket = get_irmaa_bracket(magi_for_irmaa, filing_status)
        total_cost, per_person = calculate_annual_irmaa_cost(magi_for_irmaa, filing_status, partner_exists)
        
        irmaa_brackets.append(bracket['part_b_total'])
        irmaa_annual_costs.append(total_cost)
        irmaa_surcharges.append(bracket['surcharge_monthly'])
    
    df_copy['IRMAA_Part_B_Premium'] = irmaa_brackets
    df_copy['IRMAA_Annual_Cost'] = irmaa_annual_costs
    df_copy['IRMAA_Monthly_Surcharge'] = irmaa_surcharges
    
    # Summary metrics
    st.markdown("### 📊 IRMAA Impact Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_year_cost = df_copy['IRMAA_Annual_Cost'].iloc[0]
        st.metric(
            "Current Year IRMAA",
            f"${current_year_cost:,.0f}",
            help="Total IRMAA surcharges this year (both spouses if married)"
        )
    
    with col2:
        total_irmaa_projected = df_copy['IRMAA_Annual_Cost'].sum()
        st.metric(
            "Total IRMAA Over Period",
            f"${total_irmaa_projected:,.0f}",
            help="Sum of all IRMAA surcharges over projection period"
        )
    
    with col3:
        current_bracket = df_copy['IRMAA_Part_B_Premium'].iloc[0]
        st.metric(
            "Current Part B Premium",
            f"${current_bracket:.2f}/mo",
            help="Monthly Part B premium including IRMAA (per person)"
        )
    
    with col4:
        years_with_surcharge = (df_copy['IRMAA_Monthly_Surcharge'] > 0).sum()
        st.metric(
            "Years With Surcharges",
            f"{years_with_surcharge}",
            help="Number of years paying above base premium"
        )
    
    # Visualization: MAGI vs IRMAA Thresholds
    st.markdown("### 📈 Income Trajectory vs IRMAA Thresholds")
    
    fig = go.Figure()
    
    # Plot MAGI (with 2-year lookback applied)
    fig.add_trace(go.Scatter(
        x=df_copy['Year'],
        y=df_copy['MAGI_For_IRMAA'],
        mode='lines+markers',
        name='Your MAGI (2-year lookback)',
        line=dict(color='blue', width=3),
        marker=dict(size=6)
    ))
    
    # Add threshold lines
    brackets = IRMAA_BRACKETS_2025[filing_status]
    colors = ['green', 'yellow', 'orange', 'red', 'darkred', 'purple']
    
    for idx, bracket in enumerate(brackets[1:], start=1):  # Skip first (base) bracket
        threshold = bracket['min']
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color=colors[min(idx, len(colors)-1)],
            annotation_text=f"${threshold:,.0f} - Surcharge: ${bracket['surcharge_monthly']:.2f}/mo",
            annotation_position="right"
        )
    
    fig.update_layout(
        title=f"MAGI Trajectory vs IRMAA Thresholds ({filing_status.title()})",
        xaxis_title="Year",
        yaxis_title="Modified Adjusted Gross Income (MAGI)",
        height=500,
        hovermode='x unified'
    )

    fig.update_yaxes(tickformat="$,.0f")

    # Register chart data for Claude explanations
    data_summary = {
        "chart_type": "irmaa_magi_trajectory",
        "filing_status": filing_status,
        "current_magi": float(df_copy['MAGI_For_IRMAA'].iloc[0]),
        "average_magi": float(df_copy['MAGI_For_IRMAA'].mean()),
        "max_magi": float(df_copy['MAGI_For_IRMAA'].max()),
        "min_magi": float(df_copy['MAGI_For_IRMAA'].min()),
        "years_above_base_threshold": int((df_copy['MAGI_For_IRMAA'] > brackets[0]['max']).sum()),
        "threshold_crossings": len(df_copy[df_copy['MAGI_For_IRMAA'] > brackets[1]['min']]),
        "irmaa_brackets": [{
            'threshold': int(b['min']),
            'monthly_surcharge': float(b['surcharge_monthly']),
            'annual_cost_single': float((b['surcharge_monthly'] + b['part_d_base']) * 12),
            'annual_cost_couple': float((b['surcharge_monthly'] + b['part_d_base']) * 12 * 2)
        } for b in brackets[1:]]  # Skip base bracket
    }

    register_chart_data(
        chart_id="irmaa_magi_trajectory",
        title=f"MAGI Trajectory vs IRMAA Thresholds",
        fig=fig,
        data_summary=data_summary
    )

    # Inject chart data as JavaScript
    chart_data_json = json.dumps({
        'chart_id': 'irmaa_magi_trajectory',
        'title': 'MAGI Trajectory vs IRMAA Thresholds',
        'data_summary': data_summary
    })

    st.components.v1.html(f"""
    <script>
    if (!window.parent.__CHART_DATA_REGISTRY__) {{
        window.parent.__CHART_DATA_REGISTRY__ = {{}};
    }}
    window.parent.__CHART_DATA_REGISTRY__['irmaa_magi_trajectory'] = {chart_data_json};
    console.log('[ChartRegistry] Registered irmaa_magi_trajectory:', window.parent.__CHART_DATA_REGISTRY__['irmaa_magi_trajectory']);
    </script>
    """, height=0)

    st.plotly_chart(fig, use_container_width=True, key="irmaa_magi_chart")
    
    # Annual cost visualization
    st.markdown("### 💰 Annual IRMAA Costs Over Time")
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        x=df_copy['Year'],
        y=df_copy['IRMAA_Annual_Cost'],
        name='Annual IRMAA Cost',
        marker_color='crimson',
        text=[f"${cost:,.0f}" if cost > 0 else "" for cost in df_copy['IRMAA_Annual_Cost']],
        textposition='outside'
    ))
    
    fig2.update_layout(
        title="Total Annual IRMAA Surcharges (Both Spouses)",
        xaxis_title="Year",
        yaxis_title="Annual IRMAA Cost ($)",
        height=400
    )

    # Register chart data for Claude explanations
    data_summary2 = {
        "chart_type": "irmaa_annual_costs",
        "filing_status": filing_status,
        "total_irmaa_over_period": float(df_copy['IRMAA_Annual_Cost'].sum()),
        "average_annual_cost": float(df_copy['IRMAA_Annual_Cost'].mean()),
        "max_annual_cost": float(df_copy['IRMAA_Annual_Cost'].max()),
        "years_with_costs": int((df_copy['IRMAA_Annual_Cost'] > 0).sum()),
        "years_with_surcharges": int((df_copy['IRMAA_Monthly_Surcharge'] > 0).sum()),
        "current_year_cost": float(df_copy['IRMAA_Annual_Cost'].iloc[0]),
        "year_by_year_costs": [
            {"year": int(row['Year']), "cost": float(row['IRMAA_Annual_Cost'])}
            for _, row in df_copy[['Year', 'IRMAA_Annual_Cost']].iterrows()
        ]
    }

    register_chart_data(
        chart_id="irmaa_annual_costs",
        title="Annual IRMAA Costs Over Time",
        fig=fig2,
        data_summary=data_summary2
    )

    # Inject chart data as JavaScript
    chart_data_json2 = json.dumps({
        'chart_id': 'irmaa_annual_costs',
        'title': 'Annual IRMAA Costs Over Time',
        'data_summary': data_summary2
    })

    st.components.v1.html(f"""
    <script>
    if (!window.parent.__CHART_DATA_REGISTRY__) {{
        window.parent.__CHART_DATA_REGISTRY__ = {{}};
    }}
    window.parent.__CHART_DATA_REGISTRY__['irmaa_annual_costs'] = {chart_data_json2};
    console.log('[ChartRegistry] Registered irmaa_annual_costs:', window.parent.__CHART_DATA_REGISTRY__['irmaa_annual_costs']);
    </script>
    """, height=0)

    st.plotly_chart(fig2, use_container_width=True, key="irmaa_costs_chart")
    
    # Detailed year-by-year breakdown
    with st.expander("📋 Year-by-Year IRMAA Breakdown"):
        display_df = df_copy[['Year', 'User_Age', 'Partner_Age', 'Total_Income', 'MAGI', 
                               'MAGI_For_IRMAA', 'IRMAA_Part_B_Premium', 
                               'IRMAA_Monthly_Surcharge', 'IRMAA_Annual_Cost']].copy()
        
        # Format currency columns
        display_df['Total_Income'] = display_df['Total_Income'].apply(lambda x: f"${x:,.0f}")
        display_df['MAGI'] = display_df['MAGI'].apply(lambda x: f"${x:,.0f}")
        display_df['MAGI_For_IRMAA'] = display_df['MAGI_For_IRMAA'].apply(lambda x: f"${x:,.0f}")
        display_df['IRMAA_Part_B_Premium'] = display_df['IRMAA_Part_B_Premium'].apply(lambda x: f"${x:.2f}")
        display_df['IRMAA_Monthly_Surcharge'] = display_df['IRMAA_Monthly_Surcharge'].apply(lambda x: f"${x:.2f}")
        display_df['IRMAA_Annual_Cost'] = display_df['IRMAA_Annual_Cost'].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True, height=400)
    
    # Recommendations
    st.markdown("### 💡 IRMAA Optimization Strategies")
    
    # Identify years with high IRMAA
    high_irmaa_years = df_copy[df_copy['IRMAA_Annual_Cost'] > 5000].copy()
    
    # Identify opportunities (years with low income that could absorb Roth conversions)
    low_income_years = df_copy[df_copy['MAGI_For_IRMAA'] < brackets[1]['min']].copy()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**⚠️ High IRMAA Risk Years**")
        if not high_irmaa_years.empty:
            for _, row in high_irmaa_years.head(5).iterrows():
                year = int(row['Year'])
                cost = row['IRMAA_Annual_Cost']
                magi = row['MAGI_For_IRMAA']
                st.warning(f"**{year}:** MAGI ${magi:,.0f} → ${cost:,.0f} IRMAA cost")
        else:
            st.success("No high IRMAA years projected!")
    
    with col2:
        st.markdown("**✅ Roth Conversion Opportunities**")
        if not low_income_years.empty:
            for _, row in low_income_years.head(5).iterrows():
                year = int(row['Year'])
                magi = row['MAGI_For_IRMAA']
                room = brackets[1]['min'] - magi
                if room > 0:
                    st.success(f"**{year}:** ${room:,.0f} conversion room before IRMAA")
        else:
            st.info("Income consistently above base IRMAA threshold")
    
    # Strategic recommendations
    st.markdown("### 🎯 Strategic Recommendations")
    
    recommendations = []
    
    # Check if close to threshold
    current_magi = df_copy['MAGI_For_IRMAA'].iloc[0]
    next_bracket_threshold = None
    for bracket in brackets:
        if bracket['min'] > current_magi:
            next_bracket_threshold = bracket['min']
            break
    
    if next_bracket_threshold:
        distance_to_threshold = next_bracket_threshold - current_magi
        if distance_to_threshold < 20000:
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Income Threshold Risk',
                'description': f"You're ${distance_to_threshold:,.0f} from the next IRMAA bracket. Consider:",
                'actions': [
                    "Defer income to next year if possible",
                    "Time capital gains realizations carefully",
                    "Consider QCDs to reduce taxable income",
                    "Harvest tax losses to offset gains"
                ]
            })
    
    # QCD opportunity
    user_over_70_5 = current_age >= 70.5
    partner_over_70_5 = partner_exists and partner_age >= 70.5
    
    if user_over_70_5 or partner_over_70_5:
        recommendations.append({
            'priority': 'MEDIUM',
            'title': 'Qualified Charitable Distribution (QCD)',
            'description': "You're eligible for QCDs from your IRA:",
            'actions': [
                f"Direct up to ${100000 if not partner_exists else 200000:,} annually to charity",
                "QCDs satisfy RMDs but don't count as income",
                "Reduces MAGI and IRMAA exposure",
                "Tax-free donation (better than deduction)"
            ]
        })
    
    # Roth conversion timing
    if not low_income_years.empty:
        best_year = low_income_years.iloc[0]
        recommendations.append({
            'priority': 'MEDIUM',
            'title': 'Roth Conversion Opportunity',
            'description': f"Year {int(best_year['Year'])} shows lower income:",
            'actions': [
                f"MAGI projected at ${best_year['MAGI_For_IRMAA']:,.0f}",
                f"Room for conversion: ${brackets[1]['min'] - best_year['MAGI_For_IRMAA']:,.0f}",
                "Convert traditional IRA to Roth in low-income years",
                "Reduces future RMDs and IRMAA exposure"
            ]
        })
    
    # Display recommendations
    for rec in recommendations:
        if rec['priority'] == 'HIGH':
            alert_func = st.error
            icon = "🚨"
        elif rec['priority'] == 'MEDIUM':
            alert_func = st.warning
            icon = "⚠️"
        else:
            alert_func = st.info
            icon = "ℹ️"
        
        with alert_func(f"{icon} **{rec['title']}**"):
            st.write(rec['description'])
            for action in rec['actions']:
                st.write(f"• {action}")
    
    # IRMAA bracket reference table
    with st.expander("📚 2025 IRMAA Bracket Reference"):
        st.markdown("**Medicare Part B & Part D Premiums by Income Level**")
        
        bracket_data = []
        for bracket in brackets:
            bracket_data.append({
                'MAGI Range': f"${bracket['min']:,} - ${bracket['max']:,}" if bracket['max'] < 999999999 else f"${bracket['min']:,}+",
                'Part B Monthly': f"${bracket['part_b_total']:.2f}",
                'Monthly Surcharge': f"${bracket['surcharge_monthly']:.2f}",
                'Annual Impact (Single)': f"${(bracket['surcharge_monthly'] + bracket['part_d_base']) * 12:,.0f}",
                'Annual Impact (Both Spouses)': f"${(bracket['surcharge_monthly'] + bracket['part_d_base']) * 12 * 2:,.0f}"
            })
        
        st.table(pd.DataFrame(bracket_data))
        
        st.caption("Note: Part D surcharges vary by plan but average amounts shown above")
    
    # Export option
    st.markdown("### 📥 Export IRMAA Analysis")
    
    export_df = df_copy[['Year', 'User_Age', 'Partner_Age', 'Total_Income', 'MAGI', 
                          'MAGI_For_IRMAA', 'IRMAA_Annual_Cost']].copy()
    
    csv = export_df.to_csv(index=False)
    st.download_button(
        label="📊 Download IRMAA Projection (CSV)",
        data=csv,
        file_name=f"irmaa_analysis_{date.today()}.csv",
        mime="text/csv",
        use_container_width=True
    )