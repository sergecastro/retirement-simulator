# data_manager.py - FIXED indentation and scenario loading
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
    backup_file = filename.replace('.json', '_backup.json')
    try:
        # Create backup
        if os.path.exists(filename):
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
    
    # DEBUG: Show what we received (commented out for clean UI)
    # st.sidebar.write(f"🔍 DEBUG: Received {len(scenario_data)} keys")
    # st.sidebar.write(f"🔍 Sample keys: {list(scenario_data.keys())[:5]}")
    
    # Apply all scenario fields to session state
    for key, value in scenario_data.items():
        # Skip family table keys - we'll handle them separately
        if key in ["children_data", "inheritance_data", "goals_data", 
                   "children_list", "inheritance_list", "goals_list", 
                   "children_rows", "inherit_rows", "schema_version"]:
            continue
        
        # WHITELIST: Skip widget keys (editors, buttons, nav, etc.)
        skip_suffixes = ('_editor', '_button', '_checkbox', '_radio', '_selectbox')
        skip_prefixes = ('nav_', 'FormSubmitter:')
        if key.endswith(skip_suffixes) or key.startswith(skip_prefixes):
            continue
        
        # If key already has input_ prefix, use it directly
        if key.startswith("input_"):
            st.session_state[key] = value
            # st.sidebar.write(f"✅ Set {key} = {value}")  # DEBUG
        else:
            # If key doesn't have prefix, add it
            st.session_state[f"input_{key}"] = value
            # st.sidebar.write(f"✅ Set input_{key} = {value}")  # DEBUG
    
    # CRITICAL FIX: Handle family tables
    children = (scenario_data.get("children_list") or 
                scenario_data.get("children_rows") or 
                scenario_data.get("children_data") or [])
    st.session_state["children_list"] = children
    st.session_state["children_rows"] = children
    # st.sidebar.write(f"🔍 Loaded {len(children)} children")  # DEBUG

    # Inheritances
    inheritances = (scenario_data.get("inheritance_list") or
                   scenario_data.get("inherit_rows") or
                   scenario_data.get("inheritance_data") or [])
    st.session_state["inheritance_list"] = inheritances
    st.session_state["inherit_rows"] = inheritances
    # st.sidebar.write(f"🔍 Loaded {len(inheritances)} inheritances")  # DEBUG

    # Goals
    goals = (scenario_data.get("goals_list") or
             scenario_data.get("goals_data") or [])
    st.session_state["goals_list"] = goals
    st.session_state["goals_data"] = goals
    # st.sidebar.write(f"🔍 Loaded {len(goals)} goals")  # DEBUG

    # Mortgage name variations
    if "input_mortgage_balance" in scenario_data:
        st.session_state["input_mortgage_balance"] = scenario_data["input_mortgage_balance"]
        st.session_state["input_primary_residence_mortgage"] = scenario_data["input_mortgage_balance"]
    elif "mortgage_balance" in scenario_data:
        st.session_state["input_mortgage_balance"] = scenario_data["mortgage_balance"]
        st.session_state["input_primary_residence_mortgage"] = scenario_data["mortgage_balance"]

    # Set flag to indicate scenario was loaded
    st.session_state['scenario_loaded'] = True

    # st.sidebar.success("✅ Data applied to session_state!")  # DEBUG
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
    
    # Get current scenario
    if 'force_scenario_name' in st.session_state:
        current = st.session_state['force_scenario_name']
        st.session_state['current_scenario'] = current  # Re-apply it
    else:
        current = st.session_state.get('current_scenario', 'New Scenario')
    
    # NEW: Only auto-load if no scenario is currently loaded
    if is_trusted_user and age_group == "70+" and 'scenario_auto_loaded' not in st.session_state and current == 'New Scenario':
        # st.sidebar.write("🔍 DEBUG: Auto-load check triggered")
        # st.sidebar.write(f"🔍 scenario_auto_loaded in state: {'scenario_auto_loaded' in st.session_state}")

        if "70+ Retirement Scenario (Private)" in scenario_names:
            scenario_data = scenarios["70+ Retirement Scenario (Private)"]
            apply_scenario_data_safe(scenario_data)
            st.session_state['current_scenario'] = "70+ Retirement Scenario (Private)"
            st.session_state['scenario_auto_loaded'] = True
            st.sidebar.success("✅ Auto-loaded: 70+ Retirement Scenario (Private)")
            # st.sidebar.warning("⚠️ DEBUG: Just overwrote current_scenario!")
    
    # If current scenario is imported (not in saved list), add it to dropdown
    if current != "New Scenario" and current not in scenario_names:
        if current.startswith("Imported:"):
            # Add imported scenario to the top of the list
            scenario_names.insert(0, current)
    
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
            # NEW: Clear auto-load flag only for non-imported scenarios
            if not selected_scenario.startswith("Imported:"):
                st.session_state.pop('scenario_auto_loaded', None)
            st.sidebar.success(f"✅ Loaded: {selected_scenario}")
            st.rerun()
        else:
            # Clear for new scenario
            for k in list(st.session_state.keys()):
                if k.startswith('input_') or k in ['children_list', 'children_rows', 'inheritance_list', 'inherit_rows', 'goals_list', 'goals_data']:
                    del st.session_state[k]
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
            
            # CRITICAL FIX: Collect data including NEW field names (plus compatibility)
            current_data = {}

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
            # Same collection logic (plus compatibility)
            current_data = {}

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
    
    # AVAILABLE SCENARIOS LIST - COMMENTED OUT FOR CLEAN UI
    # if scenario_names:
    #     st.sidebar.markdown("---")
    #     st.sidebar.subheader(f"📋 Available ({len(scenario_names)})")
    #     for name in scenario_names:
    #         visibility = " 🔒" if "(Private)" in name else " 🌐"
    #         st.sidebar.text(f"• {name[:25]}{'...' if len(name) > 25 else ''}{visibility}")

    return scenarios

# ============================================================================
# LOAD FROM EXTERNAL FILE (e.g., intake-payload.json)
# ============================================================================

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