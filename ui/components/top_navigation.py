"""
Top Navigation Bar Component - Hamburger Menu Version
Provides navigation between all 6 modules via collapsible menu.
Works identically on mobile and desktop.
Created: November 26, 2025
Updated: December 2, 2025 - Converted to hamburger menu
"""
import streamlit as st


def render_top_navigation(current: str = "intake"):
    """
    Renders a hamburger menu navigation at the top of every page.

    Args:
        current: The current module name to highlight
                 Options: "INTAKE", "Analysis", "Healthcare", "scenario_studio", "social_security", "historical_tracking"
    """
    modules = [
        ("📝", "My Information", "INTAKE"),
        ("📊", "Analysis", "Analysis"),
        ("🏥", "Healthcare", "Healthcare"),
        ("🎬", "Scenarios", "scenario_studio"),
        ("💰", "Social Security", "social_security"),
        ("📈", "History", "historical_tracking"),
    ]

    # Find current module label for display
    current_label = "Navigate"
    for icon, label, mode_key in modules:
        if current == mode_key:
            current_label = f"{icon} {label}"
            break

    # Hamburger menu using st.popover
    with st.popover(f"☰ {current_label}", use_container_width=False):
        st.markdown("**Go to:**")

        for icon, label, mode_key in modules:
            # Highlight current module
            if current == mode_key:
                button_type = "primary"
            else:
                button_type = "secondary"

            if st.button(
                f"{icon} {label}",
                key=f"nav_{mode_key}",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.current_mode = mode_key
                st.session_state.mode_selected = True
                st.rerun()
