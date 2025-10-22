# ⚖️ ForeCash Regulatory Compliance Disclaimers
"""
CRITICAL: These disclaimers MUST appear in all appropriate locations to ensure
ForeCash complies with financial regulatory requirements and clearly communicates
that we provide planning tools, NOT financial advice.

Last Updated: October 21, 2025
Review Frequency: Quarterly (or when regulations change)
Legal Review: REQUIRED before production deployment
"""

import streamlit as st

# =============================================================================
# PRIMARY DISCLAIMER (Use on main app header and all result pages)
# =============================================================================

PRIMARY_DISCLAIMER = """
**⚠️ IMPORTANT LEGAL DISCLAIMER:**

ForeCash is an **educational planning tool** and does **NOT provide financial, investment, 
tax, or legal advice**. All projections, simulations, and AI-generated content are for 
**informational and educational purposes only** and should not be considered professional 
financial advice or recommendations.

**Key Points:**
- 📊 **Not Financial Advice:** ForeCash does not recommend specific investments, securities, 
  or financial strategies
- 🤖 **AI-Generated Content:** AI responses are based on algorithms and may contain errors 
  or inaccuracies
- 📈 **No Guarantees:** Past performance and projections do not guarantee future results
- 👨‍💼 **Consult Professionals:** Always consult qualified financial advisors, tax 
  professionals, and legal counsel before making financial decisions
- 🔒 **Your Data:** All data is stored in your browser session only and is not saved on 
  our servers (privacy-first design)
- ⚖️ **Not Fiduciary:** ForeCash and its operators do not act in a fiduciary capacity

**By using ForeCash, you acknowledge this disclaimer and agree to use this tool at your 
own risk.**
"""


# =============================================================================
# AI PLANNING ASSISTANT DISCLAIMER (Use at start of AI chat and periodically)
# =============================================================================

AI_ADVISOR_DISCLAIMER = """
**🤖 AI PLANNING ASSISTANT - IMPORTANT NOTICE:**

This AI assistant uses Claude (Anthropic) to provide **general educational information**
about retirement planning concepts.

**What This AI Does:**
✅ Explains financial planning concepts in plain English
✅ Analyzes your scenario data to identify patterns
✅ Suggests general planning strategies for consideration
✅ Answers questions about retirement planning topics

**What This AI Does NOT Do:**
❌ Does NOT provide personalized financial advice
❌ Does NOT recommend specific investments or securities
❌ Does NOT replace qualified financial professionals
❌ Does NOT guarantee accuracy of any information
❌ Does NOT act in a fiduciary capacity

**CRITICAL LIMITATIONS:**
- AI responses may contain errors or outdated information
- AI cannot know your complete financial situation
- AI cannot provide tax, legal, or investment advice
- AI responses are not tailored to your specific needs

**⚠️ Always verify important information with qualified professionals before making
financial decisions.**

Your data is processed in real-time and is not permanently stored. We prioritize your
privacy and data security.
"""


# =============================================================================
# CHART EXPLANATION DISCLAIMER (Inject into Claude API responses)
# =============================================================================

CHART_EXPLANATION_DISCLAIMER = """
**📊 Chart Analysis Disclaimer:**

This explanation is AI-generated for educational purposes only. It analyzes patterns in 
your scenario data but does NOT constitute financial advice. Always consult qualified 
professionals before making financial decisions based on these projections.
"""


# =============================================================================
# SIMULATION RESULTS DISCLAIMER (Use before showing simulation results)
# =============================================================================

