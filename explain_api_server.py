"""
Simple API server to handle Claude explanations
Runs on port 8502 alongside Streamlit (port 8501)
This fixes the CORS issue by moving API calls to the backend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# FIXED: Explicit CORS configuration to handle preflight requests
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@app.route('/explain', methods=['POST', 'OPTIONS'])
def explain():
    """
    Receive a prompt from the frontend and return Claude's explanation
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        print(f"[API Server] Received explanation request for: {prompt[:100]}...")
        
        # Call Claude API from Python (no CORS issues here!)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        explanation = message.content[0].text
        
        print(f"[API Server] Successfully generated explanation ({len(explanation)} chars)")
        
        return jsonify({
            'explanation': explanation,
            'success': True
        })
        
    except Exception as e:
        print(f"[API Server] Error: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Explanation API server is running'})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 EXPLANATION API SERVER STARTING")
    print("="*60)
    print(f"✅ Running on: http://localhost:8502")
    print(f"✅ Health check: http://localhost:8502/health")
    print(f"✅ Explain endpoint: http://localhost:8502/explain")
    print(f"✅ CORS enabled for all origins")
    print("="*60 + "\n")
    
    app.run(host='localhost', port=8502, debug=True)