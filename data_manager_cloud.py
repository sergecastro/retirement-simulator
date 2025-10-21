# data_manager_cloud.py - localStorage-based scenario management
# Works on both local AND cloud deployments
import streamlit as st
import json
from datetime import datetime
from embedded_scenarios import EMBEDDED_SCENARIOS
import streamlit.components.v1 as components

def apply_scenario_data_safe(scenario_data):
    """SAFE: Apply loaded scenario data WITH input_ prefix to match your forms"""

    # Apply all scenario fields to session state
    for key, value in scenario_data.items():
        # Skip family table keys - we'll handle them separately
        if key in ["children_data", "inheritance_data", "goals_data",
                   "children_list", "inheritance_list", "goals_list",
                   "children_rows", "inherit_rows", "schema_version", "saved_at"]:
            continue

        # If key already has input_ prefix, use it directly
        if key.startswith("input_"):
            st.session_state[key] = value
        else:
            # If key doesn't have prefix, add it
            st.session_state[f"input_{key}"] = value

    # CRITICAL FIX: Handle family tables
    children = (scenario_data.get("children_list") or
                scenario_data.get("children_rows") or
                scenario_data.get("children_data") or [])
    st.session_state["children_list"] = children
    st.session_state["children_rows"] = children

    # Inheritances
    inheritances = (scenario_data.get("inheritance_list") or
                   scenario_data.get("inherit_rows") or
                   scenario_data.get("inheritance_data") or [])
    st.session_state["inheritance_list"] = inheritances
    st.session_state["inherit_rows"] = inheritances

    # Goals
    goals = (scenario_data.get("goals_list") or
             scenario_data.get("goals_data") or [])
    st.session_state["goals_list"] = goals
    st.session_state["goals_data"] = goals

    # Mortgage name variations
    if "input_mortgage_balance" in scenario_data:
        st.session_state["input_mortgage_balance"] = scenario_data["input_mortgage_balance"]
        st.session_state["input_primary_residence_mortgage"] = scenario_data["input_mortgage_balance"]
    elif "mortgage_balance" in scenario_data:
        st.session_state["input_mortgage_balance"] = scenario_data["mortgage_balance"]
        st.session_state["input_primary_residence_mortgage"] = scenario_data["mortgage_balance"]

    # Set flag to indicate scenario was loaded
    st.session_state['scenario_loaded'] = True

    return True


def collect_current_scenario_data():
    """Collect all current session state into a scenario dictionary"""
    current_data = {}

    # Add metadata
    current_data["schema_version"] = "3.0"
    current_data["saved_at"] = datetime.now().isoformat()

    # Save all input_ fields
    for key in st.session_state:
        if key.startswith('input_'):
            clean_key = key.replace('input_', '')
            value = st.session_state[key]
            if isinstance(value, (int, float, str, bool, list, dict, type(None))):
                current_data[clean_key] = value

    # Family data – write all variants for compatibility
    current_data["goals_list"] = st.session_state.get("goals_list", st.session_state.get("goals_data", []))
    current_data["goals_data"] = current_data["goals_list"]

    current_data["children_list"] = st.session_state.get("children_list", st.session_state.get("children_rows", []))
    current_data["children_rows"] = current_data["children_list"]
    current_data["children_data"] = current_data["children_list"]

    current_data["inheritance_list"] = st.session_state.get("inheritance_list", st.session_state.get("inherit_rows", []))
    current_data["inherit_rows"] = current_data["inheritance_list"]
    current_data["inheritance_data"] = current_data["inheritance_list"]

    # Mortgage name variations
    if "mortgage_balance" in current_data:
        current_data["primary_residence_mortgage"] = current_data["mortgage_balance"]

    return current_data


def get_user_scenarios_from_localstorage():
    """Get list of user scenarios from localStorage via JavaScript"""

    # JavaScript code to retrieve scenarios from localStorage
    js_code = """
    <script>
    // Get all user scenarios from localStorage
    const scenarios = JSON.parse(localStorage.getItem('retirement_scenarios') || '{}');
    const scenarioNames = Object.keys(scenarios);

    // Send to Streamlit
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: scenarioNames
    }, '*');
    </script>
    """

    # Return empty list by default (will be populated by JS callback)
    return []


