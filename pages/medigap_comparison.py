"""
Medigap (Medicare Supplement) Comparison Tool
==============================================
Compare Medicare Supplement Insurance Plans (Medigap)
Helps users understand Plan A through N coverage and costs.

Based on 2025 CMS standardized Medigap plans.
"""

import streamlit as st
import pandas as pd
from datetime import date


# =============================================================================
# MEDIGAP PLAN DATA (2025 STANDARDIZED PLANS)
# =============================================================================

# Coverage benefits for each plan (True = covered, False = not covered, "Partial" = partial coverage)
MEDIGAP_PLANS = {
    "Plan A": {
        "part_a_coinsurance": True,
        "part_b_coinsurance": True,
        "blood_first_3_pints": True,
        "part_a_hospice_coinsurance": True,
        "skilled_nursing_coinsurance": False,
        "part_a_deductible": False,
        "part_b_deductible": False,
        "part_b_excess_charges": False,
        "foreign_travel_emergency": False,
        "description": "Basic coverage - covers Part A & B coinsurance only",
        "popularity": "Low",
        "best_for": "Those who want minimal coverage at lowest cost"
    },
    "Plan B": {
        "part_a_coinsurance": True,
        "part_b_coinsurance": True,
        "blood_first_3_pints": True,
        "part_a_hospice_coinsurance": True,
        "skilled_nursing_coinsurance": False,
        "part_a_deductible": True,
        "part_b_deductible": False,
        "part_b_excess_charges": False,
        "foreign_travel_emergency": False,
        "description": "Basic + Part A deductible",
        "popularity": "Low",
        "best_for": "Those wanting Part A deductible coverage"
    },
    "Plan C": {
        "part_a_coinsurance": True,
        "part_b_coinsurance": True,
        "blood_first_3_pints": True,
        "part_a_hospice_coinsurance": True,
        "skilled_nursing_coinsurance": True,
        "part_a_deductible": True,
        "part_b_deductible": True,
        "part_b_excess_charges": False,
        "foreign_travel_emergency": True,
        "description": "Full coverage (not available to new Medicare enrollees after 2020)",
        "popularity": "Medium (grandfathered)",
        "best_for": "Those who enrolled before 2020 wanting full coverage",
        "note": "⚠️ Not available to new Medicare enrollees after Jan 1, 2020"
    },
    "Plan D": {
        "part_a_coinsurance": True,
        "part_b_coinsurance": True,
        "blood_first_3_pints": True,
        "part_a_hospice_coinsurance": True,
        "skilled_nursing_coinsurance": True,
        "part_a_deductible": True,
        "part_b_deductible": False,
        "part_b_excess_charges": False,
        "foreign_travel_emergency": True,
        "description": "Similar to Plan C but no Part B deductible coverage",
        "popularity": "Low",
        "best_for": "Those wanting comprehensive coverage without Part B deductible"
    },
    "Plan F": {
        "part_a_coinsurance": True,
        "part_b_coinsurance": True,
        "blood_first_3_pints": True,
        "part_a_hospice_coinsurance": True,
        "skilled_nursing_coinsurance": True,
        "part_a_deductible": True,
        "part_b_deductible": True,
        "part_b_excess_charges": True,
        "foreign_travel_emergency": True,
        "description": "Most comprehensive - covers EVERYTHING (grandfathered)",
        "popularity": "High (grandfathered)",
        "best_for": "Those who enrolled before 2020 wanting zero out-of-pocket",
        "note": "⚠️ Not available to new Medicare enrollees after Jan 1, 2020"
    },
    "Plan G": {
        "part_a_coinsurance": True,
        "part_b_coinsurance": True,
        "blood_first_3_pints": True,
        "part_a_hospice_coinsurance": True,
        "skilled_nursing_coinsurance": True,
        "part_a_deductible": True,
        "part_b_deductible": False,
        "part_b_excess_charges": True,
        "foreign_travel_emergency": True,
        "description": "Most popular - covers everything EXCEPT Part B deductible",
        "popularity": "⭐ MOST POPULAR",
        "best_for": "Best value for comprehensive coverage (you pay ~$240/year Part B deductible)"
    },
    "Plan K": {
        "part_a_coinsurance": True,
        "part_b_coinsurance": "50%",
        "blood_first_3_pints": "50%",
        "part_a_hospice_coinsurance": True,
        "skilled_nursing_coinsurance": "50%",
        "part_a_deductible": "50%",
        "part_b_deductible": False,
        "part_b_excess_charges": False,
        "foreign_travel_emergency": False,
        "description": "Cost-sharing plan - 50% coverage with out-of-pocket limit",
        "popularity": "Low",
        "best_for": "Those wanting lower premiums with out-of-pocket max ($7,060 in 2025)",
        "out_of_pocket_max": 7060
    },
    "Plan L": {
        "part_a_coinsurance": True,
        "part_b_coinsurance": "75%",
        "blood_first_3_pints": "75%",
        "part_a_hospice_coinsurance": True,
        "skilled_nursing_coinsurance": "75%",
        "part_a_deductible": "75%",
        "part_b_deductible": False,
        "part_b_excess_charges": False,
        "foreign_travel_emergency": False,
        "description": "Cost-sharing plan - 75% coverage with out-of-pocket limit",
        "popularity": "Low",
        "best_for": "Those wanting moderate premiums with out-of-pocket max ($3,530 in 2025)",
        "out_of_pocket_max": 3530
    },
    "Plan M": {
        "part_a_coinsurance": True,
        "part_b_coinsurance": True,
        "blood_first_3_pints": True,
        "part_a_hospice_coinsurance": True,
        "skilled_nursing_coinsurance": True,
        "part_a_deductible": "50%",
        "part_b_deductible": False,
        "part_b_excess_charges": False,
        "foreign_travel_emergency": True,
        "description": "50% Part A deductible coverage",
        "popularity": "Low",
        "best_for": "Those wanting good coverage with slightly lower premiums"
    },
    "Plan N": {
        "part_a_coinsurance": True,
        "part_b_coinsurance": True,
        "blood_first_3_pints": True,
        "part_a_hospice_coinsurance": True,
        "skilled_nursing_coinsurance": True,
        "part_a_deductible": True,
        "part_b_deductible": False,
        "part_b_excess_charges": False,
        "foreign_travel_emergency": True,
        "description": "Good coverage with small copays ($20 office, $50 ER)",
        "popularity": "⭐ SECOND MOST POPULAR",
        "best_for": "Those wanting comprehensive coverage with lower premiums than Plan G",
        "copays": "$20 office visit, $50 ER (waived if admitted)"
    }
}

