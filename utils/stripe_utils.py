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

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div style='text-align:center; padding: 2rem;'>
                <div style='font-size: 3rem;'>🔒</div>
                <h2 style='color: #2E86AB;'>Premium Feature</h2>
                <p style='color: #666; font-size: 1.1rem;'>
                    <strong>{feature_name}</strong> is part of FamilyForecast Premium.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not user_email:
            st.warning(
                "**Create a free account first** to unlock premium features.\n\n"
                "Go to the Review page and choose 'Create Free Account' to get started."
            )
            return

        st.markdown("### Upgrade to Premium")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                """
                **Annual Plan**
                ~~$180/year~~ → **$49/year**
                *Save 73% vs competitors*
                """
            )
            if st.button("Get Annual — $49/yr", key="upgrade_annual", use_container_width=True):
                url = create_checkout_session(user_email, "annual")
                if url:
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
                    st.markdown(f"[Click here if not redirected]({url})")
                else:
                    st.error("Could not create checkout session. Please try again.")

        with col_b:
            st.markdown(
                """
                **Monthly Plan**
                **$5/month**
                *Cancel anytime*
                """
            )
            if st.button("Get Monthly — $5/mo", key="upgrade_monthly", use_container_width=True):
                url = create_checkout_session(user_email, "monthly")
                if url:
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
                    st.markdown(f"[Click here if not redirected]({url})")
                else:
                    st.error("Could not create checkout session. Please try again.")

        st.markdown("---")
        st.markdown(
            """
            <div style='text-align:center; color: #888; font-size: 0.85rem;'>
            Secure payment via Stripe &nbsp;|&nbsp;
            Cancel anytime &nbsp;|&nbsp;
            30-day money-back guarantee
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("What's included in Premium?"):
            st.markdown("""
            - **Healthcare Hub** — Medicare IRMAA, Medigap analysis
            - **Scenario Studio** — Compare unlimited what-if scenarios
            - **Social Security Optimizer** — Find your optimal claiming age
            - **Roth Calculator** — Conversion strategy optimizer
            - **Historical Tracking** — Track your plan year over year
            - **AI Explanations** — Personalized insights on all charts
            - **Priority features** — New tools added regularly
            """)
