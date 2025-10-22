# utils/local_storage.py - Browser localStorage integration for Streamlit
"""
Provides localStorage persistence for scenarios and draft data.
Uses JavaScript via st.components to interact with browser's localStorage.
"""

import streamlit as st
import json
from typing import Dict, Any, Optional

def inject_local_storage_script():
    """
    Inject JavaScript to enable localStorage read/write from Streamlit.
    Call this once at app startup.
    """
    js_code = """
    <script>
    // Create global functions for localStorage operations
    window.saveToLocalStorage = function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('localStorage save error:', e);
            return false;
        }
    };

    window.loadFromLocalStorage = function(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('localStorage load error:', e);
            return null;
        }
    };

    window.removeFromLocalStorage = function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('localStorage remove error:', e);
            return false;
        }
    };

    window.listLocalStorageKeys = function(prefix) {
        try {
            const keys = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (!prefix || key.startsWith(prefix)) {
                    keys.push(key);
                }
            }
            return keys;
        } catch (e) {
            console.error('localStorage list error:', e);
            return [];
        }
    };

    // Signal that localStorage is ready
    window.localStorageReady = true;
    console.log('localStorage helper functions initialized');
    </script>
    """
    st.components.v1.html(js_code, height=0)


def save_to_local_storage(key: str, data: Dict[str, Any]) -> bool:
    """
    Save data to browser's localStorage.

    Args:
        key: Storage key (e.g., 'retirement_scenario_draft')
        data: Dictionary to save

    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert data to JSON string for storage
        json_data = json.dumps(data)

        # Use JavaScript to save to localStorage
        js_save = f"""
        <script>
        const data = {json_data};
        const success = window.saveToLocalStorage('{key}', data);
        if (success) {{
            console.log('Saved to localStorage:', '{key}');
        }}
        </script>
        """
        st.components.v1.html(js_save, height=0)
        return True
    except Exception as e:
        st.error(f"Failed to save to localStorage: {e}")
        return False


def load_from_local_storage_component(key: str) -> None:
    """
    Create a component that loads data from localStorage into session state.
    This uses a two-way communication approach.

    Args:
        key: Storage key to load from
    """
    component_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script>
        function loadData() {{
            try {{
                const data = localStorage.getItem('{key}');
                if (data) {{
                    // Send data back to Streamlit
                    window.parent.postMessage({{
                        type: 'localStorage_data',
                        key: '{key}',
                        data: JSON.parse(data)
                    }}, '*');
                }} else {{
                    window.parent.postMessage({{
                        type: 'localStorage_data',
                        key: '{key}',
                        data: null
                    }}, '*');
                }}
            }} catch (e) {{
                console.error('Error loading from localStorage:', e);
                window.parent.postMessage({{
                    type: 'localStorage_error',
                    key: '{key}',
                    error: e.message
                }}, '*');
            }}
        }}

        // Load data when component mounts
        window.onload = loadData;
        </script>
    </head>
    <body>
        <div style="display:none">Loading from localStorage...</div>
    </body>
    </html>
    """
    st.components.v1.html(component_html, height=0)


def save_scenario_to_local_storage(scenario_name: str, scenario_data: Dict[str, Any]) -> bool:
    """
    Save a named scenario to localStorage.

    Args:
        scenario_name: Name of the scenario
        scenario_data: Complete scenario data dictionary

    Returns:
        True if successful
    """
    storage_key = f"retirement_scenario_{scenario_name}"
    return save_to_local_storage(storage_key, scenario_data)


def save_draft_to_local_storage(draft_data: Dict[str, Any]) -> bool:
    """
    Save draft/auto-save data to localStorage.
    This is for the silent auto-save feature.

    Args:
        draft_data: Current session state data

    Returns:
        True if successful
    """
    return save_to_local_storage("retirement_draft", draft_data)


def get_scenario_list_from_local_storage() -> list:
    """
    Get list of all saved scenarios from localStorage.
    Uses a synchronous approach via session state.

    Returns:
        List of scenario names
    """
    # This requires the localStorage keys to be loaded into session state first
    # We'll implement this with a helper component
    if 'localStorage_scenario_keys' not in st.session_state:
        return []

    keys = st.session_state.get('localStorage_scenario_keys', [])
    # Extract scenario names from keys like "retirement_scenario_MyScenario"
    scenarios = []
    for key in keys:
        if key.startswith("retirement_scenario_") and key != "retirement_scenario_draft":
            scenario_name = key.replace("retirement_scenario_", "")
            scenarios.append(scenario_name)

    return scenarios


def delete_scenario_from_local_storage(scenario_name: str) -> bool:
    """
    Delete a scenario from localStorage.

    Args:
        scenario_name: Name of scenario to delete

    Returns:
        True if successful
    """
    storage_key = f"retirement_scenario_{scenario_name}"
    js_delete = f"""
    <script>
    window.removeFromLocalStorage('{storage_key}');
    console.log('Deleted from localStorage:', '{storage_key}');
    </script>
    """
    st.components.v1.html(js_delete, height=0)
    return True


# Simpler synchronous approach using st.text_input + JavaScript
def create_local_storage_bridge():
    """
    Creates a bidirectional bridge between Streamlit and localStorage.
    This uses hidden text inputs to communicate data.
    """
    st.markdown("""
    <script>
    // Function to sync all scenarios from localStorage to Streamlit
    function syncScenariosToStreamlit() {
        const scenarios = {};
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('retirement_scenario_')) {
                try {
                    scenarios[key] = JSON.parse(localStorage.getItem(key));
                } catch (e) {
                    console.error('Error parsing scenario:', key, e);
                }
            }
        }

        // Store in a data attribute that Streamlit can read
        const bridge = document.getElementById('localStorage-bridge');
        if (bridge) {
            bridge.setAttribute('data-scenarios', JSON.stringify(scenarios));
        }
    }

    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', syncScenariosToStreamlit);
    } else {
        syncScenariosToStreamlit();
    }
    </script>
    <div id="localStorage-bridge" style="display:none"></div>
    """, unsafe_allow_html=True)
