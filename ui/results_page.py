"""
Family Forecast Results Display Page
==============================
Complete results display for Analysis mode including all charts, metrics,
and analysis features.

Author: Family Forecast Development Team
Last Updated: October 22, 2025
"""

import streamlit as st
from ui.components.top_navigation import render_top_navigation
from financial_utils import display_summary_metrics
from simulation_core import run_simulation
from household_events import build_child_objects, build_inheritances, make_family_cashflows
from monte_carlo import run_simple_monte_carlo
from visualization.charts_basic import show_trajectories, show_health_dashboard
from visualization.charts_advanced import show_monte_carlo, show_sankey
from visualization.timeline import (
    show_timeline,
    show_goal_gauges,
    show_download_options,
    show_detailed_projection_table
)
from visualization.longevity_analysis import show_longevity_analysis
# ⚠️ HEALTHCARE MODULE DISABLED - Uncomment when ready to deploy healthcare features
# from visualization.irmaa_analysis import show_irmaa_analysis
import disclaimers
from utils.comparison_scenarios import save_comparison_scenario


# =============================================================================
# MAIN RESULTS PAGE
# =============================================================================

def show_results_page(nav_state, user_data, financial_data, sim_params):
    """
    Display complete results page with all analysis features

    Args:
        nav_state: Navigation state with features dict
        user_data: User demographic data
        financial_data: Financial data
        sim_params: Simulation parameters
    """
    # Header with logo (medium size)
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image("assets/branding/logo-familyforecast.png", width=100)
    with col_title:
        st.title("📊 Retirement Analysis Results")

    # Ensure sim_params has defaults for all values
    if sim_params is None:
        sim_params = {}
    sim_params.setdefault('tax_rate', 0.25)
    sim_params.setdefault('inflation_rate', 0.03)
    sim_params.setdefault('investment_return_rate', 0.07)
    sim_params.setdefault('simulation_years', 30)
    sim_params.setdefault('mc_iterations', 0)

    # Show disclaimers
    disclaimers.show_simulation_results_disclaimer()

    # Build household events
    children = build_child_objects(st.session_state.get("children_rows", []))  # ✅ FIXED: Pass children_rows argument
    inheritances = build_inheritances(st.session_state.get("inherit_rows", []))  # ✅ FIXED: Pass inherit_rows argument

    # Build family cashflows for Monte Carlo
    from datetime import date
    current_year = date.today().year
    family_cashflows = make_family_cashflows(
        children, inheritances,
        start_year=current_year,
        horizon_end=current_year + sim_params['simulation_years'],
        college_inflation_pct=4.0,
        base_public_in=20000,
        base_public_out=40000,
        base_private=60000
    )

    # Build goal_costs from session state (CRITICAL FIX)
    goal_costs = {}
    goals_list = st.session_state.get('goals_list', [])
    for goal_data in goals_list:
        goal_name = goal_data.get('goal', '').strip()
        goal_amount = goal_data.get('amount', 0)
        goal_year = goal_data.get('year', current_year + 10)
        if goal_name and goal_amount > 0:
            goal_costs[goal_name] = {
                'year': int(goal_year),
                'amount': float(goal_amount)
            }

    if goal_costs:
        st.info(f"🎯 **{len(goal_costs)} goal(s)** will be tracked in simulation")

    # Extract features
    features = nav_state.get('features', {})

    # Run main simulation
    st.subheader("🎯 Running Simulation...")

    with st.spinner("Calculating your retirement trajectory..."):
        results = run_simulation(
            age=user_data.get('age', 35),  # ✅ FIXED: Use .get() with default
            partner_exists=user_data.get('partner_exists', False),  # ✅ FIXED: Use .get() with default
            partner_age=user_data.get('partner_age', user_data.get('age', 35)),  # ✅ FIXED: Safe nested .get()
            total_income=financial_data['total_income'],
            total_expenses=financial_data['total_expenses'],
            combined_financial_assets=financial_data['liquid_assets'],
            primary_residence_value=financial_data.get('primary_residence_value', 0),
            secondary_residence_value=financial_data.get('secondary_residence_value', 0),
            combined_other_assets_total=financial_data.get('other_assets', 0),
            total_liabilities_local=financial_data['total_liabilities'],
            partner_liabilities=0,
            tax_rate=sim_params['tax_rate'],
            inflation_rate=sim_params['inflation_rate'],
            investment_return_rate=sim_params['investment_return_rate'],
            simulation_years=sim_params['simulation_years'],
            mc_iterations=sim_params.get('mc_iterations', 0),
            goal_costs=goal_costs,  # ✅ FIXED: Pass actual goals, not empty dict
            college_inflation_pct=4.0,
            base_public_in=20000,
            base_public_out=40000,
            base_private=60000,
            ira_balance=financial_data.get('ira_balance', 0),
            four01k_403b_balance=financial_data.get('four01k_403b_balance', 0),
            partner_ira_balance=financial_data.get('partner_ira_balance', 0),
            partner_four01k_403b_balance=financial_data.get('partner_four01k_403b_balance', 0),
            monthly_surplus=financial_data.get('monthly_surplus', 0),
            combined_total_liabilities=financial_data['total_liabilities'],
            custom_expenses_total=financial_data.get('custom_expenses_total', 0.0),  # ✅ CRITICAL FIX: Pass custom expenses to simulation
            custom_income_total=financial_data.get('custom_income_total', 0.0)  # ✅ CRITICAL FIX: Pass custom income to simulation
        )

    if not results:
        st.error("❌ Simulation failed. Please check your inputs.")
        return

    st.success("✅ Simulation complete!")

    # =============================================================================
    # SUMMARY METRICS
    # =============================================================================

    if features.get('show_summary_metrics'):
        st.markdown("---")
        st.subheader("📈 Financial Summary")
        try:
            display_summary_metrics(results, sim_params['simulation_years'])
        except Exception as e:
            st.error(f"Summary metrics error: {str(e)}")

    # =============================================================================
    # AI ADVISOR
    # =============================================================================

    if features.get('show_ai_advisor'):
        from ai_advisor import show_ai_consultation
        st.markdown("---")
        with st.expander("💬 Ask AI Advisor — Powered by Claude (Anthropic)", expanded=True):
            try:
                show_ai_consultation(results, user_data, financial_data, sim_params)
            except Exception as e:
                st.error(f"AI advisor temporarily unavailable: {str(e)}")

    # =============================================================================
    # BASIC CHARTS
    # =============================================================================

    if features.get('show_basic_charts'):
        st.markdown("---")
        st.subheader("📊 Savings & Net Worth Trajectories")
        try:
            show_trajectories(results)
        except Exception as e:
            st.error(f"Trajectory chart error: {str(e)}")

        try:
            show_health_dashboard(
                financial_data['liquid_assets'],
                financial_data['total_expenses'],
                financial_data['total_income'],
                financial_data['total_liabilities'],
                results
            )
        except Exception as e:
            st.error(f"Health dashboard error: {str(e)}")

    # =============================================================================
    # TIMELINE
    # =============================================================================

    if features.get('show_timeline'):
        st.markdown("---")
        st.subheader("📅 Retirement Timeline")
        try:
            # Build family_data dict for timeline
            family_timeline_data = {
                'children': st.session_state.get("children_rows", []),
                'inheritances': st.session_state.get("inherit_rows", [])
            }
            show_timeline(results, user_data, family_timeline_data)
        except Exception as e:
            st.error(f"Timeline error: {str(e)}")

        try:
            show_goal_gauges(results)
        except Exception as e:
            st.error(f"Goal gauges error: {str(e)}")

    # =============================================================================
    # MONTE CARLO (ALWAYS ENABLED - 1000 ITERATIONS)
    # =============================================================================

    if features.get('show_monte_carlo'):
        st.markdown("---")
        st.subheader("🎲 Monte Carlo Simulation")
        disclaimers.show_monte_carlo_disclaimer()

        # Monte Carlo runs automatically as part of main simulation (1000 iterations)
        # Just display the results here
        try:
            show_monte_carlo(results)
        except Exception as e:
            st.error(f"Monte Carlo display error: {str(e)}")

    # =============================================================================
    # SANKEY DIAGRAM (TRUSTED USERS)
    # =============================================================================

    if features.get('show_sankey'):
        st.markdown("---")
        st.subheader("💰 Cash Flow Sankey Diagram")
        try:
            show_sankey(results)
        except Exception as e:
            st.error(f"Sankey diagram error: {str(e)}")

    # =============================================================================
    # LONGEVITY ANALYSIS (TRUSTED USERS)
    # =============================================================================

    if features.get('show_longevity_analysis'):
        st.markdown("---")
        try:
            show_longevity_analysis(results, user_data, financial_data)
        except Exception as e:
            st.error(f"Longevity analysis error: {str(e)}")

    # =============================================================================
    # IRMAA ANALYSIS (TRUSTED USERS)
    # =============================================================================
    # ⚠️ HEALTHCARE MODULE DISABLED - Uncomment when ready to deploy healthcare features
    # if features.get('show_irmaa_analysis'):
    #     st.markdown("---")
    #     try:
    #         show_irmaa_analysis(results, user_data, financial_data)
    #     except Exception as e:
    #         st.error(f"IRMAA analysis error: {str(e)}")

    # =============================================================================
    # DETAILED PROJECTION TABLE (TRUSTED USERS)
    # =============================================================================

    if features.get('show_detailed_table'):
        st.markdown("---")
        st.subheader("📋 Detailed Year-by-Year Projection")
        try:
            show_detailed_projection_table(results)
        except Exception as e:
            st.error(f"Detailed table error: {str(e)}")

    # =============================================================================
    # QUICK PLAN COMPARISON (TEMPORAL - Current vs. Past)
    # =============================================================================

    if features.get('show_scenario_comparison'):
        st.markdown("---")
        st.subheader("📊 Quick Plan Comparison")
        st.info("Compare your current plan to a previous snapshot - see how you've progressed!")

        try:
            # Load available snapshots (user snapshots + demo snapshots)
            from utils.snapshot_manager import get_snapshots_index, load_snapshot, get_all_snapshots_with_demos
            index = get_snapshots_index()
            user_snapshots = index.get('snapshots', [])

            # Get all snapshots including demos (for users with no saved data)
            all_snapshots = get_all_snapshots_with_demos()

            if len(all_snapshots) < 2:
                st.warning("⚠️ You need at least 2 saved snapshots to compare plans. Save your current plan first!")
            else:
                # Show demo data message if user has no snapshots
                if len(user_snapshots) == 0:
                    st.info("""
                    💡 **You're viewing demo data!**

                    These are sample retirement plans to show you how the comparison feature works.
                    Complete YOUR INTAKE to see YOUR real comparison!
                    """)
                    if st.button("📝 Go to INTAKE to create YOUR plan", key="demo_goto_intake_btn"):
                        st.markdown(
                            '<meta http-equiv="refresh" content="0;url=https://intake.familyforecast.ai/intake">',
                            unsafe_allow_html=True
                        )
                        st.stop()

                snapshots = all_snapshots
                # Build dropdown options (exclude current snapshot)
                current_id = index.get('current_snapshot_id')
                comparison_options = []

                for snap in snapshots:
                    if snap['id'] != current_id:
                        # Format: "Name (Nov 15, 2025)" or "Name" for demos
                        from datetime import datetime
                        try:
                            created_dt = datetime.fromisoformat(snap.get('created', '2025-01-01T00:00:00'))
                            formatted_date = created_dt.strftime("%b %d, %Y %I:%M %p")
                            option_label = f"{snap['name']} ({formatted_date})"
                        except:
                            option_label = snap['name']

                        comparison_options.append({
                            'label': option_label,
                            'id': snap['id'],
                            'name': snap['name'],
                            'created': snap.get('created', '2025-01-01T00:00:00'),
                            'is_demo': snap.get('is_demo', False)
                        })

                # Sort by date (newest first)
                comparison_options.sort(key=lambda x: x['created'], reverse=True)

                if not comparison_options:
                    st.warning("⚠️ No previous snapshots found. Your current snapshot is the only one saved.")
                else:
                    # Dropdown selector
                    selected_label = st.selectbox(
                        "Compare your current plan to:",
                        options=[opt['label'] for opt in comparison_options],
                        help="Select a previous snapshot to compare against your current results"
                    )

                    # Get selected snapshot ID
                    selected_snapshot = next(opt for opt in comparison_options if opt['label'] == selected_label)

                    # Optional quick adjustment (collapsed by default)
                    with st.expander("🔧 Optional: Add One Quick Adjustment", expanded=False):
                        st.caption("Want to test a small change on your CURRENT plan? Select one adjustment below.")

                        adjustment_type = st.radio(
                            "Quick Adjustment",
                            ["None - Compare as-is",
                             "Delay retirement by 2 years",
                             "Increase income by 10%",
                             "Reduce expenses by 15%",
                             "Increase savings rate by 5%"],
                            index=0,
                            help="This adjustment will be applied to your CURRENT results for comparison"
                        )

                    # Compare button
                    if st.button("🚀 Compare Now", type="primary", key="quick_compare_btn"):
                        with st.spinner("Loading snapshot and comparing..."):
                            # Load the selected past snapshot
                            past_snapshot_data = load_snapshot(selected_snapshot['id'])

                            if not past_snapshot_data:
                                st.error(f"❌ Could not load snapshot: {selected_snapshot['name']}")
                            else:
                                # Run simulation on past snapshot data to get comparable results
                                past_user_data = past_snapshot_data.get('user_data', {})
                                past_financial_data = past_snapshot_data.get('financial_data', {})
                                past_sim_params = past_snapshot_data.get('sim_params', sim_params)

                                # Run simulation for past snapshot
                                past_results = run_simulation(
                                    age=past_user_data.get('age', user_data.get('age', 35)),
                                    partner_exists=past_user_data.get('partner_exists', user_data.get('partner_exists', False)),
                                    partner_age=past_user_data.get('partner_age', user_data.get('partner_age', 35)),
                                    total_income=past_financial_data.get('total_income', financial_data['total_income']),
                                    total_expenses=past_financial_data.get('total_expenses', financial_data['total_expenses']),
                                    combined_financial_assets=past_financial_data.get('liquid_assets', financial_data['liquid_assets']),
                                    primary_residence_value=past_financial_data.get('primary_residence_value', 0),
                                    secondary_residence_value=past_financial_data.get('secondary_residence_value', 0),
                                    combined_other_assets_total=past_financial_data.get('other_assets', 0),
                                    total_liabilities_local=past_financial_data.get('total_liabilities', financial_data['total_liabilities']),
                                    partner_liabilities=0,
                                    tax_rate=past_sim_params.get('tax_rate', sim_params['tax_rate']),
                                    inflation_rate=past_sim_params.get('inflation_rate', sim_params['inflation_rate']),
                                    investment_return_rate=past_sim_params.get('investment_return_rate', sim_params['investment_return_rate']),
                                    simulation_years=past_sim_params.get('simulation_years', sim_params['simulation_years']),
                                    mc_iterations=0,
                                    goal_costs={},
                                    college_inflation_pct=4.0,
                                    base_public_in=20000,
                                    base_public_out=40000,
                                    base_private=60000,
                                    ira_balance=past_financial_data.get('ira_balance', 0),
                                    four01k_403b_balance=past_financial_data.get('four01k_403b_balance', 0),
                                    partner_ira_balance=past_financial_data.get('partner_ira_balance', 0),
                                    partner_four01k_403b_balance=past_financial_data.get('partner_four01k_403b_balance', 0),
                                    monthly_surplus=past_financial_data.get('monthly_surplus', 0),
                                    combined_total_liabilities=past_financial_data.get('total_liabilities', financial_data['total_liabilities'])
                                )

                                # Apply optional adjustment to CURRENT results
                                current_results = results.copy()
                                adjustment_label = ""

                                if adjustment_type == "Delay retirement by 2 years":
                                    # Re-run current simulation with +2 years
                                    adjusted_sim_years = sim_params['simulation_years'] + 2
                                    current_results = run_simulation(
                                        age=user_data.get('age', 35),
                                        partner_exists=user_data.get('partner_exists', False),
                                        partner_age=user_data.get('partner_age', user_data.get('age', 35)),
                                        total_income=financial_data['total_income'],
                                        total_expenses=financial_data['total_expenses'],
                                        combined_financial_assets=financial_data['liquid_assets'],
                                        primary_residence_value=financial_data.get('primary_residence_value', 0),
                                        secondary_residence_value=financial_data.get('secondary_residence_value', 0),
                                        combined_other_assets_total=financial_data.get('other_assets', 0),
                                        total_liabilities_local=financial_data['total_liabilities'],
                                        partner_liabilities=0,
                                        tax_rate=sim_params['tax_rate'],
                                        inflation_rate=sim_params['inflation_rate'],
                                        investment_return_rate=sim_params['investment_return_rate'],
                                        simulation_years=adjusted_sim_years,
                                        mc_iterations=0,
                                        goal_costs={},
                                        college_inflation_pct=4.0,
                                        base_public_in=20000,
                                        base_public_out=40000,
                                        base_private=60000,
                                        ira_balance=financial_data.get('ira_balance', 0),
                                        four01k_403b_balance=financial_data.get('four01k_403b_balance', 0),
                                        partner_ira_balance=financial_data.get('partner_ira_balance', 0),
                                        partner_four01k_403b_balance=financial_data.get('partner_four01k_403b_balance', 0),
                                        monthly_surplus=financial_data.get('monthly_surplus', 0),
                                        combined_total_liabilities=financial_data['total_liabilities'],
                                        custom_expenses_total=financial_data.get('custom_expenses_total', 0.0),
                                        custom_income_total=financial_data.get('custom_income_total', 0.0)
                                    )
                                    adjustment_label = " (+ Delay 2 yrs)"
                                elif adjustment_type == "Increase income by 10%":
                                    adjusted_income = financial_data['total_income'] * 1.10
                                    current_results = run_simulation(
                                        age=user_data.get('age', 35),
                                        partner_exists=user_data.get('partner_exists', False),
                                        partner_age=user_data.get('partner_age', user_data.get('age', 35)),
                                        total_income=adjusted_income,
                                        total_expenses=financial_data['total_expenses'],
                                        combined_financial_assets=financial_data['liquid_assets'],
                                        primary_residence_value=financial_data.get('primary_residence_value', 0),
                                        secondary_residence_value=financial_data.get('secondary_residence_value', 0),
                                        combined_other_assets_total=financial_data.get('other_assets', 0),
                                        total_liabilities_local=financial_data['total_liabilities'],
                                        partner_liabilities=0,
                                        tax_rate=sim_params['tax_rate'],
                                        inflation_rate=sim_params['inflation_rate'],
                                        investment_return_rate=sim_params['investment_return_rate'],
                                        simulation_years=sim_params['simulation_years'],
                                        mc_iterations=0,
                                        goal_costs={},
                                        college_inflation_pct=4.0,
                                        base_public_in=20000,
                                        base_public_out=40000,
                                        base_private=60000,
                                        ira_balance=financial_data.get('ira_balance', 0),
                                        four01k_403b_balance=financial_data.get('four01k_403b_balance', 0),
                                        partner_ira_balance=financial_data.get('partner_ira_balance', 0),
                                        partner_four01k_403b_balance=financial_data.get('partner_four01k_403b_balance', 0),
                                        monthly_surplus=financial_data.get('monthly_surplus', 0),
                                        combined_total_liabilities=financial_data['total_liabilities'],
                                        custom_expenses_total=financial_data.get('custom_expenses_total', 0.0),
                                        custom_income_total=financial_data.get('custom_income_total', 0.0)
                                    )
                                    adjustment_label = " (+ 10% Income)"
                                elif adjustment_type == "Reduce expenses by 15%":
                                    adjusted_expenses = financial_data['total_expenses'] * 0.85
                                    current_results = run_simulation(
                                        age=user_data.get('age', 35),
                                        partner_exists=user_data.get('partner_exists', False),
                                        partner_age=user_data.get('partner_age', user_data.get('age', 35)),
                                        total_income=financial_data['total_income'],
                                        total_expenses=adjusted_expenses,
                                        combined_financial_assets=financial_data['liquid_assets'],
                                        primary_residence_value=financial_data.get('primary_residence_value', 0),
                                        secondary_residence_value=financial_data.get('secondary_residence_value', 0),
                                        combined_other_assets_total=financial_data.get('other_assets', 0),
                                        total_liabilities_local=financial_data['total_liabilities'],
                                        partner_liabilities=0,
                                        tax_rate=sim_params['tax_rate'],
                                        inflation_rate=sim_params['inflation_rate'],
                                        investment_return_rate=sim_params['investment_return_rate'],
                                        simulation_years=sim_params['simulation_years'],
                                        mc_iterations=0,
                                        goal_costs={},
                                        college_inflation_pct=4.0,
                                        base_public_in=20000,
                                        base_public_out=40000,
                                        base_private=60000,
                                        ira_balance=financial_data.get('ira_balance', 0),
                                        four01k_403b_balance=financial_data.get('four01k_403b_balance', 0),
                                        partner_ira_balance=financial_data.get('partner_ira_balance', 0),
                                        partner_four01k_403b_balance=financial_data.get('partner_four01k_403b_balance', 0),
                                        monthly_surplus=financial_data.get('monthly_surplus', 0),
                                        combined_total_liabilities=financial_data['total_liabilities'],
                                        custom_expenses_total=financial_data.get('custom_expenses_total', 0.0),
                                        custom_income_total=financial_data.get('custom_income_total', 0.0)
                                    )
                                    adjustment_label = " (- 15% Expenses)"
                                elif adjustment_type == "Increase savings rate by 5%":
                                    # Increase monthly surplus by 5% of income
                                    extra_savings = financial_data['total_income'] * 0.05 / 12
                                    adjusted_surplus = financial_data.get('monthly_surplus', 0) + extra_savings
                                    current_results = run_simulation(
                                        age=user_data.get('age', 35),
                                        partner_exists=user_data.get('partner_exists', False),
                                        partner_age=user_data.get('partner_age', user_data.get('age', 35)),
                                        total_income=financial_data['total_income'],
                                        total_expenses=financial_data['total_expenses'],
                                        combined_financial_assets=financial_data['liquid_assets'],
                                        primary_residence_value=financial_data.get('primary_residence_value', 0),
                                        secondary_residence_value=financial_data.get('secondary_residence_value', 0),
                                        combined_other_assets_total=financial_data.get('other_assets', 0),
                                        total_liabilities_local=financial_data['total_liabilities'],
                                        partner_liabilities=0,
                                        tax_rate=sim_params['tax_rate'],
                                        inflation_rate=sim_params['inflation_rate'],
                                        investment_return_rate=sim_params['investment_return_rate'],
                                        simulation_years=sim_params['simulation_years'],
                                        mc_iterations=0,
                                        goal_costs={},
                                        college_inflation_pct=4.0,
                                        base_public_in=20000,
                                        base_public_out=40000,
                                        base_private=60000,
                                        ira_balance=financial_data.get('ira_balance', 0),
                                        four01k_403b_balance=financial_data.get('four01k_403b_balance', 0),
                                        partner_ira_balance=financial_data.get('partner_ira_balance', 0),
                                        partner_four01k_403b_balance=financial_data.get('partner_four01k_403b_balance', 0),
                                        monthly_surplus=adjusted_surplus,
                                        combined_total_liabilities=financial_data['total_liabilities'],
                                        custom_expenses_total=financial_data.get('custom_expenses_total', 0.0),
                                        custom_income_total=financial_data.get('custom_income_total', 0.0)
                                    )
                                    adjustment_label = " (+ 5% Savings)"

                                if past_results and current_results:
                                    st.success("✅ Comparison complete!")

                                    # Store for potential save (optional future feature)
                                    st.session_state['last_temporal_comparison'] = {
                                        'past_snapshot_id': selected_snapshot['id'],
                                        'past_snapshot_name': selected_snapshot['name'],
                                        'adjustment_type': adjustment_type,
                                        'current_results': current_results,
                                        'past_results': past_results
                                    }

                                    # Show comparison metrics with deltas
                                    st.markdown("### 📈 Your Progress")

                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown(f"#### 📅 {selected_snapshot['name']}")
                                        st.caption("Previous Snapshot")
                                        st.metric("Final Savings", f"${past_results['final_savings']:,.0f}")
                                        st.metric("Final Net Worth", f"${past_results['final_net_worth']:,.0f}")
                                        st.metric("Years Solvent", f"{past_results['years_solvent']}")
                                        st.metric("Health Score", f"{past_results.get('health_score', 0)}/100")

                                    with col2:
                                        st.markdown(f"#### 🎯 Current Plan{adjustment_label}")
                                        st.caption("Your current results")

                                        # Calculate deltas
                                        delta_savings = current_results['final_savings'] - past_results['final_savings']
                                        delta_nw = current_results['final_net_worth'] - past_results['final_net_worth']
                                        delta_years = current_results['years_solvent'] - past_results['years_solvent']
                                        delta_health = current_results.get('health_score', 0) - past_results.get('health_score', 0)

                                        st.metric(
                                            "Final Savings",
                                            f"${current_results['final_savings']:,.0f}",
                                            delta=f"${delta_savings:+,.0f}",
                                            delta_color="normal"
                                        )
                                        st.metric(
                                            "Final Net Worth",
                                            f"${current_results['final_net_worth']:,.0f}",
                                            delta=f"${delta_nw:+,.0f}",
                                            delta_color="normal"
                                        )
                                        st.metric(
                                            "Years Solvent",
                                            f"{current_results['years_solvent']}",
                                            delta=f"{delta_years:+d} years",
                                            delta_color="normal"
                                        )
                                        st.metric(
                                            "Health Score",
                                            f"{current_results.get('health_score', 0)}/100",
                                            delta=f"{delta_health:+d} pts",
                                            delta_color="normal"
                                        )

                                    # Summary message
                                    if delta_savings > 0 and delta_years >= 0:
                                        st.success(f"🎉 **Great progress!** Your plan improved by ${delta_savings:,.0f} in final savings!")
                                    elif delta_savings < 0:
                                        st.warning(f"⚠️ Your final savings decreased by ${abs(delta_savings):,.0f}. Consider reviewing your plan.")
                                    else:
                                        st.info("📊 Your plan is stable. Minor changes detected.")

                                    # Comparison chart
                                    import plotly.graph_objects as go
                                    fig = go.Figure()
                                    fig.add_trace(go.Scatter(
                                        x=past_results['df']['Year'],
                                        y=past_results['df']['Savings_End'],
                                        mode='lines',
                                        name=f'{selected_snapshot["name"]}',
                                        line=dict(color='#FF6B6B', width=3, dash='dash')
                                    ))
                                    fig.add_trace(go.Scatter(
                                        x=current_results['df']['Year'],
                                        y=current_results['df']['Savings_End'],
                                        mode='lines',
                                        name=f'Current Plan{adjustment_label}',
                                        line=dict(color='#4ECDC4', width=3)
                                    ))
                                    fig.update_layout(
                                        title="Savings Trajectory: Past vs. Current",
                                        xaxis_title="Year",
                                        yaxis_title="Savings ($)",
                                        yaxis_tickformat='$,.0f',
                                        height=450,
                                        hovermode='x unified',
                                        legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="center",
                                            x=0.5
                                        )
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                                else:
                                    st.error("❌ Could not generate comparison results")

        except Exception as e:
            st.error(f"Quick comparison error: {str(e)}")
            import traceback
            traceback.print_exc()

        # =============================================================================
        # SCENARIO STUDIO UPSELL (Soft + Hard)
        # =============================================================================
        st.markdown("---")
        st.info("💡 **Want deeper insights?** Explore **Scenario Studio** for advanced multi-scenario planning")

        with st.expander("📖 What is Scenario Studio?", expanded=False):
            st.markdown("### 🎯 Compare Multiple Future Strategies")

            st.markdown("""
            **Example: Planning for Early Retirement**

            With Scenario Studio, you can compare 3-4 different retirement approaches side-by-side:
            """)

            # Visual example
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("""
                **📊 Scenario 1: Conservative**
                - Retire at 67
                - 6% return
                - Low risk tolerance
                - Result: **$2.1M**
                """)

            with col2:
                st.markdown("""
                **📊 Scenario 2: Optimistic**
                - Retire at 65
                - 8% return
                - Moderate risk
                - Result: **$2.3M**
                """)

            with col3:
                st.markdown("""
                **📊 Scenario 3: Aggressive**
                - Retire at 62
                - 10% return
                - Higher risk
                - Result: **$1.9M**
                """)

            st.success("➜ See all scenarios side-by-side with detailed comparison tables and charts!")

            # Features list
            st.markdown("### ✨ What's Included in Scenario Studio:")
            st.markdown("""
            - **30+ adjustable parameters** per scenario (income, expenses, investments, timing, accounts, real estate)
            - **Professional templates** (Conservative, Optimistic, Custom scenarios)
            - **Export capabilities** (PDF, Excel, CSV reports)
            - **Save unlimited scenarios** for future reference
            - **Advanced visualizations** (comparison tables, bar charts, trajectory lines, winner badges)
            - **Side-by-side comparison** of up to 4 scenarios at once
            """)

            # Soft CTA button (no pricing - just educational)
            st.markdown("---")
            if st.button("🚀 Try Scenario Studio", key="upsell_studio_btn"):
                st.session_state.current_mode = "scenario_studio"
                st.session_state.mode_selected = True
                st.rerun()

        # =============================================================================
        # SOCIAL SECURITY OPTIMIZER CROSS-LINK
        # =============================================================================
        st.markdown("---")
        st.info("🏛️ **Optimize your Social Security claiming strategy** for maximum lifetime benefits")

        with st.expander("💡 Why Social Security Timing Matters", expanded=False):
            st.markdown("""
            ### 📊 The Power of Delayed Claiming

            Claiming Social Security at the right age can mean **tens of thousands of dollars** more in lifetime benefits!

            **Example:**
            - **Age 62**: $1,800/month = $21,600/year
            - **Age 67 (FRA)**: $2,500/month = $30,000/year
            - **Age 70**: $3,100/month = $37,200/year

            **Lifetime difference can exceed $100,000+!**

            ### 🎯 What You'll Learn:
            - Your optimal claiming age based on life expectancy
            - Break-even analysis (when delayed claiming pays off)
            - Spousal optimization strategies
            - How to apply your SS income to your retirement plan
            """)

            st.markdown("---")
            if st.button("🏛️ Open Social Security Optimizer", key="go_to_ss_optimizer"):
                st.session_state.current_mode = "social_security"
                st.session_state.mode_selected = True
                st.rerun()

    # =============================================================================
    # OLD SAVE COMPARISON SCENARIO (DEPRECATED - keeping for backward compatibility)
    # =============================================================================
    # Only show if a comparison was run and data exists in session state
    if 'last_comparison_adjustments' in st.session_state and 'last_comparison_results' in st.session_state:
        st.markdown("---")

        with st.expander("💾 Save This Comparison Scenario", expanded=False):

            # CHECK FOR SUCCESS MESSAGE FROM PREVIOUS SAVE (after reload)
            if "comparison_save_success" in st.session_state:
                print("[DEBUG SAVE] ✓ Found success message in session state")
                success_data = st.session_state.comparison_save_success
                st.success(f"✅ Comparison saved: {success_data['name']}")
                st.balloons()
                st.info(f"📊 Comparison ID: `{success_data['id']}`\n\nYou can now load this comparison from the sidebar.")
                # Clear the flag so it doesn't show again
                del st.session_state.comparison_save_success

            st.markdown("""
            Save this comparison to review later or compare with other scenarios.
            Only your adjustments are saved (not your full plan data).
            """)

            # Get adjustment data from session state
            adjustments_data = st.session_state['last_comparison_adjustments']
            comp_results = st.session_state['last_comparison_results']

            # WRAP IN FORM to prevent auto-reload
            with st.form(key="save_comparison_form", clear_on_submit=False):
                col1, col2 = st.columns([2, 1])

                with col1:
                    comparison_name = st.text_input(
                        "Comparison Name",
                        placeholder="e.g., Retire at 67, Save 10% More, Lower Expenses",
                        help="Give this comparison a memorable name"
                    )

                    comparison_description = st.text_area(
                        "Description (Optional)",
                        placeholder="Describe what makes this scenario different...",
                        help="Add notes about this comparison",
                        height=100
                    )

                with col2:
                    st.markdown("**Current Adjustments:**")
                    try:
                        st.caption(f"Income: ${adjustments_data['adj_income']:,.0f}")
                        st.caption(f"Expenses: ${adjustments_data['adj_expenses']:,.0f}")
                        st.caption(f"Return Rate: {adjustments_data['adj_return'] * 100:.1f}%")
                        st.caption(f"Inflation: {adjustments_data['adj_inflation'] * 100:.1f}%")
                    except Exception as e:
                        st.error(f"Error displaying adjustments: {e}")

                # FORM SUBMIT BUTTON (prevents auto-reload)
                save_submitted = st.form_submit_button(
                    "💾 Save Comparison",
                    type="primary",
                    use_container_width=True
                )

            # ONLY PROCESS when button is ACTUALLY CLICKED
            if save_submitted:

                if not comparison_name:
                    st.error("⚠️ Please enter a name for this comparison")
                else:
                    # Get current base plan ID
                    try:
                        from utils.snapshot_manager import get_snapshots_index

                        index = get_snapshots_index()

                        current_plan_id = index.get('current_snapshot_id')
                    except Exception as e:
                        st.error(f"Error getting plan ID: {e}")
                        current_plan_id = None

                    if not current_plan_id:
                        st.error("⚠️ No base plan found. Please save a base plan first in INTAKE mode.")
                    else:
                        # Build adjustments dict from session state
                        try:
                            adjustments = {
                                "adjusted_income": float(adjustments_data['adj_income']),
                                "adjusted_expenses": float(adjustments_data['adj_expenses']),
                                "adjusted_return_rate": float(adjustments_data['adj_return']),
                                "adjusted_inflation_rate": float(adjustments_data['adj_inflation'])
                            }
                        except Exception as e:
                            st.error(f"Error building adjustments: {e}")
                            adjustments = None

                        if adjustments:
                            # Build simulation results (with error handling)
                            simulation_results = {}
                            try:
                                simulation_results = {
                                    "final_savings": comp_results.get('final_savings', 0),
                                    "final_net_worth": comp_results.get('final_net_worth', 0),
                                    "years_solvent": comp_results.get('years_solvent', 0),
                                    "health_score": comp_results.get('health_score', 0)
                                }
                            except Exception as result_err:
                                simulation_results = {}

                            # Save comparison scenario
                            try:
                                from utils.comparison_scenarios import save_comparison_scenario

                                comparison_id = save_comparison_scenario(
                                    base_plan_id=current_plan_id,
                                    name=comparison_name,
                                    description=comparison_description or "",
                                    adjustments=adjustments,
                                    simulation_results=simulation_results
                                )

                                print(f"[DEBUG SAVE] ✓ save_comparison_scenario returned: {comparison_id}")

                                if comparison_id:
                                    print(f"[DEBUG SAVE] ===== SUCCESS! Comparison ID: {comparison_id} =====")

                                    # STORE SUCCESS IN SESSION STATE (survives reload!)
                                    st.session_state.comparison_save_success = {
                                        "name": comparison_name,
                                        "id": comparison_id
                                    }
                                    print("[DEBUG SAVE] ✓ Stored success message in session state")

                                    # Force a rerun to show the success message
                                    print("[DEBUG SAVE] ✓ Triggering rerun to display success message")
                                    st.rerun()

                                else:
                                    print(f"[DEBUG SAVE] ERROR: save_comparison_scenario returned empty/None")
                                    st.error("❌ Failed to save comparison. Please try again.")

                            except Exception as e:
                                print("="*60)
                                print(f"[DEBUG SAVE] ===== SAVE FAILED WITH EXCEPTION =====")
                                print(f"[DEBUG SAVE ERROR] Exception: {e}")
                                print(f"[DEBUG SAVE ERROR] Exception type: {type(e)}")
                                print("="*60)
                                import traceback
                                traceback.print_exc()
                                st.error(f"❌ Error saving comparison: {e}")
                        else:
                            print("[DEBUG SAVE] ERROR: adjustments is None, skipping save")
                            st.error("Cannot save: adjustments could not be built")

    # =============================================================================
    # INJECT CHART EXPLANATION BUTTONS
    # =============================================================================
    # CRITICAL: Inject AFTER all charts are rendered so JavaScript can find them!
    print("[DEBUG] About to inject chart explanation system...")
    try:
        # Use the OLD WORKING version (with Flask API)
        from streamlit_explain_api import inject_explain_visual_system
        print("[DEBUG] Successfully imported inject_explain_visual_system from OLD file")
        inject_explain_visual_system()
        print("[DEBUG] inject_explain_visual_system() completed")
    except Exception as e:
        print(f"[DEBUG] Exception caught: {str(e)}")
        st.error(f"Chart explanation system error: {str(e)}")

    # =============================================================================
    # DOWNLOAD OPTIONS
    # =============================================================================

    st.markdown("---")
    try:
        show_download_options(results)
    except Exception as e:
        st.error(f"Download options error: {str(e)}")

    # =============================================================================
    # HISTORICAL SNAPSHOT - Save current plan for future comparison
    # =============================================================================

    st.markdown("---")
    st.subheader("📸 Save Historical Snapshot")
    st.markdown("Track your progress over time by saving snapshots quarterly or yearly.")

    col1, col2 = st.columns([3, 1])

    with col1:
        snapshot_name = st.text_input(
            "Snapshot Name",
            value=f"Snapshot {datetime.now().strftime('%B %Y')}",
            help="Give this snapshot a memorable name",
            key="snapshot_name_input"
        )

        snapshot_notes = st.text_area(
            "Notes (Optional)",
            placeholder="E.g., 'After 10% raise' or 'Post home purchase'",
            help="Add context about what changed since your last snapshot",
            key="snapshot_notes_input"
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("💾 Save Snapshot", use_container_width=True, key="save_snapshot_btn"):
            try:
                from utils.historical_snapshots import save_historical_snapshot
                from datetime import datetime

                # Collect current user data
                user_data = {
                    "name": st.session_state.get("user_name", ""),
                    "age": st.session_state.get("current_age", 0),
                    "retirement_age": st.session_state.get("retirement_age", 67),
                    "life_expectancy": st.session_state.get("life_expectancy", 85),
                    "income": st.session_state.get("annual_income", 0),
                    "expenses": st.session_state.get("monthly_expenses", 0) * 12,
                    "savings": st.session_state.get("current_savings", 0),
                    "contributions": st.session_state.get("annual_contribution", 0),
                }

                # Collect simulation results
                simulation_results = {
                    "success_rate": results.get("success_rate", 0),
                    "median_final_balance": results.get("median_final_balance", 0),
                    "years_of_solvency": results.get("years_of_solvency", 0),
                    "final_age": results.get("final_age", 85),
                    "total_years_simulated": results.get("total_years_simulated", 0),
                }

                # Save snapshot
                snapshot_id = save_historical_snapshot(
                    user_data,
                    simulation_results,
                    snapshot_name,
                    snapshot_notes
                )

                st.success(f"✅ Snapshot saved successfully! ID: {snapshot_id}")
                st.info("💡 Visit **Historical Tracking** from the main menu to compare your progress over time!")
                st.balloons()

            except Exception as e:
                st.error(f"❌ Failed to save snapshot: {str(e)}")


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("✅ Family Forecast Results Page Module")
    print("Functions: show_results_page")
