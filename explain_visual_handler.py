"""
Explain Visual Handler - Claude-Powered Chart Explanations
Handles communication with Anthropic's Claude API to generate intelligent explanations
for charts, graphs, and tables in the retirement simulator.
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_chart_explanation(chart_data):
    """
    Send chart data to Claude and get back an intelligent explanation.
    
    Args:
        chart_data (dict): Dictionary containing:
            - chart_type: str (e.g., "plotly", "table", "monte_carlo")
            - title: str (chart title or heading)
            - data: dict (chart-specific data like traces, values, labels)
            
    Returns:
        dict: Contains 'success' (bool) and 'explanation' (str) or 'error' (str)
    """
    
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        return {
            "success": False,
            "error": "API key not found. Please check your .env file."
        }
    
    try:
        # Initialize Anthropic client
        client = Anthropic(api_key=api_key)
        
        # Build the prompt based on chart data
        prompt = build_explanation_prompt(chart_data)
        
        # Call Claude API
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the explanation from Claude's response
        explanation = message.content[0].text
        
        return {
            "success": True,
            "explanation": explanation
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error communicating with Claude: {str(e)}"
        }


def build_explanation_prompt(chart_data):
    """
    Build a smart prompt for Claude based on the chart type and data.
    
    Args:
        chart_data (dict): Chart information
        
    Returns:
        str: The prompt to send to Claude
    """
    
    chart_type = chart_data.get("chart_type", "unknown")
    title = chart_data.get("title", "This visualization")
    data = chart_data.get("data", {})
    
    # Build context-aware prompt
    prompt = f"""You are helping explain a retirement planning visualization to a user.

**Chart Title:** {title}

**Chart Type:** {chart_type}

**Chart Data:** {json.dumps(data, indent=2)}

Please provide a clear, friendly explanation that:

1. **What it shows:** Explain what this specific visualization displays (2-3 sentences)
2. **Key insights:** Identify the most important numbers or patterns in THIS data (3-4 bullet points)
3. **What it means:** Explain what these results mean for the user's retirement planning (2-3 sentences)
4. **Example interpretation:** Give one concrete example of how to read/interpret this chart using the actual data shown

Keep your tone warm and educational. Use plain English (avoid jargon). Focus on the SPECIFIC data provided, not generic explanations.

Format your response with clear sections using markdown headers (##) for readability."""

    return prompt


# Quick test function (for debugging only)
def test_handler():
    """Test the handler with sample data"""
    sample_data = {
        "chart_type": "monte_carlo",
        "title": "Monte Carlo Retirement Simulation",
        "data": {
            "total_simulations": 10000,
            "success_rate": 0.87,
            "median_final_balance": 2300000,
            "percentile_25": 1200000,
            "percentile_75": 3800000
        }
    }
    
    result = get_chart_explanation(sample_data)
    
    if result["success"]:
        print("✅ SUCCESS!")
        print("\nExplanation:")
        print(result["explanation"])
    else:
        print("❌ ERROR!")
        print(result["error"])


if __name__ == "__main__":
    # Run test if this file is executed directly
    test_handler()