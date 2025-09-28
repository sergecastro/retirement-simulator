# ai_advisor.py - AI Financial Advisor Module
import streamlit as st
import json

# Check if OpenAI is available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def get_openai_client():
    """Initialize OpenAI client with API key from Streamlit secrets"""
    if OPENAI_AVAILABLE and 'OPENAI_API_KEY' in st.secrets:
        return OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
    return None

def show_ai_consultation(results, user_data, financial_data, sim_params):
    """Main AI consultation interface"""
    st.header("🤖 AI Financial Advisor")
    
    if not OPENAI_AVAILABLE:
        st.warning("OpenAI library not installed. Run: pip install openai")
        return
    
    if 'OPENAI_API_KEY' not in st.secrets:
        st.info("""
        **To enable AI features:**
        1. Create `.streamlit/secrets.toml` file
        2. Add: `OPENAI_API_KEY = "your-api-key"`
        3. Restart the app
        """)
        return
    
    # Create financial context
    context = create_financial_context(results, user_data, financial_data, sim_params)
    
    # Quick consultation buttons
    st.markdown("### 🎯 Quick Consultations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💡 Optimization Tips", use_container_width=True):
            question = "Based on my financial profile, what are the top 3 specific strategies to improve my retirement security?"
            response = get_ai_advice(question, context)
            display_ai_response("💡 Optimization Strategies", response)
    
    with col2:
        if st.button("⚠️ Risk Analysis", use_container_width=True):
            question = "What are the biggest risks to my financial plan and how should I mitigate them?"
            response = get_ai_advice(question, context)
            display_ai_response("⚠️ Risk Assessment", response)
    
    with col3:
        if st.button("🎯 Goal Strategy", use_container_width=True):
            question = "How should I prioritize my financial goals for maximum long-term benefit?"
            response = get_ai_advice(question, context)
            display_ai_response("🎯 Goal Strategy", response)
    
    # Custom questions
    st.markdown("### 💬 Ask Your Financial Advisor")
    
    custom_question = st.text_area(
        "Your question:",
        placeholder="Examples:\n• Should I prioritize paying off my mortgage or investing?\n• How can I optimize my tax strategy?\n• What's the best way to save for my children's education?\n• How do I balance retirement savings with current lifestyle?",
        height=100
    )
    
    if st.button("Get AI Advice", type="primary"):
        if custom_question.strip():
            with st.spinner("Consulting AI advisor..."):
                response = get_ai_advice(custom_question, context)
                display_ai_response("AI Advisor Response", response)
        else:
            st.warning("Please enter a question first")
    
    # Auto-optimization suggestions
    if st.checkbox("Show Auto-Optimization Suggestions"):
        show_auto_optimizations(results, financial_data, context)
    
    # Stress test insights
    if st.checkbox("Show AI Stress Test Analysis"):
        show_stress_test_insights(context)

def create_financial_context(results, user_data, financial_data, sim_params):
    """Create comprehensive context for AI advisor"""
    
    # SAFETY CHECK - Prevent division by zero errors
    monthly_expenses = financial_data.get('total_expenses', 0)
    if monthly_expenses <= 0:
        monthly_expenses = 1  # Set minimum to prevent division by zero
        emergency_months = 0  # If no expenses, no emergency fund needed
    else:
        emergency_months = financial_data.get('liquid_assets', 0) / (monthly_expenses * 12) * 12
    
    annual_income = financial_data.get('total_income', 0) * 12
    if annual_income <= 0:
        annual_income = 1  # Prevent division by zero
    
    context = f"""
FINANCIAL PROFILE SUMMARY
========================
Age: {user_data['age']}
Partner: {user_data['partner_name'] if user_data['partner_exists'] else 'None'}
Partner Age: {user_data.get('partner_age', 'N/A') if user_data['partner_exists'] else 'N/A'}

CURRENT FINANCIAL POSITION
=========================
Monthly Income: ${financial_data.get('total_income', 0):,.2f}
Monthly Expenses: ${monthly_expenses:,.2f}
Monthly Surplus: ${financial_data.get('monthly_surplus', 0):,.2f}
Liquid Assets: ${financial_data.get('liquid_assets', 0):,.2f}
Total Liabilities: ${financial_data.get('total_liabilities', 0):,.2f}
Emergency Fund: {emergency_months:.1f} months

SIMULATION RESULTS
==================
Projection Period: {sim_params['simulation_years']} years
Final Savings: ${results.get('final_savings', 0):,.2f}
Years Solvent: {results.get('years_solvent', 0)} of {sim_params['simulation_years']}
Success Rate: {results.get('monte_carlo_results', {}).get('success_rate', 'N/A')}%

ASSUMPTIONS
===========
Tax Rate: {sim_params['tax_rate']}%
Inflation Rate: {sim_params['inflation_rate']}%
Investment Return: {sim_params['investment_return_rate']}%

RETIREMENT ACCOUNTS
==================
IRA Balance: ${financial_data.get('ira_balance', 0):,.2f}
401k Balance: ${financial_data.get('four01k_403b_balance', 0):,.2f}
Partner IRA: ${financial_data.get('partner_ira_balance', 0):,.2f}
Partner 401k: ${financial_data.get('partner_four01k_403b_balance', 0):,.2f}
"""
    return context

