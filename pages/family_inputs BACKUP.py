# pages/family_inputs.py - FIXED delete button execution order
import streamlit as st
import pandas as pd
from datetime import date

def collect_family_events():
    """Collect family events data with FIXED delete button logic"""
    st.header("👨‍👩‍👧‍👦 Family Events")
    
    # ============================================
    # CHILDREN SECTION - Individual Fields
    # ============================================
    st.subheader("👶 Children & Education Planning")
    
    # Initialize children list
    if 'children_list' not in st.session_state:
        st.session_state['children_list'] = []
    
    # Add child button
    if st.button("➕ Add Child", key="add_child_btn"):
        st.session_state['children_list'].append({
            'Name': '',
            'Birth Year': date.today().year - 5,
            'College Plan': 'None',
            'Scholarship %': 0.0,
            'Start Age': 18,
            'Years': 4,
            'Use 529 First?': True
        })
        st.rerun()
    
    if len(st.session_state['children_list']) == 0:
        st.info("Click 'Add Child' to add children for education planning")
    else:
        st.write(f"**{len(st.session_state['children_list'])} child(ren) configured**")
        
        children_to_remove = []
        
        for idx, child_data in enumerate(st.session_state['children_list']):
            st.markdown(f"#### Child {idx + 1}")
            
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                name = st.text_input(
                    "Name:",
                    value=child_data.get('Name', ''),
                    key=f"child_name_{idx}",
                    placeholder="Child's name"
                )
                st.session_state['children_list'][idx]['Name'] = name
                
                birth_year = st.number_input(
                    "Birth Year:",
                    value=int(child_data.get('Birth Year', date.today().year - 5)),
                    min_value=1900,
                    max_value=date.today().year + 20,
                    step=1,
                    key=f"child_birth_{idx}"
                )
                st.session_state['children_list'][idx]['Birth Year'] = birth_year
            
            with col2:
                college_plan = st.selectbox(
                    "College Plan:",
                    ["None", "Public In-State", "Public Out-of-State", "Private", "Private Nonprofit"],
                    index=["None", "Public In-State", "Public Out-of-State", "Private", "Private Nonprofit"].index(child_data.get('College Plan', 'None')),
                    key=f"child_college_{idx}"
                )
                st.session_state['children_list'][idx]['College Plan'] = college_plan
                
                scholarship = st.number_input(
                    "Scholarship %:",
                    value=float(child_data.get('Scholarship %', 0.0)),
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    key=f"child_scholarship_{idx}"
                )
                st.session_state['children_list'][idx]['Scholarship %'] = scholarship
            
            with col3:
                start_age = st.number_input(
                    "Start Age:",
                    value=int(child_data.get('Start Age', 18)),
                    min_value=15,
                    max_value=25,
                    step=1,
                    key=f"child_start_{idx}"
                )
                st.session_state['children_list'][idx]['Start Age'] = start_age
                
                years = st.number_input(
                    "Years:",
                    value=int(child_data.get('Years', 4)),
                    min_value=1,
                    max_value=8,
                    step=1,
                    key=f"child_years_{idx}"
                )
                st.session_state['children_list'][idx]['Years'] = years
            
            with col4:
                use_529 = st.checkbox(
                    "Use 529 First?",
                    value=bool(child_data.get('Use 529 First?', True)),
                    key=f"child_529_{idx}"
                )
                st.session_state['children_list'][idx]['Use 529 First?'] = use_529
                
                st.write("")  # Spacer
                if st.button("🗑️", key=f"delete_child_{idx}", help="Delete this child"):
                    children_to_remove.append(idx)
            
            st.markdown("---")
        
        # Remove deleted children
        for idx in reversed(children_to_remove):
            st.session_state['children_list'].pop(idx)
        
        # Convert to rows format for backward compatibility
        st.session_state['children_rows'] = st.session_state['children_list']
        
        # Show summary
        active_children = [c for c in st.session_state['children_list'] if c.get('Name', '').strip() and c.get('College Plan', 'None') != 'None']
        st.metric("Children with Education Plans", len(active_children))
    
    # ============================================
    # INHERITANCE SECTION - Individual Fields
    # ============================================
    st.subheader("💰 Expected Inheritances")
    
    # Initialize inheritance list
    if 'inheritance_list' not in st.session_state:
        st.session_state['inheritance_list'] = []
    
    # Add inheritance button
    if st.button("➕ Add Inheritance", key="add_inheritance_btn"):
        st.session_state['inheritance_list'].append({
            'Year': date.today().year + 10,
            'Amount': 0.0,
            'Taxable?': False
        })
        st.rerun()
    
    if len(st.session_state['inheritance_list']) == 0:
        st.info("Click 'Add Inheritance' to add expected inheritances")
    else:
        st.write(f"**{len(st.session_state['inheritance_list'])} inheritance event(s)**")
        
        inheritances_to_remove = []
        
        for idx, inh_data in enumerate(st.session_state['inheritance_list']):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                year = st.number_input(
                    "Year:",
                    value=int(inh_data.get('Year', date.today().year + 10)),
                    min_value=date.today().year,
                    max_value=date.today().year + 50,
                    step=1,
                    key=f"inh_year_{idx}"
                )
                st.session_state['inheritance_list'][idx]['Year'] = year
            
            with col2:
                amount = st.number_input(
                    "Amount:",
                    value=float(inh_data.get('Amount', 0.0)),
                    min_value=0.0,
                    step=1000.0,
                    key=f"inh_amount_{idx}"
                )
                st.session_state['inheritance_list'][idx]['Amount'] = amount
            
            with col3:
                taxable = st.checkbox(
                    "Taxable?",
                    value=bool(inh_data.get('Taxable?', False)),
                    key=f"inh_taxable_{idx}"
                )
                st.session_state['inheritance_list'][idx]['Taxable?'] = taxable
                
                st.write("")  # Spacer
                if st.button("🗑️", key=f"delete_inh_{idx}", help="Delete this inheritance"):
                    inheritances_to_remove.append(idx)
            
            st.markdown("---")
        
        # Remove deleted inheritances
        for idx in reversed(inheritances_to_remove):
            st.session_state['inheritance_list'].pop(idx)
        
        # Convert to rows format for backward compatibility
        st.session_state['inherit_rows'] = st.session_state['inheritance_list']
        
        # Show summary
        active_inheritances = [i for i in st.session_state['inheritance_list'] if i.get('Amount', 0) > 0]
        total_inheritance = sum(i.get('Amount', 0) for i in active_inheritances)
        st.metric("Total Expected Inheritances", f"${total_inheritance:,.0f}")
    
    # ============================================
    # COLLEGE COST PARAMETERS
    # ============================================
    with st.expander("🎓 College Cost Parameters"):
        col1, col2 = st.columns(2)
        with col1:
            college_inflation_pct = st.number_input(
                "College Inflation Rate (%):", 
                value=float(st.session_state.get('input_college_inflation_pct', 4.0)),
                key="college_inflation_input",
                help="Annual increase in college costs"
            )
            base_public_in = st.number_input(
                "Base Public In-State Cost:", 
                value=float(st.session_state.get('input_base_public_in', 20000.0)),
                key="public_in_cost_input",
                help="Annual cost for in-state public university"
            )
        with col2:
            base_public_out = st.number_input(
                "Base Public Out-of-State Cost:", 
                value=float(st.session_state.get('input_base_public_out', 40000.0)),
                key="public_out_cost_input",
                help="Annual cost for out-of-state public university"
            )
            base_private = st.number_input(
                "Base Private College Cost:", 
                value=float(st.session_state.get('input_base_private', 60000.0)),
                key="private_cost_input",
                help="Annual cost for private university"
            )
    
    # Update session state for college parameters
    st.session_state['input_college_inflation_pct'] = college_inflation_pct
    st.session_state['input_base_public_in'] = base_public_in
    st.session_state['input_base_public_out'] = base_public_out
    st.session_state['input_base_private'] = base_private
    
    # Summary metrics
    col1, col2 = st.columns(2)
    with col1:
        active_children = [c for c in st.session_state.get('children_list', []) 
                          if c.get('Name', '').strip() and c.get('College Plan', 'None') != 'None']
        st.metric("Children with Education Plans", len(active_children))
    with col2:
        active_inheritances = [i for i in st.session_state.get('inheritance_list', []) 
                              if i.get('Amount', 0) > 0]
        total_inheritance = sum(i.get('Amount', 0) for i in active_inheritances)
        st.metric("Total Expected Inheritances", f"${total_inheritance:,.0f}")
    
    # Return data for simulation
    return {
        'children': st.session_state.get('children_list', []),
        'inheritances': st.session_state.get('inheritance_list', []),
        'college_inflation_pct': college_inflation_pct,
        'base_public_in': base_public_in,
        'base_public_out': base_public_out,
        'base_private': base_private
    }