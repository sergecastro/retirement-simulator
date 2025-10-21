# app.py - COMPLETE FULL VERSION - Widget State Fixed - NO TRUNCATION
import streamlit as st
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from financial_utils import get_all_inputs_as_dict, display_summary_metrics
from pages.user_inputs import setup_sidebar
from pages.financial_inputs import collect_financial_data
from pages.family_inputs import collect_family_events
from data_manager_cloud import manage_scenarios_cloud as manage_scenarios, apply_scenario_data_safe
from simulation_core import run_simulation
from household_events import build_child_objects, build_inheritances
from basic_analysis import run_simple_fallback_simulation, calculate_simple_health_score
from monte_carlo import run_simple_monte_carlo
from scenario_tools import run_scenario_comparison
from visualization.charts_basic import show_trajectories, show_health_dashboard
from visualization.charts_advanced import show_monte_carlo, show_sankey
from visualization.timeline import show_timeline, show_goal_gauges, show_download_options, show_detailed_projection_table
from visualization.longevity_analysis import show_longevity_analysis
from visualization.irmaa_analysis import show_irmaa_analysis
from integration.intake_loader import intake_import_ui
from streamlit_explain_api import inject_explain_visual_system

# Import intake module for Data Entry mode
from intake_integrated import show_intake_questionnaire