def get_ai_advice(question, context):
    """Get advice from AI advisor"""
    try:
        client = get_openai_client()
        if not client:
            return "AI advisor unavailable. Please check API key configuration."
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert financial advisor providing personalized retirement planning advice. 
                    Provide specific, actionable recommendations based on the client's detailed financial data. 
                    Be concise but thorough. Format responses with clear headers and bullet points for readability."""
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}"
                }
            ],
            max_tokens=800,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting AI advice: {str(e)}"

def display_ai_response(title, response):
    """Display AI response in formatted container"""
    with st.container():
        st.markdown(f"### {title}")
        st.markdown(response)
        
        # Option to copy response
        if st.button("📋 Copy to Clipboard", key=f"copy_{title}"):
            st.write("Response copied!")
            st.code(response, language=None)

def show_auto_optimizations(results, financial_data, context):
    """Show automated optimization suggestions"""
    st.subheader("🔧 Auto-Optimization Analysis")
    
    question = """Analyze this financial profile and provide:
    1. Three high-impact optimizations with specific dollar amounts
    2. Expected improvement for each change
    3. Implementation timeline
    Format as actionable steps with measurable outcomes."""
    
    with st.spinner("Generating optimizations..."):
        response = get_ai_advice(question, context)
        
        # Parse and display optimizations
        st.markdown("### 📈 Recommended Optimizations")
        st.markdown(response)
        
        # Action buttons for each optimization
        if st.button("Apply Suggested Optimizations"):
            st.info("Optimization changes would be applied to your scenario here")

def show_stress_test_insights(context):
    """Show AI insights on stress scenarios"""
    st.subheader("🔥 AI Stress Test Analysis")
    
    scenarios = {
        "Market Crash": "How would a 40% market decline affect this plan?",
        "Job Loss": "What's the impact of 1 year unemployment?",
        "Medical Crisis": "How would a $100,000 medical expense affect retirement?",
        "High Inflation": "What if inflation averages 7% for 5 years?"
    }
    
    selected = st.selectbox("Select Stress Scenario:", list(scenarios.keys()))
    
    if st.button(f"Analyze {selected} Impact"):
        question = f"{scenarios[selected]} Provide specific numbers and recovery strategies."
        
        with st.spinner(f"Analyzing {selected} scenario..."):
            response = get_ai_advice(question, context)
            display_ai_response(f"{selected} Analysis", response)

def generate_action_plan(results, financial_data):
    """Generate personalized action plan"""
    st.subheader("📋 Personalized Action Plan")
    
    if st.button("Generate My Action Plan"):
        context = create_financial_context(results, {}, financial_data, {})
        
        question = """Create a prioritized 12-month action plan with:
        1. Monthly specific tasks
        2. Target amounts and deadlines
        3. Key milestones to track
        Focus on highest impact items first."""
        
        with st.spinner("Creating your personalized action plan..."):
            response = get_ai_advice(question, context)
            
            st.markdown("### Your 12-Month Financial Action Plan")
            st.markdown(response)
            
            # Download option
            st.download_button(
                "📥 Download Action Plan",
                response,
                "financial_action_plan.md",
                "text/markdown"
            )

def show_tax_optimization(financial_data):
    """Show tax optimization strategies"""
    st.subheader("💰 Tax Optimization Strategies")
    
    context = f"""
    Retirement Accounts: ${financial_data.get('ira_balance', 0) + financial_data.get('four01k_403b_balance', 0):,.0f}
    Taxable Accounts: ${financial_data.get('taxable_investment_accounts', 0):,.0f}
    Current Tax Rate: {st.session_state.get('input_tax_rate', 22)}%
    """
    
    if st.button("Get Tax Optimization Advice"):
        question = "What tax strategies should I implement for retirement accounts, Roth conversions, and withdrawal sequencing?"
        
        with st.spinner("Analyzing tax strategies..."):
            response = get_ai_advice(question, context)
            display_ai_response("Tax Optimization Strategies", response)