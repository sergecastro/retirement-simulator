# File: visuals.py
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import calendar
import threading
from dash import callback_context
import traceback
import time
from streamlit.runtime.scriptrunner import get_script_run_ctx, add_script_run_ctx

from datetime import date  

def show_sankey(results, show_sankey):
    if show_sankey:
        st.subheader("Cash-Flow Sankey Diagram")
        labels = ["Income", "Expenses", "Savings", "RMDs", "Investments"]
        sources = [0, 0, 3]
        targets = [1, 2, 2]
        values = [sum(results['total_incomes']) * 0.7, sum(results['total_incomes']) * 0.3, sum(results['total_rmd'])]
        fig = go.Figure(data=[go.Sankey(node=dict(label=labels), link=dict(source=sources, target=targets, value=values))])
        st.plotly_chart(fig, use_container_width=True)

def show_goals(results, show_goals):
    if show_goals:
        st.subheader("Goal Funding Gauges")
        for goal, data in results['goal_achievement'].items():
            fig = go.Figure(go.Indicator(mode="gauge+number", value=(data['actual'] / data['target']) * 100 if data['target'] > 0 else 0, domain={'x': [0, 1], 'y': [0, 1]}, title={'text': goal}, gauge={'axis': {'range': [None, 200]}, 'bar': {'color': "darkblue"}, 'steps': [{'range': [0, 100], 'color': "lightgray"}, {'range': [100, 200], 'color': "green"}]}))
            st.plotly_chart(fig)

def show_calendar(results, show_calendar):
    if show_calendar:
        st.subheader("Monthly Heatmap")
        df = results['df']
        first_year = df.iloc[0]
        monthly_cash_flow = [(first_year['Total Income'] - first_year['Total Expenses']) / 12] * 12
        months = list(calendar.month_abbr)[1:]
        fig = go.Figure(data=go.Heatmap(z=[monthly_cash_flow], x=months, y=[first_year['Year']], colorscale='RdYlGn'))
        fig.update_layout(title="Monthly Monthly Cash Flow Heatmap")
        st.plotly_chart(fig)

