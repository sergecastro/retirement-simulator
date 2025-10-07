# data_manager.py - FIXED to save new field names from updated input widgets
import streamlit as st
import json
import os
from shutil import copyfile

def load_scenarios(filename="family_scenarios.json"):
    """Load scenarios from JSON file with error handling"""
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            st.warning(f"Error loading scenarios: {e}. Using backup if available.")
            backup_file = filename.replace('.json', '_backup.json')
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, "r") as f:
                        data = json.load(f)
                    return data if isinstance(data, dict) else {}
                except Exception as be:
                    st.warning(f"Backup load failed: {be}")
            return {}
    return {}

def save_scenarios(scenarios_dict, filename="family_scenarios.json"):
    """Save scenarios to JSON file with backup"""
    try:
        # Create backup
        if os.path.exists(filename):
            backup_file = filename.replace('.json', '_backup.json')
            copyfile(filename, backup_file)
        
        # Save new data with validation
        with open(filename, "w") as f:
            json.dump(scenarios_dict, f, indent=2)
        return True
    except TypeError as te:
        st.error(f"Save failed - non-serializable data: {te}. Reverting to backup.")
        if os.path.exists(backup_file):
            copyfile(backup_file, filename)
        return False
    except Exception as e:
        st.error(f"Error saving scenarios: {e}. Reverting to backup.")
        if os.path.exists(backup_file):
            copyfile(backup_file, filename)
        return False

def apply_scenario_data_safe(scenario_data):
    """SAFE: Apply loaded scenario data WITH input_ prefix to match your forms"""
    
    # Apply all scenario fields to session state WITH input_ prefix
    for key, value in scenario_data.items():
        if key not in ["children_data", "inheritance_data", "goals_data", "children_list", "inheritance_list", "goals_list"]:
            st.session_state[f"input_{key}"] = value
    
    # CRITICAL FIX: Handle both old and new field names for backward compatibility
    
    # Children data - check for new format first, then old
    if "children_list" in scenario_data:
        st.session_state["children_list"] = scenario_data["children_list"]
        st.session_state["children_rows"] = scenario_data["children_list"]  # Backward compat
    elif "children_data" in scenario_data:
        st.session_state["children_list"] = scenario_data["children_data"]
        st.session_state["children_rows"] = scenario_data["children_data"]
    
    # Inheritance data - check for new format first, then old
    if "inheritance_list" in scenario_data:
        st.session_state["inheritance_list"] = scenario_data["inheritance_list"]
        st.session_state["inherit_rows"] = scenario_data["inheritance_list"]  # Backward compat
    elif "inheritance_data" in scenario_data:
        st.session_state["inheritance_list"] = scenario_data["inheritance_data"]
        st.session_state["inherit_rows"] = scenario_data["inheritance_data"]
    
    # Goals data - check for new format first, then old
    if "goals_list" in scenario_data:
        st.session_state["goals_list"] = scenario_data["goals_list"]
        st.session_state["goals_data"] = scenario_data["goals_list"]  # Backward compat
    elif "goals_data" in scenario_data:
        st.session_state["goals_list"] = scenario_data["goals_data"]
        st.session_state["goals_data"] = scenario_data["goals_data"]
    
    # Set flag to indicate scenario was loaded
    st.session_state['scenario_loaded'] = True
    
    return True

