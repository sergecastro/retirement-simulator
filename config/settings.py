"""
Family Forecast Configuration & Settings
==================================
Application-wide settings, constants, styling, and configuration.

Author: Family Forecast Development Team
Last Updated: October 22, 2025
"""

import streamlit as st
import os
import socket


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Family Forecast Retirement Planner",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )


# =============================================================================
# CSS STYLING
# =============================================================================

CUSTOM_CSS = """
<!-- Plausible Analytics -->
<script defer data-domain="familyforecast.ai" src="https://plausible.io/js/script.js"></script>

<style>
    @import url('https://cdn.jsdelivr.net/npm/material-icons@1.13.14/iconfont/material-icons.min.css');

    /* Hide broken Material Icons text that overlaps content */
    .material-icons {
        font-size: 0 !important;
        width: 18px !important;
        display: inline-block !important;
    }

    /* Fix Streamlit expander arrow overlap */
    .streamlit-expanderHeader p {
        display: block !important;
        clear: both !important;
    }
    [data-testid="stExpander"] summary p {
        line-height: 1.5 !important;
        margin-top: 0 !important;
    }

    /* White background */
    .stApp {
        background-color: #FFFFFF !important;
    }

    /* Helvetica font */
    * {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }

    /* HIDE Streamlit's auto-generated pages navigation in sidebar */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
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

    /* Fix tooltip/popover display issues */
    [data-testid="stTooltipIcon"] {
        cursor: pointer !important;
        z-index: 999999 !important;
    }

    .stTooltipContent {
        z-index: 999999 !important;
        pointer-events: auto !important;
    }

    /* Ensure tooltips are clickable and visible */
    div[role="tooltip"] {
        z-index: 999999 !important;
        pointer-events: auto !important;
    }

    /* ==============================================
       MOBILE CONTRAST FIX - Force light theme
       Prevents dark mode from making text invisible
       ============================================== */

    /* Force light background everywhere */
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
    }

    /* Force dark text for all main content headers and labels */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp p, .stApp label, .stApp span,
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] p {
        color: #1E1E1E !important;
    }

    /* Force dark text in input labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #1E1E1E !important;
    }

    /* Info/warning boxes - ensure readable dark text */
    .stAlert p, [data-baseweb="notification"] p {
        color: #333333 !important;
    }

    /* NOTE: Sidebar uses default Streamlit styling (dark text on light background on desktop) */
    /* Do NOT override sidebar colors - only fix main content area */
</style>
"""


def apply_custom_css():
    """Apply custom CSS styling to the app"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =============================================================================
# FLASK API CONNECTION CHECK
# =============================================================================

def check_flask_connection():
    """
    Check if Flask explanation server is running

    Returns:
        bool: True if Flask server is accessible, False otherwise
    """
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


def show_flask_warning():
    """
    Display warning if Flask API is not running

    NOTE: Flask explanation server is OPTIONAL and not used in cloud deployment.
    AI Advisor uses direct Anthropic API calls instead.
    This warning is disabled for cloud deployment.
    """
    # Disable Flask warning - we use direct Anthropic API in ai_advisor.py
    # Flask server (explain_api_server.py) is optional and not deployed to Render
    return

    # Legacy code (kept for reference, not executed):
    # st.warning("""
    # ⚠️ **Claude Explanation API Not Running**
    # The "?" buttons on charts won't work without the explanation server.
    # **To enable chart explanations:**
    # 1. Open a new terminal/command prompt
    # 2. Navigate to your project folder
    # 3. Run: `start_flask_server.bat` (or `python explain_api_server.py`)
    # 4. Refresh this page
    # The app will work normally - you just won't have AI explanations for charts.
    # """)


# =============================================================================
# FEATURE FLAGS
# =============================================================================

def get_feature_flags(is_trusted_user=False):
    """
    Get feature flags based on user type

    Args:
        is_trusted_user: Whether user has trusted access

    Returns:
        dict: Feature flags
    """
    # Base features (available to all users)
    features = {
        'show_basic_charts': True,
        'show_summary_metrics': True,
        'show_timeline': True,
        'show_download_options': True,
        'show_ai_advisor': True,
    }

    # Advanced features (trusted users only)
    if is_trusted_user:
        features.update({
            'show_monte_carlo': True,
            'show_sankey': True,
            'show_longevity_analysis': True,
            'show_irmaa_analysis': True,
            'show_scenario_comparison': True,
            'show_detailed_table': True,
        })

    return features


# =============================================================================
# APPLICATION CONSTANTS
# =============================================================================

APP_VERSION = "3.0"
APP_NAME = "Family Forecast Lifecycle Retirement Planner"
APP_TAGLINE = "Interactive Financial Planning & Simulation Tool"


# =============================================================================
# FOOTER
# =============================================================================

FOOTER_HTML = f"""
<div style='text-align: center; color: #666;'>
<p><strong>{APP_NAME} v{APP_VERSION}</strong></p>
<p>Educational planning tool powered by Claude AI</p>
<p>Privacy-First Design | Session-Only Data Storage | Educational Purposes Only</p>
</div>
"""


def show_footer():
    """Display application footer"""
    st.markdown("---")

    # Footer with subtle centered logo
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.image("assets/branding/logo-familyforecast.png", width=60)

    st.markdown(FOOTER_HTML, unsafe_allow_html=True)


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_app():
    """
    Initialize the application with all settings
    Call this at the start of app.py
    """
    setup_page_config()
    apply_custom_css()

    # Check Flask API (but don't block)
    if not check_flask_connection():
        show_flask_warning()


if __name__ == "__main__":
    print("✅ Family Forecast Configuration Module")
    print(f"App: {APP_NAME} v{APP_VERSION}")
