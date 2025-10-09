# integration/intake_loader.py - Fixed to use data_manager functions
import os
import json
from pathlib import Path
import streamlit as st
from data_manager import apply_scenario_data_safe
from data_manager import load_scenarios, save_scenarios  # NEW: For auto-save
from datetime import datetime  # NEW: For timestamp on duplicates

def intake_import_ui(shared_dir: str = ""):
    """Sidebar UI to import Intake JSON by path or upload."""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Import from Intake App")
    
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
    if st.sidebar.button("📁 Load from Path", use_container_width=True, key="load_path_btn"):
        st.session_state.intake_path_to_load = path
        st.rerun()
    
    # Actually load after rerun
    if st.session_state.intake_path_to_load:
        load_path = st.session_state.intake_path_to_load
        st.session_state.intake_path_to_load = None  # Clear flag
        
        if os.path.exists(load_path):
            try:
                st.sidebar.info(f"🔄 Loading from: {Path(load_path).name}")
                
                with open(load_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if isinstance(data, dict):
                    from data_manager import apply_scenario_data_safe
                    
                    # Apply the data
                    apply_scenario_data_safe(data)
                    
                    # Set scenario name
                    scenario_name = Path(load_path).stem.replace("_", " ").replace("-", " ").title()
                    final_name = f"Imported: {scenario_name}"  # Prefix for distinction
                    
                    st.session_state["current_scenario"] = final_name  # Use final_name
                    st.session_state['scenario_loaded'] = True
                    st.session_state['scenario_auto_loaded'] = True
                    
                    # Auto-save to family_scenarios.json for persistence across reloads
                    scenarios = load_scenarios()
                    save_key = final_name
                    if save_key in scenarios:  # Handle duplicates with timestamp
                        save_key = f"{save_key} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
                    
                    # Collect current data (mirror save logic from data_manager.py)
                    current_data = {}
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
                    
                    # Mortgage name variations (for compatibility)
                    if "mortgage_balance" in current_data:
                        current_data["primary_residence_mortgage"] = current_data["mortgage_balance"]
                    
                    scenarios[save_key] = current_data
                    if save_scenarios(scenarios):
                        st.sidebar.success(f"✅ Auto-saved as: {save_key}")
                    else:
                        st.sidebar.warning("⚠️ Data loaded but auto-save failed - use 'Save Current' manually")
                    
                    st.sidebar.success(f"✅ Loaded: {final_name}")
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
            st.sidebar.info(f"🔄 Processing: {uploaded.name}")
            
            data = json.loads(uploaded.getvalue().decode("utf-8"))
            
            if isinstance(data, dict):
                from data_manager import apply_scenario_data_safe
                
                # Apply the data
                apply_scenario_data_safe(data)
                
                # Set scenario name
                scenario_name = Path(uploaded.name).stem.replace("_", " ").replace("-", " ").title()
                final_name = f"Imported: {scenario_name}"  # Prefix for distinction
                st.session_state["current_scenario"] = final_name  # Use final_name
                st.session_state['scenario_loaded'] = True
                st.session_state['scenario_auto_loaded'] = True
                
                # Auto-save to family_scenarios.json for persistence across reloads (same as above)
                scenarios = load_scenarios()
                save_key = final_name
                if save_key in scenarios:
                    save_key = f"{save_key} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
                
                current_data = {}
                for key in st.session_state:
                    if key.startswith('input_'):
                        clean_key = key.replace('input_', '')
                        value = st.session_state[key]
                        if isinstance(value, (int, float, str, bool, list, dict, type(None))):
                            current_data[clean_key] = value
                
                current_data["goals_list"] = st.session_state.get("goals_list", st.session_state.get("goals_data", []))
                current_data["goals_data"] = current_data["goals_list"]
                
                current_data["children_list"] = st.session_state.get("children_list", st.session_state.get("children_rows", []))
                current_data["children_rows"] = current_data["children_list"]
                current_data["children_data"] = current_data["children_list"]
                
                current_data["inheritance_list"] = st.session_state.get("inheritance_list", st.session_state.get("inherit_rows", []))
                current_data["inherit_rows"] = current_data["inheritance_list"]
                current_data["inheritance_data"] = current_data["inheritance_list"]
                
                if "mortgage_balance" in current_data:
                    current_data["primary_residence_mortgage"] = current_data["mortgage_balance"]
                
                scenarios[save_key] = current_data
                if save_scenarios(scenarios):
                    st.sidebar.success(f"✅ Auto-saved as: {save_key}")
                else:
                    st.sidebar.warning("⚠️ Data loaded but auto-save failed - use 'Save Current' manually")
                
                st.sidebar.success(f"✅ Loaded: {final_name}")
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