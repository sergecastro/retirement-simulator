# sidebar_snapshot_manager.py - Encrypted snapshot management for sidebar
"""
MIGRATION: Replaces data_manager_cloud.py with encrypted snapshot system
KEEPS: Exact same UI/UX
CHANGES: Backend uses utils/snapshot_manager.py (AES-256 encrypted localStorage)
"""

import streamlit as st
import json
from datetime import datetime
from embedded_scenarios import EMBEDDED_SCENARIOS
from utils.snapshot_manager import (
    get_snapshots_index,
    save_snapshots_index,
    save_snapshot,
    load_snapshot,
    delete_snapshot,
    get_current_snapshot
)
from utils.comparison_scenarios import (
    get_comparisons_for_plan,
    load_comparison_scenario,
    delete_comparison_scenario
)


def queue_scenario_load(scenario_data):
    """
    Queue scenario data for loading BEFORE widgets are created.
    Sets a pending flag instead of directly modifying session state.

    UNCHANGED: Same function as data_manager_cloud.py
    """
    # Store the scenario data to be loaded
    st.session_state['_pending_scenario_data'] = scenario_data
    st.session_state['_pending_scenario_load'] = True

    # Rerun to trigger the load in the next render cycle
    st.rerun()


def apply_scenario_data_safe(scenario_data):
    """
    SAFE: Apply loaded scenario data WITH input_ prefix to match your forms.
    This function should ONLY be called BEFORE any widgets are created.

    UNCHANGED: Same function as data_manager_cloud.py
    """
    # Clear ALL existing widget keys to prevent conflicts
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith('input_')]
    for key in keys_to_clear:
        del st.session_state[key]

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

    print("[OK] Applied scenario data to session state")


def collect_current_scenario_data():
    """
    Collect all current input values from session state.

    UNCHANGED: Same function as data_manager_cloud.py
    """
    data = {}

    # Collect all input_ keys
    for key, value in st.session_state.items():
        if key.startswith('input_'):
            data[key] = value

    # Add family tables
    data['children_list'] = st.session_state.get('children_list', [])
    data['inheritance_list'] = st.session_state.get('inheritance_list', [])
    data['goals_list'] = st.session_state.get('goals_list', [])

    return data


