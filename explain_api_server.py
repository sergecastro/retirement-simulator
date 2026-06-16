"""
Explanation API Server - Claude-powered chart explanations
Runs standalone on port 8502, serves multiple Streamlit apps
Production-ready with environment variable support
"""

from flask import Flask, request, jsonify
import stripe
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
    'https://app.familyforecast.ai,https://familyforecast.ai,https://www.familyforecast.ai,https://intake.familyforecast.ai,https://familyforecast.lovable.app,https://forcash.onrender.com,http://localhost:8501,http://localhost:8502,http://localhost:8503,http://localhost:8504,http://localhost:8505'
).split(',')

CORS(app, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False,
        "expose_headers": ["Content-Type"],
        "max_age": 3600
    }
})

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ebhzvauommuhqlcswdil.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

if not ANTHROPIC_API_KEY:
    print("WARNING: ANTHROPIC_API_KEY not found in environment!")
    print("   Please ensure .env file exists with ANTHROPIC_API_KEY")
else:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print("OK: Anthropic API key loaded successfully")


# ✅ REGULATORY COMPLIANCE: Chart explanation disclaimer
CHART_EXPLANATION_DISCLAIMER = """

---

**📊 Chart Analysis Disclaimer:**

This explanation is AI-generated for educational purposes only. It analyzes patterns in
your scenario data but does NOT constitute financial advice. Always consult qualified
professionals before making financial decisions based on these projections.
"""


@app.route('/explain', methods=['POST', 'OPTIONS'])
def explain():
    """
    Receive a prompt from frontend and return Claude's explanation
    """
    # Handle preflight OPTIONS request with explicit CORS headers
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response, 200
    
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
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        explanation = message.content[0].text

        # ✅ REGULATORY COMPLIANCE: Wrap explanation with disclaimer
        final_explanation = f"{explanation}{CHART_EXPLANATION_DISCLAIMER}"

        print(f"[API] OK: Generated explanation ({len(explanation)} chars) + disclaimer")

        # Return with explicit CORS headers
        response = jsonify({
            'explanation': final_explanation,
            'success': True
        })
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        return response
        
    except anthropic.APIError as e:
        print(f"[API] ERROR: Anthropic API Error: {e}")
        response = jsonify({
            'error': f'Claude API error: {str(e)}',
            'success': False
        })
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        return response, 500

    except Exception as e:
        print(f"[API] ERROR: Unexpected Error: {e}")
        response = jsonify({
            'error': f'Server error: {str(e)}',
            'success': False
        })
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        return response, 500


