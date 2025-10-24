"""
ForeCash - Retirement Planning Tool
====================================
Main application entry point and navigation.

Author: ForeCash Development Team
Last Updated: October 23, 2025
Version: 3.0 (Refactored - Modular Architecture)
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

# Import disclaimers
import disclaimers

# Import FULL chart explanation system (the real one!)
from streamlit_explain_api_direct import inject_explain_visual_system

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
    """Load INTAKE data from intake_payload.json into session state for Analysis mode"""
    # Get the correct path (same as intake_integrated.py uses)
    current_dir = os.getcwd()
    root_dir = Path(current_dir).parent
    shared_dir = root_dir / "SHARED"
    intake_file = shared_dir / "intake_payload.json"

    # Check if INTAKE data exists
    if not os.path.exists(intake_file):
        return  # No INTAKE data, Analysis mode will use sidebar inputs

    # ✅ CRITICAL FIX: Only load data ONCE, not on every rerun!
    # This prevents overwriting user changes in Analysis mode
    if 'intake_data_loaded' not in st.session_state:
        try:
            # Load the INTAKE data
            with open(intake_file, "r", encoding="utf-8") as f:
                intake_data = json.load(f)

            # Load all data into session state so sidebar inputs can use it
            for key, value in intake_data.items():
                st.session_state[key] = value

            # Mark as loaded so we don't reload on every rerun
            st.session_state.intake_data_loaded = True

            # Show a one-time message that INTAKE data was loaded
            st.success("✅ INTAKE data loaded! Your information has been populated.")
            st.session_state.intake_data_loaded_message_shown = True

        except Exception as e:
            st.warning(f"Could not load INTAKE data: {str(e)}")


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

    # Inject chart explanation system (? buttons on charts)
    inject_explain_visual_system()

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
    import os
    has_intake_data = os.path.exists('SHARED/intake_payload.json')

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
            default_index = 0 if st.session_state.current_mode == "INTAKE" else 1

            # Mode selector radio buttons
            mode = st.radio(
                "Choose mode:",
                options=["INTAKE", "Analysis"],
                index=default_index,
                key="mode_selector_analysis",
                help="INTAKE: Guided questionnaire | Analysis: Advanced simulation"
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
    st.title("🏠 Welcome to ForeCash!")
    st.markdown("## *Family Lifecycle Retirement Planner*")

    # Welcome message box
    st.markdown("""
    <div style='background-color: #E8E6E0; padding: 20px; border-radius: 10px; border-left: 5px solid #E8B541;'>
        <h3 style='margin-top: 0; color: #003D5B;'>👋 Welcome!</h3>
        <p style='font-size: 16px; color: #555B66;'>
            ForeCash is your comprehensive retirement planning companion. We help you visualize your
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

    # Two big buttons for mode selection
    col1, col2 = st.columns(2)

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

    st.markdown("---")

    # Help section
    with st.expander("❓ Not sure which mode to choose?"):
        st.markdown("""
        ### Making Your Choice

        **Choose INTAKE Mode if:**
        - 🆕 This is your first time using ForeCash
        - 📝 You want guided, step-by-step data collection
        - 🔄 You want to update or review your profile information
        - 🤔 You're not sure what information you need

        **Choose Analysis Mode if:**
        - 🔙 You've already completed INTAKE previously
        - 💼 You have your financial data ready to input manually
        - 🎯 You want to jump straight to retirement simulations
        - ⚡ You're familiar with financial planning tools

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

    # Show results page
    try:
        show_results_page(nav_state, user_data, financial_data, sim_params)
    except Exception as e:
        st.error(f"Results display error: {str(e)}")
        st.info("💡 Please check your simulation parameters.")


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
        'simulation_years': simulation_years
    }


# =============================================================================
# RUN APPLICATION
# =============================================================================

if __name__ == "__main__":
    main()
