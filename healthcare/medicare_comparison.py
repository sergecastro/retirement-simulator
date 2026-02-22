"""
Medicare Comparison Tool - Medigap vs Medicare Advantage
=========================================================
Compare Medigap (Medicare Supplement) plans with Medicare Advantage plans
to help users make informed coverage decisions.

Author: Family Forecast Development Team
Created: November 14, 2025
Version: 1.0 (MVP)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple, Optional

# Import INTAKE integration
from healthcare.intake_integration import load_user_data_for_healthcare, get_snapshot_name


# =============================================================================
# MEDIGAP PLAN DATA (2025)
# =============================================================================

MEDIGAP_PLANS = {
    'Plan G': {
        'description': 'Most popular plan - covers nearly everything except Part B deductible',
        'coverage': {
            'Part A coinsurance and hospital costs': True,
            'Part B coinsurance or copayment': True,
            'Blood (first 3 pints)': True,
            'Part A hospice care coinsurance': True,
            'Skilled nursing facility coinsurance': True,
            'Part A deductible': True,
            'Part B deductible': False,
            'Part B excess charges': True,
            'Foreign travel emergency (up to plan limits)': True
        },
        'avg_premium_age_65': 150,
        'avg_premium_age_70': 165,
        'avg_premium_age_75': 180,
        'avg_premium_age_80': 200,
        'best_for': 'Most people - comprehensive coverage with predictable costs'
    },

    'Plan N': {
        'description': 'Lower premium option with small copays for doctor visits',
        'coverage': {
            'Part A coinsurance and hospital costs': True,
            'Part B coinsurance or copayment': True,
            'Blood (first 3 pints)': True,
            'Part A hospice care coinsurance': True,
            'Skilled nursing facility coinsurance': True,
            'Part A deductible': True,
            'Part B deductible': False,
            'Part B excess charges': False,
            'Foreign travel emergency (up to plan limits)': True
        },
        'avg_premium_age_65': 110,
        'avg_premium_age_70': 125,
        'avg_premium_age_75': 140,
        'avg_premium_age_80': 160,
        'office_visit_copay': 20,
        'er_visit_copay': 50,
        'best_for': 'Healthy people who want lower premiums and don\'t mind copays'
    },

    'Plan F': {
        'description': 'Grandfathered plan - most comprehensive (not available to new Medicare beneficiaries after 2020)',
        'coverage': {
            'Part A coinsurance and hospital costs': True,
            'Part B coinsurance or copayment': True,
            'Blood (first 3 pints)': True,
            'Part A hospice care coinsurance': True,
            'Skilled nursing facility coinsurance': True,
            'Part A deductible': True,
            'Part B deductible': True,
            'Part B excess charges': True,
            'Foreign travel emergency (up to plan limits)': True
        },
        'avg_premium_age_65': 200,
        'avg_premium_age_70': 220,
        'avg_premium_age_75': 240,
        'avg_premium_age_80': 270,
        'best_for': 'Those enrolled before 2020 who want zero out-of-pocket costs',
        'availability': 'Grandfathered only (must have been eligible before 2020)'
    }
}


# =============================================================================
# MEDICARE ADVANTAGE DATA (2025)
# =============================================================================

ADVANTAGE_PLANS = {
    'HMO': {
        'name': 'Health Maintenance Organization',
        'description': 'Network-based plan with lower costs but less flexibility',
        'avg_premium': 0,  # Many MA plans have $0 premium
        'avg_max_out_of_pocket': 5500,
        'network_restriction': True,
        'referrals_required': True,
        'typical_copays': {
            'primary_care': 10,
            'specialist': 40,
            'er_visit': 90,
            'urgent_care': 40,
            'hospital_per_day': 350
        },
        'prescription_coverage': True,
        'dental_vision_hearing': 'Often included',
        'pros': [
            'Often $0 monthly premium',
            'Out-of-pocket maximum protects you',
            'May include dental, vision, hearing',
            'Prescription drug coverage included',
            'Care coordination'
        ],
        'cons': [
            'Must use network providers (except emergencies)',
            'Need referrals for specialists',
            'Limited coverage when traveling',
            'May have prior authorization requirements',
            'Can\'t keep if you move out of service area'
        ],
        'best_for': 'People who don\'t travel much, comfortable with network restrictions, want extra benefits'
    },

    'PPO': {
        'name': 'Preferred Provider Organization',
        'description': 'More flexibility to see any doctor but higher costs',
        'avg_premium': 50,
        'avg_max_out_of_pocket': 6500,
        'network_restriction': False,  # Can see out-of-network providers
        'referrals_required': False,
        'typical_copays': {
            'primary_care': 15,
            'specialist': 50,
            'er_visit': 100,
            'urgent_care': 50,
            'hospital_per_day': 400
        },
        'prescription_coverage': True,
        'dental_vision_hearing': 'Sometimes included',
        'pros': [
            'See any doctor (lower cost in-network)',
            'No referrals needed',
            'Works when traveling in US',
            'Out-of-pocket maximum protection',
            'Prescription coverage included'
        ],
        'cons': [
            'Higher premiums than HMO',
            'Higher costs for out-of-network care',
            'Still need to stay in service area',
            'May have prior authorization',
            'More expensive than Medigap for heavy users'
        ],
        'best_for': 'People who want flexibility, travel domestically, see multiple specialists'
    }
}


# 2026 Medicare constants
PART_B_DEDUCTIBLE_2026 = 283
PART_B_PREMIUM_2026 = 202.90


# =============================================================================
# COST CALCULATION FUNCTIONS
# =============================================================================

def calculate_medigap_annual_cost(plan_name: str, age: int, usage_scenario: str = 'average') -> Dict:
    """
    Calculate estimated annual costs for a Medigap plan.

    Args:
        plan_name: Name of Medigap plan (e.g., 'Plan G')
        age: User's current age
        usage_scenario: 'low', 'average', or 'high' healthcare usage

    Returns:
        dict with cost breakdown
    """
    plan = MEDIGAP_PLANS.get(plan_name, MEDIGAP_PLANS['Plan G'])

    # Estimate premium based on age
    if age < 68:
        monthly_premium = plan['avg_premium_age_65']
    elif age < 73:
        monthly_premium = plan['avg_premium_age_70']
    elif age < 78:
        monthly_premium = plan['avg_premium_age_75']
    else:
        monthly_premium = plan['avg_premium_age_80']

    annual_medigap_premium = monthly_premium * 12
    annual_part_b_premium = PART_B_PREMIUM_2026 * 12

    # Part B deductible (only if plan doesn't cover it)
    part_b_deductible = 0 if plan['coverage']['Part B deductible'] else PART_B_DEDUCTIBLE_2026

    # Estimate out-of-pocket for Plan N copays
    copay_costs = 0
    if plan_name == 'Plan N':
        if usage_scenario == 'low':
            # Estimate: 3 doctor visits, 0 ER visits
            copay_costs = (3 * plan.get('office_visit_copay', 0))
        elif usage_scenario == 'average':
            # Estimate: 6 doctor visits, 1 ER visit
            copay_costs = (6 * plan.get('office_visit_copay', 0)) + plan.get('er_visit_copay', 0)
        else:  # high
            # Estimate: 12 doctor visits, 2 ER visits
            copay_costs = (12 * plan.get('office_visit_copay', 0)) + (2 * plan.get('er_visit_copay', 0))

    total_annual_cost = annual_medigap_premium + annual_part_b_premium + part_b_deductible + copay_costs

    return {
        'medigap_premium': annual_medigap_premium,
        'part_b_premium': annual_part_b_premium,
        'part_b_deductible': part_b_deductible,
        'copays': copay_costs,
        'total_annual_cost': total_annual_cost,
        'monthly_average': total_annual_cost / 12
    }


def calculate_advantage_annual_cost(plan_type: str, usage_scenario: str = 'average') -> Dict:
    """
    Calculate estimated annual costs for Medicare Advantage plan.

    Args:
        plan_type: 'HMO' or 'PPO'
        usage_scenario: 'low', 'average', or 'high' healthcare usage

    Returns:
        dict with cost breakdown
    """
    plan = ADVANTAGE_PLANS.get(plan_type, ADVANTAGE_PLANS['HMO'])

    annual_premium = plan['avg_premium'] * 12

    # Estimate out-of-pocket based on usage
    if usage_scenario == 'low':
        # Light usage: 3 doctor visits, no ER, no hospitalization
        estimated_oop = (3 * plan['typical_copays']['primary_care'])
    elif usage_scenario == 'average':
        # Average: 6 doctor visits, 2 specialist, 1 ER, 0.1 hospital stays
        estimated_oop = (
            (6 * plan['typical_copays']['primary_care']) +
            (2 * plan['typical_copays']['specialist']) +
            plan['typical_copays']['er_visit'] +
            (0.1 * plan['typical_copays']['hospital_per_day'] * 3)  # 10% chance of 3-day stay
        )
    else:  # high
        # Heavy usage: 12 doctor visits, 6 specialist, 2 ER, 0.3 hospital stays
        estimated_oop = min(
            (12 * plan['typical_copays']['primary_care']) +
            (6 * plan['typical_copays']['specialist']) +
            (2 * plan['typical_copays']['er_visit']) +
            (0.3 * plan['typical_copays']['hospital_per_day'] * 5),  # 30% chance of 5-day stay
            plan['avg_max_out_of_pocket']
        )

    total_annual_cost = annual_premium + estimated_oop

    return {
        'ma_premium': annual_premium,
        'estimated_out_of_pocket': estimated_oop,
        'max_out_of_pocket': plan['avg_max_out_of_pocket'],
        'total_annual_cost': total_annual_cost,
        'monthly_average': total_annual_cost / 12
    }


# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================

def get_plan_recommendation(age: int, health_status: str, travel_frequency: str,
                           budget_preference: str) -> Dict:
    """
    Simple recommendation algorithm based on user profile.

    Args:
        age: User's age
        health_status: 'excellent', 'good', 'fair', 'poor'
        travel_frequency: 'rarely', 'occasionally', 'frequently'
        budget_preference: 'minimize_monthly', 'minimize_total', 'predictable'

    Returns:
        dict with recommendation and reasoning
    """
    score_medigap_g = 0
    score_medigap_n = 0
    score_ma_hmo = 0
    score_ma_ppo = 0

    # Age factor (Medigap premiums increase with age)
    if age < 70:
        score_ma_hmo += 2
        score_ma_ppo += 2

    # Health status
    if health_status in ['excellent', 'good']:
        score_medigap_n += 2
        score_ma_hmo += 3
    else:
        score_medigap_g += 3
        score_ma_ppo += 1

    # Travel frequency
    if travel_frequency == 'frequently':
        score_medigap_g += 3
        score_medigap_n += 3
    elif travel_frequency == 'occasionally':
        score_medigap_g += 1
        score_ma_ppo += 1
    else:  # rarely
        score_ma_hmo += 2

    # Budget preference
    if budget_preference == 'minimize_monthly':
        score_ma_hmo += 3
        score_medigap_n += 1
    elif budget_preference == 'minimize_total':
        score_medigap_n += 2
        score_ma_hmo += 1
    else:  # predictable
        score_medigap_g += 3

    # Find winner
    scores = {
        'Medigap Plan G': score_medigap_g,
        'Medigap Plan N': score_medigap_n,
        'Medicare Advantage HMO': score_ma_hmo,
        'Medicare Advantage PPO': score_ma_ppo
    }

    recommended = max(scores, key=scores.get)

    # Build reasoning
    reasons = []
    if 'Medigap' in recommended:
        reasons.append("Provides nationwide coverage and doctor choice")
        reasons.append("Predictable costs with less paperwork")
        if travel_frequency == 'frequently':
            reasons.append("Works anywhere in the US")
    else:
        reasons.append("Lower monthly premiums")
        reasons.append("Includes prescription drug coverage")
        if 'HMO' in recommended:
            reasons.append("May include dental, vision, and hearing benefits")
        else:
            reasons.append("Flexibility to see out-of-network providers")

    return {
        'recommended_plan': recommended,
        'confidence': 'High' if scores[recommended] >= 6 else 'Medium',
        'reasons': reasons,
        'scores': scores
    }


# =============================================================================
# STREAMLIT UI
# =============================================================================

def show_comparison_page():
    """Main comparison page UI"""

    # Header
    st.title("🏥 Medigap vs Medicare Advantage Comparison")
    st.markdown("**Compare coverage options to find the best fit for your situation**")

    # Back button
    if st.button("← Back to Healthcare Hub"):
        st.session_state['healthcare_page'] = 'hub'
        st.rerun()

    st.markdown("---")

    # Load INTAKE data
    intake_data = load_user_data_for_healthcare()
    snapshot_name = get_snapshot_name()

    # Sidebar inputs
    st.sidebar.header("📋 Your Profile")

    # Show auto-fill status
    if intake_data['data_loaded']:
        st.sidebar.success(f"✅ Using data from: {intake_data['user_name']}")
        if snapshot_name:
            st.sidebar.caption(f"📋 Plan: {snapshot_name}")
        st.sidebar.markdown("---")

    # Age (auto-filled)
    age = st.sidebar.number_input(
        "Your Age",
        min_value=65,
        max_value=100,
        value=intake_data.get('age', 65),
        help="Medicare eligibility starts at 65"
    )

    # Health status
    health_status = st.sidebar.selectbox(
        "Current Health Status",
        ['excellent', 'good', 'fair', 'poor'],
        index=1,
        format_func=lambda x: x.capitalize()
    )

    # Travel frequency
    travel_frequency = st.sidebar.selectbox(
        "How often do you travel?",
        ['rarely', 'occasionally', 'frequently'],
        index=1,
        format_func=lambda x: x.capitalize()
    )

    # Budget preference
    budget_preference = st.sidebar.selectbox(
        "What's most important to you?",
        ['minimize_monthly', 'predictable', 'minimize_total'],
        index=1,
        format_func=lambda x: {
            'minimize_monthly': 'Lowest Monthly Cost',
            'predictable': 'Predictable Costs',
            'minimize_total': 'Lowest Total Cost'
        }[x]
    )

    # Usage scenario
    usage_scenario = st.sidebar.radio(
        "Expected Healthcare Usage",
        ['low', 'average', 'high'],
        index=1,
        format_func=lambda x: {
            'low': 'Low (Rarely see doctor)',
            'average': 'Average (Occasional visits)',
            'high': 'High (Frequent medical needs)'
        }[x]
    )

    st.sidebar.markdown("---")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💡 Recommendation", "📊 Cost Comparison", "📋 Coverage Details", "ℹ️ Learn More"])

    with tab1:
        show_recommendation_tab(age, health_status, travel_frequency, budget_preference, usage_scenario)

    with tab2:
        show_cost_comparison_tab(age, usage_scenario)

    with tab3:
        show_coverage_details_tab()

    with tab4:
        show_learn_more_tab()


def show_recommendation_tab(age, health_status, travel_frequency, budget_preference, usage_scenario):
    """Show personalized recommendation"""
    st.header("💡 Your Personalized Recommendation")

    recommendation = get_plan_recommendation(age, health_status, travel_frequency, budget_preference)

    # Show recommendation
    st.success(f"### Recommended: {recommendation['recommended_plan']}")
    st.caption(f"Confidence: {recommendation['confidence']}")

    st.markdown("**Why this recommendation:**")
    for reason in recommendation['reasons']:
        st.markdown(f"- {reason}")

    st.markdown("---")

    # Show all scores
    st.subheader("📊 How Plans Stack Up For You")
    scores_df = pd.DataFrame([
        {'Plan': k, 'Match Score': v}
        for k, v in recommendation['scores'].items()
    ]).sort_values('Match Score', ascending=False)

    fig = px.bar(
        scores_df,
        x='Match Score',
        y='Plan',
        orientation='h',
        color='Match Score',
        color_continuous_scale='Blues'
    )
    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 **Next Steps:** Review the Cost Comparison and Coverage Details tabs to verify this recommendation fits your needs.")


def show_cost_comparison_tab(age, usage_scenario):
    """Show cost comparison between plans"""
    st.header("📊 Annual Cost Comparison")

    st.markdown(f"**Based on:** Age {age}, {usage_scenario.capitalize()} healthcare usage")

    # Calculate costs for all plans
    costs = {
        'Medigap Plan G': calculate_medigap_annual_cost('Plan G', age, usage_scenario),
        'Medigap Plan N': calculate_medigap_annual_cost('Plan N', age, usage_scenario),
        'MA HMO': calculate_advantage_annual_cost('HMO', usage_scenario),
        'MA PPO': calculate_advantage_annual_cost('PPO', usage_scenario)
    }

    # Create comparison table
    comparison_data = []
    for plan_name, cost_data in costs.items():
        comparison_data.append({
            'Plan': plan_name,
            'Monthly Cost': f"${cost_data['monthly_average']:.0f}",
            'Annual Cost': f"${cost_data['total_annual_cost']:.0f}"
        })

    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Visual comparison
    st.subheader("Annual Cost Comparison")

    chart_data = pd.DataFrame([
        {'Plan': k, 'Annual Cost': v['total_annual_cost']}
        for k, v in costs.items()
    ])

    fig = px.bar(
        chart_data,
        x='Plan',
        y='Annual Cost',
        color='Annual Cost',
        color_continuous_scale='RdYlGn_r'
    )
    fig.update_layout(
        showlegend=False,
        height=400,
        yaxis_title="Annual Cost ($)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed breakdown
    with st.expander("📋 See Detailed Cost Breakdown"):
        for plan_name, cost_data in costs.items():
            st.markdown(f"**{plan_name}:**")
            for key, value in cost_data.items():
                if key != 'monthly_average':
                    st.caption(f"  {key.replace('_', ' ').title()}: ${value:,.0f}")
            st.markdown("")


def show_coverage_details_tab():
    """Show detailed coverage comparison"""
    st.header("📋 Coverage Details")

    # Medigap coverage comparison
    st.subheader("Medigap Plan Coverage")

    coverage_items = list(MEDIGAP_PLANS['Plan G']['coverage'].keys())
    coverage_data = []

    for item in coverage_items:
        coverage_data.append({
            'Benefit': item,
            'Plan G': '✅' if MEDIGAP_PLANS['Plan G']['coverage'][item] else '❌',
            'Plan N': '✅' if MEDIGAP_PLANS['Plan N']['coverage'][item] else '❌',
            'Plan F': '✅' if MEDIGAP_PLANS['Plan F']['coverage'][item] else '❌'
        })

    df = pd.DataFrame(coverage_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.caption("✅ = Covered | ❌ = Not Covered")

    # Medicare Advantage comparison
    st.subheader("Medicare Advantage Plan Features")

    ma_comparison = pd.DataFrame([
        {'Feature': 'Average Monthly Premium', 'HMO': '$0', 'PPO': '$50'},
        {'Feature': 'Network Restrictions', 'HMO': 'Yes - Must use network', 'PPO': 'Preferred network (can go out)'},
        {'Feature': 'Referrals Required', 'HMO': 'Yes', 'PPO': 'No'},
        {'Feature': 'Prescription Coverage', 'HMO': 'Included', 'PPO': 'Included'},
        {'Feature': 'Dental/Vision/Hearing', 'HMO': 'Often included', 'PPO': 'Sometimes'},
        {'Feature': 'Max Out-of-Pocket', 'HMO': '$5,500', 'PPO': '$6,500'}
    ])

    st.dataframe(ma_comparison, use_container_width=True, hide_index=True)


def show_learn_more_tab():
    """Educational content"""
    st.header("ℹ️ Understanding Your Options")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏥 Medigap (Supplement)")
        st.markdown("""
        **What is it?**
        - Private insurance that supplements Original Medicare
        - Standardized plans (lettered A-N)
        - Covers "gaps" in Medicare coverage

        **Key Benefits:**
        - Works nationwide
        - Choose any doctor who accepts Medicare
        - Predictable costs
        - No networks or referrals

        **Considerations:**
        - Monthly premiums increase with age
        - Must purchase Part D separately
        - No dental/vision/hearing coverage
        - Guaranteed issue during initial enrollment only
        """)

    with col2:
        st.subheader("🏥 Medicare Advantage (Part C)")
        st.markdown("""
        **What is it?**
        - Alternative to Original Medicare
        - Run by private insurance companies
        - Bundles Part A, B, and usually D

        **Key Benefits:**
        - Often $0 premium
        - Out-of-pocket maximum protection
        - May include dental, vision, hearing
        - Prescription coverage included

        **Considerations:**
        - Must use network providers (except emergencies)
        - Coverage limited to service area
        - May need referrals for specialists
        - Can change annually during open enrollment
        """)

    st.markdown("---")

    st.warning("""
    ⚠️ **Important:** This tool provides educational information and estimates only.
    Actual costs vary by location, insurance company, and plan. Always consult with a
    licensed insurance agent or Medicare counselor before making coverage decisions.
    """)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Test function
    show_comparison_page()
