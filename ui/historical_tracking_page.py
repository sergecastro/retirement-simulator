"""
Historical Tracking Page
========================
Compare retirement plan snapshots over time to track progress.

Features:
- Select 2-5 snapshots to compare
- View side-by-side comparison table
- Delta analysis (change metrics)
- Timeline charts showing progress
- Snapshot management (delete, export)

Author: Family Forecast Development Team
Created: November 19, 2025
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
from typing import List, Dict
from utils.historical_snapshots import (
    list_historical_snapshots,
    load_historical_snapshot,
    delete_historical_snapshot,
    get_snapshot_count,
    export_all_snapshots,
    import_snapshots
)


def render():
    """Main render function for Historical Tracking page"""

    st.title("📊 Historical Tracking")
    st.markdown("Track your retirement plan progress over time")

    # Load all snapshots
    snapshots = list_historical_snapshots()
    snapshot_count = get_snapshot_count()

    # Check if user has enough snapshots
    if snapshot_count == 0:
        show_empty_state()
        return

    if snapshot_count == 1:
        show_single_snapshot_state()
        return

    # Main UI - User has 2+ snapshots
    st.markdown("---")

    # Snapshot selector
    st.subheader("📅 Select Snapshots to Compare")
    st.markdown(f"You have **{snapshot_count} saved snapshots**. Select 2-5 to compare.")

    # Create selection options
    snapshot_options = {s["id"]: f"{s['name']} ({s['timestamp'][:10]})" for s in snapshots}

    selected_ids = st.multiselect(
        "Choose snapshots to compare",
        options=list(snapshot_options.keys()),
        format_func=lambda id: snapshot_options[id],
        default=[snapshots[0]["id"], snapshots[-1]["id"]] if len(snapshots) >= 2 else [],
        help="Select 2-5 snapshots to see your progress over time",
        key="snapshot_selector"
    )

    if len(selected_ids) < 2:
        st.warning("⚠️ **Please select at least 2 snapshots to compare**")
        return

    if len(selected_ids) > 5:
        st.warning("⚠️ **Maximum 5 snapshots can be compared at once**")
        return

    # Load selected snapshots
    loaded_snapshots = []
    for sid in selected_ids:
        snapshot = load_historical_snapshot(sid)
        if snapshot:
            loaded_snapshots.append(snapshot)
        else:
            st.error(f"❌ Failed to load snapshot: {sid}")

    if len(loaded_snapshots) < 2:
        st.error("❌ Could not load enough snapshots for comparison")
        return

    # Sort by timestamp
    loaded_snapshots.sort(key=lambda x: x["timestamp"])

    # Export Comparison Report Button
    st.markdown("---")
    col_export, col_spacer = st.columns([2, 3])
    with col_export:
        if st.button("📊 Export This Comparison as JSON", use_container_width=True, type="secondary"):
            report = export_comparison_report(loaded_snapshots)
            json_str = json.dumps(report, indent=2)

            st.download_button(
                label="💾 Download Comparison Report",
                data=json_str,
                file_name=f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="download_comparison_report"
            )
            st.success("✅ Comparison report ready to download!")

    # Show comparison sections
    st.markdown("---")
    show_comparison_table(loaded_snapshots)

    st.markdown("---")
    show_delta_analysis(loaded_snapshots)

    st.markdown("---")
    show_timeline_charts(loaded_snapshots)

    st.markdown("---")
    show_snapshot_management(snapshots)


def show_empty_state():
    """Display when user has no snapshots"""
    st.info("👋 **Welcome to Historical Tracking!**")

    st.markdown("""
    ### 📸 How it works:

    1. **Save snapshots** from the Analysis page after running simulations
    2. **Return quarterly or yearly** to save new snapshots as your situation changes
    3. **Compare snapshots** here to see if you're improving over time

    ### 🎯 What you'll see:

    - Side-by-side comparison of your retirement plans
    - Change metrics (success rate, net worth, etc.)
    - Beautiful charts showing your progress
    - AI insights on your trajectory (coming soon!)

    ### 🚀 Get started:

    1. Go to **Analysis** mode
    2. Run a simulation with your current data
    3. Scroll to the bottom and click **"💾 Save Snapshot"**
    4. Come back here to track your progress!
    """)

    if st.button("🚀 Go to Analysis", use_container_width=True):
        st.session_state.current_mode = "Analysis"
        st.rerun()


def show_single_snapshot_state():
    """Display when user has only 1 snapshot"""
    snapshots = list_historical_snapshots()
    first = snapshots[0]

    st.info("📸 **You have 1 snapshot saved!**")

    st.markdown(f"""
    ### Your first snapshot:
    - **Name:** {first['name']}
    - **Date:** {first['timestamp'][:10]}

    ### 🎯 Next step:

    Save another snapshot to start tracking your progress!

    **Recommended:** Save snapshots:
    - After major life changes (new job, house purchase, etc.)
    - Quarterly or yearly to track long-term progress
    - Before and after financial decisions
    """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Go to Analysis", use_container_width=True):
            st.session_state.current_mode = "Analysis"
            st.rerun()

    with col2:
        if st.button("🗑️ Delete This Snapshot", use_container_width=True):
            if delete_historical_snapshot(first["id"]):
                st.success("✅ Snapshot deleted!")
                st.rerun()


def show_comparison_table(snapshots: List[Dict]):
    """Display side-by-side comparison table"""

    st.subheader("📊 Snapshot Comparison")

    # Build comparison data
    comparison_data = []

    for snapshot in snapshots:
        user_data = snapshot["user_data"]
        results = snapshot["simulation_results"]

        comparison_data.append({
            "Date": snapshot["timestamp"][:10],
            "Name": snapshot["name"],
            "Age": user_data.get("age", "N/A"),
            "Income": f"${user_data.get('income', 0):,.0f}",
            "Expenses": f"${user_data.get('expenses', 0):,.0f}",
            "Savings": f"${user_data.get('savings', 0):,.0f}",
            "Success Rate": f"{results.get('success_rate', 0):.1f}%",
            "Final Net Worth": f"${results.get('median_final_balance', 0):,.0f}",
            "Years Solvent": f"{results.get('years_of_solvency', 0):.0f}"
        })

    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Show notes if any
    st.markdown("#### 📝 Notes")
    for snapshot in snapshots:
        if snapshot.get("notes"):
            st.markdown(f"**{snapshot['name']}:** {snapshot['notes']}")


def show_delta_analysis(snapshots: List[Dict]):
    """Show change metrics between first and last snapshot"""

    st.subheader("📈 Progress Analysis")
    st.markdown("Comparing your **first** snapshot to your **most recent** snapshot:")

    first = snapshots[0]["simulation_results"]
    last = snapshots[-1]["simulation_results"]

    col1, col2, col3 = st.columns(3)

    with col1:
        delta_success = last.get("success_rate", 0) - first.get("success_rate", 0)
        st.metric(
            "Success Rate",
            f"{last.get('success_rate', 0):.1f}%",
            f"{delta_success:+.1f}%",
            help="Higher is better - shows probability of not running out of money"
        )

    with col2:
        delta_networth = last.get("median_final_balance", 0) - first.get("median_final_balance", 0)
        st.metric(
            "Final Net Worth",
            f"${last.get('median_final_balance', 0):,.0f}",
            f"${delta_networth:+,.0f}",
            help="Projected net worth at end of retirement"
        )

    with col3:
        delta_years = last.get("years_of_solvency", 0) - first.get("years_of_solvency", 0)
        st.metric(
            "Years Solvent",
            f"{last.get('years_of_solvency', 0):.0f} years",
            f"{delta_years:+.0f} years",
            help="How many years your money will last"
        )

    # Progress message
    if delta_success > 0:
        st.success(f"🎉 **Great progress!** Your success rate improved by {delta_success:.1f} percentage points!")
    elif delta_success < 0:
        st.warning(f"⚠️ **Needs attention:** Your success rate decreased by {abs(delta_success):.1f} percentage points. Consider adjusting your plan.")
    else:
        st.info("ℹ️ Your success rate remained stable.")


def show_timeline_charts(snapshots: List[Dict]):
    """Create timeline charts showing progress over time"""

    st.subheader("📈 Progress Over Time")

    # Extract data for charts
    dates = [s["timestamp"][:10] for s in snapshots]
    names = [s["name"] for s in snapshots]
    success_rates = [s["simulation_results"].get("success_rate", 0) for s in snapshots]
    net_worths = [s["simulation_results"].get("median_final_balance", 0) for s in snapshots]
    years_solvent = [s["simulation_results"].get("years_of_solvency", 0) for s in snapshots]

    # Success Rate Chart
    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=dates,
        y=success_rates,
        mode='lines+markers',
        name='Success Rate',
        line=dict(color='#00D9FF', width=3),
        marker=dict(size=12, symbol='circle'),
        text=names,
        hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Success Rate: %{y:.1f}%<extra></extra>'
    ))

    fig1.update_layout(
        title="Retirement Success Rate Over Time",
        xaxis_title="Date",
        yaxis_title="Success Rate (%)",
        height=400,
        hovermode='closest',
        yaxis=dict(range=[0, 100])
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Net Worth Chart
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=dates,
        y=net_worths,
        mode='lines+markers',
        name='Final Net Worth',
        line=dict(color='#4CAF50', width=3),
        marker=dict(size=12, symbol='diamond'),
        fill='tozeroy',
        text=names,
        hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Net Worth: $%{y:,.0f}<extra></extra>'
    ))

    fig2.update_layout(
        title="Projected Final Net Worth Over Time",
        xaxis_title="Date",
        yaxis_title="Net Worth ($)",
        height=400,
        hovermode='closest'
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Years Solvent Chart
    fig3 = go.Figure()

    fig3.add_trace(go.Bar(
        x=dates,
        y=years_solvent,
        name='Years Solvent',
        marker_color='#E8B541',
        text=names,
        hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Years: %{y:.0f}<extra></extra>'
    ))

    fig3.update_layout(
        title="Years of Retirement Funding Over Time",
        xaxis_title="Date",
        yaxis_title="Years",
        height=400,
        hovermode='closest'
    )

    st.plotly_chart(fig3, use_container_width=True)


def show_snapshot_management(snapshots: List[Dict]):
    """Snapshot management section - delete snapshots"""

    st.subheader("🗂️ Manage Snapshots")

    st.markdown(f"**Total snapshots:** {len(snapshots)}")

    # Delete snapshot selector
    col1, col2 = st.columns([3, 1])

    with col1:
        snapshot_to_delete = st.selectbox(
            "Select snapshot to delete",
            options=[""] + [s["id"] for s in snapshots],
            format_func=lambda id: "Choose a snapshot..." if id == "" else next(s["name"] + f" ({s['timestamp'][:10]})" for s in snapshots if s["id"] == id),
            key="delete_selector"
        )

    with col2:
        st.write("")  # Spacing
        if st.button("🗑️ Delete", use_container_width=True, disabled=(snapshot_to_delete == "")):
            if snapshot_to_delete:
                if delete_historical_snapshot(snapshot_to_delete):
                    st.success("✅ Snapshot deleted!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete snapshot")

    # Export/Import Section
    st.markdown("---")
    st.markdown("### 📦 Backup & Restore")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Export All Snapshots**")
        st.markdown("Download all your snapshots as a JSON file for backup or transfer.")

        if st.button("📥 Export All Snapshots", use_container_width=True, type="secondary"):
            export_data = export_all_snapshots()

            # Convert to JSON string
            json_str = json.dumps(export_data, indent=2)

            # Create download button
            st.download_button(
                label="💾 Download JSON File",
                data=json_str,
                file_name=f"family_forecast_snapshots_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )

            st.success(f"✅ Ready to download {export_data['snapshot_count']} snapshots!")

    with col2:
        st.markdown("**Import Snapshots**")
        st.markdown("Upload a previously exported JSON file to restore your snapshots.")

        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type=["json"],
            key="import_snapshots_uploader",
            help="Upload a file exported from this app"
        )

        if uploaded_file is not None:
            try:
                # Read the uploaded file
                import_data = json.loads(uploaded_file.read())

                # Show preview
                st.info(f"📄 Found {import_data.get('snapshot_count', 0)} snapshots in file")

                if st.button("⬆️ Import Snapshots", use_container_width=True, type="primary"):
                    imported_count = import_snapshots(import_data)
                    st.success(f"✅ Successfully imported {imported_count} snapshots!")
                    st.balloons()
                    st.rerun()

            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file. Please upload a valid export file.")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")


def export_comparison_report(snapshots: List[Dict]) -> Dict:
    """
    Export the current comparison as a report

    Args:
        snapshots: List of loaded snapshots being compared

    Returns:
        Dictionary containing comparison report data
    """
    report = {
        "report_type": "historical_comparison",
        "generated_date": datetime.now().isoformat(),
        "snapshot_count": len(snapshots),
        "snapshots": snapshots,
        "summary": {
            "date_range": {
                "first": snapshots[0]["timestamp"][:10],
                "last": snapshots[-1]["timestamp"][:10]
            },
            "metrics": {
                "success_rate_change": snapshots[-1]["simulation_results"]["success_rate"] - snapshots[0]["simulation_results"]["success_rate"],
                "net_worth_change": snapshots[-1]["simulation_results"]["median_final_balance"] - snapshots[0]["simulation_results"]["median_final_balance"],
                "years_solvent_change": snapshots[-1]["simulation_results"]["years_of_solvency"] - snapshots[0]["simulation_results"]["years_of_solvency"]
            }
        }
    }

    return report


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("✅ Historical Tracking Page Module")
    print("Functions: render")
