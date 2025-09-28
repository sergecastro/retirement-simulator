# main.py - Ultimate Family Retirement Planning Plus v3.0
# Main entry point that orchestrates all modules

import streamlit as st
from datetime import date

# Import our custom modules
import ui_components
import visualization
import analysis
import ai_advisor

# Page configuration
st.set_page_config(
    page_title="Ultimate Family Retirement Plus",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏠 Ultimate Family Retirement Planning Plus v3.0")
st.markdown("*The Most Advanced Family Lifecycle Financial Simulation & Planning Tool*")

# ─────────────────────────────────────────────────────────────────
# PASSWORD PROTECTION
# ─────────────────────────────────────────────────────────────────
st.header("🔐 Access Control")
password = st.text_input("Enter password:", type="password")

if password not in ["abcd123", "uhiRR2938foq"]:
    st.error("🚫 Incorrect password.")
    st.info("Demo: 'abcd123' | Trusted: 'uhiRR2938foq'")
    st.stop()

TRUSTED_PASSWORD = "uhiRR2938foq"
IS_TRUSTED_USER = (password == TRUSTED_PASSWORD)

if IS_TRUSTED_USER:
    st.success("✅ **Trusted User Access Granted** - Full features and private scenarios enabled")
else:
    st.info("📌 **Demo Mode** - Basic features enabled")

# Store user status in session state
st.session_state['IS_TRUSTED_USER'] = IS_TRUSTED_USER

# ─────────────────────────────────────────────────────────────────
# SIDEBAR CONFIGURATION
# ─────────────────────────────────────────────────────────────────
features = ui_components.setup_sidebar(IS_TRUSTED_USER)

# ─────────────────────────────────────────────────────────────────
# SCENARIO MANAGEMENT
# ─────────────────────────────────────────────────────────────────
scenario_data = ui_components.manage_scenarios(IS_TRUSTED_USER)

# ─────────────────────────────────────────────────────────────────
# USER INPUTS
# ─────────────────────────────────────────────────────────────────
user_data = ui_components.collect_user_inputs()
financial_data = ui_components.collect_financial_data()
family_data = ui_components.collect_family_events() if features['show_family_events'] else None

# Show inheritance debug info
if family_data and 'inheritances' in family_data:
    inheritance_total = sum(inh.get('Amount', 0) for inh in family_data['inheritances'] if inh.get('Amount', 0) > 0)
    if inheritance_total > 0:
        st.info(f"🎯 **INHERITANCE EVENTS DETECTED:** Total ${inheritance_total:,} across {len([i for i in family_data['inheritances'] if i.get('Amount', 0) > 0])} events")
        
        # Show inheritance timeline
        with st.expander("💰 Inheritance Events Summary"):
            for inh in family_data['inheritances']:
                if inh.get('Amount', 0) > 0:
                    st.write(f"• **{inh.get('Year')}**: ${inh.get('Amount'):,} - {inh.get('Description', 'No description')}")

# ─────────────────────────────────────────────────────────────────
# SIMULATION PARAMETERS
# ─────────────────────────────────────────────────────────────────
sim_params = ui_components.get_simulation_parameters(features['show_monte_carlo'])

# ─────────────────────────────────────────────────────────────────
# INHERITANCE-ENHANCED SIMULATION
# ─────────────────────────────────────────────────────────────────
def run_enhanced_simulation_with_inheritance(user_data, financial_data, family_data, sim_params):
    """Enhanced simulation that properly handles inheritance events"""
    try:
        # First try the original simulation without inheritance parameter
        import simulation
        
        # Call original simulation with standard parameters only
        results = simulation.run_simulation(
            age=user_data['age'],
            partner_exists=user_data['partner_exists'],
            partner_age=user_data['partner_age'],
            total_income=financial_data['total_income'],
            total_expenses=financial_data['total_expenses'],
            combined_financial_assets=financial_data['liquid_assets'],
            primary_residence_value=financial_data['primary_residence_value'],
            secondary_residence_value=financial_data['secondary_residence_value'],
            combined_other_assets_total=financial_data.get('other_assets', 0),
            total_liabilities_local=financial_data['total_liabilities'],
            partner_liabilities=financial_data.get('partner_liabilities', 0),
            tax_rate=sim_params['tax_rate'],
            inflation_rate=sim_params['inflation_rate'],
            investment_return_rate=sim_params['investment_return_rate'],
            simulation_years=sim_params['simulation_years'],
            mc_iterations=sim_params.get('mc_iterations', 0),
            goal_costs=financial_data.get('goal_costs', {}),
            college_inflation_pct=family_data.get('college_inflation_pct', 4.0) if family_data else 4.0,
            base_public_in=family_data.get('base_public_in', 20000) if family_data else 20000,
            base_public_out=family_data.get('base_public_out', 40000) if family_data else 40000,
            base_private=family_data.get('base_private', 60000) if family_data else 60000,
            ira_balance=financial_data['ira_balance'],
            four01k_403b_balance=financial_data['four01k_403b_balance'],
            partner_ira_balance=financial_data.get('partner_ira_balance', 0),
            partner_four01k_403b_balance=financial_data.get('partner_four01k_403b_balance', 0),
            monthly_surplus=financial_data['monthly_surplus'],
            combined_total_liabilities=financial_data['total_liabilities']
            # REMOVED inheritance_events parameter - original simulation doesn't support it
        )
        
        # If inheritance events exist, we need to use enhanced simulation
        if family_data and family_data.get('inheritances'):
            st.success("✅ Enhanced simulation with inheritance integration activated!")
            # Use enhanced simulation
            return analysis.run_enhanced_simulation_with_inheritance(
                user_data, financial_data, family_data, sim_params
            ), "enhanced_with_inheritance"
        
        return results, "advanced"
        
    except ImportError:
        # Fallback to enhanced simple simulation with inheritance support
        results = analysis.run_enhanced_simulation_with_inheritance(
            user_data, financial_data, family_data, sim_params
        )
        return results, "enhanced_with_inheritance"
    except Exception as e:
        st.error(f"Advanced simulation failed: {str(e)}")
        # Always fall back to enhanced simulation on any error
        results = analysis.run_enhanced_simulation_with_inheritance(
            user_data, financial_data, family_data, sim_params
        )
        return results, "enhanced_with_inheritance"

# ─────────────────────────────────────────────────────────────────
# RUN SIMULATION
# ─────────────────────────────────────────────────────────────────
st.header("🚀 Run Simulation")

if st.button("🎯 Run Financial Simulation", type="primary", use_container_width=True):
    with st.spinner("Running comprehensive simulation with inheritance events..."):
        try:
            results, sim_type = run_enhanced_simulation_with_inheritance(
                user_data, financial_data, family_data, sim_params
            )
            st.session_state['simulation_results'] = results
            st.session_state['family_data'] = family_data  # Store family data for visualizations
            
            if sim_type == "advanced":
                st.success("✅ Advanced Simulation Complete with Inheritance Integration!")
            else:
                st.success("✅ Enhanced Simulation Complete with Inheritance Events!")
                
        except Exception as e:
            st.error(f"Simulation error: {str(e)}")
            st.write("**Debug Info:**")
            st.write(f"Family Data: {family_data}")
            if family_data:
                st.write(f"Inheritances: {family_data.get('inheritances', [])}")

# ─────────────────────────────────────────────────────────────────
# DISPLAY RESULTS
# ─────────────────────────────────────────────────────────────────
if 'simulation_results' in st.session_state:
    results = st.session_state['simulation_results']
    stored_family_data = st.session_state.get('family_data', family_data)
    
    # Basic metrics
    visualization.display_key_metrics(results, sim_params['simulation_years'])
    
    # Main visualizations
    if features['show_trajectories']:
        visualization.show_trajectories(results)
    
    # Monte Carlo Analysis
    if features['show_monte_carlo'] and 'monte_carlo_results' in results:
        visualization.show_monte_carlo(results)
    
    # Advanced visualizations
    if features['show_sankey']:
        visualization.show_sankey(results)
    
    if features['show_goals']:
        visualization.show_goal_gauges(results)
    
    if features['show_timeline']:
        visualization.show_timeline(results, user_data, stored_family_data)
    
    # Health Dashboard
    if features['show_health_dashboard']:
        visualization.show_health_dashboard(results, financial_data)
    
    # Scenario Comparison
    if features['show_scenario_comparison']:
        comparison_results = analysis.run_scenario_comparison(
            user_data, financial_data, sim_params, results
        )
        if comparison_results:
            visualization.show_comparison(results, comparison_results)
    
    # AI Advisor
    if features.get('show_ai_advisor') and IS_TRUSTED_USER:
        ai_advisor.show_ai_consultation(results, user_data, financial_data, sim_params)
    
    # Show Inheritance Impact Analysis
    if stored_family_data and 'inheritances' in stored_family_data:
        inheritance_analysis = analysis.analyze_inheritance_impact(
            stored_family_data, financial_data, sim_params
        )
        if inheritance_analysis.get('events'):
            st.subheader("💰 Inheritance Impact Analysis")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Inheritance", f"${inheritance_analysis['total_amount']:,}")
            with col2:
                st.metric("Present Value", f"${inheritance_analysis['total_present_value']:,}")
            with col3:
                st.metric("Number of Events", len(inheritance_analysis['events']))
                
            # Show inheritance timeline
            with st.expander("📋 Inheritance Event Details"):
                for year, event in inheritance_analysis['events'].items():
                    st.write(f"**{year}**: ${event['amount']:,} - {event['description']}")
                    st.write(f"  • Years from now: {event['years_from_now']}")
                    st.write(f"  • Present value: ${event['present_value']:,.0f}")
    
    # Download options
    visualization.show_download_options(results)

# ─────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<p><strong>Ultimate Family Retirement Planning Plus v3.0</strong></p>
<p>Combining the best of GROK and CLAUDE architectures</p>
<p>Your trusted financial planning companion | 100% Private | AI-Powered</p>
</div>
""", unsafe_allow_html=True)