SIMULATION_RESULTS_DISCLAIMER = """
**📈 SIMULATION RESULTS - READ CAREFULLY:**

**What These Results Show:**
- Projections based on YOUR input assumptions (income, expenses, returns, etc.)
- Mathematical models of potential future outcomes
- Probabilistic scenarios (Monte Carlo) showing range of possibilities

**What These Results DO NOT Show:**
- Guaranteed future performance
- Personalized investment recommendations
- Tax advice or legal guidance
- Complete financial planning (many factors not modeled)

**Critical Assumptions & Limitations:**
⚠️ **Returns:** Investment returns are assumptions and may not reflect market reality
⚠️ **Inflation:** Actual inflation may differ significantly from assumptions
⚠️ **Life Events:** Unexpected events (health, market crashes, etc.) are not fully modeled
⚠️ **Simplifications:** Real financial situations are more complex than any model
⚠️ **No Guarantees:** These are projections, not predictions

**🎯 How to Use These Results:**
1. Treat as a **starting point** for discussion with financial advisors
2. Test multiple scenarios to understand sensitivity to assumptions
3. Update regularly as your situation changes
4. Verify all tax and legal implications with qualified professionals

**This tool helps you explore "what-if" scenarios. It does NOT tell you what to do.**
"""


# =============================================================================
# DATA PRIVACY NOTICE (Use in sidebar or footer)
# =============================================================================

DATA_PRIVACY_NOTICE = """
**🔒 YOUR DATA PRIVACY:**

**How ForeCash Handles Your Data:**
✅ **Session-Only Storage:** All financial data stored in your browser session only
✅ **No Server Storage:** We do NOT save your financial information on our servers
✅ **No Account Required:** No email, no registration, no tracking
✅ **Privacy-First Design:** Your data disappears when you close your browser

**What We Do Send to AI Services:**
- Chart data and scenario information when you request AI explanations
- Chat messages when you use the AI advisor
- These are sent securely via HTTPS to Anthropic (Claude AI provider)
- Anthropic processes requests in real-time and does not use your data for training

**Your Control:**
- Download your scenarios as JSON files (you own your data)
- Delete scenarios anytime (removes from browser session)
- Clear browser cache to remove all local data

**We are committed to your privacy and data security.**
"""


# =============================================================================
# MONTE CARLO SPECIFIC DISCLAIMER
# =============================================================================

MONTE_CARLO_DISCLAIMER = """
**🎲 MONTE CARLO SIMULATION - PROBABILITY NOTICE:**

**What This Shows:**
Monte Carlo simulation runs your scenario thousands of times with randomized investment 
returns to show a range of possible outcomes.

**Understanding the Results:**
- **10th Percentile (Pessimistic):** Better outcomes occur 90% of the time
- **50th Percentile (Median):** The middle outcome - 50% do better, 50% do worse
- **90th Percentile (Optimistic):** Only 10% of outcomes are this good or better
- **Success Rate:** Percentage of scenarios where you don't run out of money

**CRITICAL LIMITATIONS:**
⚠️ Based on statistical assumptions about market returns (normal distribution)
⚠️ Does not account for: market crashes, black swan events, policy changes
⚠️ Assumes you stick to the plan (no behavioral deviations)
⚠️ Simplified model of complex reality

**This is a statistical tool, NOT a prediction of YOUR actual future.**
"""


# =============================================================================
# TAX DISCLAIMER (for tax-related features)
# =============================================================================

TAX_DISCLAIMER = """
**💰 TAX INFORMATION DISCLAIMER:**

**IMPORTANT:** ForeCash provides **general information** about tax concepts (RMDs, Roth 
conversions, tax brackets, etc.) for **educational purposes only**.

**We Do NOT:**
❌ Provide tax advice or tax planning services
❌ Recommend specific tax strategies
❌ Replace your CPA or tax professional
❌ Guarantee accuracy of tax calculations

**Tax rules are:**
- Complex and subject to interpretation
- Different for each individual's situation
- Changed frequently by legislation
- Affected by state and federal laws

**⚠️ ALWAYS consult a qualified tax professional (CPA, EA, or tax attorney) before making 
tax-related decisions.**

The tax calculations in ForeCash use simplified assumptions and may not reflect your 
actual tax liability.
"""


# =============================================================================
# MEDICARE/IRMAA DISCLAIMER (for healthcare features)
# =============================================================================

