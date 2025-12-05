"""
Family Forecast - Retirement Planning Tool
====================================
Main application entry point and navigation.

Author: Family Forecast Development Team
Last Updated: November 18, 2025
Version: 3.2.0 (Production Hardening)
"""

# =============================================================================
# ERROR MONITORING SETUP (Must be first!)
# =============================================================================
import os
from pathlib import Path

# Initialize Sentry for error tracking (optional - only if DSN is set)
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    def before_send(event, hint):
        """
        Filter out bot noise and non-critical errors before sending to Sentry.

        Filters:
        - 404 errors (file not found) - usually bots scanning for vulnerabilities
        - Legacy browsers (pre-2020) - typically bots with fake user agents
        - Known bot patterns in URLs

        Returns None to drop the event, or the event to send it to Sentry.
        """
        # Get the exception if available
        if 'exception' in event:
            exc_values = event['exception'].get('values', [])
            for exc in exc_values:
                exc_type = exc.get('type', '')
                exc_value = exc.get('value', '')

                # Filter: Missing file errors (404s)
                if 'Missing file' in exc_value or 'MediaFileHandler' in exc_type:
                    return None  # Drop this event

        # Get request info if available
        if 'request' in event:
            request = event['request']
            url = request.get('url', '')
            headers = request.get('headers', {})

            # Filter: Bot-like paths (common vulnerability scans)
            bot_paths = [
                '/media/system/', '/wp-admin/', '/admin/',
                '/phpmyadmin/', '/.env', '/config.php',
                '/core.js', '/jquery.js', '/.git/'
            ]
            if any(bot_path in url for bot_path in bot_paths):
                return None  # Drop this event

            # Filter: Ancient browsers (likely bots)
            user_agent = headers.get('User-Agent', '')
            if user_agent:
                # Check for very old Chrome versions (pre-2020)
                if 'Chrome/3' in user_agent or 'Chrome/4' in user_agent:
                    return None  # Drop this event

                # Check for very old Firefox versions
                if 'Firefox/3' in user_agent or 'Firefox/4' in user_agent:
                    return None  # Drop this event

        # Keep all other errors (real user issues)
        return event

    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=0.1,  # 10% performance monitoring
            profiles_sample_rate=0.1,  # 10% profiling
            environment=os.getenv("RENDER_GIT_BRANCH", "development"),
            release=os.getenv("RENDER_GIT_COMMIT", "dev"),
            integrations=[FlaskIntegration()],
            before_send=before_send,  # Apply our smart filter
        )
        print("✅ Sentry error monitoring initialized (with bot filters)")
    else:
        pass  # Sentry DSN not set - error monitoring disabled
except ImportError:
    print("ℹ️ Sentry not installed - error monitoring disabled")

# =============================================================================
# STARTUP: Create empty secrets.toml to prevent warning
# =============================================================================

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
from ui.components.top_navigation import render_top_navigation
from ui.welcome import show_new_user_mode_selection

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
<script defer data-domain="familyforecast.ai" src="https://plausible.io/js/script.js"></script>
"""

# =============================================================================
# MOBILE SIDEBAR AUTO-COLLAPSE FIX
# =============================================================================
# Force sidebar to stay collapsed on mobile devices (< 768px width)
# while keeping normal behavior on desktop/laptop screens
MOBILE_SIDEBAR_CSS = """
<style>
/* Auto-collapse sidebar on mobile devices */
@media (max-width: 768px) {
    /* Force sidebar to collapsed state on mobile */
    section[data-testid="stSidebar"] {
        width: 0px !important;
        min-width: 0px !important;
    }

    /* Hide sidebar content when collapsed on mobile */
    section[data-testid="stSidebar"] > div {
        width: 0px !important;
        margin-left: -300px !important;
    }

    /* Ensure main content takes full width on mobile */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Keep the collapse/expand button visible */
    button[kind="header"] {
        display: block !important;
    }
}

