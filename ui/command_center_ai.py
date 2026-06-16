# =============================================================================
# ui/command_center_ai.py
# FamilyForecast.AI — Command Center AI Advisor
# Builds context from session_state and calls existing ai_advisor pattern
# =============================================================================

import streamlit as st
import os

def _get(key, default="Not provided"):
    val = st.session_state.get(key)
    if val is None or val == "" or val == 0:
        return default
    return val

def build_command_center_context() -> str:
    """
    Builds a plain-English summary of the user's retirement data
    from session_state input_ keys.
    This becomes the AI's context — it knows everything about the user.
    """
    name = _get("input_user_name", "the user")
    age = _get("input_age", "unknown")
    ret_age = _get("input_retirement_age", "unknown")
    partner = _get("input_partner_name", None)
    partner_age = _get("input_partner_age", None)

    # Income
    ss_monthly = _get("input_social_security_monthly", 0)
    pension = _get("input_pension_monthly", 0)
    salary = _get("input_monthly_salary", 0)
    rental = _get("input_rental_income", 0)

    # Assets
    ira = _get("input_ira_balance", 0)
    roth = _get("input_roth_balance", 0)
    taxable = _get("input_taxable_investments", 0)
    k401 = _get("input_401k_balance", 0)
    home = _get("input_home_value", 0)

    # Expenses
    expenses = _get("input_monthly_expenses", 0)

    # SS timing
    ss_age = _get("input_social_security_age", "not set")

    # Monte Carlo results (set by Analysis engine after running)
    mc_success = st.session_state.get("monte_carlo_success_rate")
    mc_label = f"{mc_success:.0f}%" if mc_success else "not yet calculated"

    partner_line = ""
    if partner and partner != "Not provided":
        partner_line = f"Partner: {partner}, age {partner_age}."

    context = f"""
USER PROFILE:
Name: {name}, Age: {age}. {partner_line}
Planned retirement age: {ret_age}.

MONTHLY INCOME SOURCES:
- Social Security: ${ss_monthly:,}/month (planned claim age: {ss_age})
- Pension: ${pension:,}/month
- Current salary/wages: ${salary:,}/month
- Rental income: ${rental:,}/month

ASSETS:
- IRA / Traditional 401k: ${ira:,}
- Roth IRA / Roth 401k: ${roth:,}
- Taxable investment accounts: ${taxable:,}
- 401k balance: ${k401:,}
- Home value: ${home:,}

MONTHLY EXPENSES: ${expenses:,}/month

RETIREMENT SIMULATION:
- Monte Carlo success rate: {mc_label}

WITHDRAWAL ORDER RULE (always follow this):
1. Taxable accounts first (lowest tax impact)
2. Traditional IRA / 401k second
3. Roth IRA last (tax-free, preserve as long as possible)
Social Security and pension income layer in on top of withdrawals.
""".strip()
    return context


def build_system_prompt() -> str:
    context = build_command_center_context()
    return f"""You are a friendly, plain-English retirement planning advisor inside FamilyForecast.AI.
You are NOT a licensed financial advisor. Always remind the user to consult a professional for major decisions.

Your job is to help the user understand their retirement plan in simple, clear language.
Never use jargon without explaining it.
Always be encouraging but honest.
When recommending actions, explain WHY in plain English.
Keep answers focused and practical — no more than 3-4 paragraphs.

Here is everything you know about this user's retirement situation:

{context}

Always reference their specific numbers when answering questions.
If a number is "Not provided" or 0, acknowledge it and suggest they add it in their plan.
Never invent numbers that are not in the data above.
End every response with one clear "Next best action" sentence.
"""


def show_cc_ai_chat(screen_name: str, screen_context: str, suggested_questions: list):
    """
    Renders the AI chat panel for a Command Center screen.
    Uses existing Anthropic SDK pattern from ai_advisor.py.

    screen_name: unique key for this screen's chat history
    screen_context: one sentence describing what this screen shows
    suggested_questions: list of 3 example questions for this screen
    """
    st.markdown("---")
    st.markdown("### 💬 Ask Your AI Retirement Advisor")
    st.caption("Powered by Claude AI · Educational purposes only · Not financial advice")

    # Initialize chat history for this screen
    history_key = f"cc_chat_history_{screen_name}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    # Suggested questions as quick-click buttons
    st.markdown("**Quick questions:**")
    cols = st.columns(len(suggested_questions))
    for i, q in enumerate(suggested_questions):
        with cols[i]:
            if st.button(q, key=f"cc_sq_{screen_name}_{i}", use_container_width=True):
                # Add question directly to history and process immediately
                st.session_state[history_key].append({
                    "role": "user",
                    "content": q
                })
                with st.spinner("Thinking…"):
                    reply = _call_claude(
                        system_prompt=build_system_prompt(),
                        messages=st.session_state[history_key]
                    )
                st.session_state[history_key].append({
                    "role": "assistant",
                    "content": reply
                })
                st.rerun()

    # Display chat history
    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input(
        f"Ask anything about {screen_context}…",
        key=f"cc_chat_input_{screen_name}"
    )

    if user_input:
        # Add user message to history
        st.session_state[history_key].append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        # Call Claude
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                reply = _call_claude(
                    system_prompt=build_system_prompt(),
                    messages=st.session_state[history_key]
                )
            st.markdown(reply)

        # Add assistant reply to history
        st.session_state[history_key].append({
            "role": "assistant",
            "content": reply
        })


def _call_claude(system_prompt: str, messages: list) -> str:
    """
    Calls Anthropic API using the same pattern as ai_advisor.py.
    Reads ANTHROPIC_API_KEY from environment or st.secrets.
    """
    try:
        import anthropic

        # Get API key — same pattern as existing ai_advisor.py
        api_key = (
            os.getenv("ANTHROPIC_API_KEY")
            or st.secrets.get("ANTHROPIC_API_KEY", None)
        )
        if not api_key:
            st.error("ANTHROPIC_API_KEY not found. Check Render environment variables.")
            return "I cannot connect to the AI service right now. Please check your API key configuration."

        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=system_prompt,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in messages
            ]
        )
        return response.content[0].text

    except Exception as e:
        return f"AI advisor temporarily unavailable: {str(e)}"
