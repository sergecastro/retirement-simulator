"""
Family Forecast - Retirement Planning Tool
====================================
Main application entry point and navigation.

Author: Family Forecast Development Team
Last Updated: November 6, 2025 - 7:30 PM EST
Version: 3.1.1 (Healthcare Hub)
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
# OLD: from data_manager_cloud import manage_scenarios_cloud as manage_scenarios
# NEW: Encrypted snapshot system
from sidebar_snapshot_manager import manage_snapshots_sidebar as manage_scenarios

# Import INTAKE module
from intake_integrated import show_intake_questionnaire

# Import Healthcare module
try:
    from healthcare.healthcare_main import main as healthcare_main
    HEALTHCARE_AVAILABLE = True
except Exception as e:
    print(f"WARNING: Healthcare module failed to import: {e}")
    HEALTHCARE_AVAILABLE = False
    healthcare_main = None

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
# ANALYTICS TRACKING (Plausible/Cloudflare/Google Analytics)
# =============================================================================
# INSTRUCTIONS: Replace the placeholder below with your actual tracking code
#
# For PLAUSIBLE (recommended - privacy-focused):
#   <script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
#
# For CLOUDFLARE Web Analytics (free):
#   <script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "YOUR_TOKEN"}'></script>
#
# For GOOGLE Analytics:
#   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX"></script>
#   <script>window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', 'G-XXXXXXX');</script>

ANALYTICS_TRACKING_CODE = """
<!-- ANALYTICS: Uncomment and add your tracking code here -->
<!-- <script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script> -->
"""


# =============================================================================
# INTAKE DATA LOADING HELPER
# =============================================================================

def load_intake_data_to_session():
    """Load INTAKE data from current snapshot into session state for Analysis mode"""
    # NEW: Load from snapshot system instead of OLD file
    from utils.snapshot_manager import get_current_snapshot

    already_loaded = 'intake_data_loaded' in st.session_state

    print(f"[LOAD_INTAKE] already_loaded flag = {already_loaded}")

    # FORCE RELOAD if we have cached snapshot data (just came from Intake)
    if '_cached_snapshots' in st.session_state and len(st.session_state['_cached_snapshots']) > 0:
        print(f"[LOAD_INTAKE] Found {len(st.session_state['_cached_snapshots'])} cached snapshot(s), forcing reload")
        already_loaded = False

    # Only load if not already loaded in this session
    if not already_loaded:
        try:
            # Try to get current snapshot (will use cache if available)
            print(f"[LOAD_INTAKE] Calling get_current_snapshot()...")
            intake_data = get_current_snapshot()

            if intake_data:
                print(f"[LOAD_INTAKE] OK Got snapshot data, user = {intake_data.get('input_user_name', 'MISSING')}")
                # Load snapshot data into session state
                for key, value in intake_data.items():
                    st.session_state[key] = value

                st.session_state.intake_data_loaded = True

                # Show welcome message ONCE
                if 'intake_welcome_shown' not in st.session_state:
                    user_name = intake_data.get('input_user_name', '')
                    if user_name:
                        st.success(f"✅ Loaded data for: {user_name}")
                    st.session_state['intake_welcome_shown'] = True
            else:
                print(f"[LOAD_INTAKE] ERROR get_current_snapshot() returned None")

        except Exception as e:
            # Silently fail - user will use sidebar inputs
            print(f"[LOAD_INTAKE] ERROR Exception: {e}")
            import traceback
            traceback.print_exc()
            pass
    else:
        print(f"[LOAD_INTAKE] WARNING Skipping load - already_loaded=True")


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point"""

    # Initialize app (page config, CSS, Flask check)
    initialize_app()

    # Inject analytics tracking code (invisible to users)
    st.markdown(ANALYTICS_TRACKING_CODE, unsafe_allow_html=True)

    # ⚠️⚠️⚠️ DEMO MODE - Authentication simplified for beta testing ⚠️⚠️⚠️
    # To re-enable full auth: Uncomment the lines below
    st.sidebar.info("🧪 **BETA DEMO** - Testing mode active")

    # DEMO MODE: Simplified authentication
    # Require authentication
    # if not require_authentication():
    #     return

    # DEMO MODE: Skip disclaimer for faster testing
    # Require disclaimer acknowledgment
    # disclaimers.require_disclaimer_acknowledgment()

    # Show sidebar header
    show_sidebar_header()

    # Initialize mode selection in session state
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = False
        st.session_state.current_mode = None

    # FORCE CHECK: If current_mode is None, MUST show landing page
    if st.session_state.current_mode is None:
        st.session_state.mode_selected = False

    # Check if user has saved snapshots (for smart landing page)
    from utils.snapshot_manager import has_user_snapshots
    has_saved_data = has_user_snapshots()

    # Get user type
    is_trusted = is_trusted_user()

    # CRITICAL: SHOW LANDING PAGE if mode not selected
    if not st.session_state.mode_selected or st.session_state.current_mode is None:
        show_mode_selection_landing_page(has_saved_data, is_trusted)
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

    elif st.session_state.current_mode == "scenario_studio":
        from ui.scenario_studio_page import render_scenario_studio_page
        render_scenario_studio_page()

    elif st.session_state.current_mode == "social_security":
        # Load INTAKE data first
        load_intake_data_to_session()
        show_sidebar_footer(is_trusted)

        # Check if user wants to open Roth Calculator
        if st.session_state.get('show_roth_calculator', False):
            st.session_state['show_roth_calculator'] = False
            st.session_state.current_mode = "roth_calculator"
            st.rerun()

        from pages.social_security_optimizer import show_social_security_optimizer
        show_social_security_optimizer()

    elif st.session_state.current_mode == "roth_calculator":
        # Roth Conversion Calculator
        load_intake_data_to_session()
        show_sidebar_footer(is_trusted)
        from pages.roth_calculator import show_roth_calculator
        show_roth_calculator()

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

            mode_options = ["INTAKE", "Analysis", "Scenario Studio", "Social Security", "Healthcare"]
            current_idx = 1  # Analysis is current

            # Mode selector radio buttons
            mode = st.radio(
                "Choose mode:",
                options=mode_options,
                index=current_idx,
                key="mode_selector_analysis",
                help="INTAKE: Guided questionnaire | Analysis: Advanced simulation | Scenario Studio: Compare scenarios | Social Security: Claiming optimizer | Healthcare: Cost planning"
            )

            # Handle mode change
            if mode != "Analysis":
                # Preserve current snapshot before mode switch
                if 'current_snapshot_id' in st.session_state:
                    st.session_state['preserved_snapshot_id'] = st.session_state['current_snapshot_id']

                if mode == "Scenario Studio":
                    st.session_state.current_mode = "scenario_studio"
                elif mode == "Social Security":
                    st.session_state.current_mode = "social_security"
                else:
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

    # "What's New" banner (dismissible)
    if 'whats_new_dismissed' not in st.session_state:
        st.session_state.whats_new_dismissed = False

    if not st.session_state.whats_new_dismissed:
        col_banner, col_dismiss = st.columns([9, 1])
        with col_banner:
            st.markdown("""
            <div style='background-color: #D4EDDA; padding: 15px; border-radius: 8px; border-left: 5px solid #28A745; margin-bottom: 20px;'>
                <h4 style='margin-top: 0; color: #155724;'>🎉 What's New - November 2025</h4>
                <p style='font-size: 15px; color: #155724; margin-bottom: 8px;'><strong>NEW:</strong></p>
                <ul style='margin: 0; padding-left: 20px; color: #155724;'>
                    <li><strong>🎬 Scenario Studio</strong> - Compare 2-4 retirement scenarios side-by-side with interactive charts!</li>
                    <li><strong>🏥 Medicare Comparison Tool</strong> - Analyze Medigap vs Medicare Advantage plans</li>
                    <li><strong>📊 Enhanced Exports</strong> - Download comparisons as PDF, Excel, or CSV</li>
                    <li><strong>💬 AI-Powered Insights</strong> - Get intelligent analysis of your retirement projections</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with col_dismiss:
            if st.button("✕", key="dismiss_whats_new", help="Dismiss this message"):
                st.session_state.whats_new_dismissed = True
                st.rerun()

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

    # Show status based on whether user has saved snapshots
    if has_intake_data:
        # User has saved snapshots (returning user with data)
        st.success("✅ **Welcome back!** You have saved retirement plans ready to analyze.\n\n**Your choices:**\n\n1️⃣ **Go to Analysis** to review and simulate your saved plans\n\n2️⃣ **Start INTAKE** to create a new plan or update existing data")
    else:
        # No saved snapshots (new user)
        st.info("ℹ️ **First time here?** Get started by creating your retirement plan.\n\n**Recommended:** Start with INTAKE to enter your financial information, or explore Analysis mode with demo data.")

    st.markdown("---")

    # BETA AGREEMENT CHECKBOX - Must acknowledge before proceeding
    beta_agreement = st.checkbox(
        "I understand this is **BETA software for educational purposes only**. "
        "This is NOT financial advice and I should consult qualified professionals.",
        key="beta_agreement"
    )

    if not beta_agreement:
        st.warning("⚠️ Please acknowledge the beta terms above to continue.")
        st.stop()

    # Mode selection header
    st.markdown("### 🎯 Choose Your Starting Point")

    # Five big buttons for mode selection (or fewer if modules unavailable)
    if HEALTHCARE_AVAILABLE:
        # First row: 3 main cards
        col1, col2, col3 = st.columns(3)
    else:
        col1, col2 = st.columns(2)
        st.warning("⚠️ Healthcare module temporarily unavailable")

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

    if HEALTHCARE_AVAILABLE:
        with col3:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #D85140 0%, #E86850 100%); padding: 15px; border-radius: 8px; height: 280px; border: 2px solid #E8B541;'>
                <h3 style='color: #FFFFFF; margin-top: 0;'>🏥 Healthcare Mode</h3>
                <p style='color: #FFFFFF;'><strong>Medicare & Healthcare Planning</strong></p>
                <ul style='color: #FFFFFF;'>
                    <li><strong>🆕 Medigap Plan Comparison Tool</strong></li>
                    <li>Medicare IRMAA calculator</li>
                    <li>Medigap vs Medicare Advantage quiz</li>
                    <li>Age-based premium estimates</li>
                </ul>
                <p style='color: #FFFFFF; margin-bottom: 0;'><strong>✨ Best for:</strong> Choosing the right Medicare supplement plan</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("")  # Spacing

            if st.button("🚀 Open Healthcare Hub", type="primary", use_container_width=True, key="btn_healthcare"):
                st.session_state.mode_selected = True
                st.session_state.current_mode = "Healthcare"
                st.rerun()

        # Second row: Scenario Studio and Social Security
        col4, col5, col_empty = st.columns(3)

        # Card 4: Scenario Studio
        with col4:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; height: 280px; border: 2px solid #E8B541;'>
                <h3 style='color: #FFFFFF; margin-top: 0;'>🎬 Scenario Studio</h3>
                <p style='color: #FFFFFF;'><strong>Multi-Scenario Comparison</strong></p>
                <ul style='color: #FFFFFF;'>
                    <li>Compare 2-4 scenarios side-by-side</li>
                    <li>Visual difference highlighting</li>
                    <li>AI-powered recommendations</li>
                    <li>Export comparison reports</li>
                </ul>
                <p style='color: #FFFFFF; margin-bottom: 0;'><strong>✨ Best for:</strong> Exploring "what-if" retirement strategies</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("")  # Spacing

            if st.button("🚀 Enter Scenario Studio", type="primary", use_container_width=True, key="btn_scenario_studio"):
                st.session_state.mode_selected = True
                st.session_state.current_mode = "scenario_studio"
                st.rerun()

        # Card 5: Social Security Optimizer
        with col5:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%); padding: 15px; border-radius: 8px; height: 280px; border: 2px solid #E8B541;'>
                <h3 style='color: #FFFFFF; margin-top: 0;'>🏛️ Social Security</h3>
                <p style='color: #FFFFFF;'><strong>SS Optimizer + Tax Planning</strong></p>
                <ul style='color: #FFFFFF;'>
                    <li>Optimal claiming age calculator</li>
                    <li><strong>🆕 SS Benefit Taxation Calculator</strong></li>
                    <li><strong>🆕 Roth Conversion Sweet Spot</strong></li>
                    <li>Break-even & spousal optimization</li>
                </ul>
                <p style='color: #FFFFFF; margin-bottom: 0;'><strong>✨ Best for:</strong> Maximize SS + minimize lifetime taxes</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("")  # Spacing

            if st.button("🚀 Optimize Social Security", type="primary", use_container_width=True, key="btn_social_security"):
                st.session_state.mode_selected = True
                st.session_state.current_mode = "social_security"
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

        **Choose Scenario Studio if:**
        - 🎬 You've saved multiple "what-if" comparison scenarios
        - 📊 You want to compare different retirement strategies side-by-side
        - 🔍 You need to see the differences between scenarios at a glance
        - 🤔 You're deciding between multiple retirement paths

        **Choose Social Security Optimizer if:**
        - 🏛️ You want to determine the optimal age to claim SS benefits
        - 💰 You need to see break-even analysis for different claiming ages
        - 👥 You want to optimize spousal benefits
        - 📊 You want to maximize lifetime Social Security income

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

    # Coming Soon features
    st.caption("🔐 **Coming Soon:** Plaid for secure bank data import • Stripe for premium features")


# =============================================================================
# INTAKE MODE
# =============================================================================

def show_intake_mode():
    """Display INTAKE questionnaire mode"""

    # AUTO-LOAD: If user has saved plans but no current plan loaded, load the most recent
    if 'current_snapshot_id' not in st.session_state or st.session_state.get('current_snapshot_id') is None:
        from utils.snapshot_manager import get_snapshots_index, load_snapshot
        index = get_snapshots_index()
        if index.get('snapshots') and len(index['snapshots']) > 0:
            # Load the most recent snapshot
            most_recent = index['snapshots'][-1]
            snapshot_data = load_snapshot(most_recent['id'])
            if snapshot_data:
                # Load data into session_state
                for key, value in snapshot_data.items():
                    st.session_state[key] = value
                st.session_state['current_snapshot_id'] = most_recent['id']
                st.success(f"✅ Loaded your saved data: **{snapshot_data.get('input_user_name', 'Unknown')}**")

    # Add Quick Mode Switch in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎯 Quick Mode Switch")

        mode_options = ["INTAKE", "Analysis", "Scenario Studio", "Social Security", "Healthcare"]
        current_idx = 0  # INTAKE is current

        mode = st.radio(
            "Choose mode:",
            options=mode_options,
            index=current_idx,
            key="mode_selector_intake",
            help="INTAKE: Guided questionnaire | Analysis: Advanced simulation | Scenario Studio: Compare scenarios | Social Security: Claiming optimizer | Healthcare: Cost planning"
        )

        # Handle mode change
        if mode != "INTAKE":
            # Preserve current snapshot before mode switch
            if 'current_snapshot_id' in st.session_state:
                st.session_state['preserved_snapshot_id'] = st.session_state['current_snapshot_id']

            if mode == "Scenario Studio":
                st.session_state.current_mode = "scenario_studio"
            elif mode == "Social Security":
                st.session_state.current_mode = "social_security"
            else:
                st.session_state.current_mode = mode
            st.session_state.mode_selected = True
            st.rerun()

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
            options=["INTAKE", "Analysis", "Scenario Studio", "Social Security", "Healthcare"],
            index=4,  # Healthcare is index 4
            key="mode_selector_healthcare",
            help="INTAKE: Guided questionnaire | Analysis: Advanced simulation | Scenario Studio: Compare scenarios | Social Security: Claiming optimizer | Healthcare: Cost planning"
        )

        if mode != st.session_state.current_mode:
            if mode == "Scenario Studio":
                st.session_state.current_mode = "scenario_studio"
            elif mode == "Social Security":
                st.session_state.current_mode = "social_security"
            else:
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
# SCENARIO STUDIO MODE - Routing handled in ui/scenario_studio_page.py
# =============================================================================


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
        # OLD: from data_manager_cloud import apply_scenario_data_safe
        # NEW: Use sidebar_snapshot_manager version
        from sidebar_snapshot_manager import apply_scenario_data_safe

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
        st.markdown("### ⚙️ Advanced Parameters")

        # Show DISABLED sliders with teaser (freemium psychology!)
        col1, col2 = st.columns(2)

        with col1:
            st.slider(
                "Tax Rate (%)",
                min_value=0.0,
                max_value=50.0,
                value=22.0,
                step=1.0,
                disabled=True,
                help="💡 Adjust in Scenario Studio"
            )

            st.slider(
                "Inflation (%)",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.5,
                disabled=True,
                help="💡 Adjust in Scenario Studio"
            )

        with col2:
            st.slider(
                "Investment Return (%)",
                min_value=0.0,
                max_value=15.0,
                value=7.0,
                step=0.5,
                disabled=True,
                help="💡 Adjust in Scenario Studio"
            )

            st.slider(
                "Years to Simulate",
                min_value=10,
                max_value=50,
                value=25,
                step=1,
                disabled=True,
                help="💡 Adjust in Scenario Studio"
            )

        # Teaser message
        st.info("💡 Want to adjust these? Try **Scenario Studio** for full control over 30+ parameters!")

        # Unlock button
        if st.button("🔓 Unlock in Scenario Studio", key="sidebar_unlock_studio"):
            st.session_state.current_mode = "scenario_studio"
            st.session_state.mode_selected = True
            st.rerun()

        # Use sensible defaults for simulation
        tax_rate = 0.22
        inflation_rate = 0.03
        investment_return_rate = 0.07
        simulation_years = 25

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