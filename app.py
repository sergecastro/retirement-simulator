"""
Family Forecast - Retirement Planning Tool
====================================
Main application entry point and navigation.

Author: Family Forecast Development Team
Last Updated: November 6, 2025
Version: 3.1 (Healthcare Hub + Modular Architecture)
"""

# =============================================================================
# STARTUP: Create empty secrets.toml to prevent warning
# =============================================================================
import os
from pathlib import Path

# Create .streamlit directory and empty secrets.toml if they don't exist
streamlit_dir = Path.home() / ".streamlit"
streamlit_dir.mkdir(exist_ok=True)
secrets_file = streamlit_dir / "secrets.toml"
if not secrets_file.exists():
    secrets_file.write_text("# Placeholder - actual secrets in environment variables\n")

# =============================================================================

import streamlit as st
import warnings

# Suppress Streamlit secrets warning for cloud deployment
warnings.filterwarnings('ignore', message='.*secrets.*')

# Import configuration
from config.settings import initialize_app, show_footer
from config.auth import require_authentication, is_trusted_user

# Import navigation
from ui.navigation import (
    show_mode_selector,
    show_feature_toggles,
    show_sidebar_header,
    show_sidebar_footer
)

# Import pages
from ui.results_page import show_results_page

# Import data collection
from pages.user_inputs import setup_sidebar as collect_user_data
from pages.financial_inputs import collect_financial_data
from pages.family_inputs import collect_family_events

# Import data management
from data_manager_cloud import manage_scenarios_cloud as manage_scenarios

# Import INTAKE module
from intake_integrated import show_intake_questionnaire

# Import Healthcare module
from healthcare.healthcare_main import main as healthcare_main

# Import disclaimers
import disclaimers

# Additional imports for INTAKE data loading
import json
import os
from pathlib import Path


# =============================================================================
# SCROLL TO TOP FIX
# =============================================================================
# JavaScript to force page scroll to top BEFORE content renders
SCROLL_TO_TOP_JS = """
<script>
    window.scrollTo(0, 0);
    document.documentElement.scrollTo(0, 0);
</script>
"""


# =============================================================================
# INTAKE DATA LOADING HELPER
# =============================================================================

