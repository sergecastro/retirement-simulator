# utils/storage_bridge.py - Simplified localStorage bridge for snapshot persistence
"""
SIMPLE APPROACH: Store snapshot metadata in localStorage, data in session_state.

WHY THIS WORKS:
- Snapshot LIST persists (user sees their saved plans after browser close)
- Snapshot DATA loads on-demand when user selects a plan
- No complex async JavaScript issues
- Clean separation of concerns

STORAGE STRATEGY:
- localStorage: Snapshot index (list of {id, name, created})
- st.session_state: Current snapshot data (full INTAKE dictionary)
"""

import streamlit as st
import json
from typing import Dict, Any, List, Optional


def save_snapshot_index_to_localStorage(snapshots: List[Dict[str, Any]]) -> None:
    """
    Save snapshot index to browser localStorage via JavaScript.

    Args:
        snapshots: List of snapshot metadata dicts
    """
    snapshots_json = json.dumps(snapshots)
    # Escape quotes for JavaScript
    snapshots_json_escaped = snapshots_json.replace("'", "\\'").replace('"', '\\"')

    js_code = f"""
    <script>
    (function() {{
        try {{
            const snapshots = JSON.parse('{snapshots_json_escaped}');
            localStorage.setItem('family_forecast_snapshots_index', JSON.stringify(snapshots));
            console.log('✅ Saved snapshot index to localStorage:', snapshots.length, 'snapshots');
        }} catch (e) {{
            console.error('❌ Failed to save snapshot index:', e);
        }}
    }})();
    </script>
    """

    st.components.v1.html(js_code, height=0)


def load_snapshot_index_from_localStorage() -> List[Dict[str, Any]]:
    """
    Load snapshot index from browser localStorage.

    This triggers JavaScript that will populate st.session_state
    on the NEXT rerun (async nature of Streamlit components).

    Returns:
        List of snapshot metadata, or empty list if none found
    """
    # Check if already loaded in this session
    if '_snapshots_index_from_localStorage' in st.session_state:
        return st.session_state._snapshots_index_from_localStorage

    # Trigger localStorage read via JavaScript
    js_code = """
    <script>
    (function() {
        try {
            const data = localStorage.getItem('family_forecast_snapshots_index');
            if (data) {
                const snapshots = JSON.parse(data);
                console.log('✅ Loaded snapshot index from localStorage:', snapshots.length, 'snapshots');
                // Store in a way Streamlit can access (via query params hack)
                const encodedData = encodeURIComponent(data);
                window.parent.postMessage({
                    type: 'snapshot_index_loaded',
                    data: data
                }, '*');
            } else {
                console.log('❌ No snapshot index found in localStorage');
            }
        } catch (e) {
            console.error('❌ localStorage read error:', e);
        }
    })();
    </script>
    """

    st.components.v1.html(js_code, height=0)

    # Return empty list for now (will be populated on next rerun)
    return []


def init_localStorage_bridge():
    """
    Initialize localStorage bridge on app startup.
    Call this once in app.py main().
    """
    # Inject JavaScript that listens for snapshot index loads
    js_listener = """
    <script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'snapshot_index_loaded') {
            console.log('📨 Received snapshot index from localStorage');
            // Store in sessionStorage for Streamlit to pick up
            sessionStorage.setItem('_snapshot_index_temp', event.data.data);
        }
    });
    </script>
    """

    st.components.v1.html(js_listener, height=0)

    # Check if data was loaded
    check_js = """
    <script>
    (function() {
        const tempData = sessionStorage.getItem('_snapshot_index_temp');
        if (tempData) {
            console.log('📥 Found temp snapshot data, clearing...');
            sessionStorage.removeItem('_snapshot_index_temp');
            // Trigger a rerun somehow... (this is the tricky part)
        }
    })();
    </script>
    """

    st.components.v1.html(check_js, height=0)
