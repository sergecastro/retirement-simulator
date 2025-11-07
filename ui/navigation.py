"""
Family Forecast Navigation & Mode Selection
=====================================
Handles navigation between different modes and features of the application.

Author: Family Forecast Development Team
Last Updated: October 22, 2025
"""

import streamlit as st
from config.settings import get_feature_flags
from config.auth import is_trusted_user


# =============================================================================
# MODE SELECTION
# =============================================================================

def show_mode_selector():
    """
    Show mode selector in sidebar

    Returns:
        str: Selected mode ('INTAKE' or 'Analysis')
    """
    with st.sidebar:
        st.markdown("### 🎯 Mode Selection")

        mode = st.radio(
            "Choose your mode:",
            options=["INTAKE", "Analysis"],
            index=0,  # Default to INTAKE
            help="INTAKE: Guided questionnaire | Analysis: Advanced simulation"
        )

        st.markdown("---")

        return mode


# =============================================================================
# FEATURE TOGGLES (ANALYSIS MODE)
# =============================================================================

def show_feature_toggles(is_trusted):
    """
    Show feature toggles in sidebar for Analysis mode

    SIMPLIFIED: All features enabled by default - no checkboxes
    This prevents confusion and broken workflows

    Args:
        is_trusted: Whether user has trusted access

    Returns:
        dict: All features enabled
    """
    # ALL FEATURES ENABLED - No user toggles
    features = {
        'show_summary_metrics': True,
        'show_basic_charts': True,
        'show_timeline': True,
        'show_ai_advisor': True,
        'show_monte_carlo': True,
        'show_sankey': True,
        'show_longevity_analysis': True,
        'show_irmaa_analysis': False,  # Healthcare module disabled
        'show_scenario_comparison': True,
        'show_detailed_table': True
    }

    return features


# =============================================================================
# NAVIGATION MENU (FOR MULTI-PAGE APPS)
# =============================================================================

def show_navigation_menu():
    """
    Show navigation menu for different app sections

    Returns:
        str: Selected page
    """
    with st.sidebar:
        st.markdown("### 📍 Navigation")

        pages = [
            "🏠 Home",
            "📊 Analysis",
            "🏥 Healthcare",  # ✅ RE-ENABLED: Healthcare Cost Projector module
            "🤖 AI Advisor",
            "ℹ️ About"
        ]

        selected = st.radio(
            "Go to:",
            options=pages,
            label_visibility="collapsed"
        )

        # Return clean page name (without emoji)
        return selected.split(" ", 1)[1]


# =============================================================================
# MAIN NAVIGATION FUNCTION
# =============================================================================

def get_navigation_state():
    """
    Get complete navigation state

    Returns:
        dict: Navigation state with mode, features, page
    """
    # Get user type
    is_trusted = is_trusted_user()

    # Get mode
    mode = show_mode_selector()

    # Get features (only for Analysis mode)
    if mode == "Analysis":
        features = show_feature_toggles(is_trusted)
    else:
        features = {}

    # Get page selection (if using multi-page navigation)
    # page = show_navigation_menu()  # Uncomment if you want page navigation

    return {
        'mode': mode,
        'features': features,
        'is_trusted': is_trusted,
        # 'page': page  # Uncomment if using page navigation
    }


# =============================================================================
# SIDEBAR HEADER
# =============================================================================

def show_sidebar_header():
    """Display sidebar header with app info"""
    with st.sidebar:
        st.title("🏠 Family Forecast")
        st.markdown("*Retirement Planning Suite*")
        st.markdown("---")


# =============================================================================
# SIDEBAR FOOTER
# =============================================================================

def show_sidebar_footer(is_trusted):
    """
    Display sidebar footer with user info

    Args:
        is_trusted: Whether user has trusted access
    """
    with st.sidebar:
        st.markdown("---")

        if is_trusted:
            st.success("✅ Full Access")
        else:
            st.info("👤 Demo Access")

        st.caption("Family Forecast v3.0")


# =============================================================================
# COMPLETE SIDEBAR SETUP
# =============================================================================

def setup_sidebar():
    """
    Setup complete sidebar with navigation and controls

    Returns:
        dict: Navigation state
    """
    show_sidebar_header()

    nav_state = get_navigation_state()

    show_sidebar_footer(nav_state['is_trusted'])

    return nav_state


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("✅ Family Forecast Navigation Module")
    print("Functions: mode_selector, feature_toggles, navigation_menu")
