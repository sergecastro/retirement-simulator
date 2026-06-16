# =============================================================================
# ui/command_center.py
# FamilyForecast.AI — Retirement Command Center
# Entry point, gate, sidebar, helpers, CSS
# Screen functions live in ui/command_center_screens.py
# =============================================================================

import streamlit as st
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — INTAKE GATE
# ─────────────────────────────────────────────────────────────────────────────

def has_intake_data() -> bool:
    core_keys = [
        "input_age",
        "input_user_name",
        "input_retirement_age",
        "input_monthly_expenses",
    ]
    for key in core_keys:
        if st.session_state.get(key) is not None:
            return True
    return False


def show_intake_required_gate():
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align:center; padding: 3rem 1rem;'>
            <div style='font-size:3rem;'>🎯</div>
            <h2 style='color:#0B2447;'>One Quick Step First</h2>
            <p style='font-size:1.1rem; color:#555; max-width:500px; margin:0 auto;'>
                The Command Center needs your retirement information to generate
                your monthly plan, guardrail status, and tax recommendations.
                <br><br>
                Complete Quick Mode (about 5 minutes) and you will land
                directly in the Command Center.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "⚡ Start Quick Mode → Command Center",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["intake_mode"] = "quick"
            st.session_state["beta_agreement"] = True
            st.session_state["mode_selected"] = True
            st.session_state["current_mode"] = "INTAKE"
            st.session_state["_after_intake_go_to"] = "command_center"
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def show_command_center():
    if not has_intake_data():
        show_intake_required_gate()
        return

    _inject_cc_styles()
    screen = _render_cc_sidebar()

    # Import here to avoid circular import at module load time
    from ui.command_center_screens import (
        screen_1_monthly_command,
        screen_2_income_recipe,
        screen_3_guardrail_zone,
        screen_4_tax_opportunities,
        screen_5_social_security,
        screen_6_rmd_forecast,
        screen_7_irmaa_watch,
        screen_8_what_changed,
        screen_9_next_best_action,
    )

    screen_map = {
        "monthly_command":   screen_1_monthly_command,
        "income_recipe":     screen_2_income_recipe,
        "guardrail_zone":    screen_3_guardrail_zone,
        "tax_opportunities": screen_4_tax_opportunities,
        "social_security":   screen_5_social_security,
        "rmd_forecast":      screen_6_rmd_forecast,
        "irmaa_watch":       screen_7_irmaa_watch,
        "what_changed":      screen_8_what_changed,
        "next_best_action":  screen_9_next_best_action,
    }

    render_fn = screen_map.get(screen, screen_1_monthly_command)
    render_fn()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def _render_cc_sidebar() -> str:
    screens = [
        ("monthly_command",   "🏠", "Monthly Command"),
        ("income_recipe",     "💵", "Income Recipe"),
        ("guardrail_zone",    "🚦", "Guardrail Zone"),
        ("tax_opportunities", "🧾", "Tax Opportunities"),
        ("social_security",   "📅", "Social Security"),
        ("rmd_forecast",      "📈", "RMD Forecast"),
        ("irmaa_watch",       "🏥", "IRMAA Watch"),
        ("what_changed",      "🔄", "What Changed"),
        ("next_best_action",  "✅", "Next Best Action"),
    ]

    if "cc_screen" not in st.session_state:
        st.session_state["cc_screen"] = "monthly_command"

    with st.sidebar:
        st.markdown(
            "<div class='cc-sidebar-title'>🎯 Command Center</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        for key, icon, label in screens:
            is_active = st.session_state["cc_screen"] == key
            if st.button(
                f"{icon}  {label}",
                key=f"cc_nav_{key}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state["cc_screen"] = key
                st.rerun()

        st.markdown("---")

        if st.button(
            "📊  Switch to Full Analysis",
            key="cc_nav_full_analysis",
            use_container_width=True,
        ):
            st.session_state["current_mode"] = "Analysis"
            st.session_state.pop("cc_screen", None)
            st.rerun()

    return st.session_state["cc_screen"]


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — SHARED HELPERS (imported by command_center_screens.py)
# ─────────────────────────────────────────────────────────────────────────────

def _screen_header(icon: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class='cc-screen-header'>
            <span class='cc-header-icon'>{icon}</span>
            <div>
                <div class='cc-header-title'>{title}</div>
                <div class='cc-header-subtitle'>{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _callout(color: str, icon: str, label: str, text: str):
    colors = {
        "green":  ("#d4edda", "#155724", "#28a745"),
        "yellow": ("#fff3cd", "#856404", "#ffc107"),
        "red":    ("#f8d7da", "#721c24", "#dc3545"),
        "blue":   ("#d1ecf1", "#0c5460", "#17a2b8"),
    }
    bg, text_color, border = colors.get(color, colors["blue"])
    st.markdown(
        f"""
        <div style='background:{bg}; border-left:4px solid {border};
                    padding:1rem 1.2rem; border-radius:6px; margin:1rem 0;
                    color:{text_color};'>
            <strong>{icon} {label}:</strong> {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _ai_ask_button(screen_name: str, context_hint: str):
    with st.expander(f"💬 Ask AI — {context_hint}", expanded=False):
        st.info(
            "AI advisor for this screen coming in Step 8. "
            "Your existing ai_advisor.py will power this chat, "
            "pre-loaded with your full retirement data as context."
        )
        st.text_input(
            "Your question:",
            key=f"cc_ai_q_{screen_name}",
            placeholder=f"Ask anything about {context_hint.lower()}…",
        )
        if st.button("Ask", key=f"cc_ai_ask_{screen_name}"):
            st.warning("AI wiring activates in Step 8 of the build.")


def _get(key: str, default=None):
    return st.session_state.get(key, default)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — CSS
# ─────────────────────────────────────────────────────────────────────────────

def _inject_cc_styles():
    st.markdown(
        """
        <style>
        .cc-sidebar-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #0B2447;
            padding: 0.5rem 0;
            letter-spacing: 0.03em;
        }
        .cc-screen-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1.2rem 0 0.5rem 0;
            border-bottom: 2px solid #E8A020;
            margin-bottom: 1.5rem;
        }
        .cc-header-icon { font-size: 2rem; line-height: 1; }
        .cc-header-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #0B2447;
            line-height: 1.2;
        }
        .cc-header-subtitle { font-size: 0.95rem; color: #666; margin-top: 0.15rem; }
        .stTable thead th {
            background-color: #0B2447 !important;
            color: white !important;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