def load_intake_data_to_session():
    """Load INTAKE data from current snapshot into session state for Analysis mode"""
    # NEW: Load from snapshot system instead of OLD file
    from utils.snapshot_manager import get_current_snapshot

    already_loaded = 'intake_data_loaded' in st.session_state

    # Only load if not already loaded in this session
    if not already_loaded:
        try:
            # Try to get current snapshot
            intake_data = get_current_snapshot()

            if intake_data:
                # Load snapshot data into session state
                for key, value in intake_data.items():
                    st.session_state[key] = value

                st.session_state.intake_data_loaded = True

                # Show welcome message
                user_name = intake_data.get('input_user_name', '')
                if user_name:
                    st.success(f"✅ Loaded data for: {user_name}")

        except Exception as e:
            # Silently fail - user will use sidebar inputs
            print(f"DEBUG: Could not load snapshot: {e}")
            pass


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point"""

    # Initialize app (page config, CSS, Flask check)
    initialize_app()

    # Require authentication
    if not require_authentication():
        return

    # Require disclaimer acknowledgment
    disclaimers.require_disclaimer_acknowledgment()

    # Show sidebar header
    show_sidebar_header()

    # Initialize mode selection in session state
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = False
        st.session_state.current_mode = None

    # FORCE CHECK: If current_mode is None, MUST show landing page
    if st.session_state.current_mode is None:
        st.session_state.mode_selected = False

    # Check if user has completed INTAKE data
    from utils.snapshot_manager import list_snapshots
    has_intake_data = len(list_snapshots()) > 0

    # Get user type
    is_trusted = is_trusted_user()

    # CRITICAL: SHOW LANDING PAGE if mode not selected
    if not st.session_state.mode_selected or st.session_state.current_mode is None:
        show_mode_selection_landing_page(has_intake_data, is_trusted)
        show_sidebar_footer(is_trusted)
        st.stop()  # ← STOP EXECUTION HERE!

    # Route based on selected mode
    # (Mode selector moved below scenario management for better UX)
    if not st.session_state.mode_selected:
        # Show welcome landing page (should never reach here due to stop above)
        show_sidebar_footer(is_trusted)
        show_mode_selection_landing_page(has_intake_data, is_trusted)
        st.stop()

    elif st.session_state.current_mode == "INTAKE":
        show_sidebar_footer(is_trusted)
        show_intake_mode()

    elif st.session_state.current_mode == "Healthcare":
        show_sidebar_footer(is_trusted)
        show_healthcare_mode()

    elif st.session_state.current_mode == "Analysis":
        # ✅ FIXED: Load INTAKE data into session state if available
        load_intake_data_to_session()

        # ✅ SCENARIO MANAGEMENT - MUST BE FIRST IN SIDEBAR!
        # Call this BEFORE feature toggles so it appears at top
        try:
            manage_scenarios(is_trusted)
        except Exception as e:
            st.sidebar.error(f"Scenario management error: {str(e)}")

        # Mode selector - appears AFTER scenario management
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🎯 Quick Mode Switch")

            # Determine smart default based on current mode
            mode_options = ["INTAKE", "Analysis", "Healthcare"]
            if st.session_state.current_mode in mode_options:
                default_index = mode_options.index(st.session_state.current_mode)
            else:
                default_index = 1  # Default to Analysis

            # Mode selector radio buttons
            mode = st.radio(
                "Choose mode:",
                options=mode_options,
                index=default_index,
                key="mode_selector_analysis",
                help="INTAKE: Guided questionnaire | Analysis: Advanced simulation | Healthcare: Cost planning"
            )

            # Sync radio button with session state
            if mode != st.session_state.current_mode:
                st.session_state.current_mode = mode
                st.session_state.mode_selected = True
                st.rerun()

        # Get feature toggles for Analysis mode (appears BELOW mode selector)
        features = show_feature_toggles(is_trusted)
        show_sidebar_footer(is_trusted)

        nav_state = {
            'mode': st.session_state.current_mode,
            'features': features,
            'is_trusted': is_trusted
        }

        show_analysis_mode(nav_state)

    # Show footer
    show_footer()


# =============================================================================
# WELCOME LANDING PAGE
# =============================================================================

def show_mode_selection_landing_page(has_intake_data, is_trusted):
    """
    Display landing page for mode selection with welcome message

    Args:
        has_intake_data: Whether INTAKE data exists
        is_trusted: Whether user has trusted access
    """
    # Welcome header
    st.title("🏠 Welcome to Family Forecast!")
    st.markdown("## *Family Lifecycle Retirement Planner*")

    # Welcome message box
    st.markdown("""
    <div style='background-color: #E8E6E0; padding: 20px; border-radius: 10px; border-left: 5px solid #E8B541;'>
        <h3 style='margin-top: 0; color: #003D5B;'>👋 Welcome!</h3>
        <p style='font-size: 16px; color: #555B66;'>
            Family Forecast is your comprehensive retirement planning companion. We help you visualize your
            financial future with interactive simulations, AI-powered insights, and detailed projections.
        </p>
        <p style='font-size: 16px; color: #555B66; margin-bottom: 0;'>
            <strong>Get started by choosing how you'd like to begin:</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")  # Spacing

    # Show status based on returning user
    if has_intake_data:
        st.success("✅ **Welcome back!** We found your previous INTAKE data. You can go straight to Analysis or update your information.")
    else:
        st.info("ℹ️ **First time here?** We recommend starting with INTAKE to collect your financial profile.")

    st.markdown("---")

    # Mode selection header
    st.markdown("### 🎯 Choose Your Starting Point")

    # Three big buttons for mode selection
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #E8E6E0 0%, #FFFFFF 100%); padding: 15px; border-radius: 8px; height: 280px; border: 2px solid #E8B541;'>
            <h3 style='color: #003D5B; margin-top: 0;'>📝 INTAKE Mode</h3>
            <p style='color: #003D5B;'><strong>Guided Questionnaire</strong></p>
            <ul style='color: #003D5B;'>
                <li>Step-by-step data collection</li>
                <li>Profile & demographic questions</li>
                <li>Financial information gathering</li>
                <li>Family & lifecycle details</li>
            </ul>
            <p style='color: #003D5B; margin-bottom: 0;'><strong>✨ Best for:</strong> First-time users or updating your profile</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

        if st.button("🚀 Start INTAKE Questionnaire", type="primary", use_container_width=True, key="btn_intake"):
            st.session_state.mode_selected = True
            st.session_state.current_mode = "INTAKE"
            st.rerun()

    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #003D5B 0%, #004D73 100%); padding: 15px; border-radius: 8px; height: 280px; border: 2px solid #E8B541;'>
            <h3 style='color: #FFFFFF; margin-top: 0;'>📊 Analysis Mode</h3>
            <p style='color: #FFFFFF;'><strong>Advanced Simulation & Planning</strong></p>
            <ul style='color: #FFFFFF;'>
                <li>Retirement trajectory projections</li>
                <li>Interactive charts & visualizations</li>
                <li>Monte Carlo probability analysis</li>
                <li>AI-powered financial advisor</li>
            </ul>
            <p style='color: #FFFFFF; margin-bottom: 0;'><strong>✨ Best for:</strong> Returning users or quick simulations</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

        if st.button("🚀 Go to Analysis Tools", type="primary", use_container_width=True, key="btn_analysis"):
            st.session_state.mode_selected = True
            st.session_state.current_mode = "Analysis"
            st.rerun()

    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #D85140 0%, #E86850 100%); padding: 15px; border-radius: 8px; height: 280px; border: 2px solid #E8B541;'>
            <h3 style='color: #FFFFFF; margin-top: 0;'>🏥 Healthcare Mode</h3>
            <p style='color: #FFFFFF;'><strong>Medicare & Healthcare Cost Projector</strong></p>
            <ul style='color: #FFFFFF;'>
                <li>Medicare IRMAA calculator</li>
                <li>Healthcare cost projections</li>
                <li>Roth conversion impacts</li>
                <li>Long-term care planning</li>
            </ul>
            <p style='color: #FFFFFF; margin-bottom: 0;'><strong>✨ Best for:</strong> Healthcare planning & Medicare costs</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

        if st.button("🚀 Open Healthcare Hub", type="primary", use_container_width=True, key="btn_healthcare"):
            st.session_state.mode_selected = True
            st.session_state.current_mode = "Healthcare"
            st.rerun()

    st.markdown("---")

    # Help section
    with st.expander("❓ Not sure which mode to choose?"):
        st.markdown("""
        ### Making Your Choice

        **Choose INTAKE Mode if:**
        - 🆕 This is your first time using Family Forecast
        - 📝 You want guided, step-by-step data collection
        - 🔄 You want to update or review your profile information
        - 🤔 You're not sure what information you need

        **Choose Analysis Mode if:**
        - 🔙 You've already completed INTAKE previously
        - 💼 You have your financial data ready to input manually
        - 🎯 You want to jump straight to retirement simulations
        - ⚡ You're familiar with financial planning tools

        **Choose Healthcare Mode if:**
        - 🏥 You want to calculate Medicare IRMAA surcharges
        - 💰 You need to project healthcare costs in retirement
        - 💊 You're planning Roth conversions and want to see Medicare impacts
        - 🩺 You want to explore long-term care planning options

        **💡 Pro Tip:** You can always switch between modes later using the sidebar button!
        """)

    # Footer with user info
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if is_trusted:
            st.success("🔓 **Full Access Granted** - All advanced features unlocked")
        else:
            st.info("👤 **Demo Access** - Core features available")


