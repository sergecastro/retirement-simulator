# File: ai_consult.py
import streamlit as st
from openai import OpenAI
import os
import json
from datetime import datetime
import numpy as np
import pandas as pd
import simulation
import visuals
import financial_utils
import requests  # For web search
from bs4 import BeautifulSoup  # Add: pip install beautifulsoup4 if needed

# Hard-code your correct API key
client = OpenAI(api_key="your_correct_full_api_key_here")  # Replace with your actual OpenAI key

def load_api_key():
    return True

def format_results_for_ai(results):
    formatted = {
        "simulation_summary": {
            "years_simulated": len(results.get('net_worth_list', [])),
            "final_net_worth": results.get('final_net_worth', 0),
            "peak_net_worth": max(results.get('net_worth_list', [0])),
            "min_net_worth": min(results.get('net_worth_list', [0])),
        },
        "key_metrics": {
            "total_income": sum(results.get('total_incomes', [])),
            "total_expenses": sum(results.get('total_expenses_list', [])),
            "rmd_total": sum(results.get('total_rmd_before_tax', [])),
            "health_score": results.get('health_score', 0),
            "savings_rate": results.get('savings_rate', 0),
            "debt_to_income": results.get('debt_to_income', 0),
        },
        "events": results.get('events', {}),
        "monte_carlo": {
            "success_rate": results.get('monte_carlo_results', {}).get('success_rate', 0),
        },
        "goal_achievement": {goal: data['achieved'] for goal, data in results.get('goal_achievement', {}).items()}
    }
    return json.dumps(formatted, indent=2)

def generate_prompt(user_query, formatted_results, user_inputs, web_results=""):
    return f"""
You are a financial advisor AI specializing in family retirement planning.
User's query: {user_query}

Simulation Results (from user form data):
{formatted_results}

User Inputs (detailed form data):
{json.dumps(user_inputs, indent=2)}

Web Search Results (if any):
{web_results}

Provide insightful advice using all data, suggestions for improvements, risks, and recommendations.
Keep response concise, under 500 words. Use bullet points for clarity.
"""

@st.cache_data(ttl=3600)
def call_openai_api(prompt, model="gpt-4o", max_tokens=500, temperature=0.7):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful financial AI consultant."}, {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI API error: {str(e)}")
        return "Error occurred while consulting AI."

def simple_web_search(query):
    try:
        url = f"https://www.bing.com/search?q={query}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('li', class_='b_algo')
        snippets = [li.find('p').text for li in results if li.find('p')]
        return '\n\n'.join(snippets[:5])  # Top 5 clean snippets
    except Exception as e:
        return f"Web search failed: {str(e)}"

def ai_consultation(results, user_inputs):
    if not load_api_key():
        return
    st.subheader("AI Financial Consultation")
    user_query = st.text_area("Ask the AI Advisor:", value="What are the key risks in this retirement plan?")
    include_web = st.checkbox("Include Web Search")
    web_query = st.text_input("Web Search Query (if included):", value=user_query) if include_web else ""
    if st.button("Get AI Advice"):
        with st.spinner("Consulting AI..."):
            web_results = simple_web_search(web_query) if include_web else ""
            formatted_results = format_results_for_ai(results)
            prompt = generate_prompt(user_query, formatted_results, user_inputs, web_results)
            advice = call_openai_api(prompt)
            st.markdown(advice)
            return advice
    return None

def monte_carlo_ai_consult(monte_carlo_results, user_inputs):
    if not load_api_key():
        return
    st.subheader("AI Insights on Monte Carlo Simulations")
    query = "Analyze the Monte Carlo results for potential improvements."
    formatted = format_results_for_ai({"monte_carlo_results": monte_carlo_results})
    prompt = generate_prompt(query, formatted, user_inputs)
    advice = call_openai_api(prompt, max_tokens=300)
    st.markdown(advice)
    return advice

