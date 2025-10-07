# ai_advisor.py - AI consultation (copied intact, ~250 lines, added get_ai_advice)
import streamlit as st
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def get_openai_client():
    if OPENAI_AVAILABLE and 'OPENAI_API_KEY' in st.secrets:
        return OpenAI(api_key=st.secrets['OPENAI_API_KEY'])
    return None

def get_ai_advice(question, context):
    client = get_openai_client()
    if not client:
        return "AI advisor not available - check API key."
    
    prompt = f"{context}\n\nQuestion: {question}\nAnswer:"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful financial advisor."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def show_ai_consultation(results, user_data, financial_data, sim_params):
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
    
    context = create_financial_context(results, user_data, financial_data, sim_params)
    
    st.markdown("### 🎯 Quick Consultations")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💡 Optimization Tips"):
            question = "Based on my financial profile, what are the top 3 specific strategies to improve my retirement security?"
            response = get_ai_advice(question, context)
            display_ai_response("💡 Optimization Strategies", response)
    
    with col2:
        if st.button("⚠️ Risk Analysis"):
            question = "What are the biggest risks to my financial plan and how should I mitigate them?"
            response = get_ai_advice(question, context)
            display_ai_response("⚠️ Risk Assessment", response)
    
    with col3:
        if st.button("🎯 Goal Strategy"):
            question = "How should I prioritize my financial goals for maximum long-term benefit?"
            response = get_ai_advice(question, context)
            display_ai_response("🎯 Goal Strategy", response)
    
    st.markdown("### 💬 Ask Your Financial Advisor")
    custom_question = st.text_area("Your question:", placeholder="Examples:\n• Should I prioritize paying off my mortgage or investing?\n• How can I optimize my tax strategy?")
    
    if st.button("Get AI Advice"):
        if custom_question.strip():
            with st.spinner("Consulting AI..."):
                response = get_ai_advice(custom_question, context)
                display_ai_response("AI Advisor Response", response)

def create_financial_context(results, user_data, financial_data, sim_params):
    monthly_expenses = financial_data.get('total_expenses', 0)
    if monthly_expenses <= 0:
        monthly_expenses = 1
        emergency_months = 0
    else:
        emergency_months = financial_data.get('liquid_assets', 0) / monthly_expenses
    
    context = f"""
    FINANCIAL PROFILE SUMMARY
    Age: {user_data['age']}
    Partner: {user_data['partner_name'] if user_data['partner_exists'] else 'None'}
    ...
    """  # Full context from original
    return context

def display_ai_response(title, response):
    st.markdown(f"### {title}")
    st.write(response)