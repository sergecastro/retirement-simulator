"""
🎨 FOR LOVABLE: LANDING PAGE FUNCTION ONLY
==========================================
This file contains ONLY the landing page function that needs ForeCash branding.

FOCUS ON: Lines 10-110 (the show_mode_selection_landing_page function)

COLOR CHANGES NEEDED:
- #f0f8ff → #E8E6E0 (welcome box background)
- #4CAF50 → #E8B541 (welcome box border - green to gold)
- #2c3e50 → #003D5B (headers - dark blue to navy)
- #34495e → #555B66 (body text - blue-gray to ForeCash gray)
- #fff3cd → #003D5B (INTAKE card - yellow to navy)
- #856404 → #E8B541 or #FFFFFF (INTAKE text - brown to gold/white)
- #d1ecf1 → #E8E6E0 (Analysis card - cyan to light gray)
- #0c5460 → #003D5B (Analysis text - dark cyan to navy)

BUTTON STYLING:
- Primary buttons need navy background (#003D5B)
- Hover state should be gold (#E8B541)
- Note: Button styling is better done in config_settings.py CSS

"""

def show_mode_selection_landing_page(has_intake_data, is_trusted):
    """
    Display landing page for mode selection with welcome message

    Args:
        has_intake_data: Whether INTAKE data exists
        is_trusted: Whether user has trusted access
    """
    import streamlit as st

    # Welcome header
    st.title("🏠 Welcome to ForeCash!")
    st.markdown("## *Family Lifecycle Retirement Planner*")

    # ========================================================================
    # 🎨 LOVABLE: BRAND THIS WELCOME BOX!
    # ========================================================================
    # CHANGE: background-color: #f0f8ff → #E8E6E0 (light gray)
    # CHANGE: border-left: 5px solid #4CAF50 → 5px solid #E8B541 (gold)
    # CHANGE: color: #2c3e50 → #003D5B (navy headers)
    # CHANGE: color: #34495e → #555B66 (gray text)
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

    # ========================================================================
    # 🎨 LOVABLE: BRAND THIS INTAKE MODE CARD!
    # ========================================================================
    # CHANGE: background-color: #fff3cd → #003D5B (navy background)
    # CHANGE: color: #856404 → #E8B541 or #FFFFFF (gold/white text on navy)
    # ADD: border: 2px solid #E8B541 (gold border)
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
            ul>
            <p style='color: #856404; margin-bottom: 0;'><strong>✨ Best for:</strong> First-time users or updating your profile</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

        # INTAKE button - styling handled by config_settings.py CSS
        if st.button("🚀 Start INTAKE Questionnaire", type="primary", use_container_width=True, key="btn_intake"):
            st.session_state.mode_selected = True
            st.session_state.current_mode = "INTAKE"
            st.rerun()

    # ========================================================================
    # 🎨 LOVABLE: BRAND THIS ANALYSIS MODE CARD!
    # ========================================================================
    # CHANGE: background-color: #d1ecf1 → #E8E6E0 (light gray)
    # CHANGE: color: #0c5460 → #003D5B (navy text)
    # ADD: border: 2px solid #003D5B (navy border)
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

        # Analysis button - styling handled by config_settings.py CSS
        if st.button("🚀 Go to Analysis Tools", type="primary", use_container_width=True, key="btn_analysis"):
            st.session_state.mode_selected = True
            st.session_state.current_mode = "Analysis"
            st.rerun()

    st.markdown("---")

    # Help section - minimal branding needed here
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


"""
🎯 SUMMARY FOR LOVABLE:

THIS IS THE LANDING PAGE - THE FIRST THING USERS SEE!

Make it look premium and professional with ForeCash brand:

1. Welcome box: Light gray background (#E8E6E0) with gold accent border (#E8B541)
2. INTAKE card: Navy background (#003D5B) with gold/white text
3. Analysis card: Light gray background (#E8E6E0) with navy text (#003D5B)
4. All headers: Navy (#003D5B)
5. All body text: Dark gray (#555B66)

The goal: Users should immediately feel they're using a premium, trustworthy financial planning tool!

Navy = Trust & Stability
Gold = Prosperity & Optimism
Light Gray = Calm & Professional

After updating this function, copy it back to the main app.py file (same function, lines ~140-255)
"""