/* Desktop and tablet - normal sidebar behavior */
@media (min-width: 769px) {
    section[data-testid="stSidebar"] {
        /* Default Streamlit behavior - no changes */
    }
}
</style>
"""

# =============================================================================
# INTAKE DATA LOADING HELPER
# =============================================================================

def load_intake_data_to_session():
    """Load INTAKE data from current snapshot into session state for Analysis mode"""
    # NEW: Load from snapshot system instead of OLD file
    from utils.snapshot_manager import get_current_snapshot

    already_loaded = 'intake_data_loaded' in st.session_state

    # FORCE RELOAD if we have cached snapshot data (just came from Intake)
    if '_cached_snapshots' in st.session_state and len(st.session_state['_cached_snapshots']) > 0:
        already_loaded = False

    # Only load if not already loaded in this session
    if not already_loaded:
        try:
            # Try cloud restore data first, then fall back to local snapshot
            intake_data = st.session_state.pop('intake_data', None) or get_current_snapshot()

            if intake_data:
                # Load snapshot data into session state
                for key, value in intake_data.items():
                    # WHITELIST: Only copy safe data keys, never widget keys
                    if key.startswith(('input_', 'temp_', '_protected')) or key in (
                        'children_list', 'children_rows', 'inheritance_list', 'inherit_rows',
                        'goals_list', 'goals_data', 'custom_expenses', 'custom_expenses_list',
                        'custom_income', 'custom_income_list', 'schema_version'
                    ):
                        # FIX: Validate age fields (widgets have min_value=18)
                        if key in ('input_age', 'input_partner_age') and isinstance(value, (int, float)):
                            if value < 18:
                                value = 55  # Default to 55 if invalid
                        st.session_state[key] = value

                st.session_state.intake_data_loaded = True

                # Show welcome message ONCE
                if 'intake_welcome_shown' not in st.session_state:
                    user_name = intake_data.get('input_user_name', '')
                    if user_name:
                        st.success(f"✅ Loaded data for: {user_name}")
                    st.session_state['intake_welcome_shown'] = True
            else:
                pass  # No intake data to load

        except Exception as e:
            # Silently fail - user will use sidebar inputs
            pass
    else:
        pass  # Already loaded


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point"""
    # =============================================================================
    # CRITICAL: initialize_app() MUST be called FIRST before any st.session_state
    # st.set_page_config() must be the first Streamlit command
    # =============================================================================
    initialize_app()

    # LOAD VAULT CREDENTIALS FROM LOCALSTORAGE (ONLY ONCE per session)
    if not st.session_state.get('_credentials_loaded'):
        if not st.session_state.get('vault_id') and not st.session_state.get('user_email'):
            from utils.safe_local_storage import get_backup_credentials
            creds = get_backup_credentials()
            if creds.get('ready') and creds.get('has_credentials'):
                if creds.get('ff_vault_id'):
                    st.session_state['vault_id'] = creds['ff_vault_id']
                if creds.get('ff_user_email'):
                    st.session_state['user_email'] = creds['ff_user_email']
                st.session_state['_credentials_loaded'] = True
            elif creds.get('ready'):
                st.session_state['_credentials_loaded'] = True

    # =============================================================================
    # HEALTH CHECK ENDPOINT - For monitoring/uptime services
    # =============================================================================
    # Usage: https://yourapp.com?health=check
    # Returns: Simple OK message and stops (doesn't load full app)
    if st.query_params.get("health") == "check":
        from datetime import datetime
        st.write("✅ OK")
        st.write(f"Version: 3.2.0")
        st.write(f"Status: Running")
        st.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        st.stop()

    # =============================================================================
    # RESTORE SHORTCUT - Go directly to cloud restore from any page
    # =============================================================================
    # Usage: http://localhost:8501/?restore=cloud
    if st.query_params.get("restore") == "cloud":
        st.session_state.mode_selected = False
        st.session_state.current_mode = None
        st.session_state.show_backup_signup = 'restore'
        st.session_state['_force_welcome'] = True  # Flag to skip auto-Analysis
        st.query_params.clear()  # Clear the param so it doesn't loop
        st.rerun()

    # Inject analytics tracking code (invisible to users)
    # Using components.html instead of markdown for better script injection
    st.components.v1.html(ANALYTICS_TRACKING_CODE, height=0)

    # Inject mobile-responsive sidebar CSS (auto-collapse on mobile devices)
    st.markdown(MOBILE_SIDEBAR_CSS, unsafe_allow_html=True)

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

    # LANDING PAGE DISABLED FOR LAUNCH - Go straight to app
    # The app's beta checkbox screen is clean enough
    if 'seen_landing_page' not in st.session_state:
        st.session_state.seen_landing_page = True  # Always skip landing page

    # Initialize mode selection in session state
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = False
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = None

    # FORCE CHECK: If current_mode is None, MUST show landing page
    if st.session_state.current_mode is None:
        st.session_state.mode_selected = False

    # Check if user has saved snapshots (for smart landing page)
    from utils.snapshot_manager import has_user_snapshots
    has_saved_data = has_user_snapshots()

    # Get user type
    is_trusted = is_trusted_user()

    # CRITICAL: Route based on new vs return user
    if not st.session_state.mode_selected or st.session_state.current_mode is None:

        # Check if forced to Welcome (e.g., ?restore=cloud)
        force_welcome = st.session_state.pop('_force_welcome', False)

        # PRIORITY: If restore form requested, show it immediately
        if st.session_state.get('show_backup_signup') == 'restore':
            from ui.welcome import show_restore_form
            show_restore_form('restore')
            show_sidebar_footer(is_trusted)
            st.stop()

        if has_saved_data and not force_welcome:
            # ═══════════════════════════════════════════════════════
            # RETURN USER: Has snapshots → Auto-load → Analysis
            # ═══════════════════════════════════════════════════════
            from utils.snapshot_manager import get_snapshots_index, load_snapshot
            index = get_snapshots_index()
            if index.get('snapshots'):
                most_recent = index['snapshots'][-1]
                snapshot_data = load_snapshot(most_recent['id'])
                if snapshot_data:
                    # Load data into session_state
                    for key, value in snapshot_data.items():
                        if key.startswith(('input_', 'temp_', '_protected')) or key in (
                            'children_list', 'children_rows', 'inheritance_list', 'inherit_rows',
                            'goals_list', 'goals_data', 'schema_version'
                        ):
                            st.session_state[key] = value
                    st.session_state['current_snapshot_id'] = most_recent['id']
            
            # Go directly to Analysis
            st.session_state["beta_agreement"] = True
            st.session_state.mode_selected = True
            st.session_state.current_mode = "Analysis"
            st.rerun()
        
        else:
            # ═══════════════════════════════════════════════════════
            # NEW USER: No snapshots → Mode Selection → INTAKE
            # ═══════════════════════════════════════════════════════

            # Check if user clicked a signup/restore button
            signup_mode = st.session_state.get('show_backup_signup')

            if signup_mode == 'account':
                from ui.welcome import show_account_signup_form
                show_account_signup_form()
            elif signup_mode == 'anonymous':
                from ui.welcome import show_anonymous_signup_form
                show_anonymous_signup_form()
            elif signup_mode == 'restore':
                from ui.welcome import show_restore_form
                show_restore_form(signup_mode)
            else:
                show_new_user_mode_selection()

            show_sidebar_footer(is_trusted)
            st.stop()

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

    elif st.session_state.current_mode == "historical_tracking":
        from ui import historical_tracking_page
        historical_tracking_page.render()

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
# HTML MARKETING LANDING PAGE
# =============================================================================

