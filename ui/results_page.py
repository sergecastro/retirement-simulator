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

                        # STORE adjusted values in session state for save form
                        st.session_state['last_comparison_adjustments'] = {
                            'adj_income': adj_income,
                            'adj_expenses': adj_expenses,
                            'adj_return': adj_return,
                            'adj_inflation': adj_inflation
                        }

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
                            # STORE comparison results in session state for save form
                            st.session_state['last_comparison_results'] = comp_results

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

                        else:
                            st.error("❌ Comparison failed to generate results")
        except Exception as e:
            st.error(f"Scenario comparison error: {str(e)}")

    # =============================================================================
    # SAVE COMPARISON SCENARIO (Sub-Phase 2A) - MOVED OUTSIDE COMPARISON FORM
    # =============================================================================
    # Only show if a comparison was run and data exists in session state
    if 'last_comparison_adjustments' in st.session_state and 'last_comparison_results' in st.session_state:
        st.markdown("---")
        print("[DEBUG RESULTS] ===== Reached Save Comparison Section (OUTSIDE comparison form) =====")

        with st.expander("💾 Save This Comparison Scenario", expanded=False):
            print("[DEBUG SAVE] Expander opened")
            st.write("🔍 [DEBUG] Save Comparison expander opened")

            # CHECK FOR SUCCESS MESSAGE FROM PREVIOUS SAVE (after reload)
            if "comparison_save_success" in st.session_state:
                print("[DEBUG SAVE] ✓ Found success message in session state")
                success_data = st.session_state.comparison_save_success
                st.success(f"✅ Comparison saved: {success_data['name']}")
                st.balloons()
                st.info(f"📊 Comparison ID: `{success_data['id']}`\n\nYou can now load this comparison from the sidebar.")
                # Clear the flag so it doesn't show again
                del st.session_state.comparison_save_success
                print("[DEBUG SAVE] ✓ Success message displayed and cleared from session state")

            st.markdown("""
            Save this comparison to review later or compare with other scenarios.
            Only your adjustments are saved (not your full plan data).
            """)

            # Get adjustment data from session state
            adjustments_data = st.session_state['last_comparison_adjustments']
            comp_results = st.session_state['last_comparison_results']

            # WRAP IN FORM to prevent auto-reload
            with st.form(key="save_comparison_form", clear_on_submit=False):
                print("[DEBUG SAVE] Form initialized")

                col1, col2 = st.columns([2, 1])

                with col1:
                    comparison_name = st.text_input(
                        "Comparison Name",
                        placeholder="e.g., Retire at 67, Save 10% More, Lower Expenses",
                        help="Give this comparison a memorable name"
                    )
                    print(f"[DEBUG SAVE] Name input widget created")

                    comparison_description = st.text_area(
                        "Description (Optional)",
                        placeholder="Describe what makes this scenario different...",
                        help="Add notes about this comparison",
                        height=100
                    )
                    print(f"[DEBUG SAVE] Description textarea widget created")

                with col2:
                    st.markdown("**Current Adjustments:**")
                    try:
                        st.caption(f"Income: ${adjustments_data['adj_income']:,.0f}")
                        st.caption(f"Expenses: ${adjustments_data['adj_expenses']:,.0f}")
                        st.caption(f"Return Rate: {adjustments_data['adj_return'] * 100:.1f}%")
                        st.caption(f"Inflation: {adjustments_data['adj_inflation'] * 100:.1f}%")
                        print(f"[DEBUG SAVE] Adjustments displayed from session state")
                    except Exception as e:
                        print(f"[DEBUG SAVE ERROR] Could not display adjustments: {e}")
                        st.error(f"Error displaying adjustments: {e}")

                # FORM SUBMIT BUTTON (prevents auto-reload)
                save_submitted = st.form_submit_button(
                    "💾 Save Comparison",
                    type="primary",
                    use_container_width=True
                )
                print(f"[DEBUG SAVE] Submit button rendered, save_submitted={save_submitted}")

            # ONLY PROCESS when button is ACTUALLY CLICKED
            if save_submitted:
                print("="*60)
                print("[DEBUG SAVE] ===== SAVE BUTTON CLICKED =====")
                print(f"[DEBUG SAVE] Comparison name: '{comparison_name}'")
                print(f"[DEBUG SAVE] Description: '{comparison_description}'")
                print("="*60)
                st.write(f"🔍 [DEBUG] Button clicked! Name: '{comparison_name}'")

                if not comparison_name:
                    print("[DEBUG SAVE] ERROR: No name provided")
                    st.error("⚠️ Please enter a name for this comparison")
                else:
                    print("[DEBUG SAVE] ✓ Name provided, proceeding to save...")
                    st.write("🔍 [DEBUG] Name validated, proceeding...")

                    # Get current base plan ID
                    try:
                        from utils.snapshot_manager import get_snapshots_index
                        print("[DEBUG SAVE] ✓ Imported get_snapshots_index")

                        index = get_snapshots_index()
                        print(f"[DEBUG SAVE] ✓ Got snapshots index: {list(index.keys())}")

                        current_plan_id = index.get('current_snapshot_id')
                        print(f"[DEBUG SAVE] Current base plan ID: '{current_plan_id}'")
                        st.write(f"🔍 [DEBUG] Base plan ID: '{current_plan_id}'")
                    except Exception as e:
                        print(f"[DEBUG SAVE ERROR] Failed to get plan ID: {e}")
                        import traceback
                        traceback.print_exc()
                        st.error(f"Error getting plan ID: {e}")
                        current_plan_id = None

                    if not current_plan_id:
                        print("[DEBUG SAVE] ERROR: No base plan ID found")
                        st.error("⚠️ No base plan found. Please save a base plan first in INTAKE mode.")
                    else:
                        print("[DEBUG SAVE] ✓ Base plan found, building adjustments...")
                        st.write("🔍 [DEBUG] Building adjustments dict...")

                        # Build adjustments dict from session state
                        try:
                            adjustments = {
                                "adjusted_income": float(adjustments_data['adj_income']),
                                "adjusted_expenses": float(adjustments_data['adj_expenses']),
                                "adjusted_return_rate": float(adjustments_data['adj_return']),
                                "adjusted_inflation_rate": float(adjustments_data['adj_inflation'])
                            }
                            print(f"[DEBUG SAVE] ✓ Adjustments dict: {adjustments}")
                        except Exception as e:
                            print(f"[DEBUG SAVE ERROR] Failed to build adjustments: {e}")
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
                                print(f"[DEBUG SAVE] ✓ Simulation results: {simulation_results}")
                            except Exception as result_err:
                                print(f"[DEBUG SAVE] ⚠ Could not capture simulation results: {result_err}")
                                simulation_results = {}

                            # Save comparison scenario
                            print("[DEBUG SAVE] ===== Calling save_comparison_scenario() =====")
                            st.write("🔍 [DEBUG] Calling save function...")

                            try:
                                from utils.comparison_scenarios import save_comparison_scenario
                                print("[DEBUG SAVE] ✓ Imported save_comparison_scenario")

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
