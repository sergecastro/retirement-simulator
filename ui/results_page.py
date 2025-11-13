"""
Family Forecast Results Display Page
==============================
Complete results display for Analysis mode including all charts, metrics,
and analysis features.

Author: Family Forecast Development Team
Last Updated: October 22, 2025
"""

import streamlit as st
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
            combined_total_liabilities=financial_data['total_liabilities']
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
    # SCENARIO COMPARISON (TRUSTED USERS)
    # =============================================================================

    if features.get('show_scenario_comparison'):
        st.markdown("---")
        st.subheader("🔀 Scenario Comparison Tool")
        st.info("Compare different financial scenarios side-by-side")

        try:
            with st.expander("⚙️ Adjust Parameters for Comparison", expanded=True):
                # Use st.form to prevent app reboot on slider changes
                with st.form("scenario_comparison_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        adj_income = st.number_input(
                            "Adjusted Annual Income",
                            min_value=0.0,
                            max_value=10000000.0,
                            value=float(financial_data['total_income']),
                            step=5000.0
                        )
                        adj_expenses = st.number_input(
                            "Adjusted Annual Expenses",
                            min_value=0.0,
                            max_value=10000000.0,
                            value=float(financial_data['total_expenses']),
                            step=5000.0
                        )

                    with col2:
                        # Safety check for sim_params values
                        return_rate = sim_params.get('investment_return_rate')
                        if return_rate is None:
                            return_rate = 0.07

                        inflation = sim_params.get('inflation_rate')
                        if inflation is None:
                            inflation = 0.03

                        adj_return = st.slider(
                            "Adjusted Investment Return (%)",
                            min_value=0.0,
                            max_value=15.0,
                            value=float(return_rate * 100),
                            step=0.5
                        ) / 100
                        adj_inflation = st.slider(
                            "Adjusted Inflation Rate (%)",
                            min_value=0.0,
                            max_value=10.0,
                            value=float(inflation * 100),
                            step=0.5
                        ) / 100

                    # Submit button for the form
                    submitted = st.form_submit_button("📊 Run Comparison", type="primary")

                if submitted:
                    with st.spinner("Running comparison..."):
                        # Build adjusted parameters
                        adjusted_financial_data = financial_data.copy()
                        adjusted_financial_data['total_income'] = adj_income
                        adjusted_financial_data['total_expenses'] = adj_expenses

                        adjusted_sim_params = sim_params.copy()
                        adjusted_sim_params['investment_return_rate'] = adj_return
                        adjusted_sim_params['inflation_rate'] = adj_inflation

                        # Run adjusted simulation
                        comp_results = run_simulation(
                            age=user_data.get('age', 35),
                            partner_exists=user_data.get('partner_exists', False),
                            partner_age=user_data.get('partner_age', user_data.get('age', 35)),
                            total_income=adjusted_financial_data['total_income'],
                            total_expenses=adjusted_financial_data['total_expenses'],
                            combined_financial_assets=adjusted_financial_data['liquid_assets'],
                            primary_residence_value=adjusted_financial_data.get('primary_residence_value', 0),
                            secondary_residence_value=adjusted_financial_data.get('secondary_residence_value', 0),
                            combined_other_assets_total=adjusted_financial_data.get('other_assets', 0),
                            total_liabilities_local=adjusted_financial_data['total_liabilities'],
                            partner_liabilities=0,
                            tax_rate=adjusted_sim_params['tax_rate'],
                            inflation_rate=adjusted_sim_params['inflation_rate'],
                            investment_return_rate=adjusted_sim_params['investment_return_rate'],
                            simulation_years=adjusted_sim_params['simulation_years'],
                            mc_iterations=0,
                            goal_costs={},
                            college_inflation_pct=4.0,
                            base_public_in=20000,
                            base_public_out=40000,
                            base_private=60000,
                            ira_balance=adjusted_financial_data.get('ira_balance', 0),
                            four01k_403b_balance=adjusted_financial_data.get('four01k_403b_balance', 0),
                            partner_ira_balance=adjusted_financial_data.get('partner_ira_balance', 0),
                            partner_four01k_403b_balance=adjusted_financial_data.get('partner_four01k_403b_balance', 0),
                            monthly_surplus=adjusted_financial_data.get('monthly_surplus', 0),
                            combined_total_liabilities=adjusted_financial_data['total_liabilities']
                        )

                        if comp_results:
                            st.success("✅ Comparison complete!")

                            # Show comparison metrics
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("#### Base Scenario")
                                st.metric("Final Savings", f"${results['final_savings']:,.0f}")
                                st.metric("Final Net Worth", f"${results['final_net_worth']:,.0f}")
                                st.metric("Years Solvent", f"{results['years_solvent']}")
                            with col2:
                                st.markdown("#### Adjusted Scenario")
                                delta_savings = comp_results['final_savings'] - results['final_savings']
                                delta_nw = comp_results['final_net_worth'] - results['final_net_worth']
                                delta_years = comp_results['years_solvent'] - results['years_solvent']
                                st.metric("Final Savings", f"${comp_results['final_savings']:,.0f}",
                                         delta=f"${delta_savings:,.0f}")
                                st.metric("Final Net Worth", f"${comp_results['final_net_worth']:,.0f}",
                                         delta=f"${delta_nw:,.0f}")
                                st.metric("Years Solvent", f"{comp_results['years_solvent']}",
                                         delta=f"{delta_years:+d} years")

                            # Comparison chart
                            import plotly.graph_objects as go
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=results['df']['Year'],
                                y=results['df']['Savings_End'],
                                mode='lines',
                                name='Base Scenario',
                                line=dict(color='blue', width=3)
                            ))
                            fig.add_trace(go.Scatter(
                                x=comp_results['df']['Year'],
                                y=comp_results['df']['Savings_End'],
                                mode='lines',
                                name='Adjusted Scenario',
                                line=dict(color='red', width=3, dash='dash')
                            ))
                            fig.update_layout(
                                title="Savings Trajectory Comparison",
                                xaxis_title="Year",
                                yaxis_title="Savings ($)",
                                height=500
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            # =================================================================
                            # SAVE COMPARISON SCENARIO SECTION (Sub-Phase 2A)
                            # =================================================================
                            st.markdown("---")
                            with st.expander("💾 Save This Comparison Scenario", expanded=False):
                                st.markdown("""
                                Save this comparison to review later or compare with other scenarios.
                                Only your adjustments are saved (not your full plan data).
                                """)

                                # WRAP IN FORM to prevent auto-reload
                                with st.form("save_comparison_form", clear_on_submit=False):
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
                                        st.caption(f"Income: ${adj_income:,.0f}")
                                        st.caption(f"Expenses: ${adj_expenses:,.0f}")
                                        st.caption(f"Return Rate: {adj_return * 100:.1f}%")
                                        st.caption(f"Inflation: {adj_inflation * 100:.1f}%")

                                    # FORM SUBMIT BUTTON (prevents auto-reload)
                                    submitted = st.form_submit_button(
                                        "💾 Save Comparison",
                                        type="primary",
                                        use_container_width=True
                                    )

                                # ONLY PROCESS when button is ACTUALLY CLICKED
                                if submitted:
                                    if not comparison_name:
                                        st.error("⚠️ Please enter a name for this comparison")
                                    else:
                                        # Get current base plan ID
                                        from utils.snapshot_manager import get_snapshots_index
                                        index = get_snapshots_index()
                                        current_plan_id = index.get('current_snapshot_id')

                                        if not current_plan_id:
                                            st.error("⚠️ No base plan found. Please save a base plan first in INTAKE mode.")
                                        else:
                                            # Build adjustments dict
                                            adjustments = {
                                                "adjusted_income": float(adj_income),
                                                "adjusted_expenses": float(adj_expenses),
                                                "adjusted_return_rate": float(adj_return),
                                                "adjusted_inflation_rate": float(adj_inflation)
                                            }

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
                                                print(f"[WARN] Could not capture simulation results: {result_err}")

                                            # Save comparison scenario
                                            try:
                                                comparison_id = save_comparison_scenario(
                                                    base_plan_id=current_plan_id,
                                                    name=comparison_name,
                                                    description=comparison_description or "",
                                                    adjustments=adjustments,
                                                    simulation_results=simulation_results
                                                )

                                                if comparison_id:
                                                    st.success(f"✅ Comparison saved: {comparison_name}")
                                                    st.balloons()
                                                    st.info(f"📊 Comparison ID: `{comparison_id}`\n\nYou can now load this comparison from the sidebar.")
                                                    print(f"[DEBUG] Saved comparison: {comparison_id}")
                                                else:
                                                    st.error("❌ Failed to save comparison. Please try again.")

                                            except Exception as e:
                                                st.error(f"❌ Error saving comparison: {e}")
                                                print(f"[ERROR] Save comparison failed: {e}")
                                                import traceback
                                                traceback.print_exc()

                        else:
                            st.error("❌ Comparison failed to generate results")
        except Exception as e:
            st.error(f"Scenario comparison error: {str(e)}")

    # =============================================================================
    # COMPARE SAVED PLANS
    # =============================================================================

    st.markdown("---")
    st.subheader("📊 Compare Saved Plans")
    st.caption("Compare your saved retirement plans to see which strategy works best.")

    try:
        from utils.snapshot_manager import get_snapshots_index, compare_snapshots, display_snapshot_comparison

        # Get available snapshots
        index = get_snapshots_index()
        snapshots = index.get("snapshots", [])

        if len(snapshots) == 0:
            st.info("💡 You haven't saved any plans yet. Complete INTAKE and save a scenario first.")
        elif len(snapshots) == 1:
            st.warning("⚠️ Save at least 2 plans to use comparison. You currently have 1 saved plan.")
        else:
            # Create snapshot options for dropdown
            snapshot_options = {f"{s['name']} ({s['id']})": s['id'] for s in snapshots}

            # Let user select 2-3 snapshots
            st.markdown("**Select 2-3 plans to compare:**")
            selected_labels = st.multiselect(
                "Choose plans",
                options=list(snapshot_options.keys()),
                max_selections=3,
                help="Pick 2-3 saved plans to compare side-by-side"
            )

            # Convert labels back to IDs
            selected_ids = [snapshot_options[label] for label in selected_labels]

            if len(selected_ids) >= 2:
                if st.button("🔍 Compare Selected Plans", type="primary", use_container_width=True):
                    with st.spinner("Comparing plans..."):
                        comparison = compare_snapshots(selected_ids)
                        if comparison:
                            display_snapshot_comparison(comparison)
                        else:
                            st.error("❌ Comparison failed. Please try again.")
            elif len(selected_ids) == 1:
                st.info("👆 Select at least one more plan to compare.")
            else:
                st.info("👆 Select 2-3 plans from the dropdown above to start comparing.")

    except Exception as e:
        st.error(f"Saved plans comparison error: {str(e)}")

    # =============================================================================
    # AI ADVISOR
    # =============================================================================

    if features.get('show_ai_advisor'):
        try:
            from ai_advisor import show_ai_consultation
            st.markdown("---")
            show_ai_consultation(results, user_data, financial_data, sim_params)
        except Exception as e:
            st.error(f"AI advisor error: {str(e)}")

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
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("✅ Family Forecast Results Page Module")
    print("Functions: show_results_page")