# =============================================================================
# INTAKE MODE
# =============================================================================

def show_intake_mode():
    """Display INTAKE questionnaire mode"""
    st.title("📝 INTAKE Questionnaire")
    st.markdown("*Guided data collection for retirement planning*")
    st.markdown("---")

    # Check if INTAKE was just completed
    if 'intake_completed' in st.session_state and st.session_state.intake_completed:
        st.success("✅ INTAKE completed! Switching to Analysis mode...")
        st.info("👉 Please select 'Analysis' mode in the sidebar to view your results.")
        # Reset the flag
        st.session_state.intake_completed = False
        return

    try:
        show_intake_questionnaire()
    except Exception as e:
        st.error(f"INTAKE error: {str(e)}")
        st.info("💡 Try switching to Analysis mode if you encounter issues.")


# =============================================================================
# HEALTHCARE MODE
# =============================================================================

def show_healthcare_mode():
    """Display Healthcare Cost Projector module"""
    st.components.v1.html(SCROLL_TO_TOP_JS, height=0)

    # Add mode selector to sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎯 Quick Mode Switch")

        mode = st.radio(
            "Choose mode:",
            options=["INTAKE", "Analysis", "Healthcare"],
            index=2,  # Healthcare is index 2
            key="mode_selector_healthcare",
            help="INTAKE: Guided questionnaire | Analysis: Advanced simulation | Healthcare: Cost planning"
        )

        if mode != st.session_state.current_mode:
            st.session_state.current_mode = mode
            st.session_state.mode_selected = True
            st.rerun()

    # Display Healthcare module
    try:
        healthcare_main()
    except Exception as e:
        st.error(f"Error loading Healthcare module: {e}")
        import traceback
        st.code(traceback.format_exc())


# =============================================================================
# ANALYSIS MODE
# =============================================================================