def show_html_landing_page():
    """Show the full marketing landing page from static/landing.html"""
    import streamlit.components.v1 as components

    # Add a HUGE visible button at the top
    st.markdown("""
    <style>
    .stButton > button {
        background-color: #E8B541 !important;
        color: #003D5B !important;
        font-size: 24px !important;
        font-weight: bold !important;
        padding: 20px 40px !important;
        border-radius: 10px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 👇 Click Here to Try the App (No Signup Needed)")
    if st.button("🚀 START PLANNING NOW - FREE", type="primary", use_container_width=True, key="enter_app_top"):
        st.session_state.seen_landing_page = True
        st.rerun()

    st.markdown("---")
    st.markdown("*Or scroll down to read more about Family Forecast...*")
    st.markdown("---")

    # Read the landing page HTML
    landing_html_path = Path(__file__).parent / "static" / "landing.html"

    if landing_html_path.exists():
        with open(landing_html_path, 'r', encoding='utf-8') as f:
            landing_html = f.read()

        # Render full-page HTML
        components.html(landing_html, height=4000, scrolling=True)

        # Add a Streamlit button at bottom too
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 ENTER APP (No Signup Required)", type="primary", use_container_width=True, key="enter_app_bottom"):
                st.session_state.seen_landing_page = True
                st.rerun()
    else:
        st.error(f"Landing page not found at {landing_html_path}")
        # Fallback - proceed to app
        st.session_state.seen_landing_page = True
        if st.button("Continue to App"):
            st.rerun()


# =============================================================================
# NEW USER MODE SELECTION - MOVED TO ui/welcome.py (Dec 2, 2025)
# =============================================================================
# Function show_new_user_mode_selection() is now imported from ui/welcome.py
# Old code removed to reduce app.py size (was 121 lines)


# =============================================================================
# WELCOME LANDING PAGE (Legacy - kept for reference)
# =============================================================================

def show_mode_selection_landing_page(has_intake_data, is_trusted):
    """
    Display landing page for mode selection with welcome message

    Args:
        has_intake_data: Whether INTAKE data exists
        is_trusted: Whether user has trusted access
    """
    # Welcome header with logo
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image("assets/branding/logo-familyforecast.png", width=120)
    with col_title:
        st.title("Welcome to Family Forecast!")
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
                    <li><strong>📊 Historical Tracking</strong> - Save quarterly snapshots and track your retirement plan progress over time!</li>
                    <li><strong>🎬 Scenario Studio</strong> - Compare 2-4 retirement scenarios side-by-side with interactive charts!</li>
                    <li><strong>🏥 Medicare Comparison Tool</strong> - Analyze Medigap vs Medicare Advantage plans</li>
                    <li><strong>📊 Enhanced Exports</strong> - Download comparisons as PDF, Excel, or CSV</li>
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
        st.success("✅ **Welcome back!** You have saved retirement plans ready to analyze.\n\n**Start INTAKE** to create a new plan or update existing data.")
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

    # DIRECT TO INTAKE: After accepting beta disclaimer, go straight to INTAKE
    # CRITICAL FIX: Only rerun if we haven't already transitioned (prevents infinite loop!)
    if not st.session_state.get('mode_selected', False) or st.session_state.get('current_mode') != "INTAKE":
        st.session_state.mode_selected = True
        st.session_state.current_mode = "INTAKE"
        st.rerun()


# =============================================================================
# INTAKE MODE
# =============================================================================

def show_intake_mode():
    """Display INTAKE questionnaire mode"""

    # WELCOME BACK: If user clicked "Continue My Plan", load from localStorage (user-triggered, safe)
    if st.session_state.get('load_from_local_storage', False):
        st.session_state['load_from_local_storage'] = False  # Clear flag FIRST to prevent loops
        try:
            from utils.snapshot_manager import _get_local_storage, decrypt_data
            localS = _get_local_storage()
            if localS:
                # Read encrypted index from localStorage
                encrypted_index = localS.get('ff_snapshots_index')
                if encrypted_index:
                    index = decrypt_data(encrypted_index, localS)
                    if index and index.get('snapshots'):
                        # Get most recent snapshot ID
                        most_recent = index['snapshots'][-1]
                        snapshot_id = most_recent['id']
                        # Read encrypted snapshot data
                        encrypted_data = localS.get(f'ff_snapshot_{snapshot_id}')
                        if encrypted_data:
                            snapshot_data = decrypt_data(encrypted_data, localS)
                            if snapshot_data:
                                # Load data into session_state
                                for key, value in snapshot_data.items():
                                    if key.startswith(('input_', 'temp_', '_protected')) or key in (
                                        'children_list', 'children_rows', 'inheritance_list', 'inherit_rows',
                                        'goals_list', 'goals_data', 'custom_expenses', 'custom_expenses_list',
                                        'custom_income', 'custom_income_list', 'schema_version'
                                    ):
                                        st.session_state[key] = value
                                st.session_state['current_snapshot_id'] = snapshot_id
                                st.session_state['_intake_autoload_attempted'] = True  # Prevent duplicate load
                                print(f"[WELCOME BACK] Loaded snapshot from localStorage: {snapshot_id}")
        except Exception as e:
            print(f"[WELCOME BACK] Error loading from localStorage: {e}")

    # AUTO-LOAD: If user has saved plans but no current plan loaded, load the most recent
    # CRITICAL: Only try loading ONCE per session to prevent localStorage rerun loop
    if st.session_state.get('_intake_autoload_attempted', False):
        pass  # Already attempted, skip
    elif 'current_snapshot_id' not in st.session_state or st.session_state.get('current_snapshot_id') is None:
        st.session_state['_intake_autoload_attempted'] = True  # Mark as attempted FIRST
        from utils.snapshot_manager import get_snapshots_index, load_snapshot
        index = get_snapshots_index()
        if index.get('snapshots') and len(index['snapshots']) > 0:
            # Load the most recent snapshot
            most_recent = index['snapshots'][-1]
            snapshot_data = load_snapshot(most_recent['id'])
            if snapshot_data:
                # Load data into session_state
                for key, value in snapshot_data.items():
                    # WHITELIST: Only copy safe data keys, never widget keys
                    if key.startswith(('input_', 'temp_', '_protected')) or key in (
                        'children_list', 'children_rows', 'inheritance_list', 'inherit_rows',
                        'goals_list', 'goals_data', 'custom_expenses', 'custom_expenses_list',
                        'custom_income', 'custom_income_list', 'schema_version'
                    ):
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
        st.session_state.intake_completed = False
        return

    # =============================================
    # MODE SELECTION GATEWAY - Must choose before Page 1
    # =============================================
    if "intake_mode" not in st.session_state or st.session_state.get("intake_mode") is None:
        st.markdown("## Choose Your Entry Mode")
        st.markdown("Select how you'd like to enter your information:")
        st.markdown("")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
### 📋 Full Mode
**Complete questionnaire with all fields**

- All income sources
- Detailed expense categories
- All asset types
- Family planning events

*Recommended for accurate projections*
            """)
            if st.button("Start Full Mode", type="primary", use_container_width=True, key="btn_full_mode"):
                st.session_state["intake_mode"] = "full"
                st.rerun()

        with col2:
            st.markdown("""
### ⚡ Quick Mode
**Essential fields only**

- Core income (SS, pension)
- Basic expenses
- Main retirement accounts
- Simplified entry

*Faster, for quick estimates*
            """)
            if st.button("Start Quick Mode", use_container_width=True, key="btn_quick_mode"):
                st.session_state["intake_mode"] = "quick"
                st.rerun()

        # Stop here - don't load intake pages until mode is chosen
        st.stop()

    # Mode is selected - proceed to intake questionnaire
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

    render_top_navigation(current="Analysis")

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