def manage_scenarios(is_trusted_user, age_group=None):
    """FIXED: Scenario management that saves new field names"""
    
    # Load existing scenarios
    scenarios = load_scenarios()
    scenario_names = list(scenarios.keys())
    scenario_names = list(dict.fromkeys(scenario_names))  # Remove duplicates
    
    # Filter private scenarios for demo mode
    if not is_trusted_user:
        scenario_names = [name for name in scenario_names if "(Private)" not in name]
    
    # Create sidebar UI
    st.sidebar.markdown("---")
    st.sidebar.header("📂 Scenario Management")
    
    # SAFE: Auto-load for trusted users
    if is_trusted_user and age_group == "70+" and 'scenario_auto_loaded' not in st.session_state:
        if "70+ Retirement Scenario (Private)" in scenario_names:
            scenario_data = scenarios["70+ Retirement Scenario (Private)"]
            apply_scenario_data_safe(scenario_data)
            st.session_state['current_scenario'] = "70+ Retirement Scenario (Private)"
            st.session_state['scenario_auto_loaded'] = True
            st.sidebar.success("✅ Auto-loaded: 70+ Retirement Scenario (Private)")
    
    # Show current scenario status
    current = st.session_state.get('current_scenario', 'New Scenario')
    if current != "New Scenario":
        st.sidebar.info(f"📋 **Currently:** {current}")
    
    # LOAD SCENARIO DROPDOWN
    if current in scenario_names:
        default_index = scenario_names.index(current) + 1
    else:
        default_index = 0
        
    selected_scenario = st.sidebar.selectbox(
        "📥 Load Scenario:", 
        ["New Scenario"] + scenario_names, 
        index=default_index,
        help="Select a saved scenario to load"
    )
    
    # Handle scenario change
    if selected_scenario != current:
        if selected_scenario != "New Scenario":
            scenario_data = scenarios[selected_scenario]
            apply_scenario_data_safe(scenario_data)
            st.session_state['current_scenario'] = selected_scenario
            st.sidebar.success(f"✅ Loaded: {selected_scenario}")
            st.rerun()
        else:
            # Clear inputs for New Scenario
            for key in list(st.session_state.keys()):
                if key.startswith('input_') or key in ['children_rows', 'inherit_rows', 'goals_data', 'children_list', 'inheritance_list', 'goals_list']:
                    del st.session_state[key]
            st.session_state['current_scenario'] = "New Scenario"
            st.session_state.pop('scenario_loaded', None)
            st.sidebar.success("✅ Started New Scenario")
            st.rerun()
    
    # SAVE SCENARIO SECTION
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Save Scenario")
    
    if st.sidebar.button("💾 Save Current", help="Saves changes to the current scenario"):
        if 'current_scenario' in st.session_state and st.session_state['current_scenario'] != 'New Scenario':
            scenario_name = st.session_state['current_scenario']
            
            # CRITICAL FIX: Collect data including NEW field names
            current_data = {}
            
            # Save all input_ fields
            for key in st.session_state:
                if key.startswith('input_'):
                    clean_key = key.replace('input_', '')
                    value = st.session_state[key]
                    if isinstance(value, (int, float, str, bool, list, dict, type(None))):
                        current_data[clean_key] = value
            
            # CRITICAL FIX: Save NEW field names (goals_list, children_list, inheritance_list)
            # Try new names first, fall back to old names for backward compatibility
            current_data["goals_list"] = st.session_state.get("goals_list", st.session_state.get("goals_data", []))
            current_data["children_list"] = st.session_state.get("children_list", st.session_state.get("children_rows", []))
            current_data["inheritance_list"] = st.session_state.get("inheritance_list", st.session_state.get("inherit_rows", []))
            
            # Also save old field names for backward compatibility
            current_data["goals_data"] = current_data["goals_list"]
            current_data["children_data"] = current_data["children_list"]
            current_data["inheritance_data"] = current_data["inheritance_list"]
            
            scenarios[scenario_name] = current_data
            
            if save_scenarios(scenarios):
                st.sidebar.success(f"💾 Updated '{scenario_name}'")
                st.sidebar.info("Saved - use Load to verify")
            else:
                st.sidebar.error("❌ Failed to save - check details above")
        else:
            st.sidebar.warning("⚠️ Load a scenario first")
    
    st.sidebar.text_input(
        "Save as New Name:", 
        placeholder="e.g., '70+ PLUS 3 KIDS'",
        key="scenario_new_name"
    )
    
    if st.sidebar.button("💾 Save as New", help="Creates a new scenario"):
        new_name = st.session_state.get('scenario_new_name', '').strip()
        if new_name:
            # Same collection logic
            current_data = {}
            for key in st.session_state:
                if key.startswith('input_'):
                    clean_key = key.replace('input_', '')
                    value = st.session_state[key]
                    if isinstance(value, (int, float, str, bool, list, dict, type(None))):
                        current_data[clean_key] = value
            
            # CRITICAL FIX: Save NEW field names
            current_data["goals_list"] = st.session_state.get("goals_list", st.session_state.get("goals_data", []))
            current_data["children_list"] = st.session_state.get("children_list", st.session_state.get("children_rows", []))
            current_data["inheritance_list"] = st.session_state.get("inheritance_list", st.session_state.get("inherit_rows", []))
            
            # Also save old field names for backward compatibility
            current_data["goals_data"] = current_data["goals_list"]
            current_data["children_data"] = current_data["children_list"]
            current_data["inheritance_data"] = current_data["inheritance_list"]
            
            scenarios[new_name] = current_data
            
            if save_scenarios(scenarios):
                st.sidebar.success(f"💾 Saved as '{new_name}'")
                st.session_state['current_scenario'] = new_name
                st.sidebar.info("Saved - use Load to verify")
            else:
                st.sidebar.error("❌ Failed to save - check details above")
        else:
            st.sidebar.warning("⚠️ Enter a new name first")
    
    if st.sidebar.button("🔄 Refresh"):
        st.rerun()
    
    # DELETE SCENARIO SECTION (trusted users only)
    if is_trusted_user and selected_scenario != "New Scenario":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🗑️ Delete Scenario")
        st.sidebar.warning(f"Delete '{selected_scenario}'?")
        
        if st.sidebar.button("🗑️ Confirm Delete"):
            if selected_scenario in scenarios:
                del scenarios[selected_scenario]
                if save_scenarios(scenarios):
                    st.sidebar.success(f"🗑️ Deleted: {selected_scenario}")
                    st.session_state['current_scenario'] = "New Scenario"
                    st.rerun()
    
    # AVAILABLE SCENARIOS LIST
    if scenario_names:
        st.sidebar.markdown("---")
        st.sidebar.subheader(f"📋 Available ({len(scenario_names)})")
        for name in scenario_names:
            visibility = " 🔒" if "(Private)" in name else " 🌐"
            st.sidebar.text(f"• {name[:25]}{'...' if len(name) > 25 else ''}{visibility}")
    
    return scenarios