def show_analysis_mode(nav_state):
    """
    Display Analysis mode with simulations

    Args:
        nav_state: Navigation state with features and settings
    """
    # ✅ PHASE 1: Handle pending scenario load BEFORE creating any widgets
    if st.session_state.get('_pending_scenario_load', False):
        # Get the queued scenario data
        scenario_data = st.session_state.get('_pending_scenario_data', {})

        # Import the apply function here to avoid circular import at module level
        from data_manager_cloud import apply_scenario_data_safe

        # Apply the scenario data (this clears old keys and sets new values)
        apply_scenario_data_safe(scenario_data)

        # Clear the pending flags
        st.session_state['_pending_scenario_load'] = False
        if '_pending_scenario_data' in st.session_state:
            del st.session_state['_pending_scenario_data']

        # Show success message
        st.sidebar.success(f"✅ Scenario loaded!")

        # Rerun to create widgets with new values
        st.rerun()

    # ✅ FORCE SCROLL TO TOP BEFORE CONTENT RENDERS
    st.markdown(SCROLL_TO_TOP_JS, unsafe_allow_html=True)

    st.title("📊 Retirement Analysis")
    st.markdown("*Advanced simulation and planning tools*")

    # ✅ Welcome message with user data from INTAKE
    user_name = st.session_state.get('input_user_name', '')
    user_age = st.session_state.get('input_age', None)
    partner_exists = st.session_state.get('input_partner_exists', False)
    partner_name = st.session_state.get('input_partner_name', '')
    partner_age = st.session_state.get('input_partner_age', None)

    if user_name:
        st.success(f"👋 **Welcome {user_name}!**")
        welcome_parts = []
        if user_age:
            welcome_parts.append(f"Your Age: **{user_age}**")
        if partner_exists and partner_name:
            partner_info = f"Partner: **{partner_name}**"
            if partner_age:
                partner_info += f", Age **{partner_age}**"
            welcome_parts.append(partner_info)
        if welcome_parts:
            st.info(" | ".join(welcome_parts))

    st.markdown("---")

    # Get user trust status
    is_trusted = nav_state['is_trusted']

    # NOTE: Scenario management is now called in main() before this function
    # It appears at top of sidebar (above features and data inputs)

    # Collect data from sidebar
    try:
        # User demographic data
        user_data = collect_user_data(is_trusted)

        # Financial data
        financial_data = collect_financial_data()

        # Family events (children, inheritances)
        collect_family_events()

        # Simulation parameters
        sim_params = get_simulation_parameters()

    except Exception as e:
        st.error(f"Data collection error: {str(e)}")
        st.info("💡 Please check your inputs in the sidebar.")
        return

    # Add RUN SIMULATION button
    st.markdown("---")
    if st.button("🚀 RUN FINANCIAL SIMULATION", type="primary", use_container_width=True):
        st.session_state.run_simulation = True

    # Show results page if button was clicked
    if st.session_state.get('run_simulation', False):
        try:
            show_results_page(nav_state, user_data, financial_data, sim_params)
        except Exception as e:
            st.error(f"Results display error: {str(e)}")
            st.info("💡 Please check your simulation parameters.")
    else:
        st.info("👆 Click 'RUN FINANCIAL SIMULATION' button above to see results")


# =============================================================================
# SIMULATION PARAMETERS
# =============================================================================

def get_simulation_parameters():
    """
    Get simulation parameters from sidebar

    Returns:
        dict: Simulation parameters
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Simulation Parameters")

        col1, col2 = st.columns(2)

        with col1:
            tax_rate = st.slider(
                "Tax Rate (%)",
                min_value=0.0,
                max_value=50.0,
                value=25.0,
                step=1.0,
                help="Effective tax rate"
            ) / 100

            inflation_rate = st.slider(
                "Inflation (%)",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.5,
                help="Annual inflation rate"
            ) / 100

        with col2:
            investment_return_rate = st.slider(
                "Investment Return (%)",
                min_value=0.0,
                max_value=15.0,
                value=7.0,
                step=0.5,
                help="Expected annual return"
            ) / 100

            simulation_years = st.number_input(
                "Years to Simulate",
                min_value=10,
                max_value=50,
                value=30,
                step=5,
                help="Simulation duration"
            )

    return {
        'tax_rate': tax_rate,
        'inflation_rate': inflation_rate,
        'investment_return_rate': investment_return_rate,
        'simulation_years': simulation_years,
        'mc_iterations': 1000  # HARDCODED: Always run Monte Carlo with 1000 iterations
    }


# =============================================================================
# RUN APPLICATION
# =============================================================================

if __name__ == "__main__":
    main()