# ─────────────────────────────────────────────────────────────────────────────
# COMMAND CENTER API ENDPOINTS
# Receive intake JSON from Lovable, return calculated results
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/cc/summary', methods=['POST', 'OPTIONS'])
def cc_summary():
    """
    Main Command Center endpoint.
    Receives full intake data from Lovable.
    Returns all calculations needed for all 9 screens in one call.
    """
    if request.method == 'OPTIONS':
        return _cors_preflight()

    try:
        data = request.get_json(force=True) or {}
        intake = data.get('intake', {}) or {}

        # The linking key to analysis_results is the frictionless session_id
        # (e.g. "TEMP-XXX") that Streamlit stored after a real Analysis. The Lovable
        # intake payload carries no stable id, so session_id is the shared key.
        # Lovable sends it as session_id (preferred); accept all spellings/locations.
        intake_id = (intake.get('session_id') or intake.get('id')
                     or data.get('session_id') or data.get('intake_id') or data.get('id'))
        # Normalize to canonical uppercase so the read key matches what Streamlit
        # stored on the write side (which applies the same .strip().upper()).
        intake_id = (intake_id or '').strip().upper()

        # No id -> we cannot locate real results. Refuse; NEVER compute proxies.
        if not intake_id:
            return jsonify({
                "success": True,
                "requiresAnalysis": True,
                "message": "Please run Analysis first for accurate numbers.",
                "data": None
            }), 200

        # Read the REAL, engine-computed results that Streamlit saved after Analysis.
        client = _get_cc_supabase()
        if client is None:
            return jsonify({
                "success": False,
                "error": "Results store unavailable. Please try again shortly."
            }), 503

        res = (
            client.table('analysis_results')
            .select('*')
            .eq('intake_id', str(intake_id))
            .order('created_at', desc=True)
            .limit(1)
            .execute()
        )
        rows = res.data or []

        # No saved results yet -> send the user through Analysis. No fake numbers.
        if not rows:
            return jsonify({
                "success": True,
                "requiresAnalysis": True,
                "message": "Please run Analysis first for accurate numbers.",
                "data": None
            }), 200

        row = rows[0]

        # Return ONLY real engine outputs. Fields the engine does not yet compute
        # (tax bracket, IRMAA, RMD) are null so Lovable shows "not yet available" —
        # never a fabricated value.
        data_out = {
            "intakeId": intake_id,
            "computedAt": row.get("created_at"),
            "monthlyCommand": {
                "mcSuccess": row.get("monte_carlo_success_rate"),
                "finalSavings": row.get("final_savings"),
                "safeMonthlySpending": row.get("safe_monthly_spending"),
            },
            "taxOpportunities": {
                "currentBracket": row.get("tax_bracket"),
                "bracketRoom": row.get("bracket_room"),
            },
            "irmaaWatch": {
                "safetyMargin": row.get("irmaa_margin"),
            },
            "rmdForecast": {
                "rmdAt73": row.get("rmd_at_73"),
            },
        }

        return jsonify({
            "success": True,
            "requiresAnalysis": False,
            "data": data_out
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/cc/chat', methods=['POST', 'OPTIONS'])
def cc_chat():
    """
    AI chat endpoint for Command Center.
    Receives user question + intake data, returns Claude response.
    """
    if request.method == 'OPTIONS':
        return _cors_preflight()

    try:
        body         = request.get_json(force=True) or {}
        question     = body.get('question', '')
        intake       = body.get('intake', {})
        history      = body.get('history', [])

        if not question:
            return jsonify({"success": False, "error": "No question provided"}), 400

        # Build context from intake
        name     = intake.get('name', 'the user')
        age      = intake.get('age', 'unknown')
        ira      = _safe_num(intake.get('iraBalance'))
        roth     = _safe_num(intake.get('rothBalance'))
        taxable  = _safe_num(intake.get('taxableInvestments'))
        ss       = _safe_num(intake.get('socialSecurityMonthly'))
        pension  = _safe_num(intake.get('pensionMonthly'))
        expenses = _safe_num(intake.get('monthlyExpenses'))
        ret_age  = intake.get('retirementAge', 'unknown')

        system_prompt = f"""You are a friendly retirement planning advisor inside FamilyForecast.AI Command Center.
You are NOT a licensed financial advisor. Always note that users should consult a professional for major decisions.
Speak in plain English. No jargon without explanation. Be encouraging but honest.
Keep answers to 3-4 paragraphs maximum. Always end with one clear "Next best action" sentence.

User: {name}, Age {age}, retiring at {ret_age}.
IRA: ${ira:,.0f} | Roth: ${roth:,.0f} | Taxable: ${taxable:,.0f}
Social Security: ${ss:,.0f}/month | Pension: ${pension:,.0f}/month
Monthly expenses: ${expenses:,.0f}/month

Always reference their specific numbers. Never invent figures not shown above."""

        messages = history + [{"role": "user", "content": question}]

        import anthropic as ac
        client = ac.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=system_prompt,
            messages=messages
        )
        reply = response.content[0].text

        return jsonify({
            "success": True,
            "reply": reply,
            "history": messages + [{"role": "assistant", "content": reply}]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _get_cc_supabase():
    """
    Supabase client for reading analysis_results. Uses the SERVICE key (bypasses
    RLS) from environment. Returns None if unavailable so callers can degrade
    gracefully instead of crashing.
    """
    try:
        from supabase import create_client
        url = SUPABASE_URL
        key = SUPABASE_SERVICE_KEY
        if not url or not key:
            print("[CC] Supabase URL/SERVICE key missing — cannot read analysis_results")
            return None
        return create_client(url, key)
    except Exception as e:
        print(f"[CC] Supabase client init failed: {type(e).__name__}: {e}")
        return None


def _safe_num(val):
    """Convert any value to float safely."""
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


def _cors_preflight():
    """Standard CORS preflight response."""
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response, 200


# ------------------------------------------------------------------
# Stripe subscription lifecycle — helpers
# ------------------------------------------------------------------

# Maps Stripe subscription.status → our `subscriptions.status` column.
# See https://stripe.com/docs/api/subscriptions/object#subscription_object-status
SUBSCRIPTION_STATUS_MAP = {
    'active': 'active',
    'trialing': 'active',
    'past_due': 'past_due',
    'unpaid': 'past_due',
    'paused': 'past_due',
    'canceled': 'canceled',
    'incomplete': 'incomplete',
    'incomplete_expired': 'canceled',
}


def _map_status(stripe_status: str) -> str:
    return SUBSCRIPTION_STATUS_MAP.get(stripe_status, 'incomplete')


def _iso_from_unix(ts) -> str:
    """Convert Stripe unix timestamp (seconds) to ISO-8601 UTC string."""
    if not ts:
        return ""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()


def upsert_subscription(
    user_email: str,
    stripe_customer_id: str = "",
    stripe_subscription_id: str = "",
    status: str = "active",
    current_period_end: str = "",
    price_id: str = "",
) -> bool:
    """
    Upsert a row in Supabase `subscriptions` keyed by user_email.
    Returns True on HTTP 200/201, False otherwise.
    """
    if not user_email or not SUPABASE_SERVICE_KEY:
        print(f"[WEBHOOK] ⚠️ Missing email or service key (email={user_email!r})")
        return False
    try:
        import requests as req
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates',
        }
        data = {
            'user_email': user_email.lower().strip(),
            'stripe_customer_id': stripe_customer_id,
            'stripe_subscription_id': stripe_subscription_id,
            'status': status,
            'updated_at': 'now()',
        }
        if current_period_end:
            data['current_period_end'] = current_period_end
        if price_id:
            data['price_id'] = price_id
        response = req.post(
            f'{SUPABASE_URL}/rest/v1/subscriptions',
            headers=headers,
            json=data,
        )
        if response.status_code in [200, 201]:
            print(f"[WEBHOOK] ✅ upsert status={status} email={user_email}")
            return True
        print(f"[WEBHOOK] ❌ Supabase {response.status_code}: {response.text}")
        return False
    except Exception as e:
        print(f"[WEBHOOK] ❌ Exception in upsert_subscription: {e}")
        return False


@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Stripe webhook endpoint — handles subscription lifecycle events.
    Writes all status transitions to Supabase `subscriptions` table.

    Handled events:
      - checkout.session.completed    → status='active' (initial purchase)
      - customer.subscription.updated → maps Stripe status, updates period end
      - customer.subscription.deleted → status='canceled'
      - invoice.paid                  → status='active', refreshes period end
      - invoice.payment_failed        → status='past_due'
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        print("[WEBHOOK] ERROR: Invalid payload")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        print("[WEBHOOK] ERROR: Invalid signature")
        return jsonify({'error': 'Invalid signature'}), 400

    event_type = event['type']
    obj = event['data']['object']
    print(f"[WEBHOOK] Received: {event_type}")

    try:
        if event_type == 'checkout.session.completed':
            # First-time subscription. current_period_end fills in on invoice.paid.
            email = obj.get('customer_email') or obj.get('customer_details', {}).get('email', '')
            upsert_subscription(
                user_email=email,
                stripe_customer_id=obj.get('customer', ''),
                stripe_subscription_id=obj.get('subscription', ''),
                status='active',
            )

        elif event_type in ('customer.subscription.updated', 'customer.subscription.deleted'):
            # Lifecycle transition. Subscription object doesn't carry email — look up via Customer.
            customer_id = obj.get('customer', '')
            customer = stripe.Customer.retrieve(customer_id) if customer_id else None
            email = customer.get('email', '') if customer else ''
            status = 'canceled' if event_type.endswith('deleted') else _map_status(obj.get('status', ''))
            items = obj.get('items', {}).get('data', [])
            price_id = items[0].get('price', {}).get('id', '') if items else ''
            upsert_subscription(
                user_email=email,
                stripe_customer_id=customer_id,
                stripe_subscription_id=obj.get('id', ''),
                status=status,
                current_period_end=_iso_from_unix(obj.get('current_period_end')),
                price_id=price_id,
            )

        elif event_type == 'invoice.paid':
            # Successful renewal — refresh current_period_end from the Subscription object.
            subscription_id = obj.get('subscription', '')
            period_end = ''
            if subscription_id:
                sub = stripe.Subscription.retrieve(subscription_id)
                period_end = _iso_from_unix(sub.get('current_period_end'))
            upsert_subscription(
                user_email=obj.get('customer_email', ''),
                stripe_customer_id=obj.get('customer', ''),
                stripe_subscription_id=subscription_id,
                status='active',
                current_period_end=period_end,
            )

        elif event_type == 'invoice.payment_failed':
            upsert_subscription(
                user_email=obj.get('customer_email', ''),
                stripe_customer_id=obj.get('customer', ''),
                stripe_subscription_id=obj.get('subscription', ''),
                status='past_due',
            )

        else:
            print(f"[WEBHOOK] ℹ️ Unhandled event type: {event_type}")

    except Exception as e:
        print(f"[WEBHOOK] ❌ Exception handling {event_type}: {e}")

    return jsonify({'status': 'ok'}), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    api_key_status = "configured" if ANTHROPIC_API_KEY else "missing"
    port = int(os.getenv('PORT', 5000))

    return jsonify({
        'status': 'healthy',
        'port': port,
        'api_key': api_key_status,
        'allowed_origins': ALLOWED_ORIGINS
    })


if __name__ == '__main__':
    # Railway sets PORT environment variable, fallback to 5000 for local dev
    port = int(os.getenv('PORT', 5000))

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