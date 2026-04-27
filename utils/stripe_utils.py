"""
Stripe subscription utilities for FamilyForecast.
Handles subscription checks and checkout session creation.
"""
import os
import stripe
import streamlit as st
from utils.supabase_sync import get_supabase_client

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

PRICE_IDS = {
    "annual": os.getenv("STRIPE_PRICE_ANNUAL", ""),
    "monthly": os.getenv("STRIPE_PRICE_MONTHLY", ""),
    "early_bird": os.getenv("STRIPE_PRICE_EARLY_BIRD", ""),
}

PREMIUM_FEATURES = [
    "Healthcare",
    "scenario_studio",
    "social_security",
    "roth_calculator",
    "historical_tracking",
]

FREE_FEATURES = [
    "INTAKE",
    "Analysis",
]


def check_subscription(user_email: str) -> bool:
    """
    Check if user has active subscription in Supabase.
    Returns True if active, False otherwise.
    """
    if not user_email:
        return False
    try:
        client = get_supabase_client()
        result = client.table("subscriptions")\
            .select("status, current_period_end")\
            .eq("user_email", user_email.lower().strip())\
            .execute()
        if result.data and len(result.data) > 0:
            return result.data[0].get("status") == "active"
        return False
    except Exception as e:
        print(f"[STRIPE] Subscription check error: {e}")
        return False


def is_premium_user() -> bool:
    """
    Check if current session user has premium access.
    Caches result in session state for performance.
    """
    # Cache check — only query Supabase once per session
    if "is_premium" in st.session_state:
        return st.session_state["is_premium"]

    user_email = st.session_state.get("user_email", "")
    if not user_email:
        st.session_state["is_premium"] = False
        return False

    result = check_subscription(user_email)
    st.session_state["is_premium"] = result
    return result


def create_checkout_session(user_email: str, price_key: str = "annual") -> str:
    """
    Create a Stripe Checkout Session and return the URL.
    """
    try:
        price_id = PRICE_IDS.get(price_key, PRICE_IDS["annual"])
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=user_email,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url="https://app.familyforecast.ai?upgrade=success",
            cancel_url="https://app.familyforecast.ai?upgrade=cancelled",
            metadata={"user_email": user_email},
            discounts=[{"coupon": "POKg7YZp"}],
        )
        return session.url
    except Exception as e:
        print(f"[STRIPE] Checkout session error: {e}")
        return ""


