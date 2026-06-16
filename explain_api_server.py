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
        intake = data.get('intake', {})

        # ── Extract fields ───────────────────────────────────────────────────
        age           = _safe_num(intake.get('age') or intake.get('profile', {}).get('age'))
        ret_age       = _safe_num(intake.get('retirementAge') or intake.get('profile', {}).get('retirementAge'))
        partner_age   = _safe_num(intake.get('partnerAge') or intake.get('profile', {}).get('partnerAge'))
        name          = intake.get('name') or intake.get('profile', {}).get('name', 'You')
        partner_name  = intake.get('partnerName') or intake.get('profile', {}).get('partnerName', '')

        ss_monthly    = _safe_num(intake.get('socialSecurityMonthly') or intake.get('income', {}).get('socialSecurity'))
        ss_age        = _safe_num(intake.get('socialSecurityAge') or intake.get('income', {}).get('socialSecurityAge')) or 67
        pension       = _safe_num(intake.get('pensionMonthly') or intake.get('income', {}).get('pension'))
        salary        = _safe_num(intake.get('monthlySalary') or intake.get('income', {}).get('salary'))
        rental        = _safe_num(intake.get('rentalIncome') or intake.get('income', {}).get('rental'))

        ira           = _safe_num(intake.get('iraBalance') or intake.get('assets', {}).get('ira'))
        roth          = _safe_num(intake.get('rothBalance') or intake.get('assets', {}).get('roth'))
        taxable       = _safe_num(intake.get('taxableInvestments') or intake.get('assets', {}).get('taxable'))
        k401          = _safe_num(intake.get('balance401k') or intake.get('assets', {}).get('balance401k'))
        home          = _safe_num(intake.get('homeValue') or intake.get('assets', {}).get('homeValue'))

        expenses      = _safe_num(intake.get('monthlyExpenses') or intake.get('expenses', {}).get('total'))

        # ── Core calculations ────────────────────────────────────────────────
        total_assets       = ira + roth + taxable + k401
        guaranteed_income  = ss_monthly + pension
        monthly_gap        = max(0, expenses - guaranteed_income)
        years_to_retire    = max(0, ret_age - age) if ret_age and age else 0

        # Guardrail zone (simplified — real Monte Carlo runs in Streamlit)
        # Use asset-to-gap ratio as proxy
        if monthly_gap > 0 and total_assets > 0:
            months_covered = total_assets / monthly_gap
            if months_covered >= 300:    # 25 years
                zone = "green"
                zone_label = "🟢 Green Zone"
                mc_proxy = 89
            elif months_covered >= 200:  # ~17 years
                zone = "yellow"
                zone_label = "🟡 Yellow Zone"
                mc_proxy = 72
            else:
                zone = "red"
                zone_label = "🔴 Red Zone"
                mc_proxy = 54
        else:
            zone = "green"
            zone_label = "🟢 Green Zone"
            mc_proxy = 92

        # Safe spending (4% rule proxy)
        safe_annual  = total_assets * 0.04
        safe_monthly = (safe_annual / 12) + guaranteed_income

        # Tax bracket estimate (single or MFJ rough)
        taxable_income_est = (ss_monthly * 0.85 * 12) + (pension * 12)
        if taxable_income_est < 23200:
            bracket = 10; bracket_label = "10%"
            next_bracket_threshold = 23200
        elif taxable_income_est < 94300:
            bracket = 12; bracket_label = "12%"
            next_bracket_threshold = 94300
        elif taxable_income_est < 201050:
            bracket = 22; bracket_label = "22%"
            next_bracket_threshold = 201050
        else:
            bracket = 24; bracket_label = "24%"
            next_bracket_threshold = 383900

        bracket_room = max(0, next_bracket_threshold - taxable_income_est)

        # Roth conversion recommendation
        roth_convert_safe   = min(bracket_room, 20000)
        roth_convert_max    = min(bracket_room * 0.9, 25000)

        # IRMAA
        magi_estimate = taxable_income_est
        irmaa_tier1   = 103000
        irmaa_margin  = max(0, irmaa_tier1 - magi_estimate)
        irmaa_safe    = magi_estimate < irmaa_tier1

        # RMD estimate at 73
        ira_at_73 = (ira + k401) * (1.07 ** max(0, 73 - age)) if age else ira + k401
        rmd_at_73 = ira_at_73 / 26.5  # IRS uniform table divisor at 73

        # SS claiming comparison
        fra_benefit  = ss_monthly
        age62_benefit = round(ss_monthly * 0.70, 0)
        age70_benefit = round(ss_monthly * 1.24, 0)

        # Withdrawal order this month
        withdrawal_sources = []
        remaining = monthly_gap
        if taxable > 0 and remaining > 0:
            from_taxable = min(remaining, taxable / 240)
            withdrawal_sources.append({
                "source": "Taxable Investments",
                "amount": round(from_taxable, 0),
                "taxTreatment": "Long-term gains rate",
                "recommended": True,
                "reason": "Use first — lowest tax impact"
            })
            remaining -= from_taxable
        if ira > 0 and remaining > 0:
            from_ira = min(remaining, ira / 240)
            withdrawal_sources.append({
                "source": "IRA / 401k",
                "amount": round(from_ira, 0),
                "taxTreatment": "Fully taxable as income",
                "recommended": remaining > 0,
                "reason": "Use second — preserve for Roth conversion"
            })
        if ss_monthly > 0:
            withdrawal_sources.insert(0, {
                "source": "Social Security",
                "amount": ss_monthly,
                "taxTreatment": "Up to 85% taxable",
                "recommended": True,
                "reason": "Use first — guaranteed income"
            })
        if pension > 0:
            withdrawal_sources.insert(1, {
                "source": "Pension",
                "amount": pension,
                "taxTreatment": "Fully taxable",
                "recommended": True,
                "reason": "Use first — guaranteed income"
            })

        # ── Build response ───────────────────────────────────────────────────
        result = {
            "user": {
                "name": name,
                "age": age,
                "retirementAge": ret_age,
                "partnerName": partner_name,
                "partnerAge": partner_age,
            },
            "monthlyCommand": {
                "safeMontlySpending": round(safe_monthly, 0),
                "zone": zone,
                "zoneLabel": zone_label,
                "mcSuccess": mc_proxy,
                "guaranteedIncome": guaranteed_income,
                "monthlyGap": round(monthly_gap, 0),
                "totalAssets": round(total_assets, 0),
            },
            "incomeRecipe": {
                "sources": withdrawal_sources,
                "totalMonthly": round(safe_monthly, 0),
            },
            "guardrailZone": {
                "zone": zone,
                "zoneLabel": zone_label,
                "mcSuccess": mc_proxy,
                "spendingAdvice": (
                    "Maintain or increase spending up to 5%" if zone == "green"
                    else "Hold spending flat" if zone == "yellow"
                    else "Reduce discretionary spending 5-10%"
                ),
                "rothAdvice": (
                    "Proceed with Roth conversion" if zone == "green"
                    else "Reduce Roth conversion" if zone == "yellow"
                    else "Pause Roth conversion"
                ),
            },
            "taxOpportunities": {
                "estimatedTaxableIncome": round(taxable_income_est, 0),
                "currentBracket": bracket_label,
                "bracketRoom": round(bracket_room, 0),
                "rothConvertSafe": round(roth_convert_safe, 0),
                "rothConvertMax": round(roth_convert_max, 0),
                "irmaaSafe": irmaa_safe,
                "irmaaMargin": round(irmaa_margin, 0),
                "capitalGainsRoom": round(min(bracket_room * 0.4, 15000), 0),
            },
            "socialSecurity": {
                "fraMonthly": fra_benefit,
                "age62Monthly": age62_benefit,
                "age70Monthly": age70_benefit,
                "plannedClaimAge": ss_age,
                "breakEvenVs62": 77,
                "breakEvenVs70": 80,
            },
            "rmdForecast": {
                "currentIraBalance": round(ira + k401, 0),
                "projectedIraAt73": round(ira_at_73, 0),
                "rmdAt73": round(rmd_at_73, 0),
                "yearsUntilRmd": max(0, 73 - age) if age else 0,
                "rothConvertRecommended": round(roth_convert_safe, 0),
            },
            "irmaaWatch": {
                "estimatedMagi": round(magi_estimate, 0),
                "tier1Threshold": irmaa_tier1,
                "safetyMargin": round(irmaa_margin, 0),
                "currentTier": "Standard" if irmaa_safe else "Tier 1+",
                "monthlyPremium": 185 if irmaa_safe else 259,
                "safe": irmaa_safe,
            },
            "actionPlan": {
                "topActions": [
                    {
                        "priority": 1,
                        "color": "red",
                        "action": f"Convert ${round(roth_convert_safe,0):,.0f} to Roth before Dec 31",
                        "deadline": "Dec 31 this year",
                        "impact": "High",
                        "screen": "Tax Opportunities",
                        "why": f"You have ${round(bracket_room,0):,.0f} of room in your {bracket_label} bracket"
                    },
                    {
                        "priority": 2,
                        "color": "red",
                        "action": f"Keep income below ${irmaa_tier1:,.0f} to avoid Medicare surcharge",
                        "deadline": "Dec 31 this year",
                        "impact": "High",
                        "screen": "IRMAA Watch",
                        "why": f"You have ${round(irmaa_margin,0):,.0f} of safety margin — protect it"
                    },
                    {
                        "priority": 3,
                        "color": "yellow",
                        "action": "Withdraw from taxable accounts first this month",
                        "deadline": "This month",
                        "impact": "Medium",
                        "screen": "Income Recipe",
                        "why": "Lowest tax impact — preserve IRA for Roth conversion window"
                    },
                    {
                        "priority": 4,
                        "color": "yellow",
                        "action": f"Review Social Security claiming age (planned: {ss_age})",
                        "deadline": "Before retirement",
                        "impact": "Very High",
                        "screen": "Social Security",
                        "why": f"Waiting from 62 to FRA increases benefit from ${age62_benefit:,.0f} to ${fra_benefit:,.0f}/month"
                    },
                    {
                        "priority": 5,
                        "color": "green",
                        "action": "Update account balances monthly",
                        "deadline": "Monthly",
                        "impact": "Low",
                        "screen": "What Changed",
                        "why": "Keeps your guardrail calculations accurate"
                    },
                ]
            }
        }

        return jsonify({"success": True, "data": result}), 200

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