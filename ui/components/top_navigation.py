"""
Top Navigation Bar Component
Provides navigation between all 5 modules on both mobile and desktop.
Created: November 26, 2025
"""

import streamlit as st


def render_top_navigation(current: str = "intake"):
    """
    Renders a horizontal navigation bar at the top of every page.

    Args:
        current: The current module name to highlight
                 Options: "INTAKE", "Analysis", "Healthcare", "scenario_studio", "social_security"
    """

    modules = [
        ("📝", "Intake", "INTAKE"),
        ("📊", "Analysis", "Analysis"),
        ("🏥", "Health", "Healthcare"),
        ("🎬", "Scenarios", "scenario_studio"),
        ("💰", "SS", "social_security"),
    ]

    # Add some spacing and a container
    st.markdown("""
        <style>
        .top-nav-container {
            background-color: #f0f2f6;
            padding: 0.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(modules))

    for i, (icon, label, mode_key) in enumerate(modules):
        with cols[i]:
            # Highlight current module
            if current == mode_key:
                button_label = f"**{icon} {label}**"
                button_type = "primary"
            else:
                button_label = f"{icon} {label}"
                button_type = "secondary"

            if st.button(
                button_label,
                key=f"nav_{mode_key}",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.current_mode = mode_key
                st.session_state.mode_selected = True
                st.rerun()