def manage_snapshots_sidebar(is_trusted_user, age_group=None):
    """
    NEW: Encrypted snapshot management for sidebar (replaces manage_scenarios_cloud)

    KEEPS: Exact same UI/UX as data_manager_cloud.py
    CHANGES: Uses utils/snapshot_manager.py backend with encryption
    """

    # Create sidebar UI
    st.sidebar.markdown("---")
    st.sidebar.header("📂 Saved Plans")

    # Get snapshots from encrypted localStorage
    try:
        index = get_snapshots_index()
        snapshots = index.get("snapshots", [])
        current_snapshot_id = index.get("current_snapshot_id")

        # DEBUG: Show what we found
        print(f"[DEBUG SIDEBAR] Loaded {len(snapshots)} snapshots from localStorage")
        for s in snapshots:
            print(f"  - {s.get('name')} (ID: {s.get('id')})")

    except Exception as e:
        print(f"[ERROR] Failed to get snapshots: {e}")
        import traceback
        traceback.print_exc()
        st.sidebar.error(f"⚠️ Error loading saved plans: {e}")
        snapshots = []
        current_snapshot_id = None

    # AUTO-LOAD DEFAULT SCENARIO ON FIRST VISIT
    # CRITICAL FIX: Only auto-load demo if user has NO saved snapshots
    if 'scenario_auto_loaded' not in st.session_state:
        if 'scenario_loaded' not in st.session_state:
            # Check if user has saved snapshots
            if len(snapshots) > 0:
                # User has saved data - use most recent snapshot
                most_recent = snapshots[-1]
                st.session_state['current_scenario'] = most_recent['name']
                st.session_state['scenario_auto_loaded'] = True
                print(f"[AUTO-LOAD] Using saved snapshot: {most_recent['name']}")
                # Don't load here - let intake_data_loaded flag handle it
            else:
                # No saved data - load demo
                if is_trusted_user:
                    default_scenario = EMBEDDED_SCENARIOS['70+_RETIREMENT_SCENARIO_PRIVATE']
                    default_name = '70+ Retirement (Private - Trusted)'
                else:
                    default_scenario = EMBEDDED_SCENARIOS['ORIGINAL_70+_RETIREMENT_SCENARIO']
                    default_name = 'Original 70+ Retirement (Demo)'

                # ✅ Queue the default scenario for loading
                st.session_state['current_scenario'] = default_name
                st.session_state['scenario_auto_loaded'] = True
                queue_scenario_load(default_scenario)  # This will rerun

    # Get current scenario name - prioritize current_snapshot_id
    if current_snapshot_id:
        # Find snapshot name from ID
        current_name = None
        for s in snapshots:
            if s['id'] == current_snapshot_id:
                current_name = s['name']
                break
        if not current_name:
            current_name = st.session_state.get('current_scenario', 'No plan loaded')
    else:
        current_name = st.session_state.get('current_scenario', 'No plan loaded')

    # ============================================
    # ANALYSIS MODE - READ ONLY INDICATOR
    # ============================================
    st.sidebar.info("ℹ️ **Analysis Mode - Read Only**\n\n📝 To edit your retirement data, go to **INTAKE** mode.")
    st.sidebar.markdown("---")

    # ============================================
    # SECTION 1: SAVED PLANS (CURRENT STATUS)
    # ============================================
    st.sidebar.subheader("📂 Saved Plans")

    # Simple info display - NOT an expander
    st.sidebar.info(f"📋 **Currently:** {current_name}")

    # Show snapshot count
    if snapshots:
        st.sidebar.caption(f"✅ Found {len(snapshots)} saved plan(s) in localStorage")
    else:
        st.sidebar.caption(f"ℹ️ No saved plans found yet")

    st.sidebar.markdown("---")

    # ============================================
    # SECTION 2: LOAD A PLAN
    # ============================================
    st.sidebar.subheader("📥 LOAD A PLAN")

    with st.sidebar.expander("📥 Select & Load Plan", expanded=False):
        # Build list: User's saved snapshots + embedded defaults
        snapshot_options = {}

        # Add user's saved snapshots FIRST
        for snapshot in snapshots:
            # Include date/time to make names unique and identifiable
            snapshot_date = snapshot['id']  # Format: 20251114_1032
            date_part = f"{snapshot_date[4:6]}/{snapshot_date[6:8]} {snapshot_date[9:11]}:{snapshot_date[11:13]}"
            display_name = f"{snapshot['name']} [{date_part}]"
            snapshot_options[display_name] = ('snapshot', snapshot['id'])

        # Add embedded options ONLY if no user snapshots exist
        if len(snapshots) == 0:
            if is_trusted_user:
                snapshot_options['70+ Retirement (Private - Trusted)'] = ('embedded', 'private')
            snapshot_options['Original 70+ Retirement (Demo)'] = ('embedded', 'demo')

        # Dropdown selector
        if snapshot_options:
            selected_display = st.selectbox(
                "Choose plan:",
                options=list(snapshot_options.keys()),
                key="select_plan_to_load"
            )

            if st.button("📥 LOAD", key="load_selected_plan", use_container_width=True, type="primary"):
                source_type, source_id = snapshot_options[selected_display]

                if source_type == 'snapshot':
                    # Load from encrypted localStorage
                    try:
                        scenario_data = load_snapshot(source_id)
                        if scenario_data:
                            # CRITICAL FIX: Update current_snapshot_id in index
                            index['current_snapshot_id'] = source_id
                            save_snapshots_index(index)
                            print(f"[LOAD] Updated current_snapshot_id to: {source_id}")

                            st.session_state['current_scenario'] = selected_display
                            st.success(f"✅ Loaded: {selected_display}")
                            queue_scenario_load(scenario_data)
                        else:
                            st.error("❌ Failed to load snapshot")
                    except Exception as e:
                        st.error(f"❌ Load error: {e}")

                elif source_type == 'embedded':
                    # Load embedded scenario
                    if source_id == 'private':
                        scenario_data = EMBEDDED_SCENARIOS['70+_RETIREMENT_SCENARIO_PRIVATE']
                    else:
                        scenario_data = EMBEDDED_SCENARIOS['ORIGINAL_70+_RETIREMENT_SCENARIO']

                    # Clear current_snapshot_id for embedded scenarios
                    index['current_snapshot_id'] = None
                    save_snapshots_index(index)
                    print(f"[LOAD] Cleared current_snapshot_id for embedded scenario")

                    st.session_state['current_scenario'] = selected_display
                    st.success(f"✅ Loaded: {selected_display}")
                    queue_scenario_load(scenario_data)
        else:
            st.caption("No saved plans yet")

    st.sidebar.markdown("---")

    # ============================================
    # SECTION 2B: COMPARISON SCENARIOS (Sub-Phase 2A)
    # ============================================
    print("[DEBUG SIDEBAR] Reached SECTION 2B: Comparison Scenarios")
    st.sidebar.write("🔍 [DEBUG] Section 2B Loading...")
    st.sidebar.subheader("🔀 Comparison Scenarios")

    # Only show if we have a current base plan loaded
    print(f"[DEBUG SIDEBAR] Current base plan ID: '{current_snapshot_id if current_snapshot_id else 'None'}'")
    if current_snapshot_id:
        print("[DEBUG SIDEBAR] Base plan exists, loading comparisons...")
        with st.sidebar.expander("🔀 View & Manage Comparisons", expanded=False):
            st.write("🔍 [DEBUG] Expander opened")
            try:
                # CACHE comparisons in session state to prevent rerun loop
                cache_key = f'comparisons_cache_{current_snapshot_id}'

                # Check if we need to refresh the cache
                refresh_needed = (
                    cache_key not in st.session_state or
                    'comparison_save_success' in st.session_state or  # Just saved a new comparison
                    'comparison_deleted' in st.session_state  # Just deleted a comparison
                )

                if refresh_needed:
                    print(f"[DEBUG SIDEBAR] Refreshing comparisons cache for plan {current_snapshot_id}")
                    st.session_state[cache_key] = get_comparisons_for_plan(current_snapshot_id)
                    # Clear the refresh flags
                    if 'comparison_deleted' in st.session_state:
                        del st.session_state['comparison_deleted']
                else:
                    print(f"[DEBUG SIDEBAR] Using cached comparisons for plan {current_snapshot_id}")

                comparisons = st.session_state[cache_key]
                print(f"[DEBUG SIDEBAR] Found {len(comparisons)} comparisons")
                st.write(f"🔍 [DEBUG] Found {len(comparisons)} comparisons")

                if not comparisons:
                    st.caption("💡 No saved comparisons yet")
                    st.caption("Go to **ANALYSIS** mode and save a comparison scenario!")
                else:
                    st.caption(f"📊 Found {len(comparisons)} comparison(s) for this plan")
                    st.markdown("---")

                    # Display each comparison with Load/Delete buttons
                    comparisons_to_delete = []
                    for idx, comp_meta in enumerate(comparisons):
                        comp_id = comp_meta['id']
                        comp_name = comp_meta['name']
                        comp_created = comp_meta.get('created_at', 'Unknown')

                        # Show comparison name and date
                        st.markdown(f"**{comp_name}**")
                        st.caption(f"Created: {comp_created[:10]}")

                        # Action buttons
                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("📥 Load", key=f"load_comp_{comp_id}_{idx}", use_container_width=True):
                                # Load comparison data
                                try:
                                    comp_data = load_comparison_scenario(comp_id)
                                    if comp_data:
                                        # Apply adjustments to session state
                                        adjustments = comp_data.get('adjustments', {})

                                        # Set comparison adjustments in session state
                                        st.session_state['comparison_income'] = adjustments.get('adjusted_income', 0)
                                        st.session_state['comparison_expenses'] = adjustments.get('adjusted_expenses', 0)
                                        st.session_state['comparison_return'] = adjustments.get('adjusted_return_rate', 0)
                                        st.session_state['comparison_inflation'] = adjustments.get('adjusted_inflation_rate', 0)

                                        # Set flag to indicate comparison is loaded
                                        st.session_state['comparison_loaded'] = True
                                        st.session_state['loaded_comparison_name'] = comp_name

                                        st.success(f"✅ Loaded: {comp_name}")
                                        st.info("📊 Go to **ANALYSIS** mode to see this comparison")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to load comparison")
                                except Exception as e:
                                    st.error(f"❌ Load error: {e}")
                                    print(f"[ERROR] Failed to load comparison {comp_id}: {e}")

                        with col2:
                            if st.button("🗑️", key=f"delete_comp_{comp_id}_{idx}", help=f"Delete {comp_name}", use_container_width=True):
                                comparisons_to_delete.append((comp_id, comp_name))

                        st.markdown("---")

                    # Process deletions
                    if comparisons_to_delete:
                        for comp_id, comp_name in comparisons_to_delete:
                            try:
                                success = delete_comparison_scenario(comp_id)
                                if success:
                                    st.success(f"✅ Deleted: {comp_name}")
                                    # Set flag to refresh cache on next load
                                    st.session_state['comparison_deleted'] = True
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to delete: {comp_name}")
                            except Exception as e:
                                st.error(f"❌ Delete error: {e}")
                                print(f"[ERROR] Failed to delete comparison {comp_id}: {e}")

            except Exception as e:
                st.error(f"⚠️ Error loading comparisons: {e}")
                print(f"[ERROR] Failed to get comparisons: {e}")
                import traceback
                traceback.print_exc()
    else:
        st.sidebar.caption("💡 Save a base plan first to create comparisons")

    st.sidebar.markdown("---")

    # ============================================
    # SECTION 3: OTHER ACTIONS (BOTTOM)
    # ============================================
    st.sidebar.subheader("🔧 OTHER ACTIONS")

    # Upload
    with st.sidebar.expander("📤 Upload Backup File", expanded=False):
        if 'last_uploaded_file' not in st.session_state:
            st.session_state['last_uploaded_file'] = None

        uploaded_file = st.file_uploader(
            "Choose .ffb or .json file:",
            type=['json', 'ffb'],
            key="upload_backup_file"
        )

        if uploaded_file is not None:
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state['last_uploaded_file'] != file_id:
                try:
                    file_content = uploaded_file.read()
                    scenario_data = json.loads(file_content)

                    if isinstance(scenario_data, dict):
                        # ✅ Queue the uploaded scenario for loading
                        scenario_name = uploaded_file.name.replace('.json', '').replace('.ffb', '')
                        st.session_state['current_scenario'] = scenario_name
                        st.session_state['last_uploaded_file'] = file_id
                        st.success(f"✅ Uploaded: {scenario_name}")
                        queue_scenario_load(scenario_data)
                except Exception as e:
                    st.error(f"❌ Upload error: {e}")

    # Delete
    with st.sidebar.expander("🗑️ Delete Plans", expanded=False):
        if not snapshots:
            st.caption("No saved plans to delete")
        else:
            st.warning("⚠️ Deletion is permanent!")

            # Show list of plans with delete buttons
            snapshots_to_delete = []
            for idx, snapshot in enumerate(snapshots):
                snapshot_name = snapshot['name']
                snapshot_id = snapshot['id']

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(snapshot_name)
                with col2:
                    # ✅ FIX: Add idx to make unique key
                    if st.button("🗑️", key=f"delete_{snapshot_id}_{idx}", help=f"Delete {snapshot_name}"):
                        snapshots_to_delete.append((snapshot_id, snapshot_name))

            # Process deletions
            if snapshots_to_delete:
                need_reload_default = False

                for snapshot_id, snapshot_name in snapshots_to_delete:
                    try:
                        # Delete from encrypted localStorage
                        success = delete_snapshot(snapshot_id)

                        if success:
                            st.success(f"✅ Deleted: {snapshot_name}")

                            # If we deleted the currently loaded scenario, switch to default
                            if st.session_state.get('current_scenario') == snapshot_name:
                                default = 'Original 70+ Retirement (Demo)'
                                st.session_state['current_scenario'] = default
                                need_reload_default = True
                    except Exception as e:
                        st.error(f"❌ Delete error: {e}")

                # ✅ Queue default scenario load if needed
                if need_reload_default:
                    queue_scenario_load(EMBEDDED_SCENARIOS['ORIGINAL_70+_RETIREMENT_SCENARIO'])
                else:
                    st.rerun()

    return {}