MEDICARE_IRMAA_DISCLAIMER = """
**🏥 MEDICARE & IRMAA INFORMATION DISCLAIMER:**

ForeCash provides **general information** about Medicare premiums and Income-Related 
Monthly Adjustment Amounts (IRMAA) for **educational purposes only**.

**Not Healthcare Advice:**
- We do NOT provide medical or health insurance advice
- IRMAA thresholds and rules change annually
- Your specific Medicare situation may vary
- Eligibility rules are complex and individualized

**⚠️ For Medicare Decisions:**
1. Visit Medicare.gov for official information
2. Consult with Medicare counselors (SHIP programs)
3. Review your specific situation with benefits specialists
4. Verify all numbers before making healthcare decisions

**The information shown is based on current rules but may become outdated.**
"""


# =============================================================================
# HELPER FUNCTIONS TO DISPLAY DISCLAIMERS
# =============================================================================

def show_primary_disclaimer(location="header"):
    """
    Display primary disclaimer in header or dedicated section
    
    Args:
        location: "header" or "sidebar" or "expander"
    """
    if location == "header":
        st.warning(PRIMARY_DISCLAIMER)
    elif location == "sidebar":
        with st.sidebar:
            with st.expander("⚖️ Legal Disclaimer", expanded=False):
                st.markdown(PRIMARY_DISCLAIMER)
    elif location == "expander":
        with st.expander("⚖️ IMPORTANT: Read Legal Disclaimer", expanded=False):
            st.markdown(PRIMARY_DISCLAIMER)


def show_ai_advisor_disclaimer():
    """Display AI advisor disclaimer at start of chat"""
    st.info(AI_ADVISOR_DISCLAIMER)


def show_simulation_results_disclaimer():
    """Display before showing simulation results"""
    with st.expander("⚠️ READ BEFORE VIEWING RESULTS", expanded=True):
        st.warning(SIMULATION_RESULTS_DISCLAIMER)


def show_monte_carlo_disclaimer():
    """Display before showing Monte Carlo charts"""
    with st.expander("🎲 Understanding Monte Carlo Simulation", expanded=False):
        st.info(MONTE_CARLO_DISCLAIMER)


def show_data_privacy_notice():
    """Display data privacy notice in sidebar"""
    with st.sidebar:
        with st.expander("🔒 Your Data Privacy", expanded=False):
            st.markdown(DATA_PRIVACY_NOTICE)


def show_tax_disclaimer():
    """Display before tax-related features"""
    st.warning(TAX_DISCLAIMER)


def show_medicare_disclaimer():
    """Display before Medicare/IRMAA analysis"""
    st.info(MEDICARE_IRMAA_DISCLAIMER)


# =============================================================================
# API RESPONSE WRAPPER (for Claude API responses)
# =============================================================================

def wrap_ai_response_with_disclaimer(ai_response: str, response_type: str = "chart") -> str:
    """
    Wrap AI-generated responses with appropriate disclaimers
    
    Args:
        ai_response: The AI's response text
        response_type: "chart" or "advisor" or "general"
    
    Returns:
        str: Response with disclaimer prepended/appended
    """
    if response_type == "chart":
        return f"{ai_response}\n\n---\n\n{CHART_EXPLANATION_DISCLAIMER}"
    
    elif response_type == "advisor":
        # For advisor, disclaimer shown once at start of chat
        # But remind periodically (every 5th message)
        return ai_response
    
    else:
        return ai_response


# =============================================================================
# CONSENT TRACKING (Optional - for enhanced compliance)
# =============================================================================

def require_disclaimer_acknowledgment():
    """
    Require user to acknowledge disclaimer before using app
    Store acknowledgment in session state
    
    Returns:
        bool: True if acknowledged, False if not yet acknowledged
    """
    if 'disclaimer_acknowledged' not in st.session_state:
        st.session_state.disclaimer_acknowledged = False
    
    if not st.session_state.disclaimer_acknowledged:
        st.title("⚖️ Before You Begin")
        
        st.markdown(PRIMARY_DISCLAIMER)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            acknowledge = st.checkbox(
                "✅ I have read and understand the disclaimer above. I acknowledge that "
                "ForeCash is an educational planning tool and does NOT provide financial advice.",
                key="disclaimer_checkbox"
            )
            
            if st.button("Continue to ForeCash", disabled=not acknowledge, type="primary"):
                st.session_state.disclaimer_acknowledged = True
                st.rerun()
        
        st.stop()
    
    return True


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
USAGE IN app.py:
----------------