def show_upgrade_wall(feature_name: str):
    """
    Show premium upgrade wall when user tries to access a locked feature.
    """
    user_email = st.session_state.get("user_email", "")

    FEATURE_DESCRIPTIONS = {
        "Healthcare": ("🏥", "Healthcare Hub", "Medicare IRMAA calculations, Medigap analysis, 20-year cost projections"),
        "scenario_studio": ("🎭", "Scenario Studio", "Compare unlimited what-if scenarios side by side"),
        "social_security": ("📊", "Social Security Optimizer", "Find your optimal claiming age — worth $100K+ lifetime"),
        "roth_calculator": ("📈", "Roth Converter", "Optimize your Roth conversion strategy for tax savings"),
        "historical_tracking": ("📅", "Historical Tracking", "Track your retirement plan year over year"),
    }

    icon, display_name, feature_desc = FEATURE_DESCRIPTIONS.get(
        feature_name, ("🔒", feature_name, "Advanced retirement planning tools")
    )

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:

        # Hero section
        st.markdown(
            f"""
            <div style='text-align:center; padding: 2rem 1rem 1rem 1rem;
                        background: linear-gradient(135deg, #2a2a44 0%, #243558 50%, #1a4878 100%);
                        border-radius: 16px; border: 1px solid #2E86AB; margin-bottom: 1.5rem;'>
                <div style='font-size: 3.5rem; margin-bottom: 0.5rem;'>{icon}</div>
                <h1 style='color: #ffffff; font-size: 1.8rem; margin: 0 0 0.5rem 0;'>
                    {display_name}
                </h1>
                <p style='color: #ffffff; font-size: 1.05rem; margin: 0 0 1rem 0;'>
                    {feature_desc}
                </p>
                <div style='display:inline-block; background: #2E86AB; color: white;
                            padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.85rem;'>
                    🔒 Premium Feature
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # No email account
        if not user_email:
            st.markdown(
                """
                <div style='background: #1a3a6e; border: 1px solid #2E86AB; border-radius: 12px;
                            padding: 1.5rem; text-align: center; margin-bottom: 1rem;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>👋</div>
                    <h3 style='color: #ffffff; margin: 0 0 0.5rem 0;'>Create Your Free Account First</h3>
                    <p style='color: #ffffff; margin: 0 0 1rem 0; font-size: 0.95rem;'>
                        A free account takes 30 seconds and unlocks everything below.
                    </p>
                    <p style='color: #e0f0ff; margin: 0; font-size: 0.9rem;'>
                        👉 Go to the <strong>Review page</strong> → choose <strong>"Create Free Account"</strong>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Show what they're missing
            with st.expander("✨ See everything included in Premium — $49/year"):
                st.markdown("""
                | Feature | What it does |
                |---------|-------------|
                | 🏥 Healthcare Hub | Medicare IRMAA, Medigap, 20-year cost projection |
                | 🎭 Scenario Studio | Unlimited what-if comparisons |
                | 📊 SS Optimizer | Optimal Social Security claiming age |
                | 📈 Roth Calculator | Tax-optimized conversion strategy |
                | 📅 Historical Tracking | Year-over-year plan tracking |
                | 🤖 AI Explanations | Personalized chart insights |
                """)
            st.stop()

        # Founding Member offer banner
        st.markdown(
            """
            <div style='background: linear-gradient(90deg, #f9a825, #f57f17);
                        border-radius: 10px; padding: 0.8rem 1.2rem;
                        text-align: center; margin-bottom: 1.2rem;'>
                <span style='color: #1a1a1a; font-weight: bold; font-size: 1rem;'>
                    🏆 Founding Member Offer — 20% off forever, automatically applied at checkout
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Pricing cards
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(
                """
                <div style='background: #0f3460; border: 2px solid #2E86AB; border-radius: 12px;
                            padding: 1.2rem; text-align: center; margin-bottom: 0.8rem;'>
                    <div style='color: #a0c4ff; font-size: 0.85rem; margin-bottom: 0.3rem;'>
                        ⭐ BEST VALUE
                    </div>
                    <div style='color: #ffffff; font-size: 1.5rem; font-weight: bold;'>$49/year</div>
                    <div style='color: #7ec8e3; font-size: 0.8rem; margin-top: 0.3rem;'>
                        <s style='color:#888'>$180/yr competitors</s> → Save 73%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("🎯 Get Annual — $49/yr", key="upgrade_annual", use_container_width=True):
                url = create_checkout_session(user_email, "annual")
                if url:
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
                    st.markdown(f"👉 [Click here to complete payment]({url})")
                else:
                    st.error("Could not open payment page. Please try again.")

        with col_b:
            st.markdown(
                """
                <div style='background: #1a1a2e; border: 1px solid #444; border-radius: 12px;
                            padding: 1.2rem; text-align: center; margin-bottom: 0.8rem;'>
                    <div style='color: #a0c4ff; font-size: 0.85rem; margin-bottom: 0.3rem;'>
                        FLEXIBLE
                    </div>
                    <div style='color: #ffffff; font-size: 1.5rem; font-weight: bold;'>$5/month</div>
                    <div style='color: #7ec8e3; font-size: 0.8rem; margin-top: 0.3rem;'>
                        Cancel anytime · No commitment
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("📅 Get Monthly — $5/mo", key="upgrade_monthly", use_container_width=True):
                url = create_checkout_session(user_email, "monthly")
                if url:
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
                    st.markdown(f"👉 [Click here to complete payment]({url})")
                else:
                    st.error("Could not open payment page. Please try again.")

        # Trust signals
        st.markdown(
            """
            <div style='text-align:center; color: #888; font-size: 0.82rem;
                        margin-top: 1rem; padding: 0.8rem;
                        border-top: 1px solid #333;'>
                🔐 Secure payment via Stripe &nbsp;·&nbsp;
                ↩️ 30-day money-back guarantee &nbsp;·&nbsp;
                ❌ Cancel anytime &nbsp;·&nbsp;
                🏆 Founding Member price locked forever
            </div>
            """,
            unsafe_allow_html=True
        )

        # What's included
        with st.expander("✨ Everything included in Premium"):
            st.markdown("""
            | Feature | What it does |
            |---------|-------------|
            | 🏥 **Healthcare Hub** | Medicare IRMAA surcharges, Medigap analysis, 20-year cost projections |
            | 🎭 **Scenario Studio** | Compare unlimited what-if retirement scenarios side by side |
            | 📊 **SS Optimizer** | Find your optimal Social Security claiming age — worth $100K+ lifetime |
            | 📈 **Roth Calculator** | Tax-optimized Roth conversion strategy year by year |
            | 📅 **Historical Tracking** | Track how your retirement plan evolves year over year |
            | 🤖 **AI Chart Explanations** | Personalized AI insights on every chart and projection |
            | 🔮 **New Tools** | Priority access to every new feature we add |
            """)
