# integration/intake_loader.py
import os, json, streamlit as st

def _apply_intake_dict(d: dict):
    """Write values into st.session_state, matching your existing input_... keys.
       Also sets children/inheritance tables if present, and recomputes totals if missing."""
    # 1) Apply all scalar fields
    for k, v in d.items():
        if k in ("children_rows", "inherit_rows", "goals_data"):
            continue
        if k.startswith("input_"):
            st.session_state[k] = v
        else:
            # also accept plain keys from older/simpler exporters
            st.session_state[f"input_{k}"] = v

    # 2) Family tables (optional)
    if "children_rows" in d:
        st.session_state["children_rows"] = d["children_rows"]
    if "inherit_rows" in d:
        st.session_state["inherit_rows"] = d["inherit_rows"]
    if "goals_data" in d:
        st.session_state["goals_data"] = d["goals_data"]

    # 3) Totals if missing
    if "input_total_income" not in st.session_state:
        income_keys = [
            "input_salary_wages","input_self_employment_income","input_rental_income",
            "input_investment_income","input_social_security_income","input_pension_income",
            "input_other_income"
        ]
        st.session_state["input_total_income"] = float(sum(st.session_state.get(k, 0.0) or 0.0 for k in income_keys))

    if "input_total_expenses" not in st.session_state:
        expense_keys = [
            "input_housing_expenses","input_utilities_expenses","input_groceries_expenses",
            "input_transportation_expenses","input_healthcare_expenses","input_insurance_expenses",
            "input_property_tax_expenses","input_entertainment_expenses","input_restaurant_expenses",
            "input_travel_expenses","input_education_expenses","input_childcare_expenses",
            "input_clothing_expenses","input_charitable_donations","input_miscellaneous_expenses",
            "input_other_expenses"
        ]
        st.session_state["input_total_expenses"] = float(sum(st.session_state.get(k, 0.0) or 0.0 for k in expense_keys))

def intake_import_ui(shared_dir: str):
    """Small sidebar UI block to import intake_payload.json from a known path or via drag&drop."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Import from Intake App")

    # Option A: type a path and click Load
    default_path = os.path.join(shared_dir, "intake_payload.json")
    path = st.sidebar.text_input("File path (.json):", value=default_path)
    if st.sidebar.button("Load from path"):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                _apply_intake_dict(data)
                st.sidebar.success("✅ Intake data loaded. Review values, then run simulation.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Failed to load: {e}")
        else:
            st.sidebar.warning("Path not found. Check the file exists.")

    # Option B: drag&drop the JSON
    uploaded = st.sidebar.file_uploader("…or drop intake_payload.json here", type=["json"])
    if uploaded is not None:
        try:
            data = json.loads(uploaded.getvalue().decode("utf-8"))
            _apply_intake_dict(data)
            st.sidebar.success("✅ Intake data loaded from upload.")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Upload failed: {e}")
