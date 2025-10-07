# scenario_tools.py - FIXED: Added button to trigger comparison
import streamlit as st
from simulation_core import run_simulation

def run_scenario_comparison(user_data, financial_data, sim_params, base_results):
    st.subheader("📊 Scenario Comparison Tool")
    
    st.info("💡 Adjust the sliders below and click 'Run Comparison' to see how changes affect your projections")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        income_adjust = st.slider("Income Adjustment (%):", -50, 50, 0, key="income_slider")
    with col2:
        expense_adjust = st.slider("Expense Adjustment (%):", -50, 50, 0, key="expense_slider")
    with col3:
        return_adjust = st.slider("Return Rate Adjustment (%):", -5, 5, 0, key="return_slider")
    
    # FIXED: Added button to trigger comparison
    if st.button("🔄 Run Comparison", type="primary", use_container_width=True):
        with st.spinner("Running comparison scenario..."):
            # Apply adjustments
            adjusted_financial_data = financial_data.copy()
            adjusted_financial_data['total_income'] *= (1 + income_adjust / 100)
            adjusted_financial_data['total_expenses'] *= (1 + expense_adjust / 100)
            
            adjusted_sim_params = sim_params.copy()
            adjusted_sim_params['investment_return_rate'] += return_adjust
            
            try:
                adjusted_results = run_simulation(
                    age=user_data['age'],
                    partner_exists=user_data['partner_exists'],
                    partner_age=user_data['partner_age'],
                    total_income=adjusted_financial_data['total_income'],
                    total_expenses=adjusted_financial_data['total_expenses'],
                    combined_financial_assets=adjusted_financial_data['liquid_assets'],
                    primary_residence_value=adjusted_financial_data['primary_residence_value'],
                    secondary_residence_value=adjusted_financial_data['secondary_residence_value'],
                    combined_other_assets_total=adjusted_financial_data.get('other_assets', 0),
                    total_liabilities_local=adjusted_financial_data['total_liabilities'],
                    partner_liabilities=adjusted_financial_data.get('partner_liabilities', 0),
                    tax_rate=adjusted_sim_params['tax_rate'],
                    inflation_rate=adjusted_sim_params['inflation_rate'],
                    investment_return_rate=adjusted_sim_params['investment_return_rate'],
                    simulation_years=adjusted_sim_params['simulation_years'],
                    mc_iterations=0,
                    goal_costs=adjusted_financial_data.get('goal_costs', {}),
                    college_inflation_pct=4.0,
                    base_public_in=20000.0,
                    base_public_out=40000.0,
                    base_private=60000.0,
                    ira_balance=adjusted_financial_data.get('ira_balance', 0),
                    four01k_403b_balance=adjusted_financial_data.get('four01k_403b_balance', 0),
                    partner_ira_balance=adjusted_financial_data.get('partner_ira_balance', 0),
                    partner_four01k_403b_balance=adjusted_financial_data.get('partner_four01k_403b_balance', 0),
                    monthly_surplus=adjusted_financial_data.get('monthly_surplus', 0),
                    combined_total_liabilities=adjusted_financial_data['total_liabilities']
                )
                
                if adjusted_results:
                    st.success("✅ Comparison complete!")
                    
                    # Show comparison metrics
                    st.subheader("📈 Comparison Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Base Scenario")
                        st.metric("Final Savings", f"${base_results.get('final_savings', 0):,.0f}")
                        st.metric("Final Net Worth", f"${base_results.get('final_net_worth', 0):,.0f}")
                        st.metric("Years Solvent", f"{base_results.get('years_solvent', 0)}")
                        st.metric("Health Score", f"{base_results.get('health_score', 0)}/100")
                    
                    with col2:
                        st.markdown("#### Adjusted Scenario")
                        savings_delta = adjusted_results.get('final_savings', 0) - base_results.get('final_savings', 0)
                        networth_delta = adjusted_results.get('final_net_worth', 0) - base_results.get('final_net_worth', 0)
                        years_delta = adjusted_results.get('years_solvent', 0) - base_results.get('years_solvent', 0)
                        health_delta = adjusted_results.get('health_score', 0) - base_results.get('health_score', 0)
                        
                        st.metric("Final Savings", 
                                 f"${adjusted_results.get('final_savings', 0):,.0f}",
                                 delta=f"${savings_delta:,.0f}")
                        st.metric("Final Net Worth", 
                                 f"${adjusted_results.get('final_net_worth', 0):,.0f}",
                                 delta=f"${networth_delta:,.0f}")
                        st.metric("Years Solvent", 
                                 f"{adjusted_results.get('years_solvent', 0)}",
                                 delta=f"{years_delta:+d} years")
                        st.metric("Health Score", 
                                 f"{adjusted_results.get('health_score', 0)}/100",
                                 delta=f"{health_delta:+d}")
                    
                    # Chart comparison
                    import plotly.graph_objects as go
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=base_results['df']['Year'],
                        y=base_results['df']['Savings_End'],
                        mode='lines',
                        name='Base Scenario',
                        line=dict(color='blue', width=2)
                    ))
                    fig.add_trace(go.Scatter(
                        x=adjusted_results['df']['Year'],
                        y=adjusted_results['df']['Savings_End'],
                        mode='lines',
                        name='Adjusted Scenario',
                        line=dict(color='red', width=2, dash='dash')
                    ))
                    fig.update_layout(
                        title="Savings Projection Comparison",
                        xaxis_title="Year",
                        yaxis_title="Savings ($)",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Store for download
                    st.session_state['comparison_results'] = adjusted_results
                    
                    return adjusted_results
                else:
                    st.error("Comparison returned no results")
                    return None
                    
            except Exception as e:
                st.error(f"Comparison failed: {str(e)}")
                return None
    
    return None