# =============================================================================
# ui/command_center_screens.py
# FamilyForecast.AI — Command Center: The 9 Screen Functions
# All placeholder content — wired with real data in Steps 4–7
# Imported by ui/command_center.py
# =============================================================================

import streamlit as st
from ui.command_center import _screen_header, _callout, _get
from ui.command_center_ai import show_cc_ai_chat


def screen_1_monthly_command():
    _screen_header(
        "🏠",
        "Monthly Command",
        "What is my plan for this month?",
    )
    st.info(
        "📋 **Placeholder — Step 4 wires real data.**\n\n"
        "This screen will show: Safe monthly spending, Plan Zone (Green/Yellow/Red), "
        "Monte Carlo success %, and Portfolio value — all pulled from your existing "
        "Analysis engine."
    )
    st.markdown("**Preview of final table:**")
    st.table({
        "Metric": [
            "Safe monthly spending",
            "Monte Carlo success",
            "Portfolio value",
            "Plan zone",
            "Cash reserve",
        ],
        "This Month": [
            "Calculated from Analysis engine",
            "Calculated from Monte Carlo",
            "From input_ keys",
            "Green / Yellow / Red",
            "Months of expenses covered",
        ],
        "Status": ["🟢", "🟢", "—", "🟢", "🟢"],
    })
    show_cc_ai_chat("screen1", "your monthly spending plan", [
        "How much can I safely spend this month?",
        "What happens if markets drop 20%?",
        "Am I saving enough?",
    ])


def screen_2_income_recipe():
    _screen_header(
        "💵",
        "Income Recipe",
        "Where does this month's money come from?",
    )
    st.info(
        "📋 **Placeholder — Step 5 wires real data.**\n\n"
        "This screen will show: Every income source ranked by tax efficiency, "
        "the recommended withdrawal order (taxable → IRA → Roth), and a "
        "'What if I withdrew from IRA instead?' comparison table."
    )
    st.table({
        "Source": ["Social Security", "Pension", "Taxable savings", "IRA withdrawal", "Roth withdrawal"],
        "This Month": ["From SS inputs", "From pension inputs", "Calculated", "$0 recommended", "$0 last resort"],
        "Tax Treatment": ["Partially taxable", "Fully taxable", "Long-term gains", "Fully taxable", "Tax-free"],
        "Recommended?": ["✅ Use first", "✅ Use first", "✅ Use second", "⏸ Hold for Roth", "🔒 Last resort"],
    })
    show_cc_ai_chat("screen2", "your income sources and withdrawal order", [
        "Why should I use Social Security before my IRA?",
        "What is the best order to take my money?",
        "Should I touch my Roth account this year?",
    ])


def screen_3_guardrail_zone():
    _screen_header(
        "🚦",
        "Guardrail Zone",
        "Is my plan on track?",
    )
    st.info(
        "📋 **Placeholder — Step 5 wires real data.**\n\n"
        "This screen will show: Your current zone (Green/Yellow/Red) based on "
        "Monte Carlo success %, the thresholds for each zone, what actions each "
        "zone triggers, and what would move you between zones."
    )
    st.table({
        "Zone": ["🟢 Green", "🟡 Yellow", "🔴 Red"],
        "Success Rate": ["80–100%", "65–80%", "Below 65%"],
        "Spending": ["Maintain or +3–5%", "Hold flat", "Reduce 5–10%"],
        "Roth Conversion": ["✅ Proceed", "⚠️ Reduce", "🚫 Stop"],
        "Your Status": ["← You are here", "", ""],
    })
    show_cc_ai_chat("screen3", "your guardrail zone status", [
        "What puts me in the Red Zone?",
        "Can I spend more since I am in Green?",
        "How do guardrails protect my plan?",
    ])


def screen_4_tax_opportunities():
    _screen_header(
        "🧾",
        "Tax Opportunities",
        "What tax moves should I make before December 31?",
    )
    st.info(
        "📋 **Placeholder — Step 6 wires real data.**\n\n"
        "This screen will show: Current bracket, room before next bracket, "
        "Roth conversion options comparison table, capital gains harvesting "
        "table, and the single best recommended action."
    )
    st.table({
        "Option": ["Do nothing", "✅ Convert small amount", "Convert medium", "Convert large"],
        "Tax Cost Now": ["$0", "Calculated", "Calculated", "Calculated"],
        "Tax Saved Later": ["$0", "Calculated", "Calculated", "Calculated"],
        "Net Lifetime Benefit": ["$0", "Best balance", "Good", "IRMAA risk"],
        "Recommended?": ["❌", "✅", "⚠️", "🚫"],
    })
    show_cc_ai_chat("screen4", "your tax opportunities this year", [
        "Should I do a Roth conversion this year?",
        "How much can I convert without paying more tax?",
        "What is capital gains harvesting?",
    ])


def screen_5_social_security():
    _screen_header(
        "📅",
        "Social Security Strategy",
        "When should I claim — and what does it do to my whole plan?",
    )
    st.info(
        "📋 **Placeholder — Step 6 wires real data.**\n\n"
        "This screen will show: Claiming age comparison (62 / FRA / 70) "
        "across monthly benefit, lifetime total, Roth conversion room, "
        "IRMAA risk, Monte Carlo impact, and estate value. "
        "Pulls from your existing Social Security Optimizer engine."
    )
    st.table({
        "Factor": [
            "Monthly benefit",
            "Roth conversion room/yr",
            "IRMAA exposure",
            "Monte Carlo success",
            "Estate value at 90",
        ],
        "Claim at 62": ["Lower", "High", "Low", "Lower", "Lower"],
        "✅ Claim at FRA": ["Medium", "Medium", "Moderate", "Best balance", "Medium"],
        "Claim at 70": ["Highest", "Low", "Risk", "Highest", "Highest"],
    })
    show_cc_ai_chat("screen5", "your Social Security claiming decision", [
        "Should I claim Social Security at 62 or wait?",
        "How does claiming age affect my taxes?",
        "What happens to my spouse if I claim early?",
    ])