# Average monthly premiums by plan (2025 estimates - varies significantly by state/age)
# These are BASE rates for age 65, non-tobacco user
AVERAGE_PREMIUMS_BASE = {
    "Plan A": 150,
    "Plan B": 180,
    "Plan C": 220,  # Grandfathered
    "Plan D": 190,
    "Plan F": 250,  # Grandfathered
    "Plan G": 200,
    "Plan K": 90,
    "Plan L": 140,
    "Plan M": 170,
    "Plan N": 160
}

# Age rating factors (how premiums increase with age)
AGE_FACTORS = {
    65: 1.00,
    66: 1.03,
    67: 1.06,
    68: 1.10,
    69: 1.14,
    70: 1.18,
    71: 1.22,
    72: 1.27,
    73: 1.32,
    74: 1.37,
    75: 1.43,
    76: 1.49,
    77: 1.55,
    78: 1.62,
    79: 1.69,
    80: 1.77,
    81: 1.85,
    82: 1.94,
    83: 2.03,
    84: 2.13,
    85: 2.24
}

# State cost factors (relative to national average)
STATE_FACTORS = {
    "AL": 0.85, "AK": 1.35, "AZ": 0.95, "AR": 0.80, "CA": 1.15,
    "CO": 1.00, "CT": 1.20, "DE": 1.10, "FL": 0.90, "GA": 0.85,
    "HI": 1.25, "ID": 0.90, "IL": 1.05, "IN": 0.95, "IA": 0.85,
    "KS": 0.88, "KY": 0.90, "LA": 0.88, "ME": 1.15, "MD": 1.10,
    "MA": 1.25, "MI": 1.00, "MN": 1.00, "MS": 0.82, "MO": 0.88,
    "MT": 0.95, "NE": 0.90, "NV": 1.00, "NH": 1.18, "NJ": 1.22,
    "NM": 0.92, "NY": 1.30, "NC": 0.88, "ND": 0.88, "OH": 0.95,
    "OK": 0.85, "OR": 1.05, "PA": 1.08, "RI": 1.18, "SC": 0.85,
    "SD": 0.90, "TN": 0.85, "TX": 0.90, "UT": 0.92, "VT": 1.15,
    "VA": 0.98, "WA": 1.10, "WV": 0.92, "WI": 0.95, "WY": 0.95
}

