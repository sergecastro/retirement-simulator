# File: data_manager.py
import json
import os
import streamlit as st

def load_scenarios(scenario_file):
    if os.path.exists(scenario_file):
        try:
            with open(scenario_file, "r") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            st.warning(f"Error loading scenarios: {e}. Auto-fixing scenario file to empty dict.")
            # Auto-fix: Overwrite with empty dict
            save_scenarios({}, scenario_file)
            return {}
    else:
        if st.session_state.get('IS_TRUSTED_USER', False):
            save_scenarios(st.session_state.get('EMBEDDED_SCENARIOS', {}), scenario_file)
            return st.session_state.get('EMBEDDED_SCENARIOS', {})
        return {}

def save_scenarios(scenarios_dict, scenario_file):
    try:
        tmp_file = scenario_file + ".tmp"
        with open(tmp_file, "w") as f:
            json.dump(scenarios_dict, f, indent=2)
        os.replace(tmp_file, scenario_file)
        return True
    except Exception as e:
        st.error(f"Error saving scenarios: {e}")
        return False