def screen_6_rmd_forecast():
    _screen_header(
        "📈",
        "RMD Forecast",
        "What forced income is coming — and what should I do now?",
    )
    st.info(
        "📋 **Placeholder — Step 6 wires real data.**\n\n"
        "This screen will show: Year-by-year RMD projections from age 73, "
        "bracket impact of each RMD, and a comparison table of "
        "'Do nothing vs Convert $X/year' showing lifetime tax savings. "
        "Pulls from existing RMD engine in Analysis."
    )
    st.table({
        "Strategy": ["❌ Do nothing", "Convert $10K/yr", "✅ Convert $18K/yr", "Convert $25K/yr"],
        "RMD at Age 73": ["Largest", "Smaller", "Much smaller", "Smallest"],
        "Lifetime Tax Saved": ["$0", "Good", "Best balance", "IRMAA risk"],
        "Recommended?": ["❌", "⚠️", "✅", "🚫"],
    })
    show_cc_ai_chat("screen6", "your RMD forecast and Roth conversion strategy", [
        "What is an RMD and why does it matter?",
        "Should I do Roth conversions before 73?",
        "How much will my RMDs be?",
    ])


def screen_7_irmaa_watch():
    _screen_header(
        "🏥",
        "IRMAA Watch",
        "Will my income trigger higher Medicare premiums?",
    )
    st.info(
        "📋 **Placeholder — Step 7 wires real data.**\n\n"
        "This screen will show: All IRMAA tier thresholds, your projected MAGI, "
        "your safety margin to the next tier, and a table showing "
        "which income actions would push you into a higher tier. "
        "Pulls from your existing Healthcare Hub / IRMAA engine."
    )
    st.table({
        "Tier": ["✅ Standard (you)", "Tier 1", "Tier 2", "Tier 3"],
        "MAGI Threshold": ["Under $103K", "$103K–$129K", "$129K–$161K", "$161K–$193K"],
        "Monthly Premium": ["$185", "$259", "$370", "$481"],
        "Annual Extra Cost": ["$0 (baseline)", "+$888", "+$2,220", "+$3,551"],
        "Your Status": ["← You are here", "", "", ""],
    })
    show_cc_ai_chat("screen7", "your IRMAA and Medicare premium risk", [
        "What is IRMAA and how does it affect me?",
        "How do I avoid higher Medicare premiums?",
        "Will my income trigger a surcharge?",
    ])


def screen_8_what_changed():
    _screen_header(
        "🔄",
        "What Changed",
        "What is different since last month?",
    )
    st.info(
        "📋 **Placeholder — Step 7 wires real data.**\n\n"
        "This screen will show: Month-over-month delta for portfolio value, "
        "Monte Carlo success %, safe spending amount, IRMAA margin, "
        "and Roth conversion room. "
        "Pulls from your existing historical_tracking module."
    )
    st.table({
        "Item": [
            "Portfolio value",
            "Monte Carlo success",
            "Safe spending",
            "IRMAA margin",
            "Roth conversion room",
            "Plan zone",
        ],
        "Last Month": ["Snapshot", "Snapshot", "Calculated", "Calculated", "Calculated", "Green"],
        "This Month": ["Current", "Current", "Calculated", "Calculated", "Calculated", "Green"],
        "Change": ["+/-", "+/-", "+/-", "+/-", "+/-", "Stable"],
        "Status": ["🟢", "🟢", "🟢", "🟢", "🟢", "🟢"],
    })
    show_cc_ai_chat("screen8", "what changed in your plan this month", [
        "Is my plan improving or getting worse?",
        "What should I do differently next month?",
        "How do market changes affect my plan?",
    ])


def screen_9_next_best_action():
    _screen_header(
        "✅",
        "Next Best Action",
        "What should I actually do right now?",
    )
    st.info(
        "📋 **Placeholder — Step 7 wires real data.**\n\n"
        "This screen is the synthesis of all 8 screens. "
        "It will show: A priority action table ranked by impact and deadline, "
        "followed by a plain-English paragraph summarizing the whole plan. "
        "Below that: the full AI chat panel pre-loaded with all your data."
    )
    st.table({
        "Priority": ["🔴 1", "🔴 2", "🟡 3", "🟡 4", "🟢 5"],
        "Action": [
            "Roth conversion (amount TBD)",
            "Capital gains harvest (amount TBD)",
            "Stay below IRMAA threshold",
            "Review SS claiming age",
            "Update balances next month",
        ],
        "Deadline": ["Dec 31", "Dec 31", "Dec 31", "Before age 63", "Monthly"],
        "Impact": ["High", "High", "Medium", "Very High", "Low"],
        "Complexity": ["Low", "Low", "Monitor", "One meeting", "5 min"],
    })
    show_cc_ai_chat("screen9", "your complete retirement plan", [
        "Give me my top 3 actions right now",
        "Am I going to be okay in retirement?",
        "What is the biggest risk in my plan?",
    ])