def show_timeline(results, show_timeline, partner_name, DASH_AVAILABLE, age, partner_age, partner_exists):  
    if show_timeline:
        st.subheader("Family Timeline")
        events = results.get('events', {})
        current_year = date.today().year

        # Prepare draggable events (user-added like college, inheritance)
        draggable_events = sorted([
            {
                'year': year, 
                'type': 'College' if delta['expense_delta'] > 0 else 'Inheritance', 
                'color': 'red' if delta['expense_delta'] > 0 else 'green',
                'avatar_key': 'child' if delta['expense_delta'] > 0 else None,
                'delta': delta
            } 
            for year, delta in events.items()
        ], key=lambda e: e['year'])

        # Prepare static events (RMD starts)
        static_events = []
        self_rmd_year = current_year + max(0, 73 - age)
        static_events.append({
            'year': self_rmd_year, 
            'type': 'RMD Start - Self', 
            'color': 'blue',
            'avatar_key': 'self'}
        )
        if partner_exists:
            partner_rmd_year = current_year + max(0, 73 - partner_age)
            static_events.append({
                'year': partner_rmd_year, 
                'type': f'RMD Start - {partner_name}', 
                'color': 'blue',
                'avatar_key': 'partner'
            })
        static_events.sort(key=lambda e: e['year'])

        # Calculate min/max years for xaxis
        all_years = [e['year'] for e in draggable_events + static_events]
        min_year = min(all_years) - 1 if all_years else current_year
        max_year = max(all_years) + 1 if all_years else current_year + 50

        if not DASH_AVAILABLE:
            # Static fallback
            event_list = draggable_events + static_events
            df_timeline = pd.DataFrame([
                {'Event': e['type'], 'Start': e['year'], 'Finish': e['year'] + 0.01, 'Color': e['color']} 
                for e in event_list
            ])
            if not df_timeline.empty:
                fig = px.timeline(df_timeline, x_start='Start', x_end='Finish', y='Event', color='Color')
                fig.update_traces(marker=dict(size=15), textposition='auto')
                fig.update_layout(height=600, font_size=12)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No events to display in timeline.")
        else:
            # Interactive Dash timeline
            if 'updated_events' not in st.session_state:
                st.session_state['updated_events'] = events.copy()

            dash_app = Dash(__name__)

            # Layout with uploads for avatars and graph
            layout_children = [
                dcc.Store(id='avatar-store', data={'self': None, 'partner': None, 'child': None}),
                html.Div([
                    'Upload Avatar for Self: ',
                    dcc.Upload(id='upload-self', children=html.Div(['Drag or Select File']), multiple=False)
                ]),
            ]
            if partner_exists:
                layout_children.insert(1, html.Div([
                    f'Upload Avatar for {partner_name}: ',
                    dcc.Upload(id='upload-partner', children=html.Div(['Drag or Select File']), multiple=False)
                ]))
            layout_children.insert(2, html.Div([
                'Upload Avatar for Child: ',
                dcc.Upload(id='upload-child', children=html.Div(['Drag or Select File']), multiple=False)
            ]))

            dash_app.layout = html.Div(layout_children + [dcc.Graph(id='timeline', config={'editable': False, 'scrollZoom': True})])  # Changed editable to False

            # Callback for handling avatar uploads
            @dash_app.callback(
                Output('avatar-store', 'data'),
                Input('upload-self', 'contents'),
                Input('upload-partner', 'contents'),
                Input('upload-child', 'contents'),
                State('avatar-store', 'data')
            )
            def update_avatars(self_content, partner_content, child_content, data):
                ctx = callback_context
                if not ctx.triggered:
                    return data
                triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if triggered_id == 'upload-self' and self_content:
                    data['self'] = self_content
                elif triggered_id == 'upload-partner' and partner_content:
                    data['partner'] = partner_content
                elif triggered_id == 'upload-child' and child_content:
                    data['child'] = child_content
                return data

            # Callback for updating the timeline graph
            @dash_app.callback(
                Output('timeline', 'figure'),
                Input('timeline', 'relayoutData'),
                State('avatar-store', 'data')
            )
            def update_timeline(relayout_data, avatar_data):
                fig = go.Figure()
                # Add static events
                for e in static_events:
                    fig.add_trace(go.Scatter(x=[e['year']], y=[e['type']], mode='markers+text', marker=dict(color=e['color'], size=15), text=e['type']))
                    if e['avatar_key'] and avatar_data.get(e['avatar_key']):
                        fig.add_layout_image(dict(source=avatar_data[e['avatar_key']], x=e['year'], y=e['type'], xref="x", yref="y", sizex=1, sizey=1, xanchor="center", yanchor="middle"))
                # Add draggable events
                for e in draggable_events:
                    fig.add_trace(go.Scatter(x=[e['year']], y=[e['type']], mode='markers+text', marker=dict(color=e['color'], size=15), text=e['type']))
                    if e['avatar_key'] and avatar_data.get(e['avatar_key']):
                        fig.add_layout_image(dict(source=avatar_data[e['avatar_key']], x=e['year'], y=e['type'], xref="x", yref="y", sizex=1, sizey=1, xanchor="center", yanchor="middle"))
                fig.update_layout(xaxis=dict(range=[min_year, max_year]), yaxis=dict(type='category'), dragmode='lasso', height=600)
                # Handle drag updates (but since editable=False, no drag, but keep for future)
                if relayout_data and 'dragmode' in relayout_data:
                    pass  # Placeholder
                return fig

            # Run Dash in background thread with error handling and context fix
            def run_dash():
                ctx = get_script_run_ctx()
                if ctx is not None:
                    add_script_run_ctx(ctx)
                try:
                    dash_app.run_server(port=8502, debug=False, use_reloader=False, host='0.0.0.0')
                except Exception as e:
                    st.error(f"Error starting interactive timeline server (port may be busy or Dash issue): {str(e)}\nFull traceback: {traceback.format_exc()}")
                    # Fallback to static if failed
                    st.warning("Falling back to static timeline due to interactive mode failure.")
                    show_static_timeline(draggable_events, static_events)

            def show_static_timeline(draggable_events, static_events):
                event_list = draggable_events + static_events
                df_timeline = pd.DataFrame([
                    {'Event': e['type'], 'Start': e['year'], 'Finish': e['year'] + 0.01, 'Color': e['color']} 
                    for e in event_list
                ])
                if not df_timeline.empty:
                    fig = px.timeline(df_timeline, x_start='Start', x_end='Finish', y='Event', color='Color')
                    fig.update_traces(marker=dict(size=15), textposition='auto')
                    fig.update_layout(height=600, font_size=12)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No events to display in timeline.")

            thread = threading.Thread(target=run_dash, daemon=True)
            thread.start()
            time.sleep(5)  # Shortened delay

            # Embed the Dash app via iframe
            st.components.v1.html('<iframe src="http://127.0.0.1:8502/" style="width:100%; height=600px; border:none;"></iframe>', height=600, scrolling=True)

            # Button to apply changes to main app
            if st.button("Apply Timeline Changes and Refresh Simulation"):
                st.session_state['events'] = st.session_state['updated_events']
                st.experimental_rerun()

