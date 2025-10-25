# ai_advisor.py - AI Planning Assistant Module
# Direct Claude API integration (no Flask server needed)
# Bulletproof error handling, context-aware responses, proactive recommendations

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json
import disclaimers  # Regulatory compliance

# We'll use the Anthropic SDK if available, with fallback to requests
try:
    import anthropic
    ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    ANTHROPIC_SDK_AVAILABLE = False
    import requests


# ============================================
# CONFIGURATION & SETUP
# ============================================

def get_api_key() -> Optional[str]:
    """
    Get Claude API key from Streamlit secrets or environment variables.
    Supports multiple possible key names for flexibility.
    Cloud deployment (Render) uses environment variables.
    Local development can use secrets.toml or environment variables.
    """
    import os

    # First try environment variables (for Render deployment)
    env_keys = ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY']
    for key_name in env_keys:
        value = os.getenv(key_name)
        if value:
            return value

    # Fallback to Streamlit secrets (for local development)
    possible_keys = [
        'ANTHROPIC_API_KEY',
        'CLAUDE_API_KEY',
        'anthropic_api_key',
        'claude_api_key'
    ]

    for key_name in possible_keys:
        try:
            if key_name in st.secrets:
                return st.secrets[key_name]
        except:
            pass  # secrets.toml doesn't exist, continue

    return None


def test_claude_connection() -> Tuple[bool, str]:
    """
    Test Claude API connection.
    Returns: (success: bool, message: str)
    """
    api_key = get_api_key()
    
    if not api_key:
        return False, "❌ No API key found in secrets. Add ANTHROPIC_API_KEY to .streamlit/secrets.toml"
    
    try:
        if ANTHROPIC_SDK_AVAILABLE:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                messages=[{"role": "user", "content": "Reply with: Connection successful!"}]
            )
            return True, "✅ Claude API connected successfully!"
        else:
            # Fallback to requests
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            data = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Reply with: Connection successful!"}]
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                return True, "✅ Claude API connected successfully!"
            else:
                return False, f"❌ API error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return False, f"❌ Connection test failed: {str(e)}"


# ============================================
# CONTEXT ASSEMBLY
# ============================================

def assemble_user_context(user_data: Dict, financial_data: Dict, sim_params: Dict, results: Dict) -> str:
    """
    Assemble complete user context for Claude.
    This is the "brain" - Claude needs to know EVERYTHING about the user.
    """
    
    # Extract key information
    age = user_data.get('age', 'Unknown')
    partner_exists = user_data.get('partner_exists', False)
    partner_age = user_data.get('partner_age', age)
    partner_name = user_data.get('partner_name', 'Partner')
    
    # Financial snapshot
    total_income = financial_data.get('total_income', 0)
    total_expenses = financial_data.get('total_expenses', 0)
    liquid_assets = financial_data.get('liquid_assets', 0)
    total_assets = financial_data.get('total_assets', 0)
    total_liabilities = financial_data.get('total_liabilities', 0)
    net_worth = total_assets - total_liabilities
    monthly_surplus = total_income - total_expenses
    
    # Simulation results
    final_savings = results.get('final_savings', 0)
    final_net_worth = results.get('final_net_worth', 0)
    years_solvent = results.get('years_solvent', 0)
    health_score = results.get('health_score', 0)
    
    # Build context string
    context = f"""
# USER FINANCIAL PROFILE

## Demographics
- **Your Age**: {age}
- **Partner**: {"Yes" if partner_exists else "No"}
"""
    
    if partner_exists:
        context += f"- **Partner Name**: {partner_name}\n"
        context += f"- **Partner Age**: {partner_age}\n"
    
    context += f"""
## Current Financial Situation
- **Annual Income**: ${total_income:,.0f}
- **Annual Expenses**: ${total_expenses:,.0f}
- **Monthly Surplus**: ${monthly_surplus:,.0f}
- **Liquid Assets**: ${liquid_assets:,.0f}
- **Total Assets**: ${total_assets:,.0f}
- **Total Liabilities**: ${total_liabilities:,.0f}
- **Net Worth**: ${net_worth:,.0f}

## Simulation Parameters
- **Tax Rate**: {sim_params.get('tax_rate', 0)}%
- **Inflation Rate**: {sim_params.get('inflation_rate', 0)}%
- **Investment Return Rate**: {sim_params.get('investment_return_rate', 0)}%
- **Simulation Years**: {sim_params.get('simulation_years', 0)}

## Simulation Results
- **Final Savings**: ${final_savings:,.0f}
- **Final Net Worth**: ${final_net_worth:,.0f}
- **Years Solvent**: {years_solvent}
- **Financial Health Score**: {health_score}/100

## Additional Context
"""
    
    # Add children/family events if available
    if 'children_list' in st.session_state and st.session_state['children_list']:
        context += "\n### Children & Education Planning:\n"
        for idx, child in enumerate(st.session_state['children_list'], 1):
            name = child.get('Name', f'Child {idx}')
            birth_year = child.get('Birth Year', 'Unknown')
            college_plan = child.get('College Plan', 'None')
            context += f"- {name} (Born {birth_year}): {college_plan}\n"
    
    # Add inheritances if available
    if 'inheritance_list' in st.session_state and st.session_state['inheritance_list']:
        context += "\n### Expected Inheritances:\n"
        for inh in st.session_state['inheritance_list']:
            year = inh.get('Year', 'Unknown')
            amount = inh.get('Amount', 0)
            context += f"- Year {year}: ${amount:,.0f}\n"
    
    # Add retirement accounts if available
    ira = financial_data.get('ira_balance', 0)
    k401 = financial_data.get('four01k_403b_balance', 0)
    if ira > 0 or k401 > 0:
        context += "\n### Retirement Accounts:\n"
        if ira > 0:
            context += f"- IRA Balance: ${ira:,.0f}\n"
        if k401 > 0:
            context += f"- 401(k)/403(b) Balance: ${k401:,.0f}\n"
    
    return context