def save_scenario_to_localstorage(scenario_name, scenario_data):
    """Save scenario to browser localStorage"""

    scenario_json = json.dumps(scenario_data)

    # JavaScript to save to localStorage
    js_code = f"""
    <script>
    (function() {{
        try {{
            // Get existing scenarios
            let scenarios = JSON.parse(localStorage.getItem('retirement_scenarios') || '{{}}');

            // Add/update this scenario
            scenarios['{scenario_name}'] = {scenario_json};

            // Save back to localStorage
            localStorage.setItem('retirement_scenarios', JSON.stringify(scenarios));

            console.log('Saved scenario: {scenario_name}');

            // Notify Streamlit of success
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: {{success: true, name: '{scenario_name}'}}
            }}, '*');
        }} catch(e) {{
            console.error('localStorage save failed:', e);
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: {{success: false, error: e.message}}
            }}, '*');
        }}
    }})();
    </script>
    """

    components.html(js_code, height=0)
    return True


def load_scenario_from_localstorage(scenario_name):
    """Load scenario from browser localStorage"""

    # We'll use session state to pass the scenario name, then JS will load it
    st.session_state['_load_scenario_name'] = scenario_name

    js_code = f"""
    <script>
    (function() {{
        try {{
            // Get scenarios from localStorage
            const scenarios = JSON.parse(localStorage.getItem('retirement_scenarios') || '{{}}');
            const scenario = scenarios['{scenario_name}'];

            if (scenario) {{
                // Send scenario data to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: {{success: true, data: scenario}}
                }}, '*');
            }} else {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: {{success: false, error: 'Scenario not found'}}
                }}, '*');
            }}
        }} catch(e) {{
            console.error('localStorage load failed:', e);
        }}
    }})();
    </script>
    """

    components.html(js_code, height=0)


def delete_scenario_from_localstorage(scenario_name):
    """Delete scenario from browser localStorage"""

    js_code = f"""
    <script>
    (function() {{
        try {{
            let scenarios = JSON.parse(localStorage.getItem('retirement_scenarios') || '{{}}');
            delete scenarios['{scenario_name}'];
            localStorage.setItem('retirement_scenarios', JSON.stringify(scenarios));
            console.log('Deleted scenario: {scenario_name}');

            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: {{success: true}}
            }}, '*');
        }} catch(e) {{
            console.error('localStorage delete failed:', e);
        }}
    }})();
    </script>
    """

    components.html(js_code, height=0)
    return True


