"""
Scenario Studio Page
Self-contained scenario creation and side-by-side comparison
"""

import streamlit as st
from utils.comparison_scenarios import get_comparisons_for_plan, load_comparison_scenario
from utils.snapshot_manager import get_current_snapshot


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def export_comparison_to_csv(scenarios, base_plan_id):
    """Export comparison data to CSV format"""
    import pandas as pd
    from io import StringIO

    try:
        # Prepare comparison data
        rows = []
        for scenario in scenarios:
            sim_results = scenario.get('simulation_results', {})
            row = {
                'Scenario Name': scenario.get('name', 'Unknown'),
                'Created Date': scenario.get('created_at', '')[:10],
                'Final Savings': sim_results.get('final_savings', 0),
                'Final Net Worth': sim_results.get('final_net_worth', 0),
                'Years Solvent': sim_results.get('years_solvent', 0),
                'Health Score': sim_results.get('health_score', 0),
                'Emergency Fund (Months)': sim_results.get('emergency_fund_months', 0),
                'Debt to Income Ratio': sim_results.get('debt_to_income', 0),
                'Savings Rate': sim_results.get('savings_rate', 0),
            }
            rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Convert to CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        return csv_buffer.getvalue()

    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None


def export_comparison_to_excel(scenarios, base_plan_id):
    """Export comparison data to Excel with multiple sheets"""
    import pandas as pd
    from io import BytesIO

    try:
        # Create Excel writer
        excel_buffer = BytesIO()

        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # Sheet 1: Summary Comparison
            summary_rows = []
            for scenario in scenarios:
                sim_results = scenario.get('simulation_results', {})
                row = {
                    'Scenario Name': scenario.get('name', 'Unknown'),
                    'Created Date': scenario.get('created_at', '')[:10],
                    'Final Savings': sim_results.get('final_savings', 0),
                    'Final Net Worth': sim_results.get('final_net_worth', 0),
                    'Years Solvent': sim_results.get('years_solvent', 0),
                    'Health Score': sim_results.get('health_score', 0),
                    'Emergency Fund (Months)': sim_results.get('emergency_fund_months', 0),
                    'Debt to Income Ratio': sim_results.get('debt_to_income', 0),
                    'Savings Rate': sim_results.get('savings_rate', 0),
                }
                summary_rows.append(row)

            summary_df = pd.DataFrame(summary_rows)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Sheet 2: Parameters for each scenario
            for idx, scenario in enumerate(scenarios, 1):
                adjustments = scenario.get('adjustments', {})
                param_data = []
                for key, value in adjustments.items():
                    param_data.append({
                        'Parameter': key.replace('_', ' ').title(),
                        'Value': value
                    })

                param_df = pd.DataFrame(param_data)
                sheet_name = f"Params_{idx}"[:31]  # Excel limit 31 chars
                param_df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Sheet 3: Year-by-year data for first scenario (if available)
            if scenarios and 'simulation_results' in scenarios[0]:
                df_data = scenarios[0]['simulation_results'].get('df', {}).get('data', {})
                if df_data:
                    trajectory_df = pd.DataFrame(df_data)
                    trajectory_df.to_excel(writer, sheet_name='Trajectory', index=False)

        excel_buffer.seek(0)
        return excel_buffer.getvalue()

    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return None


def export_comparison_to_pdf(scenarios, base_plan_id):
    """Export comparison data to PDF with professional formatting"""
    from io import BytesIO

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import datetime

        # Create PDF buffer
        pdf_buffer = BytesIO()

        # Create document
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)

        # Container for PDF elements
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title Page
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph("Scenario Comparison Report", title_style))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                                 styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(f"Base Plan ID: {base_plan_id}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(f"Number of Scenarios: {len(scenarios)}", styles['Normal']))
        elements.append(PageBreak())

        # Comparison Table
        elements.append(Paragraph("Scenario Comparison Summary", heading_style))
        elements.append(Spacer(1, 0.2*inch))

        # Prepare table data
        table_data = [
            ['Scenario', 'Final Savings', 'Net Worth', 'Years Solvent', 'Health Score']
        ]

        for scenario in scenarios:
            sim_results = scenario.get('simulation_results', {})
            table_data.append([
                scenario.get('name', 'Unknown')[:20],  # Truncate long names
                f"${sim_results.get('final_savings', 0):,.0f}",
                f"${sim_results.get('final_net_worth', 0):,.0f}",
                f"{sim_results.get('years_solvent', 0)}",
                f"{sim_results.get('health_score', 0)}/100"
            ])

        # Create table
        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.5*inch))

        # Detailed metrics for each scenario
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Scenario Metrics", heading_style))

        for scenario in scenarios:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(f"<b>{scenario.get('name', 'Unknown')}</b>", styles['Heading3']))
            elements.append(Spacer(1, 0.1*inch))

            sim_results = scenario.get('simulation_results', {})

            details = [
                ['Metric', 'Value'],
                ['Final Savings', f"${sim_results.get('final_savings', 0):,.2f}"],
                ['Final Net Worth', f"${sim_results.get('final_net_worth', 0):,.2f}"],
                ['Years Solvent', f"{sim_results.get('years_solvent', 0)} years"],
                ['Health Score', f"{sim_results.get('health_score', 0)}/100"],
                ['Emergency Fund', f"{sim_results.get('emergency_fund_months', 0):.1f} months"],
                ['Debt/Income Ratio', f"{sim_results.get('debt_to_income', 0):.2f}%"],
                ['Savings Rate', f"{sim_results.get('savings_rate', 0):.2%}"],
            ]

            detail_table = Table(details, colWidths=[3*inch, 3*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightblue])
            ]))

            elements.append(detail_table)
            elements.append(Spacer(1, 0.3*inch))

        # Build PDF
        doc.build(elements)

        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    except ImportError:
        print("Error: reportlab not installed")
        return None
    except Exception as e:
        print(f"Error exporting to PDF: {e}")
        import traceback
        traceback.print_exc()
        return None