def build_system_prompt() -> str:
    """
    Build the system prompt that defines Claude's role and behavior.
    This makes Claude act as a professional financial advisor.
    """
    return """You are an expert CFP®-level AI Planning Assistant. 

Your role is to provide personalized, actionable financial advice based on the user's COMPLETE financial profile (which will be provided in context).

## Your Communication Style:
- **Always be specific, never generic**: Use the user's actual numbers, not examples
- **Always quantify impact**: Show how recommendations affect their retirement plan (dollars, years, percentages)
- **Always explain trade-offs**: There's rarely one "right" answer - explain pros/cons
- **Always acknowledge their goals**: Reference what they've told you about priorities
- **Always offer multiple options**: Let them choose based on their values
- **Be warm but professional**: Friendly, empathetic, but never cavalier about serious decisions

## Critical Rules:
1. **Use THEIR data, not examples**: Say "Your mortgage is $280k at 5%" not "If someone has a mortgage..."
2. **Quantify everything**: "This improves your success rate from 82% to 87%" not "This helps"
3. **Explain WHY**: Don't just recommend, explain the reasoning
4. **Flag uncertainty**: If you don't have enough info, ask clarifying questions
5. **No stock picks**: Never recommend specific stocks, crypto, or individual securities
6. **Encourage professional review**: For major decisions (>$50k impact), suggest consulting a CPA/CFP
7. **Include disclaimers**: Remind that this is educational, not professional financial advice

## Disclaimer (include at end of each response):
⚠️ *This analysis is for educational purposes only and does not constitute professional financial, tax, or legal advice. Consult a licensed CFP®, CPA, or attorney before making major financial decisions.*

## Your Goal:
Help users make BETTER financial decisions by providing context-aware, personalized, actionable advice they can't get from generic internet articles or simple calculators.
"""


# ============================================
# CLAUDE API INTEGRATION
# ============================================