# Page config
st.set_page_config(page_title="Ultimate Family Retirement Plus", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

# PROFESSIONAL CSS STYLING
st.markdown("""
<style>
    /* Compact headers */
    h1 {
        padding-top: 0rem !important;
        padding-bottom: 0.5rem !important;
    }
    h2 {
        padding-top: 0.5rem !important;
        padding-bottom: 0.25rem !important;
    }
    h3 {
        padding-top: 0.25rem !important;
        padding-bottom: 0.25rem !important;
    }

    /* Reduce spacing between elements */
    .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* Make metrics look professional */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
    }

    /* Tighter spacing for columns */
    .row-widget {
        gap: 0.5rem !important;
    }

    /* Clean separator lines */
    hr {
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# CHECK FLASK SERVER CONNECTION (does NOT auto-start)
import os
import socket

def check_flask_connection():
    """Check if Flask explanation server is running"""
    try:
        # Get Flask API URL from secrets (cloud) or environment (local)
        api_url = os.getenv('FLASK_API_URL', 'http://localhost:5000')

        # If using Streamlit secrets, prefer that
        if hasattr(st, 'secrets') and 'FLASK_API_URL' in st.secrets:
            api_url = st.secrets['FLASK_API_URL']

        # For cloud URLs, use HTTP health check instead of socket
        if api_url.startswith('http'):
            import requests
            response = requests.get(f"{api_url}/health", timeout=3)
            return response.status_code == 200
        else:
            # Fallback to socket for localhost
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', 5000))
                return result == 0
    except:
        return False

# Show warning if Flask is not running (but don't block the app)
if not check_flask_connection():
    st.warning("""
    ⚠️ **Claude Explanation API Not Running**
    
    The "?" buttons on charts won't work without the explanation server.
    
    **To enable chart explanations:**
    1. Open a new terminal/command prompt
    2. Navigate to your project folder
    3. Run: `start_flask_server.bat` (or `python explain_api_server.py`)
    4. Refresh this page
    
    The app will work normally - you just won't have AI explanations for charts.
    """)

# Initialize authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'IS_TRUSTED_USER' not in st.session_state:
    st.session_state.IS_TRUSTED_USER = False

# Show password screen ONLY if not authenticated
if not st.session_state.authenticated:
    st.title("🏠 Ultimate Family Retirement Planning Plus v3.0")
    st.markdown("*The Most Advanced Family Lifecycle Financial Simulation & Planning Tool*")

    # Password protection
    st.header("🔒 Access Control")
    st.markdown("Enter your password to access the retirement planning tools.")

    # Show demo password only
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px; margin: 10px 0;'>
        <p style='margin: 0; color: #666; font-size: 14px;'><strong>Demo Access:</strong></p>
        <p style='margin: 5px 0 0 0; font-size: 20px; font-family: monospace;'>
            Password: <code style='background: #fff; padding: 5px 10px; border-radius: 3px; font-size: 20px;'>abcd123</code>
        </p>
    </div>
    """, unsafe_allow_html=True)

    password = st.text_input("Enter password:", type="password", placeholder="Type or paste password here")

    # Only show error if user actually entered something wrong
    if password and password not in ["abcd123", "uhiRR2938foq"]:
        st.error("🚫 Incorrect password. Please try again.")
        st.stop()
    elif not password:
        st.info("👆 Please enter a password to continue")
        st.stop()
    else:
        # Password correct - authenticate!
        st.session_state.authenticated = True
        st.session_state.IS_TRUSTED_USER = (password == "uhiRR2938foq")
        st.rerun()

# User is authenticated - get IS_TRUSTED_USER from session state
IS_TRUSTED_USER = st.session_state.IS_TRUSTED_USER

# Initialize mode in session state if not exists
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = None  # Not chosen yet

# Initialize intake_in_progress flag
if 'intake_in_progress' not in st.session_state:
    st.session_state.intake_in_progress = False

# ========== MODE SELECTOR (Only show if mode not chosen OR if explicitly requested) ==========
# Don't show mode selector if user is in the middle of Intake
if st.session_state.app_mode is None and not st.session_state.intake_in_progress:
    # First time - show access level
    if IS_TRUSTED_USER:
        st.success("✅ Trusted User Access Granted - Full features enabled")
    else:
        st.info("📌 Demo Mode - Basic features enabled")

    st.divider()
    st.header("🚀 Choose Your Mode")
    st.markdown("""
    Select how you'd like to use the app:
    - **📝 Data Entry Mode**: Step-by-step questionnaire to enter all your financial information
    - **📊 Analysis Mode**: Run simulations, view charts, and use AI advisor (main app)
    """)

    # Mode selector buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Data Entry Mode", use_container_width=True, type="secondary"):
            st.session_state.app_mode = 'Data Entry'
            st.session_state.intake_in_progress = True  # Mark that user is entering Intake
            st.rerun()
    with col2:
        if st.button("📊 Analysis Mode", use_container_width=True, type="primary"):
            st.session_state.app_mode = 'Analysis'
            st.rerun()

    st.stop()  # Don't proceed until user chooses

st.divider()

# ========== ROUTE TO APPROPRIATE MODE ==========
if st.session_state.app_mode == 'Data Entry':
    # Call the intake questionnaire module (separate file)
    show_intake_questionnaire()
    st.stop()  # Stop here, don't load main app

# If we reach here, we're in Analysis Mode - continue with main app as normal

# AUTO-LOAD INTAKE DATA if user just completed Intake questionnaire
if st.session_state.get('intake_just_completed', False):
    import json
    from pathlib import Path
    from data_manager_cloud import apply_scenario_data_safe

    # Clear the flag
    st.session_state.intake_just_completed = False

    # Load the intake data
    current_dir = os.getcwd()
    root_dir = Path(current_dir).parent
    intake_path = root_dir / "SHARED" / "intake_payload.json"

    if intake_path.exists():
        try:
            with open(intake_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Apply the data to session state
            apply_scenario_data_safe(data)

            # Load custom_expenses if exists
            if "custom_expenses" in data:
                st.session_state['custom_expenses'] = data['custom_expenses']
            else:
                st.session_state['custom_expenses'] = []

            # Set scenario name
            st.session_state["current_scenario"] = "Imported from Intake"
            st.session_state['scenario_loaded'] = True

            # CELEBRATION BALLOONS! 🎉
            st.balloons()

            st.success("🎉 **Congratulations!** Your Intake data has been automatically loaded!")
            st.info("💡 You can now review your data below and run simulations.")
        except Exception as e:
            st.error(f"❌ Error loading Intake data: {e}")

# Subtle mode switcher at top (for Analysis mode)
with st.container():
    col1, col2, col3 = st.columns([6, 1, 1])
    with col2:
        if st.button("📝 Data Entry", help="Switch to Data Entry Mode", use_container_width=True):
            st.session_state.app_mode = 'Data Entry'
            st.session_state.intake_in_progress = True
            st.rerun()
    with col3:
        st.markdown("**📊 Analysis**")
    st.divider()

# Inject Explain Visual system (Claude-powered chart explanations)
inject_explain_visual_system()


# CRITICAL FIX: Load scenarios AFTER intake to respect imported scenarios
age_group_for_autoload = st.session_state.get('input_age_group', '70+')
# For deployment: intake_import_ui uses file uploader (no shared dir needed)
intake_import_ui(shared_dir="")
scenario_data = manage_scenarios(IS_TRUSTED_USER, age_group_for_autoload)



# User inputs that read from loaded session state
def collect_user_inputs():
    """Collect user inputs reading from loaded scenario data"""
    st.header("👤 User Profile")

    # Welcome message
    st.markdown("""
    **Welcome!** Please review and update your information below. Make any necessary corrections
    before running your simulation to ensure accurate results.
    """)

    col1, col2 = st.columns(2)

    with col1:
        # User name field
        user_name = st.text_input(
            "Your Name:",
            value=st.session_state.get('input_user_name', ''),
            placeholder="Enter your name",
            key="input_user_name"
        )

        age_group_options = ["25-55", "56-69", "70+"]
        current_age_group = st.session_state.get('input_age_group', '70+')
        try:
            age_group_index = age_group_options.index(current_age_group)
        except ValueError:
            age_group_index = 2  # Default to 70+

        age_group = st.selectbox("Age Group:", age_group_options, index=age_group_index, key="input_age_group")

        age = st.number_input(
            "Your Age:",
            min_value=18,
            max_value=100,
            value=int(st.session_state.get('input_age', 76)),
            key="input_age"
        )

    with col2:
        # Always show partner fields - leave empty if no partner
        partner_name = st.text_input(
            "Partner's Name:",
            value=st.session_state.get('input_partner_name', ''),
            placeholder="Leave empty if no partner",
            key="input_partner_name"
        )

        partner_age = st.number_input(
            "Partner's Age:",
            min_value=18,
            max_value=100,
            value=int(st.session_state.get('input_partner_age', 0)) if st.session_state.get('input_partner_age', 0) > 0 else 35,
            key="input_partner_age",
            help="Leave at default or set to 0 if no partner"
        )

    # Determine if partner exists based on whether name is filled
    partner_exists = bool(partner_name and partner_name.strip())

    return {
        'age_group': age_group,
        'age': age,
        'partner_exists': partner_exists,
        'partner_name': partner_name,
        'partner_age': partner_age,
        'user_name': user_name
    }

# Collect user data first (needed for manage_scenarios)
user_data = collect_user_inputs()

# Show currently loaded scenario prominently
current_scenario = st.session_state.get('current_scenario', 'New Scenario')
if current_scenario != "New Scenario":
    st.info(f"📋 **Currently Loaded**: {current_scenario}")
    
    # Show loaded data confirmation
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Age", f"{st.session_state.get('input_age', 'N/A')}")
    with col2:
        partner_name_display = st.session_state.get('input_partner_name', 'None')
        st.metric("Partner", partner_name_display if partner_name_display else "None")
    with col3:
        st.metric("Income", f"${st.session_state.get('input_total_income', 0):,.0f}")
    with col4:
        st.metric("Expenses", f"${st.session_state.get('input_total_expenses', 0):,.0f}")

# Sidebar features
features = setup_sidebar(IS_TRUSTED_USER)

# Financial and family inputs (these will read from loaded session state)
financial_data = collect_financial_data()

# PROFESSIONAL DASHBOARD - Always visible
st.markdown("---")
st.subheader("📊 Financial Snapshot")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    annual_income = financial_data['total_income']
    st.metric("Annual Income", f"${annual_income:,.0f}", delta=None, help="Total annual income from all sources")

with col2:
    annual_expenses = financial_data['total_expenses']
    st.metric("Annual Expenses", f"${annual_expenses:,.0f}", delta=None, help="Total annual expenses")

with col3:
    monthly_surplus = financial_data['monthly_surplus']
    surplus_color = "normal" if monthly_surplus >= 0 else "inverse"
    st.metric("Monthly Cash Flow", f"${monthly_surplus:,.0f}", delta=None, help="Monthly income minus expenses")

with col4:
    total_assets = financial_data['liquid_assets'] + financial_data['primary_residence_value'] + financial_data.get('secondary_residence_value', 0)
    net_worth = total_assets - financial_data['total_liabilities']
    st.metric("Net Worth", f"${net_worth:,.0f}", delta=None, help="Assets minus liabilities")

with col5:
    emergency_months = financial_data['liquid_assets'] / (annual_expenses / 12) if annual_expenses > 0 else 0
    st.metric("Emergency Fund", f"{emergency_months:.1f} mo", delta=None, help="Months of expenses covered by liquid assets")

st.markdown("---")

family_data = collect_family_events() if features.get('show_family_events', False) else None

if family_data:
    st.session_state["children_rows"] = family_data['children']
    st.session_state["inherit_rows"] = family_data['inheritances']
    inheritance_total = sum(inh.get('Amount', 0) for inh in family_data['inheritances'] if inh.get('Amount', 0) > 0)
    if inheritance_total > 0:
        st.info(f"🎯 INHERITANCE EVENTS DETECTED: Total ${inheritance_total:,} across events")
        with st.expander("💰 Inheritance Summary"):
            for inh in family_data['inheritances']:
                if inh.get('Amount', 0) > 0:
                    st.write(f"• {inh.get('Year')}: ${inh.get('Amount'):,} - {inh.get('Description', 'No description')}")

# Simulation params (read from loaded session state)
st.header("⚙️ Simulation Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    tax_rate = st.number_input("Tax Rate (%):", value=float(st.session_state.get('input_tax_rate', 25.0)), key="input_tax_rate")
    inflation_rate = st.number_input("Inflation (%):", value=float(st.session_state.get('input_inflation_rate', 2.5)), key="input_inflation_rate")
with col2:
    return_rate = st.number_input("Return Rate (%):", value=float(st.session_state.get('input_investment_return_rate', 5.0)), key="input_investment_return_rate")
    years = st.number_input("Years:", value=int(st.session_state.get('input_simulation_years', 14)), key="input_simulation_years")
with col3:
    mc_iters = st.number_input("Monte Carlo Iterations:", value=int(st.session_state.get('input_mc_iterations', 1000)), min_value=0, key="input_mc_iterations") if features.get('show_monte_carlo') else 0

sim_params = {
    'tax_rate': tax_rate,
    'inflation_rate': inflation_rate,
    'investment_return_rate': return_rate,
    'simulation_years': years,
    'mc_iterations': mc_iters
}

# FIXED: Run simulation with proper error handling and DEBUG output

# Add this to app.py in the "Run Financial Simulation" button section
# Replace the existing button handler (around line 160-220)


   
if st.button("🎯 Run Financial Simulation", type="primary", use_container_width=True):
    with st.spinner("Running simulation..."):
        try:
            # Save current state before running
            stored_user_data = user_data
            stored_financial_data = financial_data
            stored_family_data = family_data if family_data else {}
            stored_sim_params = sim_params

            # Run the simulation with collected data
            results = run_simulation(
                age=stored_user_data['age'],
                partner_exists=stored_user_data['partner_exists'],
                partner_age=stored_user_data['partner_age'],
                total_income=stored_financial_data['total_income'],
                total_expenses=stored_financial_data['total_expenses'],
                combined_financial_assets=stored_financial_data['liquid_assets'],
                primary_residence_value=stored_financial_data['primary_residence_value'],
                secondary_residence_value=stored_financial_data['secondary_residence_value'],
                combined_other_assets_total=stored_financial_data.get('other_assets', 0),
                total_liabilities_local=stored_financial_data['total_liabilities'],
                partner_liabilities=stored_financial_data.get('partner_liabilities', 0),
                tax_rate=stored_sim_params['tax_rate'],
                inflation_rate=stored_sim_params['inflation_rate'],
                investment_return_rate=stored_sim_params['investment_return_rate'],
                simulation_years=stored_sim_params['simulation_years'],
                mc_iterations=stored_sim_params['mc_iterations'],
                goal_costs=stored_financial_data['goal_costs'],
                college_inflation_pct=stored_family_data.get('college_inflation_pct', 4.0),
                base_public_in=stored_family_data.get('base_public_in', 20000),
                base_public_out=stored_family_data.get('base_public_out', 40000),
                base_private=stored_family_data.get('base_private', 60000),
                ira_balance=stored_financial_data['ira_balance'],
                four01k_403b_balance=stored_financial_data['four01k_403b_balance'],
                partner_ira_balance=stored_financial_data.get('partner_ira_balance', 0),
                partner_four01k_403b_balance=stored_financial_data.get('partner_four01k_403b_balance', 0),
                monthly_surplus=stored_financial_data['monthly_surplus'],
                combined_total_liabilities=stored_financial_data['total_liabilities'],
                custom_expenses_total=stored_financial_data.get('custom_expenses_total', 0.0)
            )
            
                       

            # Check if results were returned
            if results is not None:
                st.session_state['simulation_results'] = results
                st.session_state['family_data'] = family_data
                st.session_state['financial_data'] = financial_data
                st.session_state['user_data'] = user_data
                st.session_state['sim_params'] = sim_params  # Store sim params for comparison
                st.success("✅ Simulation Complete!")

                # Info about AI chart explanations
                st.info("💡 **AI Chart Explanations**: Click any chart below to activate the **?** buttons (or wait ~20 seconds for auto-load), then click **?** to get AI-powered insights about your data!")

                # Show Monte Carlo status
                if 'monte_carlo_results' in results:
                    st.success("✅ Fresh Monte Carlo data generated - longevity analysis will be accurate")
                else:
                    st.info("ℹ️ Monte Carlo not run - enable in parameters for longevity analysis")

                display_summary_metrics(results, sim_params['simulation_years'])
            else:
                st.error("❌ Simulation returned no results")
                
        except Exception as e:
            st.error(f"❌ Simulation error: {str(e)}")
            st.info("💡 **Tip**: Check your inputs and try again. If the problem persists, try loading a saved scenario or starting fresh.")



# FIXED: Display results with proper variable scoping
if 'simulation_results' in st.session_state:
    results = st.session_state['simulation_results']
    
    # INJECT CHART REGISTRY AFTER CHARTS ARE CREATED
    if '__chart_registry__' in st.session_state and st.session_state['__chart_registry__']:
        import json
        registry_json = json.dumps(st.session_state['__chart_registry__'])
        st.components.v1.html(f"""
        <script>
        window.parent.__CHART_DATA_REGISTRY__ = {registry_json};
        console.log('[Injected After Charts] Registry:', window.parent.__CHART_DATA_REGISTRY__);
        </script>
        """, height=0)
    stored_family_data = st.session_state.get('family_data')
    stored_financial_data = st.session_state.get('financial_data')
    stored_user_data = st.session_state.get('user_data')
    stored_sim_params = st.session_state.get('sim_params', sim_params)
    
    # Ensure we have valid results before proceeding
    if results is not None:
        st.markdown("---")
        st.header("📊 Simulation Results & Analysis")
        
        # ============================================
        # DETAILED PROJECTION TABLE
        # ============================================
        try:
            show_detailed_projection_table(results)
        except Exception as e:
            st.error(f"Detailed table error: {str(e)}")
        
        st.markdown("---")
        
        # Financial trajectories
        try:
            if features.get('show_trajectories'):
                show_trajectories(results)
        except Exception as e:
            st.error(f"Trajectories error: {str(e)}")
        
        # Monte Carlo
        try:
            if features.get('show_monte_carlo') and 'monte_carlo_results' in results:
                show_monte_carlo(results)
        except Exception as e:
            st.error(f"Monte Carlo error: {str(e)}")
            
        # Longevity Analysis (NEW!)
        try:
            if features.get('show_monte_carlo') and 'monte_carlo_results' in results:
                st.markdown("---")
                show_longevity_analysis(results, stored_user_data, stored_sim_params)
        except Exception as e:
            st.error(f"Longevity analysis error: {str(e)}")
        
        # IRMAA Medicare Planning Analysis (NEW!)
        try:
            st.markdown("---")
            show_irmaa_analysis(results, stored_user_data, stored_sim_params)
        except Exception as e:
            st.error(f"IRMAA analysis error: {str(e)}")
        
        
        
        
        # Sankey diagram
        try:
            if features.get('show_sankey'):
                show_sankey(results)
        except Exception as e:
            st.error(f"Sankey error: {str(e)}")
        
        # Goal gauges
        try:
            if features.get('show_goals'):
                show_goal_gauges(results)
        except Exception as e:
            st.error(f"Goals error: {str(e)}")
        
        # Timeline
        try:
            if features.get('show_timeline'):
                show_timeline(results, stored_user_data, stored_family_data)
        except Exception as e:
            st.error(f"Timeline error: {str(e)}")
        
        # Health dashboard
        try:
            if features.get('show_health_dashboard'):
                show_health_dashboard(
                    stored_financial_data['liquid_assets'], 
                    stored_financial_data['total_expenses'], 
                    stored_financial_data['total_income'], 
                    stored_financial_data['total_liabilities'], 
                    results
                )
        except Exception as e:
            st.error(f"Health dashboard error: {str(e)}")
        
        # ============================================
        # SCENARIO COMPARISON TOOL - COMPLETE VERSION
        # ============================================
        try:
            if features.get('show_scenario_comparison'):
                st.markdown("---")
                st.subheader("📊 Scenario Comparison Tool")
                st.info("💡 Adjust sliders and click 'Run Comparison' to see how changes affect projections")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    income_adj = st.slider("Income Adjustment (%):", -100, 100, 0, key="comp_income")
                with col2:
                    expense_adj = st.slider("Expense Adjustment (%):", -100, 100, 0, key="comp_expense")
                with col3:
                    return_adj = st.slider("Return Rate Adjustment (%):", -10, 10, 0, key="comp_return")
                
                if st.button("🔄 Run Comparison", key="run_comparison_btn", type="primary"):
                    # Calculate adjusted values
                    adj_income = stored_financial_data['total_income'] * (1 + income_adj/100)
                    adj_expenses = stored_financial_data['total_expenses'] * (1 + expense_adj/100)
                    adj_return = stored_sim_params['investment_return_rate'] + return_adj
                    
                    st.write(f"**Adjustments Applied:**")
                    st.write(f"• Base Income: ${stored_financial_data['total_income']:,.0f} → Adjusted: ${adj_income:,.0f} ({income_adj:+.0f}%)")
                    st.write(f"• Base Expenses: ${stored_financial_data['total_expenses']:,.0f} → Adjusted: ${adj_expenses:,.0f} ({expense_adj:+.0f}%)")
                    st.write(f"• Base Return: {stored_sim_params['investment_return_rate']:.1f}% → Adjusted: {adj_return:.1f}% ({return_adj:+.1f}%)")
                    
                    with st.spinner("Running comparison scenario..."):
                        comp_results = run_simulation(
                            age=stored_user_data['age'],
                            partner_exists=stored_user_data['partner_exists'],
                            partner_age=stored_user_data['partner_age'],
                            total_income=adj_income,
                            total_expenses=adj_expenses,
                            combined_financial_assets=stored_financial_data['liquid_assets'],
                            primary_residence_value=stored_financial_data['primary_residence_value'],
                            secondary_residence_value=stored_financial_data['secondary_residence_value'],
                            combined_other_assets_total=stored_financial_data.get('other_assets', 0),
                            total_liabilities_local=stored_financial_data['total_liabilities'],
                            partner_liabilities=0,
                            tax_rate=stored_sim_params['tax_rate'],
                            inflation_rate=stored_sim_params['inflation_rate'],
                            investment_return_rate=adj_return,
                            simulation_years=stored_sim_params['simulation_years'],
                            mc_iterations=0,
                            goal_costs={},
                            college_inflation_pct=4.0,
                            base_public_in=20000, base_public_out=40000, base_private=60000,
                            ira_balance=stored_financial_data['ira_balance'],
                            four01k_403b_balance=stored_financial_data['four01k_403b_balance'],
                            partner_ira_balance=stored_financial_data.get('partner_ira_balance', 0),
                            partner_four01k_403b_balance=stored_financial_data.get('partner_four01k_403b_balance', 0),
                            monthly_surplus=adj_income - adj_expenses,
                            combined_total_liabilities=stored_financial_data['total_liabilities']
                        )
                        
                        if comp_results:
                            st.success("✅ Comparison complete!")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("#### Base Scenario")
                                st.metric("Final Savings", f"${results['final_savings']:,.0f}")
                                st.metric("Final Net Worth", f"${results['final_net_worth']:,.0f}")
                                st.metric("Years Solvent", f"{results['years_solvent']}")
                            with col2:
                                st.markdown("#### Adjusted Scenario")
                                delta_savings = comp_results['final_savings'] - results['final_savings']
                                delta_nw = comp_results['final_net_worth'] - results['final_net_worth']
                                delta_years = comp_results['years_solvent'] - results['years_solvent']
                                st.metric("Final Savings", f"${comp_results['final_savings']:,.0f}", delta=f"${delta_savings:,.0f}")
                                st.metric("Final Net Worth", f"${comp_results['final_net_worth']:,.0f}", delta=f"${delta_nw:,.0f}")
                                st.metric("Years Solvent", f"{comp_results['years_solvent']}", delta=f"{delta_years:+d} years")
                            
                            # Comparison chart
                            import plotly.graph_objects as go
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=results['df']['Year'],
                                y=results['df']['Savings_End'],
                                mode='lines',
                                name='Base Scenario',
                                line=dict(color='blue', width=3)
                            ))
                            fig.add_trace(go.Scatter(
                                x=comp_results['df']['Year'],
                                y=comp_results['df']['Savings_End'],
                                mode='lines',
                                name='Adjusted Scenario',
                                line=dict(color='red', width=3, dash='dash')
                            ))
                            fig.update_layout(
                                title="Savings Trajectory Comparison",
                                xaxis_title="Year",
                                yaxis_title="Savings ($)",
                                height=500
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error("❌ Comparison failed to generate results")
        except Exception as e:
            st.error(f"Scenario comparison error: {str(e)}")
        
        # ============================================
        # DUAL SCENARIO ANALYSIS - COMPLETE VERSION
        # ============================================
        try:
            if features.get('show_scenario_comparison'):
                st.markdown("---")
                st.subheader("🔀 Dual Scenario Analysis")
                st.info("Compare WITH vs WITHOUT major life events (inheritances, college costs)")
                
                if st.button("📊 Run Dual Analysis", key="run_dual_btn", type="primary"):
                    with st.spinner("Running dual scenario analysis..."):
                        # Save current family events
                        saved_children = st.session_state.get('children_rows', [])
                        saved_inherit = st.session_state.get('inherit_rows', [])
                        
                        # Temporarily clear for "without" scenario
                        st.session_state['children_rows'] = []
                        st.session_state['inherit_rows'] = []
                        
                        # Run without events
                        without_results = run_simulation(
                            age=stored_user_data['age'],
                            partner_exists=stored_user_data['partner_exists'],
                            partner_age=stored_user_data['partner_age'],
                            total_income=stored_financial_data['total_income'],
                            total_expenses=stored_financial_data['total_expenses'],
                            combined_financial_assets=stored_financial_data['liquid_assets'],
                            primary_residence_value=stored_financial_data['primary_residence_value'],
                            secondary_residence_value=stored_financial_data['secondary_residence_value'],
                            combined_other_assets_total=stored_financial_data.get('other_assets', 0),
                            total_liabilities_local=stored_financial_data['total_liabilities'],
                            partner_liabilities=0,
                            tax_rate=stored_sim_params['tax_rate'],
                            inflation_rate=stored_sim_params['inflation_rate'],
                            investment_return_rate=stored_sim_params['investment_return_rate'],
                            simulation_years=stored_sim_params['simulation_years'],
                            mc_iterations=0,
                            goal_costs={},
                            college_inflation_pct=4.0,
                            base_public_in=20000, base_public_out=40000, base_private=60000,
                            ira_balance=stored_financial_data['ira_balance'],
                            four01k_403b_balance=stored_financial_data['four01k_403b_balance'],
                            partner_ira_balance=0,
                            partner_four01k_403b_balance=0,
                            monthly_surplus=stored_financial_data['monthly_surplus'],
                            combined_total_liabilities=stored_financial_data['total_liabilities']
                        )
                        
                        # Restore family events
                        st.session_state['children_rows'] = saved_children
                        st.session_state['inherit_rows'] = saved_inherit
                        
                        if without_results:
                            st.success("✅ Dual analysis complete!")
                            
                            # Show comparison chart
                            import plotly.graph_objects as go
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=results['df']['Year'], 
                                y=results['df']['Savings_End'],
                                mode='lines', 
                                name='With Life Events', 
                                line=dict(color='green', width=3)
                            ))
                            fig.add_trace(go.Scatter(
                                x=without_results['df']['Year'], 
                                y=without_results['df']['Savings_End'],
                                mode='lines', 
                                name='Without Life Events', 
                                line=dict(color='orange', width=3, dash='dot')
                            ))
                            fig.update_layout(
                                title="Impact of Major Life Events on Savings",
                                xaxis_title="Year",
                                yaxis_title="Savings ($)",
                                height=500
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("With Events", f"${results['final_savings']:,.0f}")
                            with col2:
                                st.metric("Without Events", f"${without_results['final_savings']:,.0f}")
                            with col3:
                                impact = results['final_savings'] - without_results['final_savings']
                                st.metric("Net Impact", f"${impact:,.0f}", delta=f"${impact:,.0f}")
                        else:
                            st.error("❌ Dual analysis failed")
        except Exception as e:
            st.error(f"Dual scenario error: {str(e)}")
        
        # ============================================
        # AI ADVISOR (Available to ALL users)
        # ============================================
        try:
            if features.get('show_ai_advisor'):
                from ai_advisor import show_ai_consultation
                st.markdown("---")
                show_ai_consultation(results, stored_user_data, stored_financial_data, stored_sim_params)
        except Exception as e:
            st.error(f"AI advisor error: {str(e)}")
        
        # ============================================
        # DOWNLOAD OPTIONS
        # ============================================
        st.markdown("---")
        try:
            show_download_options(results)
        except Exception as e:
            st.error(f"Download options error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<p><strong>Ultimate Family Retirement Planning Plus v3.0</strong></p>
<p>Combining the best of GROK and CLAUDE architectures</p>
<p>Your trusted financial planning companion | 100% Private | AI-Powered</p>
</div>
""", unsafe_allow_html=True)