"""
Explanation API Server - Claude-powered chart explanations
Runs standalone on port 8502, serves multiple Streamlit apps
Production-ready with environment variable support
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# IMPROVED: Explicit CORS for multiple Streamlit ports + production
# In production, set ALLOWED_ORIGINS environment variable
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 
    'http://localhost:8501,http://localhost:8502,http://localhost:8503,http://localhost:8504,http://localhost:8505'
).split(',')

CORS(app, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    print("WARNING: ANTHROPIC_API_KEY not found in environment!")
    print("   Please ensure .env file exists with ANTHROPIC_API_KEY")
else:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print("OK: Anthropic API key loaded successfully")


@app.route('/explain', methods=['POST', 'OPTIONS'])
def explain():
    """
    Receive a prompt from frontend and return Claude's explanation
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Check if API key is available
        if not ANTHROPIC_API_KEY:
            return jsonify({
                'error': 'API key not configured',
                'success': False
            }), 500
        
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided', 'success': False}), 400
        
        print(f"[API] Received request - Prompt length: {len(prompt)} chars")
        
        # Call Claude API
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        explanation = message.content[0].text
        
        print(f"[API] OK: Generated explanation ({len(explanation)} chars)")
        
        return jsonify({
            'explanation': explanation,
            'success': True
        })
        
    except anthropic.APIError as e:
        print(f"[API] ERROR: Anthropic API Error: {e}")
        return jsonify({
            'error': f'Claude API error: {str(e)}',
            'success': False
        }), 500

    except Exception as e:
        print(f"[API] ERROR: Unexpected Error: {e}")
        return jsonify({
            'error': f'Server error: {str(e)}',
            'success': False
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    api_key_status = "configured" if ANTHROPIC_API_KEY else "missing"
    
    return jsonify({
        'status': 'healthy',
        'port': 8502,
        'api_key': api_key_status,
        'allowed_origins': ALLOWED_ORIGINS
    })


if __name__ == '__main__':
    # Railway sets PORT environment variable, fallback to 8502 for local dev
    port = int(os.getenv('PORT', 8502))

    print("\n" + "="*60)
    print("EXPLANATION API SERVER STARTING")
    print("="*60)
    print(f"Running on: http://localhost:{port}")
    print(f"Health check: http://localhost:{port}/health")
    print(f"Explain endpoint: http://localhost:{port}/explain")
    print(f"CORS enabled for origins:")
    for origin in ALLOWED_ORIGINS:
        print(f"   - {origin}")
    print("="*60 + "\n")

    # Run server - bind to 0.0.0.0 for Railway/cloud deployment
    app.run(host='0.0.0.0', port=port, debug=False)