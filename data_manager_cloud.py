# data_manager_cloud.py - Cloud-compatible scenario management
# Uses file upload/download instead of local filesystem
import streamlit as st
import json
from datetime import datetime

def apply_scenario_data_safe(scenario_data):
    """SAFE: Apply loaded scenario data WITH input_ prefix to match your forms"""

    # Apply all scenario fields to session state
    for key, value in scenario_data.items():
        # Skip family table keys - we'll handle them separately
        if key in ["children_data", "inheritance_data", "goals_data",
                   "children_list", "inheritance_list", "goals_list",
                   "children_rows", "inherit_rows", "schema_version"]:
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


def manage_scenarios_cloud(is_trusted_user, age_group=None):
    """Cloud-compatible scenario management using file upload/download"""

    # Create sidebar UI
    st.sidebar.markdown("---")
    st.sidebar.header("📂 Scenario Management")

    # Get current scenario name
    current = st.session_state.get('current_scenario', 'New Scenario')

    if current != "New Scenario":
        st.sidebar.info(f"📋 **Currently:** {current}")

    # ============================================
    # LOAD SCENARIO FROM FILE
    # ============================================
    st.sidebar.subheader("📥 Load Scenario")

    uploaded_file = st.sidebar.file_uploader(
        "Upload scenario JSON file:",
        type=['json'],
        help="Select a previously saved scenario file",
        key="scenario_uploader"
    )

    if uploaded_file is not None:
        try:
            # Read the uploaded file
            file_content = uploaded_file.read()
            scenario_data = json.loads(file_content)

            # Validate it's a dictionary
            if not isinstance(scenario_data, dict):
                st.sidebar.error("❌ Invalid scenario file format")
            else:
                # Apply the scenario data
                apply_scenario_data_safe(scenario_data)

                # Update current scenario name
                scenario_name = uploaded_file.name.replace('.json', '')
                st.session_state['current_scenario'] = scenario_name
                st.session_state['scenario_loaded'] = True

                st.sidebar.success(f"✅ Loaded: {scenario_name}")
                st.rerun()

        except json.JSONDecodeError as e:
            st.sidebar.error(f"❌ Invalid JSON file: {e}")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading file: {e}")

    # ============================================
    # SAVE SCENARIO TO FILE
    # ============================================
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Save Scenario")

    # Scenario name input
    default_name = current if current != "New Scenario" else "my-scenario"
    scenario_save_name = st.sidebar.text_input(
        "Scenario name:",
        value=default_name,
        placeholder="e.g., retirement-plan-2025",
        help="Enter a name for your scenario (will be saved as .json file)",
        key="scenario_save_name_input"
    )

    # Generate download filename
    if scenario_save_name:
        # Clean filename (remove invalid characters)
        clean_name = "".join(c for c in scenario_save_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '-')
        download_filename = f"{clean_name}.json"
    else:
        download_filename = "scenario.json"

    # Collect current data
    scenario_data = collect_current_scenario_data()
    scenario_json = json.dumps(scenario_data, indent=2)

    # Download button
    st.sidebar.download_button(
        label="💾 Download Scenario",
        data=scenario_json,
        file_name=download_filename,
        mime="application/json",
        help="Download your current scenario as a JSON file",
        use_container_width=True
    )

    st.sidebar.info("""
    **💡 How it works:**
    - Click "Download Scenario" to save current data to your computer
    - Use "Upload scenario" to load it back later
    - Share files with others or keep backups!
    """)

    # ============================================
    # CLEAR/RESET SCENARIO
    # ============================================
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗑️ Clear Scenario")

    if st.sidebar.button("🔄 Start New Scenario", help="Clear all data and start fresh"):
        # Clear all input fields
        for k in list(st.session_state.keys()):
            if k.startswith('input_') or k in ['children_list', 'children_rows', 'inheritance_list', 'inherit_rows', 'goals_list', 'goals_data']:
                del st.session_state[k]

        st.session_state['current_scenario'] = "New Scenario"
        st.session_state.pop('scenario_loaded', None)
        st.sidebar.success("✅ Started New Scenario")
        st.rerun()

    return {}  # Return empty dict for compatibility with old code


def load_scenario_from_path(uploaded_file):
    """
    Load a scenario from an uploaded JSON file (e.g., intake-payload.json)
    Returns: (success: bool, scenario_data: dict or None)
    """
    try:
        # Read the uploaded file
        file_content = uploaded_file.read()
        scenario_data = json.loads(file_content)

        # Validate it's a dictionary
        if not isinstance(scenario_data, dict):
            return False, None

        # Apply the scenario data using our safe function
        apply_scenario_data_safe(scenario_data)

        # Mark as loaded from external file
        st.session_state['current_scenario'] = f"Imported: {uploaded_file.name}"
        st.session_state['scenario_loaded'] = True

        return True, scenario_data

    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON file: {e}")
        return False, None
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return False, None
