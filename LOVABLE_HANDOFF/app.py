"""
ForeCash - Retirement Planning Tool
====================================
Main application entry point and navigation.

Author: ForeCash Development Team
Last Updated: October 22, 2025
Version: 3.0 (Refactored - Modular Architecture)
"""

import streamlit as st

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
    import os
    has_intake_data = os.path.exists('SHARED/intake_payload.json')

    # Get user type
    is_trusted = is_trusted_user()

    # CRITICAL: SHOW LANDING PAGE if mode not selected
    if not st.session_state.mode_selected or st.session_state.current_mode is None:
        show_mode_selection_landing_page(has_intake_data, is_trusted)
        show_sidebar_footer(is_trusted)
        st.stop()  # ← STOP EXECUTION HERE!

    # Show mode selector in sidebar (always visible for easy switching)
    with st.sidebar:
        st.markdown("### 🎯 Quick Mode Switch")

        # Determine smart default based on current mode
        default_index = 0 if st.session_state.current_mode == "INTAKE" else 1

        # Mode selector radio buttons
        mode = st.radio(
            "Choose mode:",
            options=["INTAKE", "Analysis"],
            index=default_index,
            key="mode_selector",
            help="INTAKE: Guided questionnaire | Analysis: Advanced simulation"
        )

        # Sync radio button with session state
        if mode != st.session_state.current_mode:
            st.session_state.current_mode = mode
            st.session_state.mode_selected = True

        st.markdown("---")

    # Route based on selected mode
    if not st.session_state.mode_selected:
        # Show welcome landing page (should never reach here due to stop above)
        show_sidebar_footer(is_trusted)
        show_mode_selection_landing_page(has_intake_data, is_trusted)
        st.stop()

    elif st.session_state.current_mode == "INTAKE":
        show_sidebar_footer(is_trusted)
        show_intake_mode()

    elif st.session_state.current_mode == "Analysis":
        # Get feature toggles for Analysis mode
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
    <div style='background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;'>
        <h3 style='margin-top: 0; color: #2c3e50;'>👋 Welcome!</h3>
        <p style='font-size: 16px; color: #34495e;'>
            ForeCash is your comprehensive retirement planning companion. We help you visualize your
            financial future with interactive simulations, AI-powered insights, and detailed projections.
        </p>
        <p style='font-size: 16px; color: #34495e; margin-bottom: 0;'>
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
        <div style='background-color: #fff3cd; padding: 15px; border-radius: 8px; height: 280px;'>
            <h3 style='color: #856404; margin-top: 0;'>📝 INTAKE Mode</h3>
            <p style='color: #856404;'><strong>Guided Questionnaire</strong></p>
            <ul style='color: #856404;'>
                <li>Step-by-step data collection</li>
                <li>Profile & demographic questions</li>
                <li>Financial information gathering</li>
                <li>Family & lifecycle details</li>
            </ul>
            <p style='color: #856404; margin-bottom: 0;'><strong>✨ Best for:</strong> First-time users or updating your profile</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

        if st.button("🚀 Start INTAKE Questionnaire", type="primary", use_container_width=True, key="btn_intake"):
            st.session_state.mode_selected = True
            st.session_state.current_mode = "INTAKE"
            st.rerun()

    with col2:
        st.markdown("""
        <div style='background-color: #d1ecf1; padding: 15px; border-radius: 8px; height: 280px;'>
            <h3 style='color: #0c5460; margin-top: 0;'>📊 Analysis Mode</h3>
            <p style='color: #0c5460;'><strong>Advanced Simulation & Planning</strong></p>
            <ul style='color: #0c5460;'>
                <li>Retirement trajectory projections</li>
                <li>Interactive charts & visualizations</li>
                <li>Monte Carlo probability analysis</li>
                <li>AI-powered financial advisor</li>
            </ul>
            <p style='color: #0c5460; margin-bottom: 0;'><strong>✨ Best for:</strong> Returning users or quick simulations</p>
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
    st.title("📊 Retirement Analysis")
    st.markdown("*Advanced simulation and planning tools*")
    st.markdown("---")

    # Collect data from sidebar
    try:
        # Get user trust status
        is_trusted = nav_state['is_trusted']

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

    # Scenario management
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💾 Scenario Management")
        try:
            manage_scenarios()
        except Exception as e:
            st.error(f"Scenario management error: {str(e)}")

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