import disclaimers

# At top of app (after password check)
disclaimers.require_disclaimer_acknowledgment()

# In sidebar
disclaimers.show_data_privacy_notice()
disclaimers.show_primary_disclaimer(location="sidebar")

# Before simulation results
if results:
    disclaimers.show_simulation_results_disclaimer()
    # ... display charts

# Before Monte Carlo
if show_monte_carlo:
    disclaimers.show_monte_carlo_disclaimer()
    # ... display MC charts

# In AI advisor section
if show_ai_advisor:
    disclaimers.show_ai_advisor_disclaimer()
    # ... display chat interface

# Before tax features
if show_tax_optimization:
    disclaimers.show_tax_disclaimer()
    # ... display tax features

# Before IRMAA analysis
if show_irmaa:
    disclaimers.show_medicare_disclaimer()
    # ... display IRMAA charts
"""

"""
USAGE IN explain_api_server.py (Flask API):
--------------------------------------------

from disclaimers import wrap_ai_response_with_disclaimer

@app.route('/explain', methods=['POST'])
def explain():
    # ... get AI response from Claude
    
    explanation = message.content[0].text
    
    # Wrap with disclaimer
    final_response = wrap_ai_response_with_disclaimer(
        explanation, 
        response_type="chart"
    )
    
    return jsonify({
        'explanation': final_response,
        'success': True
    })
"""

"""
USAGE IN ai_advisor.py:
-----------------------

import disclaimers

def show_ai_consultation(user_data, financial_data, results):
    st.header("🤖 AI Planning Assistant")
    
    # Show disclaimer FIRST
    disclaimers.show_ai_advisor_disclaimer()
    
    # Initialize messages with system disclaimer
    if 'advisor_messages' not in st.session_state:
        st.session_state.advisor_messages = []
    
    # ... rest of chat interface
"""


# =============================================================================
# COMPLIANCE CHECKLIST FOR DEVELOPMENT
# =============================================================================

COMPLIANCE_CHECKLIST = """
✅ COMPLIANCE IMPLEMENTATION CHECKLIST:
---------------------------------------

MUST HAVE (CRITICAL):
[ ] Primary disclaimer on main app header
[ ] AI advisor disclaimer at start of chat
[ ] Simulation results disclaimer before charts
[ ] Chart explanation disclaimer in API responses
[ ] Data privacy notice in sidebar
[ ] Disclaimer acknowledgment before app access

SHOULD HAVE (IMPORTANT):
[ ] Monte Carlo disclaimer before MC charts
[ ] Tax disclaimer before tax features
[ ] Medicare/IRMAA disclaimer before healthcare analysis
[ ] Periodic reminder in AI chat (every 5 messages)
[ ] Footer disclaimer on every page
[ ] Disclaimer in PDF exports (when implemented)

NICE TO HAVE (BEST PRACTICE):
[ ] Disclaimer version tracking
[ ] Timestamp of last disclaimer review
[ ] User acknowledgment logging (anonymized)
[ ] Professional legal review confirmation
[ ] Quarterly disclaimer update process

ONGOING MAINTENANCE:
[ ] Review disclaimers quarterly
[ ] Update when regulations change
[ ] Monitor competitor disclaimers
[ ] Consult legal counsel annually
[ ] Document all changes
"""


if __name__ == "__main__":
    print("✅ ForeCash Regulatory Disclaimers Module")
    print("=" * 60)
    print("\nThis module provides comprehensive legal disclaimers for:")
    print("  • Main application")
    print("  • AI advisor chat")
    print("  • Chart explanations")
    print("  • Simulation results")
    print("  • Data privacy")
    print("  • Tax and healthcare features")
    print("\n⚠️  CRITICAL: These must be implemented before production use!")
    print("\nSee usage examples at bottom of this file.")
    print("=" * 60)