# Tobacco surcharge
TOBACCO_SURCHARGE = 0.25  # 25% higher for tobacco users


def show_medigap_comparison():
    """
    Main Medigap Comparison Tool page.
    """
    st.title("🏥 Medigap (Medicare Supplement) Comparison")
    st.markdown("**Compare Medicare Supplement Insurance Plans to find the best coverage for your needs**")

    # Educational disclaimer
    st.warning("""
    ⚠️ **EDUCATIONAL TOOL** - Premium estimates are based on 2025 national averages.
    Actual premiums vary significantly by insurance company, state, and your health history.
    Contact insurance companies directly for accurate quotes.
    """)

    # Navigation
    col_nav1, col_nav2 = st.columns([1, 3])
    with col_nav1:
        if st.button("↩️ Back to Healthcare Hub", key="back_to_healthcare"):
            st.session_state.current_mode = "Analysis"
            st.session_state.mode_selected = True
            st.rerun()

    st.markdown("---")

    # Create tabs
    tabs = st.tabs([
        "📋 Plan Comparison",
        "💰 Cost Calculator",
        "⚖️ Medigap vs Medicare Advantage"
    ])

    # =========================================================================
    # TAB 1: PLAN COMPARISON
    # =========================================================================
    with tabs[0]:
        st.markdown("### 📋 Compare Medigap Plans (A through N)")
        st.info("All Medigap plans are **standardized by the federal government** - Plan G from one company covers the same benefits as Plan G from another. Only the price varies!")

        # Quick plan selector
        st.markdown("#### 🎯 Quick Recommendation")
        col_q1, col_q2 = st.columns(2)

        with col_q1:
            eligible_after_2020 = st.radio(
                "When did you become eligible for Medicare?",
                options=["After January 1, 2020", "Before January 1, 2020"],
                index=0,
                key="medicare_eligibility"
            )

        with col_q2:
            coverage_preference = st.radio(
                "Coverage preference:",
                options=["Maximum coverage (lowest out-of-pocket)", "Balance coverage & cost", "Lower premiums (accept some out-of-pocket)"],
                index=0,
                key="coverage_pref"
            )

        # Recommendation based on selections
        if eligible_after_2020 == "After January 1, 2020":
            if "Maximum" in coverage_preference:
                recommended = "Plan G"
                reason = "Most comprehensive plan available to you (Plan F/C not available after 2020)"
            elif "Balance" in coverage_preference:
                recommended = "Plan N"
                reason = "Great coverage with lower premiums (small copays for office visits)"
            else:
                recommended = "Plan K or L"
                reason = "Lower premiums with out-of-pocket maximum protection"
        else:
            if "Maximum" in coverage_preference:
                recommended = "Plan F"
                reason = "Covers EVERYTHING - zero out-of-pocket costs"
            elif "Balance" in coverage_preference:
                recommended = "Plan G"
                reason = "Same as Plan F but you pay Part B deductible (~$240/year)"
            else:
                recommended = "Plan N"
                reason = "Good coverage with lower premiums than F or G"

        st.success(f"📌 **Recommended for you: {recommended}** - {reason}")

        # Full comparison table
        st.markdown("#### 📊 Full Coverage Comparison")

        # Create comparison DataFrame
        coverage_items = [
            ("Part A coinsurance (hospital stays)", "part_a_coinsurance"),
            ("Part B coinsurance (doctor visits)", "part_b_coinsurance"),
            ("Blood (first 3 pints)", "blood_first_3_pints"),
            ("Part A hospice coinsurance", "part_a_hospice_coinsurance"),
            ("Skilled nursing facility coinsurance", "skilled_nursing_coinsurance"),
            ("Part A deductible ($1,632 in 2025)", "part_a_deductible"),
            ("Part B deductible ($240 in 2025)", "part_b_deductible"),
            ("Part B excess charges", "part_b_excess_charges"),
            ("Foreign travel emergency (80%)", "foreign_travel_emergency"),
        ]

        # Build table data
        table_data = {"Benefit": [item[0] for item in coverage_items]}

        for plan_name in ["Plan A", "Plan B", "Plan D", "Plan G", "Plan N", "Plan K", "Plan L"]:
            plan_coverage = []
            for _, key in coverage_items:
                value = MEDIGAP_PLANS[plan_name][key]
                if value is True:
                    plan_coverage.append("✅")
                elif value is False:
                    plan_coverage.append("❌")
                else:
                    plan_coverage.append(str(value))
            table_data[plan_name] = plan_coverage

        df_comparison = pd.DataFrame(table_data)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True, height=400)

        # Note about Plan C and F
        st.warning("""
        **Note:** Plan C and Plan F are not shown above because they are **not available to people who became eligible for Medicare after January 1, 2020**.
        If you enrolled before 2020, these plans offer the most comprehensive coverage (Plan F covers EVERYTHING).
        """)

        # Plan details expander
        with st.expander("📖 Detailed Plan Descriptions", expanded=False):
            for plan_name, details in MEDIGAP_PLANS.items():
                st.markdown(f"**{plan_name}**")
                st.markdown(f"- {details['description']}")
                st.markdown(f"- Popularity: {details['popularity']}")
                st.markdown(f"- Best for: {details['best_for']}")
                if 'note' in details:
                    st.caption(details['note'])
                if 'copays' in details:
                    st.caption(f"Copays: {details['copays']}")
                if 'out_of_pocket_max' in details:
                    st.caption(f"Out-of-pocket max: ${details['out_of_pocket_max']:,}")
                st.markdown("---")

    # =========================================================================
    # TAB 2: COST CALCULATOR
    # =========================================================================
    with tabs[1]:
        st.markdown("### 💰 Medigap Premium Calculator")
        st.info("Estimate your monthly premiums based on age, location, and tobacco use. These are estimates - actual costs vary by insurance company.")

        col_calc1, col_calc2 = st.columns(2)

        with col_calc1:
            user_age = st.number_input(
                "Your age (or age when enrolling)",
                min_value=65,
                max_value=85,
                value=65,
                step=1,
                help="Medigap premiums increase with age",
                key="medigap_age"
            )

            user_state = st.selectbox(
                "Your state",
                options=sorted(STATE_FACTORS.keys()),
                index=sorted(STATE_FACTORS.keys()).index("CA"),
                key="medigap_state",
                help="Premiums vary significantly by state"
            )

        with col_calc2:
            tobacco_use = st.radio(
                "Tobacco use?",
                options=["No", "Yes"],
                index=0,
                key="medigap_tobacco",
                help="Tobacco users typically pay 15-25% higher premiums"
            )

            show_all_plans = st.checkbox(
                "Show all plans (including C & F)",
                value=False,
                key="show_all_plans",
                help="Plan C and F only available if you enrolled before 2020"
            )

        # Calculate premiums
        st.markdown("---")
        st.markdown("#### 📊 Estimated Monthly Premiums")

        age_factor = AGE_FACTORS.get(user_age, AGE_FACTORS[85])
        state_factor = STATE_FACTORS.get(user_state, 1.0)
        tobacco_factor = 1.0 + (TOBACCO_SURCHARGE if tobacco_use == "Yes" else 0)

        premium_data = []
        plans_to_show = list(MEDIGAP_PLANS.keys()) if show_all_plans else ["Plan A", "Plan B", "Plan D", "Plan G", "Plan K", "Plan L", "Plan M", "Plan N"]

        for plan_name in plans_to_show:
            base_premium = AVERAGE_PREMIUMS_BASE[plan_name]
            monthly = base_premium * age_factor * state_factor * tobacco_factor
            annual = monthly * 12

            premium_data.append({
                "Plan": plan_name,
                "Monthly": f"${monthly:,.0f}",
                "Annual": f"${annual:,.0f}",
                "Popularity": MEDIGAP_PLANS[plan_name]["popularity"],
                "Best For": MEDIGAP_PLANS[plan_name]["best_for"][:50] + "..."
            })

        df_premiums = pd.DataFrame(premium_data)
        st.dataframe(df_premiums, use_container_width=True, hide_index=True)

        # Highlight recommendation
        st.success(f"""
        **💡 For your profile ({user_age} years old in {user_state}):**

        - **Plan G** - ${AVERAGE_PREMIUMS_BASE['Plan G'] * age_factor * state_factor * tobacco_factor:,.0f}/month - Most popular, comprehensive coverage
        - **Plan N** - ${AVERAGE_PREMIUMS_BASE['Plan N'] * age_factor * state_factor * tobacco_factor:,.0f}/month - Good coverage, lower premium (small copays)
        """)

        # Cost comparison over time
        st.markdown("#### 📈 10-Year Cost Projection")

        col_proj1, col_proj2 = st.columns(2)

        with col_proj1:
            plan_to_project = st.selectbox(
                "Select plan to project:",
                options=plans_to_show,
                index=plans_to_show.index("Plan G") if "Plan G" in plans_to_show else 0,
                key="plan_projection"
            )

        with col_proj2:
            premium_increase = st.slider(
                "Annual premium increase (%)",
                min_value=0,
                max_value=10,
                value=5,
                step=1,
                help="Medigap premiums typically increase 5-8% annually",
                key="premium_increase"
            )

        # Calculate 10-year projection
        projection_data = []
        current_premium = AVERAGE_PREMIUMS_BASE[plan_to_project] * age_factor * state_factor * tobacco_factor
        cumulative = 0

        for year in range(10):
            age_at_year = user_age + year
            age_factor_year = AGE_FACTORS.get(age_at_year, AGE_FACTORS[85])

            # Premium increases due to both age and inflation
            if year == 0:
                monthly = current_premium
            else:
                monthly = current_premium * ((1 + premium_increase / 100) ** year)

            annual = monthly * 12
            cumulative += annual

            projection_data.append({
                "Year": year + 1,
                "Your Age": age_at_year,
                "Monthly": f"${monthly:,.0f}",
                "Annual": f"${annual:,.0f}",
                "Cumulative": f"${cumulative:,.0f}"
            })

        df_projection = pd.DataFrame(projection_data)
        st.dataframe(df_projection, use_container_width=True, hide_index=True)

        st.info(f"**10-Year Total Cost Estimate:** ${cumulative:,.0f} for {plan_to_project}")

    # =========================================================================
    # TAB 3: MEDIGAP VS MEDICARE ADVANTAGE
    # =========================================================================
    with tabs[2]:
        st.markdown("### ⚖️ Medigap vs Medicare Advantage (MA)")
        st.info("Two fundamentally different approaches to Medicare coverage. Understanding the trade-offs is crucial.")

        # Side-by-side comparison
        col_mg, col_ma = st.columns(2)

        with col_mg:
            st.markdown("#### 🏥 Medigap (Medicare Supplement)")

            st.markdown("""
            **How it works:**
            - Supplements Original Medicare (Parts A & B)
            - You keep Original Medicare
            - Medigap pays what Medicare doesn't

            **✅ Advantages:**
            - **Any doctor** that accepts Medicare (nationwide)
            - **No referrals** needed for specialists
            - **Predictable costs** - low/no out-of-pocket
            - **No network restrictions**
            - **Travel friendly** - coverage anywhere in US
            - **Guaranteed renewable** - can't be cancelled

            **❌ Disadvantages:**
            - **Higher monthly premiums** ($100-$300+)
            - **No prescription drug coverage** (need separate Part D)
            - **No extra benefits** (no dental, vision, hearing)
            - **Premiums increase with age**
            - **Medical underwriting** (if not in open enrollment)
            """)

        with col_ma:
            st.markdown("#### 🌟 Medicare Advantage (Part C)")

            st.markdown("""
            **How it works:**
            - Replaces Original Medicare
            - Private insurance company manages your care
            - All-in-one coverage (often includes Part D)

            **✅ Advantages:**
            - **Low/no monthly premiums** ($0-$50 typical)
            - **Extra benefits** (dental, vision, hearing, gym)
            - **Out-of-pocket maximum** ($3,000-$8,000/year)
            - **Prescription drugs often included**
            - **No medical underwriting**
            - **Care coordination**

            **❌ Disadvantages:**
            - **Network restrictions** (HMO/PPO)
            - **Prior authorization** often required
            - **Referrals needed** for specialists (HMO)
            - **Geographic limitations** (service area)
            - **Cost unpredictable** (copays/coinsurance)
            - **Can change benefits annually**
            """)

        st.markdown("---")
        st.markdown("### 🎯 Which is Right for You?")

        # Decision quiz
        st.markdown("#### Answer these questions:")

        q1 = st.radio(
            "1. How important is doctor choice?",
            options=["Very important - I want to see any doctor", "Somewhat important", "Not important - I'll use network doctors"],
            key="mg_q1"
        )

        q2 = st.radio(
            "2. How often do you travel?",
            options=["Frequently (snowbird, vacation homes)", "Occasionally", "Rarely leave my area"],
            key="mg_q2"
        )

        q3 = st.radio(
            "3. What's your budget for premiums?",
            options=["Can afford $150-$300/month", "$50-$150/month", "Want lowest possible ($0-$50/month)"],
            key="mg_q3"
        )

        q4 = st.radio(
            "4. Do you need dental/vision/hearing coverage?",
            options=["No - I'll buy separately", "Would be nice to have", "Yes - very important"],
            key="mg_q4"
        )

        q5 = st.radio(
            "5. How's your current health?",
            options=["Excellent - rarely see doctors", "Good - occasional visits", "Fair/Poor - frequent medical needs"],
            key="mg_q5"
        )

        # Score the answers
        medigap_score = 0
        ma_score = 0

        # Q1: Doctor choice
        if "Very" in q1:
            medigap_score += 2
        elif "Somewhat" in q1:
            medigap_score += 1
            ma_score += 1
        else:
            ma_score += 2

        # Q2: Travel
        if "Frequently" in q2:
            medigap_score += 2
        elif "Occasionally" in q2:
            medigap_score += 1
            ma_score += 1
        else:
            ma_score += 2

        # Q3: Budget
        if "$150-$300" in q3:
            medigap_score += 2
        elif "$50-$150" in q3:
            medigap_score += 1
            ma_score += 1
        else:
            ma_score += 2

        # Q4: Extra benefits
        if "No" in q4:
            medigap_score += 2
        elif "nice" in q4:
            medigap_score += 1
            ma_score += 1
        else:
            ma_score += 2

        # Q5: Health
        if "Excellent" in q5:
            ma_score += 1
        elif "Good" in q5:
            medigap_score += 1
            ma_score += 1
        else:
            medigap_score += 2  # Higher medical needs = more doctor choice important

        # Recommendation
        st.markdown("---")
        st.markdown("### 🎯 Your Recommendation")

        if medigap_score > ma_score + 2:
            st.success(f"""
            **Strong recommendation: Medigap (Medicare Supplement)**

            Based on your answers, Medigap appears to be the better choice for you.

            **Why:**
            - You value doctor choice and flexibility
            - You travel or may need care outside your area
            - You can afford higher premiums for predictable costs
            - You prefer traditional Medicare with supplements

            **Next steps:**
            1. Compare Plan G vs Plan N (most popular)
            2. Get quotes from multiple insurance companies
            3. Consider enrolling during your Medigap Open Enrollment Period
            4. Don't forget to add a Part D prescription drug plan
            """)
        elif ma_score > medigap_score + 2:
            st.info(f"""
            **Strong recommendation: Medicare Advantage**

            Based on your answers, Medicare Advantage appears to be the better choice for you.

            **Why:**
            - You prefer lower monthly premiums
            - You value extra benefits (dental, vision, hearing)
            - You're comfortable with network restrictions
            - You don't travel frequently

            **Next steps:**
            1. Research plans in your area at Medicare.gov
            2. Compare HMO vs PPO options
            3. Check if your doctors are in-network
            4. Look at the out-of-pocket maximum
            5. Review prescription drug coverage (formulary)
            """)
        else:
            st.warning(f"""
            **Mixed recommendation - Both could work for you**

            Your answers suggest either option could be appropriate.

            **Consider Medigap if:**
            - Doctor choice is your top priority
            - You want predictable, low out-of-pocket costs
            - You travel frequently

            **Consider Medicare Advantage if:**
            - Budget is your top priority
            - You want extra benefits included
            - You're okay with network restrictions

            **Next step:** Talk to a licensed Medicare insurance agent who can show you specific plans in your area.
            """)

        # Important notes
        st.markdown("---")
        st.markdown("### ⚠️ Important Considerations")

        st.error("""
        **CRITICAL: Switching from Medicare Advantage to Medigap**

        If you've been on Medicare Advantage and want to switch to Medigap later:
        - You may face **medical underwriting** (health questions)
        - You could be **denied coverage** or pay much higher rates
        - Only guaranteed issue is during your initial Medigap Open Enrollment Period (6 months after Part B starts at age 65+)

        **This decision can be difficult to reverse!** Choose carefully.
        """)

        st.info("""
        **💡 Pro Tip:** Many people start with Medigap when they first turn 65, then re-evaluate as they get older.
        Starting with Medicare Advantage is harder to reverse due to underwriting.
        """)

    # Footer
    st.markdown("---")
    st.caption("🏥 *Medigap information based on 2025 CMS guidelines. Premium estimates are illustrative only - contact insurance companies for actual quotes.*")


# Allow direct execution for testing
if __name__ == "__main__":
    show_medigap_comparison()