def show_trajectories(results):
    if 'df' in results:
        df = results['df']
        st.subheader("Income vs Expenses vs Savings Over Years")
        fig = px.line(df, x='Year', y=['Total Income', 'Total Expenses'], title='Income and Expenses Trajectory')
        possible_savings_cols = ['Savings End', 'Ending Balance', 'Principal', 'Savings Balance', 'Balance', 'Portfolio Balance']
        savings_col = next((col for col in possible_savings_cols if col in df.columns), None)
        if savings_col:
            fig.add_scatter(x=df['Year'], y=df[savings_col], mode='lines', name='Savings Balance', yaxis='y2')
        else:
            st.warning("Savings balance column not found (tried 'Savings End', 'Ending Balance', 'Principal', etc.)—showing income/expenses only. Add st.write(results['df'].columns) in main.py to share columns.")
        fig.update_layout(
            yaxis2=dict(title='Savings Balance', overlaying='y', side='right'),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

def show_monte_carlo(results):
    mc_key = 'monte_carlo_results'
    if mc_key in results:
        mc_data = results[mc_key]
        if 'final_balances' in mc_data:
            final_balances = mc_data['final_balances']
        elif 'mc_df' in mc_data:
            mc_df = mc_data['mc_df']
            final_balances = mc_df.iloc[-1].values
            results[mc_key]['final_balances'] = final_balances  # Cache for next
        else:
            final_balances = None
        if final_balances is not None:
            st.subheader("Monte Carlo Distribution of Final Savings")
            fig_hist = px.histogram(final_balances, nbins=50, title='Uncertainty in Final Savings Balance')
            fig_hist.update_layout(height=600)
            st.plotly_chart(fig_hist, use_container_width=True)

            # Restore fan chart from old app
            if 'mc_df' in mc_data:
                mc_df = mc_data['mc_df']
                med = mc_df.median(axis=1)
                p10 = mc_df.quantile(0.1, axis=1)
                p90 = mc_df.quantile(0.9, axis=1)
                fig_fan = go.Figure([
                    go.Scatter(x=mc_df.index, y=p90, line=dict(width=0), mode='lines', name=''),
                    go.Scatter(x=mc_df.index, y=p10, fill='tonexty', fillcolor='rgba(0,0,255,0.2)', line=dict(width=0), mode='lines', name=''),
                    go.Scatter(x=mc_df.index, y=med, line=dict(color='royalblue'), mode='lines', name='Median')
                ])
                fig_fan.update_layout(title="Monte Carlo Fan Chart (Savings Trajectories)", xaxis_title="Year", yaxis_title="Savings ($)", height=600)
                st.plotly_chart(fig_fan, use_container_width=True)
        else:
            st.warning("Monte Carlo results ('final_balances' or 'mc_df') not found—graph skipped. Ensure simulation.run_simulation returns 'monte_carlo_results' with mc_df if mc_iterations > 0.")
    else:
        st.warning("Monte Carlo not run (mc_iterations=0?)—graph skipped. Set mc_iterations >0 and rerun simulation.")

def show_comparison(base_results, adjusted_results):
    st.subheader("Scenario Comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Base Scenario")
        show_trajectories(base_results)
    with col2:
        st.write("Adjusted Scenario")
        show_trajectories(adjusted_results)

def show_competitive_analysis():
    st.subheader("Competitive Analysis")
    data = pd.DataFrame({
        "Feature": ["Family Modeling", "AI Insights", "Monte Carlo", "Privacy"],
        "Grok": ["✅", "✅", "✅", "✅"],
        "Others": ["❌", "⚠️", "⚠️", "⚠️"]
    })
    st.table(data)