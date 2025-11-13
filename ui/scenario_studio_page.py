"""
Scenario Studio Page
Side-by-side comparison of multiple retirement scenarios
"""

import streamlit as st
from utils.comparison_scenarios import get_comparisons_for_plan, load_comparison_scenario
from utils.snapshot_manager import get_current_snapshot

def render_scenario_studio_page():
    """Render the Scenario Studio page"""

    # Page header
    st.markdown("# 🎬 Scenario Studio")
    st.markdown("**Compare multiple retirement strategies side-by-side**")
    st.markdown("---")

    # Get current base plan
    try:
        current_snapshot = get_current_snapshot()
        if not current_snapshot:
            st.warning("⚠️ Please complete the INTAKE questionnaire first to create scenarios.")
            if st.button("📝 Go to INTAKE"):
                st.session_state['mode'] = 'intake'
                st.rerun()
            return

        base_plan_id = current_snapshot.get('id')
        user_name = current_snapshot.get('user_info', {}).get('name', 'User')

        st.success(f"✅ Creating scenarios for: **{user_name}'s Base Plan**")

    except Exception as e:
        st.error(f"❌ Error loading base plan: {str(e)}")
        return

    # Get saved comparisons
    comparisons = get_comparisons_for_plan(base_plan_id)

    st.markdown("---")

    # Show saved scenarios count
    if len(comparisons) == 0:
        st.info("💡 **No saved scenarios yet!**")
        st.markdown("""
        To create scenarios:
        1. Go to **ANALYSIS** mode
        2. Adjust the sliders (income, expenses, etc.)
        3. Click **Run Comparison**
        4. Scroll down and click **💾 Save This Comparison**

        Come back here when you have 2+ scenarios to compare!
        """)

        if st.button("📊 Go to ANALYSIS"):
            st.session_state['mode'] = 'analysis'
            st.rerun()
        return

    elif len(comparisons) == 1:
        st.info(f"💡 **Found 1 saved scenario.** Save at least one more to enable side-by-side comparison.")
        st.markdown("Go to ANALYSIS mode to create more scenarios.")

        if st.button("📊 Go to ANALYSIS"):
            st.session_state['mode'] = 'analysis'
            st.rerun()

    else:
        # Show scenario selection (coming in next step)
        st.success(f"📊 **Found {len(comparisons)} saved scenarios!**")
        st.markdown("### Select Scenarios to Compare")
        st.info("🚧 **Comparison table coming in Step 3...** (Next 1 hour)")

        # List the scenarios for now
        st.markdown("**Your Saved Scenarios:**")
        for comp in comparisons:
            st.markdown(f"- {comp['name']} (Created: {comp['created_at'][:10]})")

    st.markdown("---")
    st.markdown("*More features coming soon: AI insights, probability analysis, timeline views*")