def call_claude_api(user_message: str, context: str, conversation_history: List[Dict] = None) -> Optional[str]:
    """
    Call Claude API with user question + full context.
    Returns AI response or None if error.
    """
    api_key = get_api_key()
    
    if not api_key:
        st.error("❌ No API key configured. Add ANTHROPIC_API_KEY to .streamlit/secrets.toml")
        return None
    
    # Build the full prompt
    full_prompt = f"""{context}

---

# USER QUESTION:
{user_message}

# YOUR RESPONSE:
Provide a personalized, actionable answer based on the financial profile above. Use specific numbers from their data.
"""
    
    # Prepare messages for Claude
    messages = []
    
    # Add conversation history if available
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current question
    messages.append({
        "role": "user",
        "content": full_prompt
    })
    
    try:
        if ANTHROPIC_SDK_AVAILABLE:
            # Use official Anthropic SDK
            client = anthropic.Anthropic(api_key=api_key)
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=build_system_prompt(),
                messages=messages
            )
            
            # Extract text from response
            return response.content[0].text
        
        else:
            # Fallback to requests library
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "system": build_system_prompt(),
                "messages": messages
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                st.error(f"❌ API Error: {response.status_code} - {response.text}")
                return None
    
    except anthropic.APIConnectionError:
        st.error("❌ Network connection error. Check your internet connection and try again.")
        return None
    except anthropic.RateLimitError:
        st.warning("⚠️ API rate limit reached. Please wait 60 seconds and try again.")
        return None
    except Exception as e:
        st.error(f"❌ Error calling Claude API: {str(e)}")
        return None


# ============================================
# PROACTIVE RECOMMENDATIONS
# ============================================

def generate_proactive_recommendations(context: str, results: Dict) -> Optional[str]:
    """
    Generate proactive recommendations by having Claude analyze the user's plan.
    """
    health_score = results.get('health_score', 0)
    years_solvent = results.get('years_solvent', 0)
    final_savings = results.get('final_savings', 0)
    
    analysis_prompt = f"""{context}

---

# TASK: Proactive Financial Analysis

Analyze this user's complete financial plan and identify 3-5 specific opportunities or concerns.

Focus on:
1. **Inefficiencies**: Are they paying too much tax? Missing opportunities?
2. **Risks**: Low success rate? Concentrated assets? Timing issues?
3. **Opportunities**: Can they improve outcomes with specific changes?

For each insight:
- **State the issue/opportunity clearly**
- **Quantify the impact** (dollars, years, percentages)
- **Recommend specific action** (what should they do?)
- **Explain why** (reasoning behind recommendation)

Format as a numbered list with clear, actionable items.

Their current metrics:
- Health Score: {health_score}/100
- Years Solvent: {years_solvent}
- Final Savings: ${final_savings:,.0f}
"""
    
    try:
        api_key = get_api_key()
        if not api_key:
            return None
        
        if ANTHROPIC_SDK_AVAILABLE:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                system=build_system_prompt(),
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            return response.content[0].text
        else:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            data = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 3000,
                "system": build_system_prompt(),
                "messages": [{"role": "user", "content": analysis_prompt}]
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=60
            )
            if response.status_code == 200:
                return response.json()['content'][0]['text']
    except:
        return None


# ============================================
# CHAT INTERFACE
# ============================================

