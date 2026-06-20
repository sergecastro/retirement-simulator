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

        # Roth conversion guidance is age-conditional. Converting at a high working
        # income adds tax cost; the real window opens when income drops at retirement.
        # Ages come from the Track-D intake snapshot (raw_results.intake), falling
        # back to the posted request body for older rows.
        _snap = (row.get("raw_results") or {}).get("intake") or {}
        def _age_num(*vals):
            for v in vals:
                try:
                    if v not in (None, ""):
                        return float(v)
                except (ValueError, TypeError):
                    pass
            return None
        user_age = _age_num(_snap.get("age"), intake.get("age"))
        ret_age  = _age_num(_snap.get("retirement_age"), intake.get("retirementAge"))
        _bracket_room = row.get("bracket_room")

        if user_age is not None and ret_age is not None and user_age < ret_age:
            # Still working — suppress the misleading "room" number.
            roth_status  = "window_not_open"
            roth_message = ("Your Roth conversion window opens at retirement — "
                            "converting now at your income level adds tax cost, "
                            "not savings.")
            bracket_room_out = 0
        else:
            roth_status = "window_open"
            try:
                _amt = f"${float(_bracket_room):,.0f}" if _bracket_room is not None else "the available amount"
            except (ValueError, TypeError):
                _amt = "the available amount"
            roth_message = f"You can convert up to {_amt} this year and stay in your current bracket."
            bracket_room_out = _bracket_room

        # IRMAA is a Medicare-age concern (65; 2-yr lookback at 63). Gate it for
        # younger users so we don't show a misleading "safe $X" margin. Uses the
        # stored flag (Track G) and falls back to the resolved age.
        _raw = row.get("raw_results") or {}
        if (_raw.get("irmaa_relevant") is False) or (user_age is not None and user_age < 63):
            _irmaa_watch = {
                "status": "not_yet_relevant",
                "message": _raw.get("irmaa_message") or ("IRMAA Medicare surcharges become "
                           "relevant at 65. We will flag this when you approach Medicare age."),
                "safetyMargin": None,
            }
        else:
            _irmaa_watch = {
                "status": "relevant",
                "safetyMargin": row.get("irmaa_margin"),
            }

        # Home equity from the intake snapshot (surfaced only when a home exists).
        _home_value = _snap.get("primary_residence_value") or 0
        _mortgage = _snap.get("mortgage_balance") or 0

        # Return ONLY real engine outputs (tax bracket, bracket room, IRMAA margin,
        # RMD at 73 are derived from the user's projected income using the engine's
        # own 2025 bracket tables). safe_monthly_spending is a labeled 4% guideline.
        # Any field the engine could not compute stays null — never a fabricated value.
        data_out = {
            "intakeId": intake_id,
            "computedAt": row.get("created_at"),
            "monthlyCommand": {
                "mcSuccess": row.get("monte_carlo_success_rate"),
                "finalSavings": row.get("final_savings"),
                "safeMonthlySpending": row.get("safe_monthly_spending"),
                # Methodology caveat for safeMonthlySpending — Lovable should show it
                # near the number (currently the 4%-rule guideline note).
                "safeSpendingNote": (row.get("raw_results") or {}).get("safe_spending_method"),
                # Intake values for the income picture + asset summary (monthly $).
                "monthlyExpenses": row.get("monthly_expenses"),
                "guaranteedIncome": row.get("guaranteed_income"),
                "totalAssets": row.get("total_assets"),
            },
            "taxOpportunities": {
                "currentBracket": row.get("tax_bracket"),
                "bracketRoom": bracket_room_out,
                "rothConversionStatus": roth_status,
                "rothConversionMessage": roth_message,
                "rothConvertMax": bracket_room_out,
                "iraBalance": _snap.get("ira_balance", 0),
                "rothBalance": _snap.get("roth_balance", 0),
                "taxableInvestments": _snap.get("taxable_investment_accounts", 0),
                "four01kBalance": _snap.get("four01k_403b_balance", 0),
                "grossAnnualIncome": (_snap.get("total_income", 0) or 0) * 12,
            },
            "irmaaWatch": _irmaa_watch,
            "rmdForecast": {
                "rmdAt73": row.get("rmd_at_73"),
            },
        }

        # Include home equity only when the user actually has a home.
        if _home_value and _home_value > 0:
            data_out["homeEquity"] = {
                "homeValue": _home_value,
                "mortgage": _mortgage,
                "equity": _home_value - _mortgage,
            }

        # College planning — built from the intake snapshot children list.
        _cost_map = {
            "Public In-State": 120000,
            "Public Out-of-State": 180000,
            "Private": 280000,
        }
        _five29 = _snap.get("five29_plan_balance", 0) or 0
        college_plan = []
        for child in _snap.get("children_list", []):
            plan = child.get("College Plan", "None")
            if plan == "None":
                continue
            estimated_cost = _cost_map.get(plan, 120000)
            college_plan.append({
                "name": child.get("Name", "Child"),
                "startYear": child.get("Birth Year", 2000) + 18,
                "estimatedCost": estimated_cost,
                "current529": _five29,
                "gap": max(0, estimated_cost - _five29),
            })
        data_out["collegePlanning"] = college_plan

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
        intake       = body.get('intake', {}) or {}
        history      = body.get('history', [])

        if not question:
            return jsonify({"success": False, "error": "No question provided"}), 400

        # Session-aware: when a user opens the Command Center via a link, Lovable
        # has no form state, so `intake` is empty. Load the user's saved results +
        # intake snapshot from analysis_results (keyed by session_id) so the AI has
        # full context. Posted intake values take precedence; the DB fills the gaps.
        session_id = (intake.get('session_id') or body.get('session_id')
                      or intake.get('id') or body.get('intake_id') or '')
        session_id = (session_id or '').strip().upper()

        row = {}     # computed results from analysis_results
        snap = {}    # intake snapshot stored in raw_results.intake
        if session_id:
            client = _get_cc_supabase()
            if client is not None:
                try:
                    res = (client.table('analysis_results').select('*')
                           .eq('intake_id', session_id)
                           .order('created_at', desc=True).limit(1).execute())
                    rows = res.data or []
                    if rows:
                        row = rows[0]
                        snap = (row.get('raw_results') or {}).get('intake') or {}
                except Exception as _e:
                    print(f"[CC_CHAT] analysis_results lookup failed: {_e}")

        # Resolve each field: posted intake (camelCase) first, then DB snapshot.
        def _pick(posted_key, snap_key, default=None):
            v = intake.get(posted_key)
            if v not in (None, "", 0):
                return v
            v = snap.get(snap_key)
            return v if v not in (None, "") else default

        name     = _pick('name', 'name', 'the user')
        age      = _pick('age', 'age', 'unknown')
        ret_age  = _pick('retirementAge', 'retirement_age', 'unknown')
        ira      = _safe_num(intake.get('iraBalance'))          or _safe_num(snap.get('ira_balance'))
        roth     = _safe_num(intake.get('rothBalance'))         or _safe_num(snap.get('roth_balance'))
        taxable  = _safe_num(intake.get('taxableInvestments'))  or _safe_num(snap.get('taxable_investment_accounts'))
        k401     = _safe_num(intake.get('balance401k'))         or _safe_num(snap.get('four01k_403b_balance'))
        ss       = _safe_num(intake.get('socialSecurityMonthly')) or _safe_num(snap.get('social_security_income'))
        pension  = _safe_num(intake.get('pensionMonthly'))      or _safe_num(snap.get('pension_income'))
        salary   = _safe_num(intake.get('monthlySalary'))       or _safe_num(snap.get('salary_wages'))
        expenses = _safe_num(intake.get('monthlyExpenses'))     or _safe_num(snap.get('total_expenses'))
        total_income = _safe_num(intake.get('totalMonthlyIncome')) or _safe_num(snap.get('total_income'))

        # Their REAL computed results — let the AI reason from actual outputs.
        def _money(v):
            try:
                return f"${float(v):,.0f}" if v is not None else "not yet available"
            except (ValueError, TypeError):
                return "not yet available"

        results_block = ""
        if row:
            note = (row.get('raw_results') or {}).get('safe_spending_method') or ""
            mc = row.get('monte_carlo_success_rate')
            results_block = f"""

THEIR LATEST ANALYSIS RESULTS (real, engine-computed — reason from these):
- Monte Carlo success rate: {f'{mc:.0f}%' if mc is not None else 'not yet available'}
- Safe monthly spending: {_money(row.get('safe_monthly_spending'))}{(' — ' + note) if note else ''}
- Projected final savings: {_money(row.get('final_savings'))}
- Total assets: {_money(row.get('total_assets'))}
- Guaranteed monthly income (SS + pension): {_money(row.get('guaranteed_income'))}
- Current tax bracket: {row.get('tax_bracket') or 'not yet available'} (room before next bracket: {_money(row.get('bracket_room'))})
- IRMAA safety margin: {_money(row.get('irmaa_margin'))}
- Projected RMD at age 73: {_money(row.get('rmd_at_73'))}"""

        partner_name = _pick('partnerName', 'partner_name', '')
        partner_line = f" Partner: {partner_name}." if partner_name and partner_name != 'the user' else ""

        system_prompt = f"""You are a friendly retirement planning advisor inside FamilyForecast.AI Command Center.
You are NOT a licensed financial advisor. Always note that users should consult a professional for major decisions.
Speak in plain English. No jargon without explanation. Be encouraging but honest.
Keep answers to 3-4 paragraphs maximum. Always end with one clear "Next best action" sentence.

User: {name}, Age {age}, retiring at {ret_age}.{partner_line}
IRA: ${ira:,.0f} | Roth: ${roth:,.0f} | Taxable: ${taxable:,.0f} | 401k: ${k401:,.0f}
Social Security: ${ss:,.0f}/month | Pension: ${pension:,.0f}/month | Salary: ${salary:,.0f}/month
Monthly expenses: ${expenses:,.0f}/month | Total monthly income: ${total_income:,.0f}/month{results_block}

When discussing Social Security claiming age, always connect to: (1) whether the user needs SS income early given their other assets, (2) break-even age ~78-80 for claiming at 70 vs 62, (3) the Roth conversion window between retirement and SS claiming, (4) IRMAA impact if income is high. Never give generic pros/cons — tie every point to the user's actual numbers.

Always reference their specific numbers. Never invent figures not shown above. If a number shows "not yet available," tell the user it will appear after they run their Analysis."""

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