def export_ai_advice(advice, scenario_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{scenario_name}_ai_advice_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(advice)
    st.download_button("Download AI Advice", data=advice, file_name=filename)

def auto_optimization(results, user_inputs):
    st.subheader("AI Auto-Optimization")
    if not load_api_key():
        return
    with st.spinner("Analyzing for optimizations..."):
        formatted_results = format_results_for_ai(results)
        opt_prompt = f"""Analyze the simulation for optimizations. Suggest 3-5 actionable tweaks to improve health score, MC success rate, or goal achievement.
        For each, estimate impact (e.g., +10% success). Format as JSON list: [{{"suggestion": "text", "action": "adjust_expenses -10", "impact": "+15% success"}}]
        Results: {formatted_results} Inputs: {json.dumps(user_inputs, indent=2)}"""
        opt_response = call_openai_api(opt_prompt, max_tokens=400)
        try:
            suggestions = json.loads(opt_response)
        except:
            suggestions = []  # Fallback rule-based
            if results['health_score'] < 70:
                suggestions.append({"suggestion": "Increase monthly savings by $500", "action": "adjust_income +500", "impact": "+10 health score"})
            if results.get('monte_carlo_results', {}).get('success_rate', 0) < 80:
                suggestions.append({"suggestion": "Reduce expenses by 10%", "action": "adjust_expenses -10", "impact": "+15% MC success"})
        if suggestions:
            st.write("Suggested Optimizations:")
            for sug in suggestions:
                col1, col2 = st.columns([3,1])
                with col1:
                    st.write(f"- {sug['suggestion']} (Est. impact: {sug['impact']})")
                with col2:
                    if st.button("Apply", key=f"apply_{sug['suggestion']}"):
                        # Parse action and update inputs
                        action_parts = sug['action'].split()
                        if len(action_parts) == 2:
                            param, value = action_parts
                            value = float(value)
                            if param == "adjust_expenses":
                                st.session_state['total_expenses'] = user_inputs['total_expenses'] * (1 + value / 100)
                            elif param == "adjust_income":
                                st.session_state['total_income'] = user_inputs['total_income'] + value
                            # Re-run sim
                            updated_results = simulation.run_simulation(**st.session_state.get('sim_params', user_inputs))  # Assume params stored
                            st.experimental_rerun()  # Refresh app with new results

def stress_tests(results, user_inputs):
    st.subheader("AI Stress Tests / What-If Scenarios")
    scenarios = {
        "Market Crash": {"return_adj": -20, "duration": 2, "desc": "-20% returns for 2 years"},
        "Health Event": {"expenses_adj": 50000, "duration": 1, "desc": "+$50k one-time expense"},
        "Job Loss": {"income_adj": -50, "duration": 1, "desc": "-50% income for 1 year"},
        "High Inflation": {"inflation_adj": 2, "duration": 5, "desc": "+2% inflation for 5 years"}
    }
    for name, params in scenarios.items():
        with st.expander(f"Run {name} Stress Test"):
            if st.button(f"Simulate {name}"):
                with st.spinner(f"Running {name}..."):
                    # Modify inputs for scenario
                    temp_inputs = user_inputs.copy()
                    if "return_adj" in params:
                        temp_inputs['investment_return_rate'] += params['return_adj']  # Simplified; apply to first duration years in sim
                    if "expenses_adj" in params:
                        temp_inputs['total_expenses'] += params['expenses_adj']
                    if "income_adj" in params:
                        temp_inputs['total_income'] *= (1 + params['income_adj'] / 100)
                    if "inflation_adj" in params:
                        temp_inputs['inflation_rate'] += params['inflation_adj']
                    stress_results = simulation.run_simulation(**temp_inputs, mc_iterations=100)  # Force MC
                    st.write(f"Success Rate: {stress_results['monte_carlo_results']['success_rate']}% (Base: {results['monte_carlo_results'].get('success_rate', 'N/A')}%)")
                    visuals.show_monte_carlo(stress_results)  # Histogram & fan
                    if load_api_key():
                        insight = call_openai_api(f"Analyze stress test impact: {format_results_for_ai(stress_results)}", max_tokens=200)
                        st.markdown(insight)

def integrate_ai_section(results, user_inputs, scenario_name):
    with st.container():
        tab1, tab2, tab3 = st.tabs(["General Advice", "Auto-Optimization", "Stress Tests"])
        with tab1:
            advice = ai_consultation(results, user_inputs)
            if 'monte_carlo_results' in results:
                mc_advice = monte_carlo_ai_consult(results['monte_carlo_results'], user_inputs)
            if advice or mc_advice:
                full_advice = (advice or "") + "\n\n" + (mc_advice or "")
                export_ai_advice(full_advice, scenario_name)
        with tab2:
            auto_optimization(results, user_inputs)
        with tab3:
            stress_tests(results, user_inputs)