def manage_scenarios_cloud(is_trusted_user, age_group=None):
    """Cloud-compatible scenario management using session_state + download backups"""

    # Initialize user scenarios storage
    if 'user_scenarios' not in st.session_state:
        st.session_state['user_scenarios'] = {}

    # Create sidebar UI
    st.sidebar.markdown("---")
    st.sidebar.header("📂 Scenario Management")

    # AUTO-LOAD DEFAULT SCENARIO ON FIRST VISIT
    if 'scenario_auto_loaded' not in st.session_state:
        if 'scenario_loaded' not in st.session_state:
            # Load appropriate default based on user type
            if is_trusted_user:
                default_scenario = EMBEDDED_SCENARIOS['70+_RETIREMENT_SCENARIO_PRIVATE']
                default_name = '70+ Retirement (Private - Trusted)'
            else:
                default_scenario = EMBEDDED_SCENARIOS['ORIGINAL_70+_RETIREMENT_SCENARIO']
                default_name = 'Original 70+ Retirement (Demo)'

            apply_scenario_data_safe(default_scenario)
            st.session_state['current_scenario'] = default_name
            st.session_state['scenario_auto_loaded'] = True
            st.session_state['scenario_loaded'] = True

    # Get current scenario name
    current = st.session_state.get('current_scenario', 'Original 70+ Retirement (Demo)')

    st.sidebar.info(f"📋 **Currently:** {current}")

    # ============================================
    # LOAD SCENARIO SECTION - COMPACT
    # ============================================
    st.sidebar.subheader("📥 Load Scenario")

    # Build list of available scenarios (embedded + user's saved)
    embedded_options = []
    if is_trusted_user:
        embedded_options.append('70+ Retirement (Private - Trusted)')
    embedded_options.append('Original 70+ Retirement (Demo)')

    # Add user's saved scenarios
    user_scenario_names = list(st.session_state.get('user_scenarios', {}).keys())
    all_scenarios = embedded_options + user_scenario_names

    # Compact selector
    selected_scenario = st.sidebar.selectbox(
        "Select:",
        options=all_scenarios,
        index=0 if current not in all_scenarios else all_scenarios.index(current),
        key="scenario_selector"
    )

    if st.sidebar.button("📂 Load", use_container_width=True):
        # Check if it's a user-saved scenario first
        if selected_scenario in st.session_state.get('user_scenarios', {}):
            scenario_data = st.session_state['user_scenarios'][selected_scenario]
        # Otherwise load from embedded
        elif selected_scenario == 'Original 70+ Retirement (Demo)':
            scenario_data = EMBEDDED_SCENARIOS['ORIGINAL_70+_RETIREMENT_SCENARIO']
        else:
            scenario_data = EMBEDDED_SCENARIOS['70+_RETIREMENT_SCENARIO_PRIVATE']

        apply_scenario_data_safe(scenario_data)
        st.session_state['current_scenario'] = selected_scenario
        st.sidebar.success(f"✅ Loaded")
        st.rerun()

    # Upload - in expander to save space
    with st.sidebar.expander("📤 Upload File"):
        if 'last_uploaded_file' not in st.session_state:
            st.session_state['last_uploaded_file'] = None

        uploaded_file = st.file_uploader(
            "Choose JSON:",
            type=['json'],
            key="scenario_uploader"
        )

        if uploaded_file is not None:
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state['last_uploaded_file'] != file_id:
                try:
                    file_content = uploaded_file.read()
                    scenario_data = json.loads(file_content)
                    if isinstance(scenario_data, dict):
                        apply_scenario_data_safe(scenario_data)
                        scenario_name = uploaded_file.name.replace('.json', '')
                        st.session_state['current_scenario'] = scenario_name
                        st.session_state['last_uploaded_file'] = file_id
                        st.success(f"✅ Loaded")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # ============================================
    # SAVE SCENARIO SECTION - COMPACT
    # ============================================
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Save Scenario")

    # Show current name (READ-ONLY)
    st.sidebar.caption(f"**Current:** {current}")

    # SAVE CURRENT button - saves to session_state
    if st.sidebar.button("💾 Save Current Scenario", use_container_width=True, type="primary"):
        scenario_data = collect_current_scenario_data()

        # Save to session_state (persists during session)
        st.session_state['user_scenarios'][current] = scenario_data

        # Also prepare download
        st.session_state['show_download_reminder'] = True
        st.session_state['last_saved_scenario'] = scenario_data
        st.session_state['last_saved_name'] = current

        st.sidebar.success(f"✅ Saved: {current}")
        st.rerun()

    # SAVE AS NEW - Compact
    with st.sidebar.expander("💾 Save As New Scenario"):
        new_scenario_name = st.text_input(
            "New name:",
            value="",
            placeholder="My Retirement Plan 2025",
            key="new_scenario_name_input"
        )

        if st.button("💾 Create New", use_container_width=True, disabled=not new_scenario_name):
            if new_scenario_name:
                scenario_data = collect_current_scenario_data()

                # Save to session_state
                st.session_state['user_scenarios'][new_scenario_name] = scenario_data
                st.session_state['current_scenario'] = new_scenario_name

                # Prepare download
                st.session_state['show_download_reminder'] = True
                st.session_state['last_saved_scenario'] = scenario_data
                st.session_state['last_saved_name'] = new_scenario_name

                st.success(f"✅ Created: {new_scenario_name}")
                st.rerun()


    # DOWNLOAD REMINDER (after save)
    if st.session_state.get('show_download_reminder', False):
        st.sidebar.warning("💡 **Recommended:** Download a backup copy for safety!")

        scenario_data = st.session_state.get('last_saved_scenario', collect_current_scenario_data())
        scenario_name = st.session_state.get('last_saved_name', current)
        scenario_json = json.dumps(scenario_data, indent=2)

        clean_name = "".join(c for c in scenario_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '-')
        download_filename = f"{clean_name}.json"

        st.sidebar.download_button(
            label="📥 Download Backup",
            data=scenario_json,
            file_name=download_filename,
            mime="application/json",
            help="Download this scenario as a backup file",
            use_container_width=True,
            type="secondary"
        )

        if st.sidebar.button("✅ Got it, dismiss", use_container_width=True):
            st.session_state['show_download_reminder'] = False
            st.rerun()

    # ============================================
    # DELETE SCENARIO - COMPACT
    # ============================================
    with st.sidebar.expander("🗑️ Delete Scenarios"):
        st.caption("Coming soon: Select & delete saved scenarios")

    return {}


def load_scenario_from_path(uploaded_file):
    """
    Load a scenario from an uploaded JSON file (e.g., intake-payload.json)
    Returns: (success: bool, scenario_data: dict or None)
    """
    try:
        file_content = uploaded_file.read()
        scenario_data = json.loads(file_content)

        if not isinstance(scenario_data, dict):
            return False, None

        apply_scenario_data_safe(scenario_data)
        st.session_state['current_scenario'] = f"Imported: {uploaded_file.name}"
        st.session_state['scenario_loaded'] = True

        return True, scenario_data

    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON file: {e}")
        return False, None
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return False, None
