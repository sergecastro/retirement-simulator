"""
Chart Tooltip System
====================
Provides help/explanation buttons next to charts since Streamlit's native
help="..." parameter doesn't work on Plotly charts.
"""

import streamlit as st


def get_chart_explanation(chart_id):
    """
    Get the explanation text for a specific chart.
    Returns a dictionary with 'title', 'explanation', and 'key_insights'.
    """
    explanations = {
        # ANALYSIS PAGE CHARTS
        "financial_trajectories": {
            "title": "Financial Projections Chart",
            "explanation": """
This chart shows your projected financial trajectory over time. It includes four key metrics:

**Savings (Blue Line):** Your liquid savings balance over time. This is the money you can access for expenses. If this line dips below zero, it means you've run out of accessible funds.

**Net Worth (Orange Line):** Your total assets minus total liabilities. This includes home equity, investments, and all other assets. Net worth can remain positive even when savings are depleted (e.g., home equity).

**Income (Green Line):** Your total annual income from all sources - salary, Social Security, pensions, investments, etc. Watch how this changes at retirement age.

**Expenses (Red Line):** Your total annual expenses adjusted for inflation. Expenses typically increase over time due to inflation and healthcare costs.
            """,
            "key_insights": [
                "Watch where the Savings line crosses zero - that's when you run out of liquid funds",
                "The gap between Income and Expenses determines your savings rate",
                "Net Worth includes illiquid assets like home equity",
                "Lines trending upward are good; steep downward trends are concerning"
            ]
        },

        "health_dashboard": {
            "title": "Financial Health Dashboard",
            "explanation": """
This dashboard provides key financial health metrics to assess your retirement readiness:

**Emergency Fund (Months):** How many months of expenses your liquid savings can cover. Financial advisors recommend 6-12 months minimum.

**Debt-to-Income Ratio:** Your total liabilities divided by annual income. Lower is better. Above 40% is concerning.

**Savings Rate:** What percentage of your income you're saving. 15-20% is considered healthy for retirement planning.

**Health Score (0-100):** An overall score combining multiple factors. 80+ is excellent, 60-79 is good, 40-59 needs attention, below 40 is concerning.
            """,
            "key_insights": [
                "Emergency fund should cover 6-12 months of expenses",
                "Keep debt-to-income below 36% if possible",
                "Aim for 15-20% savings rate minimum",
                "Health score above 80 indicates strong financial position"
            ]
        },

        "goal_achievement_gauges": {
            "title": "Goal Achievement Gauges",
            "explanation": """
These gauges show your progress toward each financial goal you've set:

**Progress Percentage:** Shows how close you are to reaching your target amount by the target year. 100% means you'll meet or exceed the goal.

**Target vs Actual:** Compares your projected savings at the goal year against your target amount.

**Color Coding:**
- Green: Goal achieved or on track (100%+)
- Red: Goal not yet achieved (below 100%)
            """,
            "key_insights": [
                "Goals are based on your projected savings at the target year",
                "Exceeding 100% means you'll surpass your goal",
                "Consider adjusting savings rate if goals are falling short",
                "Multiple goals help ensure comprehensive retirement planning"
            ]
        },

        "monte_carlo_simulation": {
            "title": "Monte Carlo Simulation",
            "explanation": """
Monte Carlo analysis runs thousands of simulations with random market variations to show the range of possible outcomes:

**Success Rate:** Percentage of simulations where you don't run out of money. 85%+ is considered acceptable.

**Percentile Bands:** Shows different outcome scenarios:
- 10th percentile: Worst case (only 10% of outcomes are worse)
- 50th percentile: Median/most likely outcome
- 90th percentile: Best case (only 10% of outcomes are better)

**Why It Matters:** Real markets are unpredictable. This analysis accounts for market volatility, giving you a more realistic view of potential outcomes.
            """,
            "key_insights": [
                "85%+ success rate is generally considered acceptable",
                "Wide bands indicate high uncertainty/volatility",
                "Focus on the 10th percentile (worst case) for safety",
                "Results depend on assumed return and volatility parameters"
            ]
        },

        "family_timeline": {
            "title": "Family Financial Timeline",
            "explanation": """
This timeline visualizes major life events and their financial impact:

**Children Events:** College costs, weddings, and other child-related expenses appear at their expected years.

**Inheritances:** Expected inheritance amounts shown at their projected years.

**Goals:** Your financial goals plotted on the timeline.

**Event Markers:** Each event shows its year and dollar amount, helping you see the cumulative impact on your finances.
            """,
            "key_insights": [
                "Large expenses cluster together can strain finances",
                "College costs typically occur in 4-year bursts",
                "Inheritances can provide significant financial boosts",
                "Plan ahead for overlapping major expenses"
            ]
        },

        "sankey_diagram": {
            "title": "Income Flow Sankey Diagram",
            "explanation": """
This diagram shows how your money flows from income sources to expenses:

**Left Side:** Income sources (salary, Social Security, pensions, investments)

**Right Side:** Expense categories (housing, healthcare, groceries, etc.)

**Flow Width:** Thicker flows represent larger amounts. This helps visualize where your money comes from and where it goes.
            """,
            "key_insights": [
                "Thicker flows indicate larger money movements",
                "Identify your largest expense categories",
                "See how income diversification affects stability",
                "Track where each income dollar ends up"
            ]
        },

        # SCENARIO STUDIO CHARTS
        "scenario_comparison_bar": {
            "title": "Scenario Comparison - Final Savings",
            "explanation": """
This bar chart compares the final savings amount across different scenarios you've created:

**Bar Height:** Represents the projected savings at the end of your planning horizon (typically age 90+).

**Comparison:** Easily see which scenario produces the best financial outcome.

**Dollar Values:** Exact amounts shown above each bar for precision.
            """,
            "key_insights": [
                "Higher bars indicate better final outcomes",
                "Compare scenarios to find optimal strategy",
                "Consider trade-offs not just final numbers",
                "Factor in quality of life, not just savings"
            ]
        },

        "scenario_trajectory_lines": {
            "title": "Savings Trajectory Comparison",
            "explanation": """
This line chart shows how savings evolve over time for each scenario:

**Multiple Lines:** Each line represents a different scenario's savings path.

**Crossover Points:** Where lines cross indicates when one strategy overtakes another.

**Trend Analysis:** See if savings grow steadily, peak and decline, or follow other patterns.
            """,
            "key_insights": [
                "Watch for scenarios that peak early then decline",
                "Crossover points show strategy trade-offs",
                "Steeper upward slopes mean faster growth",
                "Negative slopes indicate savings depletion"
            ]
        },

        "scenario_income_expenses": {
            "title": "Income vs Expenses by Scenario",
            "explanation": """
This grouped bar chart compares first-year income and expenses across scenarios:

**Blue Bars (Income):** Total annual income from all sources.

**Red Bars (Expenses):** Total annual expenses.

**Gap Analysis:** The difference between income and expenses is your savings capacity.
            """,
            "key_insights": [
                "Larger gap between income and expenses is better",
                "Red bars exceeding blue indicate negative cash flow",
                "Compare how different strategies affect this balance",
                "First year sets the foundation for future projections"
            ]
        },

        "scenario_health_scores": {
            "title": "Financial Health Score Comparison",
            "explanation": """
Horizontal bar chart showing financial health scores for each scenario:

**Score Range (0-100):**
- 80-100: Excellent (Green)
- 60-79: Good (Yellow/Gold)
- 40-59: Needs Attention (Orange)
- 0-39: Concerning (Red)

**Color Coding:** Bars are colored based on health score ranges for quick visual assessment.
            """,
            "key_insights": [
                "Aim for scores above 80 for peace of mind",
                "Health score combines multiple financial metrics",
                "Compare scenarios to see health score trade-offs",
                "Lower scores indicate higher financial risk"
            ]
        },

        # HEALTHCARE HUB CHARTS
        "medicare_irmaa_brackets": {
            "title": "Medicare IRMAA Premium Brackets",
            "explanation": """
This chart shows Medicare premium costs based on your Modified Adjusted Gross Income (MAGI):

**IRMAA (Income-Related Monthly Adjustment Amount):** Higher income means higher Medicare premiums.

**Brackets:** Income thresholds that trigger higher premium levels.

**Impact:** Understanding these brackets helps optimize Roth conversions and retirement income planning.
            """,
            "key_insights": [
                "IRMAA uses income from 2 years ago",
                "Roth conversions can push you into higher brackets",
                "Premium increases can be significant ($1000+/year)",
                "Plan Roth conversions to minimize IRMAA impact"
            ]
        }
    }

    return explanations.get(chart_id, {
        "title": "Chart Information",
        "explanation": "This chart displays financial data relevant to your retirement planning.",
        "key_insights": ["Hover over data points for specific values", "Use this visualization to inform your decisions"]
    })


