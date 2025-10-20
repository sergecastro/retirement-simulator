# integration/intake_loader.py - Cloud-compatible version with file upload
import os
import json
from pathlib import Path
import streamlit as st
from data_manager_cloud import apply_scenario_data_safe
from datetime import datetime

def sanitize_intake_data(data: dict) -> dict:
    """
    Sanitize imported data to prevent validation errors.
    - Caps birth years at reasonable max (current year + 20)
    - Validates other fields
    """
    max_birth_year = datetime.now().year + 20  # Match family_inputs.py validation
    warnings = []

    # Sanitize children data
    if "children_list" in data:
        for child in data["children_list"]:
            if "Birth Year" in child:
                original_year = child["Birth Year"]
                if original_year > max_birth_year:
                    child["Birth Year"] = max_birth_year
                    warnings.append(f"⚠️ Child '{child.get('Name', 'Unknown')}' birth year adjusted from {original_year} to {max_birth_year}")

    # Also sanitize children_rows (backward compatibility)
    if "children_rows" in data:
        for child in data["children_rows"]:
            if "Birth Year" in child:
                original_year = child["Birth Year"]
                if original_year > max_birth_year:
                    child["Birth Year"] = max_birth_year
                    warnings.append(f"⚠️ Child '{child.get('Name', 'Unknown')}' birth year adjusted from {original_year} to {max_birth_year}")

    # Show warnings to user
    if warnings:
        for warning in warnings:
            st.sidebar.warning(warning)

    return data

def intake_import_ui(shared_dir: str = ""):
    """Sidebar UI to import Intake JSON by path or upload."""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔥 Import from Intake App")
    
    # PATH LOADER - Fixed to point to SHARED folder at root level
    current_dir = os.getcwd()
    root_dir = Path(current_dir).parent
    default_path = str(root_dir / "SHARED" / "intake_payload.json")
    
    # Use a session state key to track if we should load
    if 'intake_path_to_load' not in st.session_state:
        st.session_state.intake_path_to_load = None
    
    path = st.sidebar.text_input(
        "Load from path:", 
        value=default_path,
        placeholder="C:/path/to/intake_payload.json",
        key="intake_path_input"
    )
    
    # Button sets a flag instead of loading directly
    if st.sidebar.button("📂 Load from Path", use_container_width=True, key="load_path_btn"):
        st.session_state.intake_path_to_load = path
        st.rerun()
    
    # Actually load after rerun
    if st.session_state.intake_path_to_load:
        load_path = st.session_state.intake_path_to_load
        st.session_state.intake_path_to_load = None  # Clear flag
        
        if os.path.exists(load_path):
            try:
                st.sidebar.info(f"📄 Loading from: {Path(load_path).name}")
                
                with open(load_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, dict):
                    # Sanitize data to prevent validation errors
                    data = sanitize_intake_data(data)

                    # Apply the data
                    apply_scenario_data_safe(data)

                    # CRITICAL FIX: Load custom_expenses into session state
                    if "custom_expenses" in data:
                        st.session_state['custom_expenses'] = data['custom_expenses']
                    else:
                        st.session_state['custom_expenses'] = []

                    # Set scenario name
                    scenario_name = Path(load_path).stem.replace("_", " ").replace("-", " ").title()
                    final_name = f"Imported: {scenario_name}"

                    st.session_state["current_scenario"] = final_name
                    st.session_state['scenario_loaded'] = True
                    st.session_state['scenario_auto_loaded'] = True

                    st.sidebar.success(f"✅ Loaded: {final_name}")
                    st.sidebar.info("💡 Use 'Download Scenario' to save this data!")
                else:
                    st.sidebar.error("❌ Invalid JSON format")
                    
            except json.JSONDecodeError as e:
                st.sidebar.error(f"❌ Invalid JSON: {e}")
            except Exception as e:
                st.sidebar.error(f"❌ Load failed: {e}")
        else:
            st.sidebar.warning(f"⚠️ File not found: {load_path}")
    
    # FILE UPLOADER
    st.sidebar.markdown("**...or upload file:**")
    uploaded = st.sidebar.file_uploader(
        "Drop intake_payload.json here", 
        type=["json"],
        label_visibility="collapsed",
        key="intake_file_upload"
    )
    
    if uploaded is not None:
        try:
            st.sidebar.info(f"📄 Processing: {uploaded.name}")
            
            data = json.loads(uploaded.getvalue().decode("utf-8"))

            if isinstance(data, dict):
                # Sanitize data to prevent validation errors
                data = sanitize_intake_data(data)

                # Apply the data
                apply_scenario_data_safe(data)

                # CRITICAL FIX: Load custom_expenses into session state
                if "custom_expenses" in data:
                    st.session_state['custom_expenses'] = data['custom_expenses']
                else:
                    st.session_state['custom_expenses'] = []

                # Set scenario name
                scenario_name = Path(uploaded.name).stem.replace("_", " ").replace("-", " ").title()
                final_name = f"Imported: {scenario_name}"
                st.session_state["current_scenario"] = final_name
                st.session_state['scenario_loaded'] = True
                st.session_state['scenario_auto_loaded'] = True

                st.sidebar.success(f"✅ Loaded: {final_name}")
                st.sidebar.info("💡 Use 'Download Scenario' to save this data!")
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid JSON format")
                
        except json.JSONDecodeError as e:
            st.sidebar.error(f"❌ Invalid JSON: {e}")
        except Exception as e:
            st.sidebar.error(f"❌ Upload failed: {e}")

# Back-compat alias for older imports
def sidebar_intake_importer():
    return intake_import_ui()