def show_ai_consultation(results: Dict, user_data: Dict, financial_data: Dict, sim_params: Dict):
    """
    Main function called by app.py to show AI Planning Assistant interface.
    This is what appears when users enable the AI Planning Assistant feature.
    """
    st.header("🤖 AI Planning Assistant")
    st.markdown("*Ask any financial question and get personalized advice based on your complete financial profile.*")

    # ✅ REGULATORY COMPLIANCE: Show AI advisor disclaimer
    disclaimers.show_ai_advisor_disclaimer()

    # Test API connection on first load
    if 'ai_advisor_tested' not in st.session_state:
        with st.spinner("Testing Claude API connection..."):
            success, message = test_claude_connection()
            if success:
                st.success(message)
                st.session_state['ai_advisor_tested'] = True
            else:
                st.error(message)
                st.info("💡 **How to fix:**\n1. Create file: `.streamlit/secrets.toml`\n2. Add: `ANTHROPIC_API_KEY = \"your-key-here\"`\n3. Restart app")
                return
    
    # Initialize conversation history
    if 'ai_conversation' not in st.session_state:
        st.session_state['ai_conversation'] = []
    
    # Assemble user context (this is what makes responses personalized)
    context = assemble_user_context(user_data, financial_data, sim_params, results)
    
    # ============================================
    # PROACTIVE RECOMMENDATIONS SECTION
    # ============================================
    with st.expander("💡 **Proactive Insights** (Click to see what Claude noticed about your plan)", expanded=False):
        if st.button("🔍 Analyze My Plan", key="analyze_plan_btn"):
            with st.spinner("Analyzing your financial plan..."):
                recommendations = generate_proactive_recommendations(context, results)
                if recommendations:
                    st.markdown(recommendations)
                    st.session_state['proactive_recommendations'] = recommendations
                else:
                    st.error("Could not generate recommendations. Check API connection.")
        
        # Show cached recommendations if available
        if 'proactive_recommendations' in st.session_state:
            st.markdown(st.session_state['proactive_recommendations'])
    
    # ============================================
    # CONVERSATION HISTORY
    # ============================================
    st.markdown("---")
    st.subheader("💬 Ask Me Anything")
    
    # Display conversation history
    if st.session_state['ai_conversation']:
        for idx, msg in enumerate(st.session_state['ai_conversation']):
            if msg['role'] == 'user':
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**AI Assistant:**\n\n{msg['content']}")

                # Voice feature - Read Aloud
                from features.ai_voice_handler import create_voice_player
                create_voice_player(msg['content'], f"voice_{idx}")

            st.markdown("---")
    else:
        st.info("👋 **Hi! I'm your AI Planning Assistant.**\n\nI've analyzed your complete financial profile. Ask me anything:\n- Should I buy or lease my next car?\n- Can I afford to retire early?\n- Should I pay off my mortgage or invest?\n- How can I reduce my taxes?\n- What's the impact of [any life decision] on my retirement?")
    
    # ============================================
    # EXAMPLE QUESTIONS (Quick Starts)
    # ============================================
    with st.expander("📝 Example Questions (Click any to ask)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Should I pay off my mortgage early?", key="q1"):
                st.session_state['ai_input'] = "Should I pay off my mortgage early or invest the money instead?"
                st.rerun()
            if st.button("Can I afford to retire 2 years earlier?", key="q2"):
                st.session_state['ai_input'] = "What would happen if I retired 2 years earlier than planned?"
                st.rerun()
            if st.button("Should I do Roth conversions?", key="q3"):
                st.session_state['ai_input'] = "Should I do Roth IRA conversions? When and how much?"
                st.rerun()
        
        with col2:
            if st.button("Buy or lease my next car?", key="q4"):
                st.session_state['ai_input'] = "Should I buy or lease my next car? Which is better for my situation?"
                st.rerun()
            if st.button("How can I improve my plan?", key="q5"):
                st.session_state['ai_input'] = "What are the top 3 things I should do to improve my retirement plan?"
                st.rerun()
            if st.button("What if I need to help my kids?", key="q6"):
                st.session_state['ai_input'] = "What if I need to help my children with a down payment or college costs?"
                st.rerun()
    
    # ============================================
    # USER INPUT
    # ============================================
    user_input = st.text_area(
        "Your Question:",
        value=st.session_state.get('ai_input', ''),
        height=100,
        placeholder="Type your question here... (e.g., 'Should I pay off my mortgage or invest?')",
        key="ai_question_input"
    )
    
    # Clear the pre-filled input after it's shown
    if 'ai_input' in st.session_state:
        del st.session_state['ai_input']
    
    col1, col2 = st.columns([3, 1])
    with col1:
        ask_button = st.button("💬 Ask AI Assistant", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state['ai_conversation'] = []
            st.rerun()
    
    # ============================================
    # PROCESS QUESTION
    # ============================================
    if ask_button and user_input.strip():
        # Add user question to history
        st.session_state['ai_conversation'].append({
            'role': 'user',
            'content': user_input
        })
        
        # Get AI response
        with st.spinner("🤔 Thinking... (this may take 5-10 seconds)"):
            # Prepare conversation history for Claude
            claude_history = []
            for msg in st.session_state['ai_conversation'][:-1]:  # Exclude the question we just added
                claude_history.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            
            # Call Claude API
            response = call_claude_api(user_input, context, claude_history)
            
            if response:
                # Add AI response to history
                st.session_state['ai_conversation'].append({
                    'role': 'assistant',
                    'content': response
                })
                st.rerun()
            else:
                st.error("❌ Failed to get response from AI. Please try again.")
    
    elif ask_button:
        st.warning("⚠️ Please enter a question first.")
    
    # ============================================
    # FOOTER / HELP
    # ============================================
    st.markdown("---")
    st.markdown("""
    **💡 Tips for best results:**
    - Be specific about your situation
    - Ask about real decisions you're considering
    - Include timeframes when relevant (e.g., "in the next 5 years")
    - Ask follow-up questions to dig deeper
    
    **🔒 Privacy:** Your conversation is not stored permanently. It exists only during this session.
    """)
