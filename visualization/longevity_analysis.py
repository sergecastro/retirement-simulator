# visualization/longevity_analysis.py - FIXED to detect stale Monte Carlo data
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import date

def show_longevity_analysis(results, user_data, sim_params):
    """
    Analyze and visualize portfolio longevity - answers "Will my money outlast me?"
    Uses Monte Carlo results to show probability of success at different ages
    """
    
    st.subheader("⏳ Portfolio Longevity Analysis")

    # Monte Carlo is always enabled (hardcoded to 1000 iterations)
    mc_iterations = sim_params.get('mc_iterations', 1000)

    # Get Monte Carlo results
    if 'monte_carlo_results' not in results:
        st.error("Monte Carlo data not found in results. This is a bug - please report it!")
        return
    
    mc_results = results['monte_carlo_results']
    mc_df = mc_results.get('mc_df')
    
    if mc_df is None or mc_df.empty:
        st.warning("No Monte Carlo data available")
        return
    
    st.info(f"Analysis based on {mc_iterations} Monte Carlo scenarios")
    
    # Get user's current age and partner info
    current_age = user_data.get('age', 65)
    partner_exists = user_data.get('partner_exists', False)
    partner_age = user_data.get('partner_age', current_age)
    
    # Calculate ages for each year in simulation
    num_years = len(mc_df)
    start_year = date.today().year
    years = list(range(start_year, start_year + num_years))
    user_ages = [current_age + i for i in range(num_years)]
    
    # Calculate survival probability for each year
    survival_probabilities = []
    for year_idx in range(num_years):
        year_values = mc_df.iloc[year_idx].values
        survival_count = (year_values > 0).sum()
        survival_prob = (survival_count / len(year_values)) * 100
        survival_probabilities.append(survival_prob)
    
    # CRITICAL: Show warning if results don't match extreme negative scenario
    final_prob = survival_probabilities[-1]
    final_savings = results.get('final_savings', 0)
    
    if final_savings < 0 and final_prob > 90:
        st.error("""
        **⚠️ WARNING: Monte Carlo Results May Be Stale**
        
        Your deterministic simulation shows negative final savings (${:,.0f}), 
        but Monte Carlo shows {}% success rate.
        
        This suggests Monte Carlo results are from a previous simulation.
        
        **To fix:** Re-run the simulation with Monte Carlo enabled to generate fresh probability data.
        """.format(final_savings, final_prob))
        return
    
    # Create main longevity chart
    fig = go.Figure()
    
    # Add survival probability line
    fig.add_trace(go.Scatter(
        x=user_ages,
        y=survival_probabilities,
        mode='lines',
        name='Portfolio Survival Probability',
        line=dict(color='blue', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 123, 255, 0.1)'
    ))
    
    # Add confidence zones
    fig.add_hline(y=95, line_dash="dash", line_color="green", 
                  annotation_text="High Confidence Zone (95%+)", 
                  annotation_position="right")
    fig.add_hline(y=75, line_dash="dash", line_color="orange", 
                  annotation_text="Moderate Risk Zone (75%)", 
                  annotation_position="right")
    fig.add_hline(y=50, line_dash="dash", line_color="red", 
                  annotation_text="High Risk Zone (50%)", 
                  annotation_position="right")
    
    # Highlight key age milestones
    milestone_ages = [85, 90, 95, 100]
    for milestone in milestone_ages:
        if milestone <= user_ages[-1]:
            idx = milestone - current_age
            if 0 <= idx < len(survival_probabilities):
                fig.add_vline(x=milestone, line_dash="dot", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title="Portfolio Survival Probability by Age",
        xaxis_title="Your Age",
        yaxis_title="Probability Portfolio Remains Solvent (%)",
        height=500,
        hovermode='x unified',
        yaxis=dict(range=[0, 105])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key metrics at important ages
    st.markdown("### Key Age Milestones")
    
    milestone_cols = st.columns(4)
    milestone_data = []
    
    for milestone in milestone_ages:
        if milestone <= user_ages[-1]:
            idx = milestone - current_age
            if 0 <= idx < len(survival_probabilities):
                prob = survival_probabilities[idx]
                milestone_data.append((milestone, prob))
    
    for i, (age, prob) in enumerate(milestone_data[:4]):
        with milestone_cols[i]:
            # Color code based on probability
            if prob >= 95:
                color_emoji = "🟢"
                status = "Excellent"
            elif prob >= 75:
                color_emoji = "🟡"
                status = "Good"
            elif prob >= 50:
                color_emoji = "🟠"
                status = "Moderate"
            else:
                color_emoji = "🔴"
                status = "Concern"
            
            st.metric(
                f"Age {age}",
                f"{prob:.1f}%",
                delta=f"{status}",
                help=f"Probability your portfolio lasts until age {age}"
            )
            st.caption(f"{color_emoji} {status}")
    
    # Depletion risk analysis
    st.markdown("### Depletion Risk Timeline")
    
    # Find when probability drops below key thresholds
    risk_thresholds = {
        "High confidence ends": 95,
        "Moderate risk begins": 75,
        "High risk begins": 50
    }
    
    risk_ages = {}
    for threshold_name, threshold_value in risk_thresholds.items():
        for idx, prob in enumerate(survival_probabilities):
            if prob < threshold_value:
                risk_ages[threshold_name] = user_ages[idx]
                break
    
    if risk_ages:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Risk Milestones:**")
            for threshold_name, age in risk_ages.items():
                years_away = age - current_age
                st.write(f"• {threshold_name}: Age {age} ({years_away} years)")
        
        with col2:
            # Calculate expected depletion age (when probability = 50%)
            depletion_idx = None
            for idx, prob in enumerate(survival_probabilities):
                if prob < 50:
                    depletion_idx = idx
                    break
            
            if depletion_idx:
                depletion_age = user_ages[depletion_idx]
                years_until = depletion_age - current_age
                st.metric(
                    "Expected Portfolio Longevity",
                    f"{years_until} years",
                    delta=f"Until age {depletion_age}",
                    help="Age when probability drops below 50%"
                )
            else:
                st.metric(
                    "Expected Portfolio Longevity",
                    f"{num_years}+ years",
                    delta="Exceeds simulation",
                    help="Portfolio maintains >50% probability throughout simulation"
                )
    
    # Partner longevity comparison (if partner exists)
    if partner_exists:
        st.markdown("### Joint Longevity Analysis")
        
        partner_ages = [partner_age + i for i in range(num_years)]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Your age at end:** {user_ages[-1]}")
            st.write(f"**Partner age at end:** {partner_ages[-1]}")
        
        with col2:
            survivor_age = max(user_ages[-1], partner_ages[-1])
            st.write(f"**Survivor likely age:** {survivor_age}")
        
        with col3:
            final_prob = survival_probabilities[-1]
            if final_prob >= 75:
                st.success(f"Portfolio strong for both: {final_prob:.1f}%")
            elif final_prob >= 50:
                st.warning(f"Portfolio moderate for both: {final_prob:.1f}%")
            else:
                st.error(f"Portfolio at risk for survivor: {final_prob:.1f}%")
    
    # Statistical analysis
    with st.expander("📊 Detailed Statistical Analysis"):
        st.markdown("**Portfolio Depletion Scenarios:**")
        
        # Calculate statistics from Monte Carlo
        final_values = mc_df.iloc[-1].values
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Outcome Distribution:**")
            positive_count = (final_values > 0).sum()
            total_count = len(final_values)
            
            st.write(f"• Scenarios remaining solvent: {positive_count}/{total_count} ({positive_count/total_count*100:.1f}%)")
            st.write(f"• Scenarios depleted: {total_count - positive_count}/{total_count} ({(total_count-positive_count)/total_count*100:.1f}%)")
            
            if positive_count > 0:
                avg_remaining = final_values[final_values > 0].mean()
                st.write(f"• Average final balance (if solvent): ${avg_remaining:,.0f}")
        
        with col2:
            st.write("**Age-Based Probabilities:**")
            
            # Create probability table
            prob_data = []
            for age in range(current_age + 5, min(current_age + 41, 101), 5):
                idx = age - current_age
                if 0 <= idx < len(survival_probabilities):
                    prob = survival_probabilities[idx]
                    prob_data.append({
                        'Age': age,
                        'Probability': f"{prob:.1f}%",
                        'Status': '🟢' if prob >= 95 else '🟡' if prob >= 75 else '🟠' if prob >= 50 else '🔴'
                    })
            
            if prob_data:
                st.dataframe(pd.DataFrame(prob_data), use_container_width=True, hide_index=True)
    
    # Recommendations based on analysis
    st.markdown("### Recommendations")
    
    final_prob = survival_probabilities[-1]
    
    if final_prob >= 95:
        st.success("""
        **Excellent Portfolio Health**
        
        Your portfolio shows strong longevity with >95% probability of lasting throughout retirement.
        
        Consider:
        - Reviewing withdrawal rates for potential increased spending
        - Estate planning to maximize legacy
        - Charitable giving strategies
        """)
    elif final_prob >= 75:
        st.info("""
        **Good Portfolio Health with Monitoring Needed**
        
        Your portfolio shows good probability of success but requires monitoring.
        
        Consider:
        - Regular review of withdrawal rates
        - Maintaining flexibility in spending
        - Healthcare cost contingency planning
        """)
    elif final_prob >= 50:
        st.warning("""
        **Moderate Risk - Action Recommended**
        
        Your portfolio has moderate depletion risk requiring attention.
        
        Consider:
        - Reducing discretionary spending
        - Delaying Social Security if not yet claimed
        - Part-time work to reduce portfolio withdrawals
        - Downsizing housing to reduce expenses
        """)
    else:
        st.error("""
        **High Risk - Immediate Action Needed**
        
        Your portfolio shows high probability of depletion requiring immediate changes.
        
        Urgently consider:
        - Significant spending reductions
        - Additional income sources
        - Liquidating non-essential assets
        - Professional financial planning consultation
        """)