def render_scenario_studio_page():
    """Render the Scenario Studio page - Full self-contained experience"""

    # Add Quick Mode Switch in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎯 Quick Mode Switch")

        mode_options = ["INTAKE", "Analysis", "Scenario Studio", "Healthcare"]
        current_idx = 2  # Scenario Studio is current

        mode = st.radio(
            "Choose mode:",
            options=mode_options,
            index=current_idx,
            key="mode_selector_scenario_studio",
            help="INTAKE: Guided questionnaire | Analysis: Advanced simulation | Scenario Studio: Compare scenarios | Healthcare: Cost planning"
        )

        # Handle mode change
        if mode != "Scenario Studio":
            # Preserve current snapshot before mode switch
            if 'current_snapshot_id' in st.session_state:
                st.session_state['preserved_snapshot_id'] = st.session_state['current_snapshot_id']

            st.session_state.current_mode = mode
            st.session_state.mode_selected = True
            st.rerun()

    # Page header with reload button
    col_h1, col_h2 = st.columns([5, 1])

    with col_h1:
        st.markdown("# 🎬 Scenario Studio")
        st.markdown("**Create, simulate, and compare multiple retirement strategies**")

    with col_h2:
        st.markdown("")  # Spacing
        if st.button("🔄 Reload", key="reload_studio", help="Refresh page to see latest changes", width='stretch'):
            # Clear any cached data
            if 'pending_scenario' in st.session_state:
                del st.session_state['pending_scenario']
            st.rerun()

    st.markdown("---")

    # Get current base plan
    try:
        current_snapshot = get_current_snapshot()
        if not current_snapshot:
            st.warning("⚠️ Please complete the INTAKE questionnaire first to create a base plan.")
            if st.button("📝 Go to INTAKE"):
                st.session_state['current_mode'] = 'INTAKE'
                st.session_state['mode_selected'] = True
            return

        # Get the current snapshot ID from the index
        from utils.snapshot_manager import get_snapshots_index
        index = get_snapshots_index()
        base_plan_id = index.get('current_snapshot_id')

        if not base_plan_id:
            st.error("❌ No current snapshot ID found. Please save a snapshot in INTAKE mode first.")
            if st.button("📝 Go to INTAKE"):
                st.session_state['current_mode'] = 'INTAKE'
                st.session_state['mode_selected'] = True
            return

        # Extract user info from snapshot data (snapshot uses 'input_' prefix)
        user_name = current_snapshot.get('input_user_name', 'User')

        # Get the FULL plan name from the index (not just user_name)
        base_plan_name = user_name  # Default fallback
        for snapshot in index.get('snapshots', []):
            if snapshot['id'] == base_plan_id:
                base_plan_name = snapshot.get('name', user_name)
                break

        # Welcome message with user name
        st.markdown(f"### 👋 Welcome **{user_name}**!")
        st.success(f"✅ Base Plan: **{base_plan_name}** (ID: {base_plan_id[:8]}...)")

    except Exception as e:
        st.error(f"❌ Error loading base plan: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return

    # =============================================================================
    # SECTION 1: CREATE NEW SCENARIO
    # =============================================================================

    st.markdown("---")
    st.markdown("### 🎨 Create New Scenario")
    st.markdown("**Choose a preset template or customize your own scenario below**")

    # QUICK START TEMPLATES
    st.markdown("#### 🎯 Quick Start Templates")
    col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns(5)

    with col_t1:
        if st.button("🌅 Early Retirement", width='stretch', help="Retire at 60"):
            st.session_state['template'] = 'early_retirement'
            st.rerun()

    with col_t2:
        if st.button("💰 High Income", width='stretch', help="3x salary increase"):
            st.session_state['template'] = 'high_income'
            st.rerun()

    with col_t3:
        if st.button("🛡️ Conservative", width='stretch', help="Low risk, bonds heavy"):
            st.session_state['template'] = 'conservative'
            st.rerun()

    with col_t4:
        if st.button("🚀 Aggressive", width='stretch', help="High risk, stocks heavy"):
            st.session_state['template'] = 'aggressive'
            st.rerun()

    with col_t5:
        if st.button("💵 Frugal Living", width='stretch', help="Reduced expenses"):
            st.session_state['template'] = 'frugal'
            st.rerun()

    st.markdown("")  # Spacing

    # Get template adjustments if template was selected
    template_adjustments = {}
    template_name = ""

    # Get base plan values (needed for templates)
    snapshot_data = current_snapshot.get('data', current_snapshot)

    def get_value(key, default=0):
        if f'input_{key}' in snapshot_data:
            return snapshot_data[f'input_{key}']
        if key in snapshot_data:
            return snapshot_data[key]
        return default

    # Get current age for validation
    current_age = int(get_value('age', 45))

    if 'template' in st.session_state:
        template = st.session_state['template']

        if template == 'early_retirement':
            template_name = "Early Retirement (Age 60)"
            # Check if user is already past early retirement age
            if current_age >= 60:
                st.warning(f"⚠️ **Age Validation**: Your current age is {current_age}. Early retirement at age 60 is in the past. This template may not be suitable.")
                template_name = f"Early Retirement (Already {current_age})"
            template_adjustments = {
                'retirement_age': 60,
                'life_expectancy': 90,
            }
        elif template == 'high_income':
            template_name = "High Income Strategy"
            base_salary = get_value('salary_wages', 100000) * 12  # Convert monthly to annual
            template_adjustments = {
                'salary_wages': base_salary * 3,  # 3x annual salary
            }
        elif template == 'conservative':
            template_name = "Conservative Approach"
            template_adjustments = {
                'stocks_allocation': 30,
                'bonds_allocation': 70,
                'return_rate': 0.05,
            }
        elif template == 'aggressive':
            template_name = "Aggressive Growth"
            template_adjustments = {
                'stocks_allocation': 90,
                'bonds_allocation': 10,
                'return_rate': 0.09,
            }
        elif template == 'frugal':
            template_name = "Frugal Living"
            base_housing = get_value('housing_expenses', 24000) * 12  # Convert monthly to annual
            base_other = get_value('other_expenses', 12000) * 12  # Convert monthly to annual
            template_adjustments = {
                'housing_expenses': int(base_housing * 0.7),  # 70% of annual housing
                'other_expenses': int(base_other * 0.5),  # 50% of annual other
            }

        # Store template data persistently until form is submitted
        st.session_state['active_template_name'] = template_name
        st.session_state['active_template_adjustments'] = template_adjustments

        # CRITICAL: Clear cached widget values so form shows new template values
        # This forces Streamlit to use our template_adjustments instead of cached values
        keys_to_clear = [
            'adj_salary_wages', 'adj_social_security', 'adj_pension',
            'adj_investment_income', 'adj_other_income',
            'adj_housing_expenses', 'adj_healthcare_expenses',
            'adj_groceries', 'adj_transportation', 'adj_other_expenses'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        # Clear the trigger
        del st.session_state['template']

    # Use active template if it exists (persists across form interactions)
    if 'active_template_name' in st.session_state:
        template_name = st.session_state['active_template_name']
        template_adjustments = st.session_state['active_template_adjustments']

    with st.form(key="create_scenario_form"):

        # Scenario name - PROMINENT & MANDATORY
        st.markdown("#### 📝 Scenario Name (Required)")
        if template_name:
            st.info(f"📋 **Template Applied:** {template_name}")
        st.markdown("**Give this scenario a unique, memorable name before adjusting parameters**")

        scenario_name = st.text_input(
            "Enter scenario name:",
            value=template_name if template_name else "",
            placeholder="e.g., High Income Strategy, Early Retirement at 60, Conservative Plan",
            help="⚠️ REQUIRED: You must enter a scenario name to run the simulation",
            label_visibility="collapsed"
        )

        # Show warning if name is empty (visual cue)
        if not scenario_name or scenario_name.strip() == "":
            st.warning("⚠️ **Please enter a scenario name above before running the simulation**")
        else:
            st.success(f"✅ Scenario name set: **{scenario_name}**")

        # Get all base plan values from current_snapshot for defaults
        # The snapshot stores raw input values with 'input_' prefix
        snapshot_data = current_snapshot.get('data', current_snapshot)

        # Helper function to safely get values with defaults
        def get_value(key, default=0):
            """Get value from snapshot, handling both with and without input_ prefix"""
            # Try with input_ prefix first
            if f'input_{key}' in snapshot_data:
                return snapshot_data[f'input_{key}']
            # Try without prefix
            if key in snapshot_data:
                return snapshot_data[key]
            # Return default
            return default

        st.markdown("---")

        # =============================================================================
        # INCOME & EXPENSES
        # =============================================================================
        st.markdown("#### 💰 Income & Expenses")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Income Sources (Annual)**")
            st.caption("💡 Values from INTAKE (monthly) are converted to annual (*12)")

            # Convert monthly INTAKE values to annual for display
            adj_salary_wages = st.number_input(
                "Annual Salary/Wages",
                min_value=0,
                max_value=10000000,
                value=int(template_adjustments.get('salary_wages', get_value('salary_wages', 100000) * 12)),
                step=5000,
                help="Employment income (annual)"
            )

            adj_social_security = st.number_input(
                "Annual Social Security",
                min_value=0,
                max_value=100000,
                value=int(get_value('social_security_income', 0) * 12),
                step=1000,
                help="Expected Social Security benefits (annual)"
            )

            adj_pension = st.number_input(
                "Annual Pension",
                min_value=0,
                max_value=500000,
                value=int(get_value('pension_income', 0) * 12),
                step=1000,
                help="Pension income (annual)"
            )

            adj_investment_income = st.number_input(
                "Annual Investment Income",
                min_value=0,
                max_value=1000000,
                value=int(get_value('investment_income', 0) * 12),
                step=1000,
                help="Dividends, interest, rental income (annual)"
            )

            adj_other_income = st.number_input(
                "Other Annual Income",
                min_value=0,
                max_value=1000000,
                value=int(get_value('other_income', 0) * 12),
                step=1000,
                help="Other income sources (annual)"
            )

        with col2:
            st.markdown("**Expense Categories (Annual)**")
            st.caption("💡 Values from INTAKE (monthly) are converted to annual (*12)")

            adj_housing_expenses = st.number_input(
                "Annual Housing Expenses",
                min_value=0,
                max_value=500000,
                value=int(template_adjustments.get('housing_expenses', get_value('housing_expenses', 24000) * 12)),
                step=1000,
                help="Rent/mortgage, maintenance, utilities (annual)"
            )

            adj_healthcare_expenses = st.number_input(
                "Annual Healthcare Expenses",
                min_value=0,
                max_value=100000,
                value=int(get_value('healthcare_expenses', 6000) * 12),
                step=500,
                help="Medical, insurance, prescriptions (annual)"
            )

            adj_groceries = st.number_input(
                "Annual Groceries",
                min_value=0,
                max_value=50000,
                value=int(get_value('groceries_expenses', 7200) * 12),
                step=500,
                help="Food and household supplies (annual)"
            )

            adj_transportation = st.number_input(
                "Annual Transportation",
                min_value=0,
                max_value=50000,
                value=int(get_value('transportation_expenses', 4800) * 12),
                step=500,
                help="Car, gas, insurance, public transit (annual)"
            )

            adj_other_expenses = st.number_input(
                "Other Annual Expenses",
                min_value=0,
                max_value=200000,
                value=int(template_adjustments.get('other_expenses', get_value('other_expenses', 12000) * 12)),
                step=500,
                help="Entertainment, travel, misc (annual)"
            )

        st.markdown("---")

        # =============================================================================
        # RETIREMENT TIMING
        # =============================================================================
        st.markdown("#### 🎯 Retirement Timing & Life Planning")

        col3, col4, col5 = st.columns(3)

        with col3:
            adj_age = st.number_input(
                "Current Age",
                min_value=18,
                max_value=100,
                value=int(get_value('age', 45)),
                step=1,
                help="Your current age"
            )

            adj_retirement_age = st.slider(
                "Planned Retirement Age",
                min_value=50,
                max_value=80,
                value=int(template_adjustments.get('retirement_age', get_value('retirement_age', 65))),
                step=1,
                help="Age you plan to retire"
            )

        with col4:
            adj_life_expectancy = st.slider(
                "Life Expectancy",
                min_value=75,
                max_value=105,
                value=int(template_adjustments.get('life_expectancy', get_value('life_expectancy', 90))),
                step=1,
                help="Planning horizon"
            )

            adj_ss_claiming_age = st.slider(
                "Social Security Claiming Age",
                min_value=62,
                max_value=70,
                value=int(get_value('ss_claiming_age', 67)),
                step=1,
                help="Age to start Social Security"
            )

        with col5:
            adj_partner_exists = st.checkbox(
                "Partner/Spouse?",
                value=bool(get_value('partner_exists', False)),
                help="Include partner in planning"
            )

            if adj_partner_exists:
                adj_partner_age = st.number_input(
                    "Partner's Age",
                    min_value=18,
                    max_value=100,
                    value=int(get_value('partner_age', 45)),
                    step=1
                )
            else:
                adj_partner_age = None

        st.markdown("---")

        # =============================================================================
        # INVESTMENT STRATEGY
        # =============================================================================
        st.markdown("#### 📈 Investment Strategy & Returns")

        col6, col7 = st.columns(2)

        with col6:
            adj_return_rate = st.slider(
                "Expected Annual Return Rate",
                min_value=0.0,
                max_value=0.20,
                value=float(template_adjustments.get('return_rate', get_value('return_rate', 0.07))),
                step=0.005,
                format="%.2f%%",
                help="Average annual investment return (before inflation)"
            )

            adj_stocks_allocation = st.slider(
                "Stocks Allocation %",
                min_value=0,
                max_value=100,
                value=int(template_adjustments.get('stocks_allocation', get_value('stocks_allocation', 60))),
                step=5,
                format="%d%%",
                help="Percentage allocated to stocks/equity"
            )

            adj_bonds_allocation = st.slider(
                "Bonds Allocation %",
                min_value=0,
                max_value=100,
                value=int(template_adjustments.get('bonds_allocation', get_value('bonds_allocation', 40))),
                step=5,
                format="%d%%",
                help="Percentage allocated to bonds/fixed income"
            )

        with col7:
            adj_inflation_rate = st.slider(
                "Expected Inflation Rate",
                min_value=0.0,
                max_value=0.10,
                value=float(get_value('inflation_rate', 0.03)),
                step=0.005,
                format="%.2f%%",
                help="Average annual inflation rate"
            )

            # Allocation warning
            total_allocation = adj_stocks_allocation + adj_bonds_allocation
            if total_allocation != 100:
                st.warning(f"⚠️ Allocation total: {total_allocation}% (should be 100%)")
            else:
                st.success(f"✅ Allocation total: {total_allocation}%")

        st.markdown("---")

        # =============================================================================
        # ACCOUNT BALANCES
        # =============================================================================
        st.markdown("#### 💼 Current Account Balances")

        col8, col9, col10 = st.columns(3)

        with col8:
            st.markdown("**Tax-Advantaged**")

            adj_ira_balance = st.number_input(
                "Traditional IRA Balance",
                min_value=0,
                max_value=50000000,
                value=int(get_value('ira_balance', 0)),
                step=10000,
                help="Traditional IRA accounts"
            )

            adj_401k_balance = st.number_input(
                "401(k)/403(b) Balance",
                min_value=0,
                max_value=50000000,
                value=int(get_value('four01k_403b_balance', 0)),
                step=10000,
                help="Employer retirement accounts"
            )

        with col9:
            st.markdown("**Tax-Free**")

            adj_roth_balance = st.number_input(
                "Roth IRA Balance",
                min_value=0,
                max_value=50000000,
                value=int(get_value('roth_balance', 0)),
                step=10000,
                help="Roth IRA accounts"
            )

            adj_hsa_balance = st.number_input(
                "HSA Balance",
                min_value=0,
                max_value=1000000,
                value=int(get_value('hsa_balance', 0)),
                step=1000,
                help="Health Savings Account"
            )

        with col10:
            st.markdown("**Taxable**")

            adj_taxable_accounts = st.number_input(
                "Taxable Investment Accounts",
                min_value=0,
                max_value=100000000,
                value=int(get_value('taxable_investment_accounts', 0)),
                step=10000,
                help="Brokerage accounts"
            )

            adj_savings = st.number_input(
                "High-Yield Savings",
                min_value=0,
                max_value=10000000,
                value=int(get_value('high_yield_savings_account', 0)),
                step=5000,
                help="Cash savings accounts"
            )

        # Partner accounts (if applicable)
        if adj_partner_exists:
            st.markdown("---")
            st.markdown("**Partner's Accounts**")

            col11, col12, col13 = st.columns(3)

            with col11:
                adj_partner_ira = st.number_input(
                    "Partner's IRA Balance",
                    min_value=0,
                    max_value=50000000,
                    value=int(get_value('partner_ira_balance', 0)),
                    step=10000
                )

            with col12:
                adj_partner_401k = st.number_input(
                    "Partner's 401(k) Balance",
                    min_value=0,
                    max_value=50000000,
                    value=int(get_value('partner_four01k_403b_balance', 0)),
                    step=10000
                )

            with col13:
                st.write("")  # Spacing
        else:
            adj_partner_ira = 0
            adj_partner_401k = 0

        st.markdown("---")

        # =============================================================================
        # REAL ESTATE & ASSETS
        # =============================================================================
        st.markdown("#### 🏠 Real Estate & Other Assets")

        col14, col15 = st.columns(2)

        with col14:
            adj_home_value = st.number_input(
                "Primary Residence Value",
                min_value=0,
                max_value=50000000,
                value=int(get_value('primary_residence_value', 0)),
                step=25000,
                help="Current market value of primary home"
            )

            adj_mortgage_balance = st.number_input(
                "Primary Mortgage Balance",
                min_value=0,
                max_value=10000000,
                value=int(get_value('primary_residence_mortgage', 0)),
                step=10000,
                help="Remaining mortgage principal on primary home"
            )

            adj_secondary_residence = st.number_input(
                "Secondary Residence Value",
                min_value=0,
                max_value=50000000,
                value=int(get_value('secondary_residence_value', 0)),
                step=25000,
                help="Current market value of vacation/second home"
            )

            adj_vehicles_value = st.number_input(
                "Vehicles Value",
                min_value=0,
                max_value=1000000,
                value=int(get_value('vehicles_value', 0)),
                step=5000,
                help="Total value of vehicles"
            )

        with col15:
            adj_secondary_mortgage = st.number_input(
                "Secondary Mortgage Balance",
                min_value=0,
                max_value=10000000,
                value=int(get_value('secondary_residence_mortgage', 0)),
                step=10000,
                help="Remaining mortgage principal on secondary home"
            )

            adj_other_assets = st.number_input(
                "Other Assets",
                min_value=0,
                max_value=100000000,
                value=int(get_value('other_assets', 0)),
                step=10000,
                help="Business, rental property, collectibles, etc."
            )

            adj_other_liabilities = st.number_input(
                "Other Debts/Liabilities",
                min_value=0,
                max_value=10000000,
                value=int(get_value('other_liabilities', 0)),
                step=5000,
                help="Credit cards, loans, etc."
            )

        st.markdown("---")

        # =============================================================================
        # FORM SUBMIT
        # =============================================================================

        col_submit1, col_submit2 = st.columns([3, 1])

        with col_submit1:
            st.markdown("**Ready to simulate this scenario?**")
            st.markdown("Click below to run the retirement simulation with these adjusted parameters.")

        with col_submit2:
            run_scenario = st.form_submit_button(
                "🔍 Run This Scenario",
                type="primary",
                width='stretch'
            )

    # =============================================================================
    # HANDLE FORM SUBMISSION
    # =============================================================================

    if run_scenario:
        if not scenario_name or scenario_name.strip() == "":
            st.error("⚠️ **Please enter a scenario name** before running the simulation.")
        else:
            # =============================================================================
            # RUN SIMULATION
            # =============================================================================

            st.markdown("---")
            st.markdown("### 🔍 Running Simulation...")

            with st.spinner(f"Calculating '{scenario_name}' retirement trajectory..."):
                try:
                    from simulation_core import run_simulation

                    # Calculate total income and expenses
                    total_income = (adj_salary_wages + adj_social_security +
                                  adj_pension + adj_investment_income + adj_other_income)

                    total_expenses = (adj_housing_expenses + adj_healthcare_expenses +
                                    adj_groceries + adj_transportation + adj_other_expenses)

                    # Calculate liquid assets (retirement accounts + taxable + savings)
                    liquid_assets = (adj_ira_balance + adj_401k_balance + adj_roth_balance +
                                   adj_hsa_balance + adj_taxable_accounts + adj_savings +
                                   adj_partner_ira + adj_partner_401k)

                    # Calculate total liabilities (includes both mortgages)
                    total_liabilities = adj_mortgage_balance + adj_secondary_mortgage + adj_other_liabilities

                    # Calculate simulation years (from current age to life expectancy)
                    simulation_years = adj_life_expectancy - adj_age

                    # Monthly surplus
                    monthly_surplus = (total_income - total_expenses) / 12

                    # Run the simulation!
                    results = run_simulation(
                        age=adj_age,
                        partner_exists=adj_partner_exists,
                        partner_age=adj_partner_age if adj_partner_exists else adj_age,
                        total_income=total_income,
                        total_expenses=total_expenses,
                        combined_financial_assets=liquid_assets,
                        primary_residence_value=adj_home_value,
                        secondary_residence_value=adj_secondary_residence,
                        combined_other_assets_total=adj_other_assets + adj_vehicles_value,
                        total_liabilities_local=total_liabilities,
                        partner_liabilities=0,
                        tax_rate=22.0,  # Default tax rate
                        inflation_rate=adj_inflation_rate * 100,  # Convert to percentage
                        investment_return_rate=adj_return_rate * 100,  # Convert to percentage
                        simulation_years=simulation_years,
                        mc_iterations=0,  # No Monte Carlo for quick preview
                        goal_costs={},
                        college_inflation_pct=4.0,
                        base_public_in=20000,
                        base_public_out=40000,
                        base_private=60000,
                        ira_balance=adj_ira_balance,
                        four01k_403b_balance=adj_401k_balance,
                        partner_ira_balance=adj_partner_ira,
                        partner_four01k_403b_balance=adj_partner_401k,
                        monthly_surplus=monthly_surplus,
                        combined_total_liabilities=total_liabilities
                    )

                    if results:
                        st.success(f"✅ **Simulation complete for '{scenario_name}'!**")

                        # =============================================================================
                        # RESULTS PREVIEW
                        # =============================================================================

                        st.markdown("---")
                        st.markdown("### 📊 Results Preview")

                        # Key metrics in columns
                        col_r1, col_r2, col_r3 = st.columns(3)

                        with col_r1:
                            final_savings = results.get('final_savings', 0)
                            st.metric(
                                "Final Savings",
                                f"${final_savings:,.0f}",
                                help="Projected savings at life expectancy"
                            )

                        with col_r2:
                            years_solvent = results.get('years_solvent', 0)
                            st.metric(
                                "Years Solvent",
                                f"{years_solvent} years",
                                help="How many years your money lasts"
                            )

                        with col_r3:
                            final_net_worth = results.get('final_net_worth', 0)
                            st.metric(
                                "Final Net Worth",
                                f"${final_net_worth:,.0f}",
                                help="Total net worth at end"
                            )

                        # Additional metrics
                        col_r4, col_r5, col_r6 = st.columns(3)

                        with col_r4:
                            health_score = results.get('health_score', 0)
                            st.metric(
                                "Financial Health Score",
                                f"{health_score}/100",
                                help="Overall financial health rating"
                            )

                        with col_r5:
                            savings_rate = results.get('savings_rate', 0)
                            st.metric(
                                "Savings Rate",
                                f"{savings_rate:.1f}%",
                                help="Percentage of income saved"
                            )

                        with col_r6:
                            emergency_months = results.get('emergency_fund_months', 0)
                            st.metric(
                                "Emergency Fund",
                                f"{emergency_months:.1f} months",
                                help="Months of expenses covered"
                            )

                        # Store results for comparison and saving
                        st.session_state['pending_scenario'] = {
                            'name': scenario_name,
                            'base_plan_id': base_plan_id,
                            'adjustments': {
                                # Income
                                'salary_wages': adj_salary_wages,
                                'social_security_income': adj_social_security,
                                'pension_income': adj_pension,
                                'investment_income': adj_investment_income,
                                'other_income': adj_other_income,

                                # Expenses
                                'housing_expenses': adj_housing_expenses,
                                'healthcare_expenses': adj_healthcare_expenses,
                                'groceries_expenses': adj_groceries,
                                'transportation_expenses': adj_transportation,
                                'other_expenses': adj_other_expenses,

                                # Timing
                                'age': adj_age,
                                'retirement_age': adj_retirement_age,
                                'life_expectancy': adj_life_expectancy,
                                'ss_claiming_age': adj_ss_claiming_age,
                                'partner_exists': adj_partner_exists,
                                'partner_age': adj_partner_age,

                                # Investment
                                'return_rate': adj_return_rate,
                                'inflation_rate': adj_inflation_rate,
                                'stocks_allocation': adj_stocks_allocation,
                                'bonds_allocation': adj_bonds_allocation,

                                # Accounts
                                'ira_balance': adj_ira_balance,
                                'four01k_403b_balance': adj_401k_balance,
                                'roth_balance': adj_roth_balance,
                                'hsa_balance': adj_hsa_balance,
                                'taxable_investment_accounts': adj_taxable_accounts,
                                'high_yield_savings_account': adj_savings,
                                'partner_ira_balance': adj_partner_ira,
                                'partner_four01k_403b_balance': adj_partner_401k,

                                # Real Estate
                                'primary_residence_value': adj_home_value,
                                'primary_residence_mortgage': adj_mortgage_balance,
                                'secondary_residence_value': adj_secondary_residence,
                                'secondary_residence_mortgage': adj_secondary_mortgage,
                                'vehicles_value': adj_vehicles_value,
                                'other_assets': adj_other_assets,
                                'other_liabilities': adj_other_liabilities,
                            },
                            'simulation_results': results
                        }

                        # Save button moved outside form block for reliability
                        st.markdown("---")
                        st.info("✅ **Simulation complete!** Scroll down to save this scenario.")

                    else:
                        st.error("❌ Simulation failed. Please check your parameters.")

                except Exception as e:
                    st.error(f"❌ Error running simulation: {str(e)}")
                    import traceback
                    with st.expander("🐛 Show error details"):
                        st.code(traceback.format_exc())

    # =============================================================================
    # SECTION 1.5: SAVE PENDING SCENARIO (OUTSIDE FORM BLOCK)
    # =============================================================================

    # Check if there's a pending scenario to save (moved outside form submission)
    if 'pending_scenario' in st.session_state and st.session_state.get('pending_scenario'):
        pending = st.session_state['pending_scenario']

        st.markdown("---")
        st.markdown("---")
        st.markdown("### 💾 Save This Scenario")
        st.markdown(f"**Scenario:** {pending['name']}")
        st.markdown("This scenario has been simulated. Click below to save it permanently.")

        col_save1, col_save2, col_save3 = st.columns([1, 2, 1])

        with col_save2:
            # Unique key based on scenario name
            save_button_key = f"save_btn_{pending['name'].replace(' ', '_')}"

            if st.button(
                "💾 Save Scenario",
                type="primary",
                width='stretch',
                key=save_button_key
            ):
                from utils.comparison_scenarios import save_comparison_scenario

                try:
                    print(f"[SCENARIO STUDIO] Save button clicked! Scenario: {pending['name']}")

                    # Prepare simulation results - convert DataFrame to dict for JSON serialization
                    sim_results = pending.get('simulation_results', {})
                    serializable_results = {}

                    for key, value in sim_results.items():
                        # Check if it's a DataFrame
                        if hasattr(value, 'to_dict'):
                            # Convert DataFrame to dict (orient='list' is most compact)
                            serializable_results[key] = {
                                '_type': 'dataframe',
                                'data': value.to_dict(orient='list')
                            }
                        else:
                            # Keep as-is for other types
                            serializable_results[key] = value

                    print(f"[SCENARIO STUDIO] Serialized {len(serializable_results)} result keys")

                    comparison_id = save_comparison_scenario(
                        base_plan_id=pending['base_plan_id'],
                        name=pending['name'],
                        description=f"Created in Scenario Studio",
                        adjustments=pending['adjustments'],
                        simulation_results=serializable_results
                    )

                    if comparison_id:
                        print(f"[SCENARIO STUDIO] Save successful! ID: {comparison_id}")

                        # CELEBRATION!
                        st.balloons()

                        # Clear pending scenario and active template
                        del st.session_state['pending_scenario']
                        if 'active_template_name' in st.session_state:
                            del st.session_state['active_template_name']
                        if 'active_template_adjustments' in st.session_state:
                            del st.session_state['active_template_adjustments']

                        # Show success inline (NO RERUN!)
                        st.success(f"✅ **Saved!** Scenario '{pending['name']}' (ID: {comparison_id[:8]}...)")
                        st.info("🔄 **Reload the page manually** to see it in your saved scenarios list below.")
                    else:
                        st.error("❌ Save failed - no comparison ID returned")
                        print(f"[SCENARIO STUDIO] ERROR: No ID returned")

                except Exception as e:
                    st.error(f"❌ Error saving: {str(e)}")
                    print(f"[SCENARIO STUDIO] ERROR saving: {e}")
                    import traceback
                    traceback.print_exc()

    # =============================================================================
    # SECTION 2: SAVED SCENARIOS (List)
    # =============================================================================

    st.markdown("---")
    st.markdown("---")
    st.markdown("### 📊 Your Saved Scenarios")

    # Get saved comparisons
    comparisons = get_comparisons_for_plan(base_plan_id)

    if len(comparisons) == 0:
        st.info("💡 **No saved scenarios yet!** Create and save your first scenario above.")

    elif len(comparisons) == 1:
        st.info(f"✅ **Found 1 saved scenario.** Create at least one more to enable side-by-side comparison.")
        st.markdown("**Saved Scenarios:**")
        for idx, comp in enumerate(comparisons):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{comp['name']}**")
                st.caption(f"Created: {comp['created_at'][:16].replace('T', ' ')}")
            with col2:
                if st.button("🗑️ Delete", key=f"delete_single_{idx}_{comp['id']}", type="secondary", width='stretch'):
                    from utils.comparison_scenarios import delete_comparison_scenario
                    if delete_comparison_scenario(comp['id']):
                        st.success(f"✅ Deleted: {comp['name']}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete scenario")

    else:
        # 2+ scenarios - SHOW COMPARISON TABLE!
        st.success(f"📊 **Found {len(comparisons)} saved scenarios!**")

        # MANAGE SCENARIOS SECTION
        st.markdown("---")
        st.markdown("### 📋 Manage Saved Scenarios")

        with st.expander("View & Delete Scenarios", expanded=False):
            for idx, comp in enumerate(comparisons):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{comp['name']}**")
                    st.caption(f"Created: {comp['created_at'][:16].replace('T', ' ')} | ID: {comp['id'][:8]}...")
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{idx}_{comp['id']}", type="secondary", width='stretch'):
                        from utils.comparison_scenarios import delete_comparison_scenario
                        if delete_comparison_scenario(comp['id']):
                            st.success(f"✅ Deleted: {comp['name']}")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete scenario")
                st.markdown("")  # Spacing

        st.markdown("---")
        st.markdown("### 🔀 Compare Scenarios Side-by-Side")
        st.markdown("**Click on 2-4 scenarios below to compare them:**")

        # Initialize selected scenarios in session state
        if 'selected_scenario_ids' not in st.session_state:
            st.session_state['selected_scenario_ids'] = []

        # Option to include base plan in comparison
        if 'include_base_in_comparison' not in st.session_state:
            st.session_state['include_base_in_comparison'] = False

        include_base = st.checkbox(
            f"📊 Include Base Plan (**{base_plan_name}**) in comparison",
            value=st.session_state['include_base_in_comparison'],
            key="include_base_checkbox",
            help="Check this to compare your saved scenarios against the original base plan"
        )
        st.session_state['include_base_in_comparison'] = include_base
        if include_base:
            st.info(f"✅ Base Plan **{base_plan_name}** will be included in comparison")

        # Display ALL scenarios as clickable cards
        num_scenarios = len(comparisons)
        cols_per_row = min(4, num_scenarios)  # Max 4 columns per row

        # Create rows of scenario cards
        for row_start in range(0, num_scenarios, cols_per_row):
            row_scenarios = comparisons[row_start:row_start + cols_per_row]
            cols = st.columns(len(row_scenarios))

            for idx, comp in enumerate(row_scenarios):
                with cols[idx]:
                    is_selected = comp['id'] in st.session_state['selected_scenario_ids']

                    # Card styling based on selection
                    if is_selected:
                        button_type = "primary"
                        button_label = f"✅ {comp['name']}"
                    else:
                        button_type = "secondary"
                        button_label = comp['name']

                    # Clickable card
                    if st.button(
                        button_label,
                        key=f"select_compare_{comp['id']}",
                        type=button_type,
                        width='stretch',
                        help=f"Created: {comp['created_at'][:16].replace('T', ' ')}"
                    ):
                        # Toggle selection
                        if is_selected:
                            st.session_state['selected_scenario_ids'].remove(comp['id'])
                        else:
                            # Check if already have 4 selected
                            if len(st.session_state['selected_scenario_ids']) >= 4:
                                st.warning("⚠️ Maximum 4 scenarios can be compared at once. Deselect one first.")
                            else:
                                st.session_state['selected_scenario_ids'].append(comp['id'])
                        st.rerun()

                    # Show selection number
                    if is_selected:
                        selection_num = st.session_state['selected_scenario_ids'].index(comp['id']) + 1
                        st.caption(f"🔢 Selection #{selection_num}")
                    else:
                        st.caption(f"ID: {comp['id'][:8]}...")

        # Show selection summary
        num_selected = len(st.session_state['selected_scenario_ids'])
        if num_selected > 0:
            if num_selected == 1:
                if include_base:
                    st.success(f"✅ **{num_selected} scenario + Base Plan selected!** Comparison will appear below.")
                else:
                    st.info(f"💡 **{num_selected} scenario selected.** Select at least 1 more to compare, OR check **'Include Base Plan'** above!")
            elif num_selected >= 2:
                st.success(f"✅ **{num_selected} scenarios selected!** Comparison table will appear below.")

            # Clear selection button
            if st.button("🔄 Clear Selection", key="clear_comparison_selection"):
                st.session_state['selected_scenario_ids'] = []
                st.rerun()
        else:
            st.info("💡 **No scenarios selected.** Click on 2-4 scenario cards above to compare them.")

        # Get selected scenario names for comparison
        selected_names = [comp['name'] for comp in comparisons if comp['id'] in st.session_state['selected_scenario_ids']]

        if len(selected_names) >= 2 or (len(selected_names) >= 1 and include_base):
            total_in_comparison = len(selected_names) + (1 if include_base else 0)
            st.markdown(f"**Comparing {total_in_comparison} scenarios...**")

            # Load full data for selected scenarios
            selected_comparisons = [comp for comp in comparisons if comp['name'] in selected_names]

            # Load detailed data for each
            from utils.comparison_scenarios import load_comparison_scenario
            detailed_scenarios = []

            # If including base plan, add it first
            if include_base:
                # Run simulation for base plan to get its results
                try:
                    from simulation_core import run_simulation

                    # Get base plan values from current_snapshot
                    base_salary = get_value('salary_wages', 100000)
                    base_ss = get_value('social_security_income', 0)
                    base_pension = get_value('pension_income', 0)
                    base_inv_income = get_value('investment_income', 0)
                    base_other_income = get_value('other_income', 0)

                    base_housing = get_value('housing_expenses', 24000)
                    base_healthcare = get_value('healthcare_expenses', 6000)
                    base_groceries = get_value('groceries_expenses', 7200)
                    base_transportation = get_value('transportation_expenses', 4800)
                    base_other_expenses = get_value('other_expenses', 12000)

                    base_age = int(get_value('age', 45))
                    base_life_expectancy = int(get_value('life_expectancy', 90))
                    base_partner_exists = bool(get_value('partner_exists', False))
                    base_partner_age = int(get_value('partner_age', 45))

                    base_return_rate = float(get_value('return_rate', 0.07))
                    base_inflation_rate = float(get_value('inflation_rate', 0.03))

                    base_ira = int(get_value('ira_balance', 0))
                    base_401k = int(get_value('four01k_403b_balance', 0))
                    base_roth = int(get_value('roth_balance', 0))
                    base_hsa = int(get_value('hsa_balance', 0))
                    base_taxable = int(get_value('taxable_investment_accounts', 0))
                    base_savings_acct = int(get_value('high_yield_savings_account', 0))
                    base_partner_ira = int(get_value('partner_ira_balance', 0))
                    base_partner_401k = int(get_value('partner_four01k_403b_balance', 0))

                    base_home_value = int(get_value('primary_residence_value', 0))
                    base_mortgage = int(get_value('primary_residence_mortgage', 0))
                    base_secondary = int(get_value('secondary_residence_value', 0))
                    base_secondary_mortgage = int(get_value('secondary_residence_mortgage', 0))
                    base_vehicles = int(get_value('vehicles_value', 0))
                    base_other_assets = int(get_value('other_assets', 0))
                    base_other_liabilities = int(get_value('other_liabilities', 0))

                    # Calculate totals
                    total_income = base_salary + base_ss + base_pension + base_inv_income + base_other_income
                    total_expenses = base_housing + base_healthcare + base_groceries + base_transportation + base_other_expenses
                    liquid_assets = base_ira + base_401k + base_roth + base_hsa + base_taxable + base_savings_acct + base_partner_ira + base_partner_401k
                    total_liabilities = base_mortgage + base_secondary_mortgage + base_other_liabilities
                    simulation_years = base_life_expectancy - base_age
                    monthly_surplus = (total_income - total_expenses) / 12

                    # Run simulation for base plan
                    base_results = run_simulation(
                        age=base_age,
                        partner_exists=base_partner_exists,
                        partner_age=base_partner_age if base_partner_exists else base_age,
                        total_income=total_income,
                        total_expenses=total_expenses,
                        combined_financial_assets=liquid_assets,
                        primary_residence_value=base_home_value,
                        secondary_residence_value=base_secondary,
                        combined_other_assets_total=base_other_assets + base_vehicles,
                        total_liabilities_local=total_liabilities,
                        partner_liabilities=0,
                        tax_rate=22.0,
                        inflation_rate=base_inflation_rate * 100,
                        investment_return_rate=base_return_rate * 100,
                        simulation_years=simulation_years,
                        mc_iterations=0,
                        goal_costs={},
                        college_inflation_pct=4.0,
                        base_public_in=20000,
                        base_public_out=40000,
                        base_private=60000,
                        ira_balance=base_ira,
                        four01k_403b_balance=base_401k,
                        partner_ira_balance=base_partner_ira,
                        partner_four01k_403b_balance=base_partner_401k,
                        monthly_surplus=monthly_surplus,
                        combined_total_liabilities=total_liabilities
                    )

                    if base_results:
                        # Serialize DataFrame in results
                        serializable_results = {}
                        for key, value in base_results.items():
                            if hasattr(value, 'to_dict'):
                                serializable_results[key] = {
                                    '_type': 'dataframe',
                                    'data': value.to_dict(orient='list')
                                }
                            else:
                                serializable_results[key] = value

                        # Create base plan as a "scenario" for comparison
                        base_scenario = {
                            'name': f"📊 BASE: {base_plan_name}",
                            'adjustments': {
                                'salary_wages': base_salary,
                                'social_security_income': base_ss,
                                'pension_income': base_pension,
                                'investment_income': base_inv_income,
                                'other_income': base_other_income,
                                'housing_expenses': base_housing,
                                'healthcare_expenses': base_healthcare,
                                'groceries_expenses': base_groceries,
                                'transportation_expenses': base_transportation,
                                'other_expenses': base_other_expenses,
                                'age': base_age,
                                'return_rate': base_return_rate,
                                'inflation_rate': base_inflation_rate,
                                'stocks_allocation': int(get_value('stocks_allocation', 60)),
                                'bonds_allocation': int(get_value('bonds_allocation', 40)),
                            },
                            'simulation_results': serializable_results
                        }
                        detailed_scenarios.append(base_scenario)
                        st.info(f"✅ Base plan **{base_plan_name}** included in comparison")
                except Exception as e:
                    st.warning(f"⚠️ Could not include base plan: {e}")

            for comp in selected_comparisons:
                detailed = load_comparison_scenario(comp['id'])
                if detailed:
                    detailed_scenarios.append(detailed)
                else:
                    st.warning(f"⚠️ Could not load scenario: {comp['name']} (ID: {comp['id']})")

            # DEBUG: Show what we loaded
            print(f"[COMPARISON DEBUG] Loaded {len(detailed_scenarios)} scenarios for comparison")
            for idx, scen in enumerate(detailed_scenarios):
                print(f"  Scenario {idx+1}: {scen.get('name', 'UNNAMED')}")
                print(f"    - Has 'adjustments': {'adjustments' in scen}")
                print(f"    - Has 'simulation_results': {'simulation_results' in scen}")
                if 'adjustments' in scen:
                    print(f"    - Adjustment keys: {list(scen['adjustments'].keys())}")
                if 'simulation_results' in scen:
                    print(f"    - Result keys: {list(scen['simulation_results'].keys())[:5]}...")

            # DEFENSIVE FIX: Ensure all scenarios have same adjustment keys (fill missing with 'N/A')
            # This fixes the issue with 3+ scenarios + BASE plan
            if len(detailed_scenarios) >= 2:
                all_adjustment_keys = set()
                all_result_keys = set()

                # Collect all keys from all scenarios
                for scen in detailed_scenarios:
                    if 'adjustments' in scen:
                        all_adjustment_keys.update(scen['adjustments'].keys())
                    if 'simulation_results' in scen:
                        all_result_keys.update(scen['simulation_results'].keys())

                print(f"[COMPARISON DEBUG] Total unique adjustment keys: {len(all_adjustment_keys)}")
                print(f"[COMPARISON DEBUG] Total unique result keys: {len(all_result_keys)}")

                # Fill missing keys with 'N/A' in all scenarios
                for scen in detailed_scenarios:
                    if 'adjustments' not in scen:
                        scen['adjustments'] = {}
                    if 'simulation_results' not in scen:
                        scen['simulation_results'] = {}

                    for key in all_adjustment_keys:
                        if key not in scen['adjustments']:
                            scen['adjustments'][key] = 'N/A'
                            print(f"  [FILL] Added missing adjustment key '{key}' to {scen.get('name', 'UNNAMED')}")

                    for key in all_result_keys:
                        if key not in scen['simulation_results']:
                            scen['simulation_results'][key] = 'N/A'

                print(f"[COMPARISON DEBUG] All scenarios now have consistent keys")

            if len(detailed_scenarios) >= 2:
                # Debug info
                st.caption(f"🔍 Comparing {len(detailed_scenarios)} scenarios")

                # Wrap entire comparison table in try/except for debugging
                try:
                    # Helper function for visual comparisons
                    def compare_to_base(scenario_value, base_value, higher_is_better=True):
                        """Return indicator and delta for comparison"""
                        if scenario_value == 'N/A' or base_value == 'N/A':
                            return '', ''

                        try:
                            delta = scenario_value - base_value
                            if delta > 0:
                                if higher_is_better:
                                    indicator = "🟢 ↑"
                                else:
                                    indicator = "🔴 ↑"
                            elif delta < 0:
                                if higher_is_better:
                                    indicator = "🔴 ↓"
                                else:
                                    indicator = "🟢 ↓"
                            else:
                                indicator = "⚪ →"
                                delta = 0
                            return indicator, delta
                        except:
                            return '', ''

                    # Build comparison table
                    import pandas as pd

                    comparison_data = []

                    # Row 1: Scenario Name
                    comparison_data.append({
                        'Metric': '📝 Scenario Name',
                        **{f'Scenario {i+1}': s['name'] for i, s in enumerate(detailed_scenarios)}
                    })

                    # Section: Key Results
                    comparison_data.append({
                        'Metric': '─── 📊 KEY RESULTS ───',
                        **{f'Scenario {i+1}': '' for i in range(len(detailed_scenarios))}
                    })

                    # Get simulation results (if available) with comparisons
                    for metric_key, metric_label, higher_is_better in [
                        ('final_savings', '💰 Final Savings', True),
                        ('final_net_worth', '💎 Final Net Worth', True),
                        ('years_solvent', '⏳ Years Solvent', True),
                        ('health_score', '❤️ Health Score', True),
                        ('savings_rate', '📈 Savings Rate', True),
                    ]:
                        row = {'Metric': metric_label}

                        # Get base value (first scenario)
                        base_sim_results = detailed_scenarios[0].get('simulation_results', {})
                        base_value = base_sim_results.get(metric_key, 'N/A')

                        for i, s in enumerate(detailed_scenarios):
                            sim_results = s.get('simulation_results', {})
                            value = sim_results.get(metric_key, 'N/A')

                            # Format the value
                            if value == 'N/A':
                                formatted = 'N/A'
                            elif metric_key in ['final_savings', 'final_net_worth']:
                                formatted = f"${value:,.0f}"
                                # Add comparison for non-base scenarios
                                if i > 0 and value != 'N/A' and base_value != 'N/A':
                                    indicator, delta = compare_to_base(value, base_value, higher_is_better)
                                    if delta != 0:
                                        formatted += f"\n{indicator} ${abs(delta):,.0f}"
                            elif metric_key == 'years_solvent':
                                formatted = f"{value} years"
                                if i > 0 and value != 'N/A' and base_value != 'N/A':
                                    indicator, delta = compare_to_base(value, base_value, higher_is_better)
                                    if delta != 0:
                                        formatted += f"\n{indicator} {abs(delta):.0f} yrs"
                            elif metric_key == 'health_score':
                                formatted = f"{value}/100"
                                if i > 0 and value != 'N/A' and base_value != 'N/A':
                                    indicator, delta = compare_to_base(value, base_value, higher_is_better)
                                    if delta != 0:
                                        formatted += f"\n{indicator} {abs(delta):.0f} pts"
                            elif metric_key == 'savings_rate':
                                formatted = f"{value:.1f}%"
                                if i > 0 and value != 'N/A' and base_value != 'N/A':
                                    indicator, delta = compare_to_base(value, base_value, higher_is_better)
                                    if delta != 0:
                                        formatted += f"\n{indicator} {abs(delta):.1f}%"
                            else:
                                formatted = str(value)

                            row[f'Scenario {i+1}'] = formatted

                        comparison_data.append(row)

                    # Section: Income & Expenses
                    comparison_data.append({
                        'Metric': '─── 💰 INCOME & EXPENSES ───',
                        **{f'Scenario {i+1}': '' for i in range(len(detailed_scenarios))}
                    })

                    for adj_key, adj_label in [
                        ('salary_wages', '💵 Salary/Wages'),
                        ('social_security_income', '🏛️ Social Security'),
                        ('pension_income', '🎖️ Pension'),
                        ('housing_expenses', '🏠 Housing'),
                        ('healthcare_expenses', '⚕️ Healthcare'),
                    ]:
                        row = {'Metric': adj_label}
                        for i, s in enumerate(detailed_scenarios):
                            adjustments = s.get('adjustments', {})
                            value = adjustments.get(adj_key, 'N/A')
                            row[f'Scenario {i+1}'] = f"${value:,.0f}" if value != 'N/A' else 'N/A'
                        comparison_data.append(row)

                    # Section: Investment Strategy
                    comparison_data.append({
                        'Metric': '─── 📈 INVESTMENT STRATEGY ───',
                        **{f'Scenario {i+1}': '' for i in range(len(detailed_scenarios))}
                    })

                    for adj_key, adj_label in [
                        ('return_rate', '📊 Return Rate'),
                        ('inflation_rate', '📉 Inflation Rate'),
                        ('stocks_allocation', '📈 Stocks %'),
                        ('bonds_allocation', '🔒 Bonds %'),
                    ]:
                        row = {'Metric': adj_label}
                        for i, s in enumerate(detailed_scenarios):
                            adjustments = s.get('adjustments', {})
                            value = adjustments.get(adj_key, 'N/A')

                            if value != 'N/A':
                                if 'rate' in adj_key:
                                    formatted = f"{value * 100:.1f}%"
                                elif 'allocation' in adj_key:
                                    formatted = f"{value}%"
                                else:
                                    formatted = str(value)
                            else:
                                formatted = 'N/A'

                            row[f'Scenario {i+1}'] = formatted
                        comparison_data.append(row)

                    # Create DataFrame and display
                    # DEFENSIVE FIX: Ensure all rows have same columns (handles edge cases)
                    if comparison_data:
                        expected_columns = set(comparison_data[0].keys())
                        for row in comparison_data:
                            row_columns = set(row.keys())
                            if row_columns != expected_columns:
                                # Add missing columns with 'N/A'
                                for col in expected_columns - row_columns:
                                    row[col] = 'N/A'

                    df = pd.DataFrame(comparison_data)

                    st.dataframe(
                        df,
                        width='stretch',
                        hide_index=True,
                        height=600
                    )

                    st.success("✅ Comparison complete! Scroll to see all metrics.")

                except Exception as table_error:
                    st.error(f"❌ Error building comparison table: {str(table_error)}")
                    print(f"[COMPARISON ERROR] {type(table_error).__name__}: {table_error}")
                    import traceback
                    traceback.print_exc()

                    # Show partial debug info
                    st.warning("📊 Debug info for troubleshooting:")
                    st.write(f"- Number of scenarios: {len(detailed_scenarios)}")
                    for idx, scen in enumerate(detailed_scenarios):
                        st.write(f"- Scenario {idx+1}: {scen.get('name', 'UNNAMED')}")
                        st.write(f"  - Has adjustments: {'adjustments' in scen}")
                        st.write(f"  - Has simulation_results: {'simulation_results' in scen}")

                # WINNER BADGES SECTION
                st.markdown("---")
                st.markdown("### 🏆 Top Performers")

                try:
                    col_w1, col_w2, col_w3 = st.columns(3)

                    # Find winners for key metrics
                    # DEFENSIVE: Filter out scenarios with 'N/A' or invalid final_savings
                    valid_scenarios = []
                    for s in detailed_scenarios:
                        final_savings = s.get('simulation_results', {}).get('final_savings', 'N/A')
                        # Check if it's a valid number (not 'N/A' string and not None)
                        if final_savings != 'N/A' and final_savings is not None and isinstance(final_savings, (int, float)):
                            valid_scenarios.append(s)

                    print(f"[WINNER BADGES] Found {len(valid_scenarios)} valid scenarios out of {len(detailed_scenarios)}")

                    if valid_scenarios:
                        # Best Final Savings
                        best_savings = max(valid_scenarios, key=lambda x: x.get('simulation_results', {}).get('final_savings', 0))
                        with col_w1:
                            st.metric(
                                "🏆 Highest Final Savings",
                                best_savings['name'],
                                f"${best_savings['simulation_results']['final_savings']:,.0f}"
                            )

                        # Best Health Score
                        best_health = max(valid_scenarios, key=lambda x: x.get('simulation_results', {}).get('health_score', 0))
                        with col_w2:
                            st.metric(
                                "💪 Best Financial Health",
                                best_health['name'],
                                f"{best_health['simulation_results']['health_score']}/100"
                            )

                        # Most Years Solvent
                        best_solvent = max(valid_scenarios, key=lambda x: x.get('simulation_results', {}).get('years_solvent', 0))
                        with col_w3:
                            st.metric(
                                "⏳ Most Years Solvent",
                                best_solvent['name'],
                                f"{best_solvent['simulation_results']['years_solvent']} years"
                            )

                except Exception as winner_error:
                    st.warning(f"⚠️ Could not display winner badges: {str(winner_error)}")
                    print(f"[WINNER BADGES ERROR] {type(winner_error).__name__}: {winner_error}")

                # =============================================================================
                # CHARTS & VISUALIZATIONS SECTION
                # =============================================================================

                st.markdown("---")
                st.markdown("### 📊 Visual Analysis")
                st.markdown("Interactive charts to help you compare scenarios at a glance.")

                # Chart 1: Final Savings Comparison (Bar Chart)
                from utils.chart_tooltips import add_chart_help_button
                add_chart_help_button("scenario_comparison_bar")
                st.markdown("#### 💰 Final Savings Comparison")

                try:
                    import plotly.graph_objects as go
                    import plotly.express as px

                    # DEFENSIVE: Re-calculate valid_scenarios if not defined (in case winner badges failed)
                    if 'valid_scenarios' not in locals() or not valid_scenarios:
                        valid_scenarios = []
                        for s in detailed_scenarios:
                            final_savings = s.get('simulation_results', {}).get('final_savings', 'N/A')
                            if final_savings != 'N/A' and final_savings is not None and isinstance(final_savings, (int, float)):
                                valid_scenarios.append(s)
                        print(f"[CHARTS] Re-calculated valid_scenarios: {len(valid_scenarios)} scenarios")

                    # Prepare data for bar chart
                    chart_data = []
                    for scenario in valid_scenarios:
                        chart_data.append({
                            'Scenario': scenario['name'],
                            'Final Savings': scenario['simulation_results']['final_savings']
                        })

                    # Sort by final savings descending
                    chart_data = sorted(chart_data, key=lambda x: x['Final Savings'], reverse=True)

                    # Create bar chart
                    fig1 = go.Figure(data=[
                        go.Bar(
                            x=[d['Scenario'] for d in chart_data],
                            y=[d['Final Savings'] for d in chart_data],
                            marker_color='rgb(55, 83, 109)',
                            text=[f"${d['Final Savings']:,.0f}" for d in chart_data],
                            textposition='outside',
                        )
                    ])

                    fig1.update_layout(
                        title="Final Savings by Scenario",
                        xaxis_title="Scenario",
                        yaxis_title="Final Savings ($)",
                        yaxis_tickformat='$,.0f',
                        height=400,
                        showlegend=False,
                    )

                    st.plotly_chart(fig1, width='stretch')

                except ImportError:
                    st.warning("📊 Plotly not available. Install with: pip install plotly")
                except Exception as e:
                    st.error(f"Error creating chart: {e}")

                # Chart 2: Savings Trajectory Over Time (Line Chart)
                add_chart_help_button("scenario_trajectory_lines")
                st.markdown("#### 📈 Savings Trajectory Over Time")

                try:
                    fig2 = go.Figure()

                    # Add a line for each scenario
                    for scenario in valid_scenarios:
                        df_data = scenario['simulation_results']['df']['data']
                        years = df_data['Year']
                        savings = df_data['Savings_End']

                        fig2.add_trace(go.Scatter(
                            x=years,
                            y=savings,
                            mode='lines+markers',
                            name=scenario['name'],
                            line=dict(width=2),
                            marker=dict(size=6)
                        ))

                    fig2.update_layout(
                        title="Savings Growth Over Time",
                        xaxis_title="Year",
                        yaxis_title="Savings Balance ($)",
                        yaxis_tickformat='$,.0f',
                        height=500,
                        hovermode='x unified',
                        legend=dict(
                            orientation="v",
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=0.01
                        )
                    )

                    st.plotly_chart(fig2, width='stretch')

                except Exception as e:
                    st.error(f"Error creating trajectory chart: {e}")

                # Chart 3: Income vs Expenses Comparison (Grouped Bar)
                add_chart_help_button("scenario_income_expenses")
                st.markdown("#### 💵 First Year Income vs Expenses")

                try:
                    # Get first year income and expenses for each scenario
                    income_expense_data = []
                    for scenario in valid_scenarios:
                        df_data = scenario['simulation_results']['df']['data']
                        # First year data (index 0)
                        total_income = df_data['Total_Income'][0]
                        total_expenses = df_data['Total_Expenses'][0]

                        income_expense_data.append({
                            'Scenario': scenario['name'],
                            'Income': total_income,
                            'Expenses': total_expenses,
                            'Surplus': total_income - total_expenses
                        })

                    # Create grouped bar chart
                    fig3 = go.Figure()

                    scenarios_list = [d['Scenario'] for d in income_expense_data]

                    fig3.add_trace(go.Bar(
                        name='Income',
                        x=scenarios_list,
                        y=[d['Income'] for d in income_expense_data],
                        marker_color='rgb(26, 118, 255)',
                        text=[f"${d['Income']:,.0f}" for d in income_expense_data],
                        textposition='outside',
                    ))

                    fig3.add_trace(go.Bar(
                        name='Expenses',
                        x=scenarios_list,
                        y=[d['Expenses'] for d in income_expense_data],
                        marker_color='rgb(255, 65, 54)',
                        text=[f"${d['Expenses']:,.0f}" for d in income_expense_data],
                        textposition='outside',
                    ))

                    fig3.update_layout(
                        title="Annual Income vs Expenses (First Year)",
                        xaxis_title="Scenario",
                        yaxis_title="Amount ($)",
                        yaxis_tickformat='$,.0f',
                        barmode='group',
                        height=400,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )

                    st.plotly_chart(fig3, width='stretch')

                except Exception as e:
                    st.error(f"Error creating income/expenses chart: {e}")

                # Chart 4: Financial Health Score Comparison (Gauge-style Bar)
                add_chart_help_button("scenario_health_scores")
                st.markdown("#### 🎯 Financial Health Score Comparison")

                try:
                    # Prepare health score data
                    health_data = []
                    for scenario in valid_scenarios:
                        health_score = scenario['simulation_results'].get('health_score', 0)
                        health_data.append({
                            'Scenario': scenario['name'],
                            'Health Score': health_score
                        })

                    # Sort by health score
                    health_data = sorted(health_data, key=lambda x: x['Health Score'], reverse=True)

                    # Create horizontal bar chart with color gradient
                    colors = []
                    for score in [d['Health Score'] for d in health_data]:
                        if score >= 80:
                            colors.append('rgb(34, 139, 34)')  # Green
                        elif score >= 60:
                            colors.append('rgb(255, 215, 0)')  # Gold
                        elif score >= 40:
                            colors.append('rgb(255, 165, 0)')  # Orange
                        else:
                            colors.append('rgb(220, 20, 60)')  # Red

                    fig4 = go.Figure(data=[
                        go.Bar(
                            y=[d['Scenario'] for d in health_data],
                            x=[d['Health Score'] for d in health_data],
                            orientation='h',
                            marker_color=colors,
                            text=[f"{d['Health Score']}/100" for d in health_data],
                            textposition='inside',
                        )
                    ])

                    fig4.update_layout(
                        title="Financial Health Score (0-100)",
                        xaxis_title="Health Score",
                        yaxis_title="Scenario",
                        xaxis=dict(range=[0, 100]),
                        height=max(300, len(health_data) * 60),
                        showlegend=False,
                    )

                    st.plotly_chart(fig4, width='stretch')

                except Exception as e:
                    st.error(f"Error creating health score chart: {e}")

                # =============================================================================
                # API FEEDBACK - Claude AI Chart Explanations
                # =============================================================================
                try:
                    from streamlit_explain_api import inject_explain_visual_system
                    print("[DEBUG] Injecting AI explanation system into Scenario Studio...")
                    inject_explain_visual_system()
                    st.caption("💡 **Click the ❓ button** on any chart above for AI-powered explanations")
                except Exception as e:
                    print(f"[DEBUG] Could not inject explain system: {e}")
                    # Silently fail - not critical

                # =============================================================================
                # EXPORT OPTIONS SECTION
                # =============================================================================

                st.markdown("---")
                st.markdown("### 📥 Export Comparison Results")
                st.markdown("Download your scenario comparison in various formats for sharing or further analysis.")

                col_exp1, col_exp2, col_exp3 = st.columns(3)

                with col_exp1:
                    if st.button("📄 Export to PDF", width='stretch', type="secondary"):
                        try:
                            from io import BytesIO
                            import datetime

                            # Generate PDF export
                            pdf_bytes = export_comparison_to_pdf(detailed_scenarios, base_plan_id)

                            if pdf_bytes:
                                st.download_button(
                                    label="⬇️ Download PDF Report",
                                    data=pdf_bytes,
                                    file_name=f"scenario_comparison_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                    mime="application/pdf",
                                    width='stretch'
                                )
                                st.success("✅ PDF generated! Click Download above.")
                        except ImportError as e:
                            st.error(f"❌ PDF export requires reportlab. Install with: pip install reportlab")
                        except Exception as e:
                            st.error(f"❌ Error generating PDF: {e}")

                with col_exp2:
                    if st.button("📊 Export to Excel", width='stretch', type="secondary"):
                        try:
                            from io import BytesIO
                            import datetime

                            # Generate Excel export
                            excel_bytes = export_comparison_to_excel(detailed_scenarios, base_plan_id)

                            if excel_bytes:
                                st.download_button(
                                    label="⬇️ Download Excel File",
                                    data=excel_bytes,
                                    file_name=f"scenario_comparison_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    width='stretch'
                                )
                                st.success("✅ Excel file generated! Click Download above.")
                        except Exception as e:
                            st.error(f"❌ Error generating Excel: {e}")

                with col_exp3:
                    if st.button("📋 Export to CSV", width='stretch', type="secondary"):
                        try:
                            import datetime

                            # Generate CSV export
                            csv_data = export_comparison_to_csv(detailed_scenarios, base_plan_id)

                            if csv_data:
                                st.download_button(
                                    label="⬇️ Download CSV File",
                                    data=csv_data,
                                    file_name=f"scenario_comparison_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                    mime="text/csv",
                                    width='stretch'
                                )
                                st.success("✅ CSV file generated! Click Download above.")
                        except Exception as e:
                            st.error(f"❌ Error generating CSV: {e}")

            else:
                st.warning("⚠️ Could not load detailed data for selected scenarios.")

    st.markdown("---")
    st.markdown("*🎬 Scenario Studio - Create, simulate, and compare retirement strategies*")