def add_chart_help_button(chart_id, position="above"):
    """
    Add a help button that shows explanation for a specific chart.

    Args:
        chart_id: ID of the chart to explain
        position: "above" or "below" the chart (default: above)

    Usage:
        add_chart_help_button("financial_trajectories")
        st.plotly_chart(fig, ...)
    """
    explanation = get_chart_explanation(chart_id)

    with st.expander(f"❓ **What does this chart mean?** - {explanation['title']}", expanded=False):
        st.markdown(explanation['explanation'])

        if explanation.get('key_insights'):
            st.markdown("**Key Insights:**")
            for insight in explanation['key_insights']:
                st.markdown(f"• {insight}")


def add_inline_chart_help(chart_id):
    """
    Add a small help icon with tooltip-like behavior inline.
    Returns HTML/markdown that can be placed next to chart title.
    """
    explanation = get_chart_explanation(chart_id)

    # Create a compact help section
    col1, col2 = st.columns([10, 1])

    with col2:
        if st.button("❓", key=f"help_btn_{chart_id}", help=f"Click for help with {explanation['title']}"):
            st.session_state[f"show_help_{chart_id}"] = not st.session_state.get(f"show_help_{chart_id}", False)

    if st.session_state.get(f"show_help_{chart_id}", False):
        with st.info("ℹ️ **Chart Explanation**"):
            st.markdown(explanation['explanation'])
            if explanation.get('key_insights'):
                st.markdown("**Key Insights:**")
                for insight in explanation['key_insights']:
                    st.markdown(f"• {insight}")
            if st.button("Close", key=f"close_help_{chart_id}"):
                st.session_state[f"show_help_{chart_id}"] = False
                st.rerun()


def wrap_chart_with_help(chart_id, chart_title=None):
    """
    Create a section header with integrated help for a chart.
    Call this BEFORE displaying the chart.

    Usage:
        wrap_chart_with_help("financial_trajectories", "📈 Financial Trajectories")
        st.plotly_chart(fig, ...)
    """
    explanation = get_chart_explanation(chart_id)
    title = chart_title or explanation['title']

    # Create header with help button
    col1, col2 = st.columns([9, 1])

    with col1:
        st.subheader(title)

    with col2:
        # Use expander for clean UI
        pass

    # Add collapsible help section
    with st.expander("❓ Help: What does this chart show?", expanded=False):
        st.markdown(explanation['explanation'])

        if explanation.get('key_insights'):
            st.markdown("---")
            st.markdown("**💡 Key Insights:**")
            for insight in explanation['key_insights']:
                st.markdown(f"✓ {insight}")
