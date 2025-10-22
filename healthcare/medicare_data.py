"""
Medicare Data Repository
========================
Comprehensive data tables for Medicare costs, IRMAA brackets, regional adjustments,
and historical trends. This module provides all the reference data needed for
Medicare cost projections.

Author: ForeCash Development Team
Last Updated: October 22, 2025
Data Sources: CMS, Kaiser Family Foundation, AARP
"""

from typing import Dict, List
from dataclasses import dataclass


# =============================================================================
# HISTORICAL MEDICARE PREMIUMS (2020-2025)
# =============================================================================

HISTORICAL_PART_B_PREMIUMS = {
    2020: 144.60,
    2021: 148.50,
    2022: 170.10,  # Large jump due to Aduhelm drug coverage
    2023: 164.90,  # Slight decrease after Aduhelm removal
    2024: 174.70,
    2025: 174.70,  # Projected (actual may vary)
}

HISTORICAL_PART_D_BASE_PREMIUMS = {
    2020: 32.74,
    2021: 33.06,
    2022: 33.00,
    2023: 32.74,
    2024: 55.00,  # Estimated average
    2025: 55.00,  # Projected average
}


# =============================================================================
# IRMAA HISTORICAL BRACKETS (Single Filers)
# =============================================================================

IRMAA_BRACKETS_HISTORY = {
    2023: {
        "brackets": [
            {"max": 97000, "part_b": 0, "part_d": 0},
            {"max": 123000, "part_b": 65.90, "part_d": 12.20},
            {"max": 153000, "part_b": 164.90, "part_d": 31.50},
            {"max": 183000, "part_b": 263.90, "part_d": 50.70},
            {"max": 500000, "part_b": 362.90, "part_d": 70.00},
            {"max": float('inf'), "part_b": 395.60, "part_d": 76.40},
        ]
    },
    2024: {
        "brackets": [
            {"max": 103000, "part_b": 0, "part_d": 0},
            {"max": 129000, "part_b": 69.90, "part_d": 12.90},
            {"max": 161000, "part_b": 174.70, "part_d": 33.30},
            {"max": 193000, "part_b": 279.50, "part_d": 53.80},
            {"max": 500000, "part_b": 384.30, "part_d": 74.20},
            {"max": float('inf'), "part_b": 419.30, "part_d": 81.00},
        ]
    },
    2025: {
        "brackets": [
            {"max": 106000, "part_b": 0, "part_d": 0},
            {"max": 133000, "part_b": 69.90, "part_d": 12.90},
            {"max": 167000, "part_b": 174.70, "part_d": 33.30},
            {"max": 200000, "part_b": 279.50, "part_d": 53.80},
            {"max": 500000, "part_b": 384.30, "part_d": 74.20},
            {"max": float('inf'), "part_b": 419.30, "part_d": 81.00},
        ]
    }
}


# =============================================================================
# PART A (HOSPITAL INSURANCE) DATA
# =============================================================================

# Part A Premium (for those without 40 quarters of coverage)
PART_A_PREMIUM_2025 = {
    "30_39_quarters": 278.00,  # Monthly premium with 30-39 quarters
    "less_than_30_quarters": 505.00,  # Monthly premium with <30 quarters
}

# Part A Deductibles and Coinsurance
PART_A_COST_SHARING_2025 = {
    "inpatient_deductible": 1632,  # Per benefit period
    "skilled_nursing_coinsurance": {
        "days_1_20": 0,
        "days_21_100": 204.00  # Per day
    },
    "daily_coinsurance": {
        "days_61_90": 408,  # Per day
        "lifetime_reserve_days": 816  # Per day (60 lifetime days)
    }
}


# =============================================================================
# PART B (MEDICAL INSURANCE) COST SHARING
# =============================================================================

PART_B_COST_SHARING_2025 = {
    "annual_deductible": 240,
    "coinsurance_rate": 0.20,  # 20% of Medicare-approved amount
    "preventive_services_copay": 0  # Most preventive services are free
}


# =============================================================================
# PART D (PRESCRIPTION DRUGS) STRUCTURE
# =============================================================================

PART_D_COST_STRUCTURE_2025 = {
    "annual_deductible_max": 545,  # Maximum deductible (plans vary)
    "initial_coverage_limit": 5030,  # Total drug costs before coverage gap
    "catastrophic_threshold": 8000,  # Out-of-pocket costs before catastrophic coverage
    "coverage_gap": {
        "brand_name_discount": 0.70,  # 70% manufacturer discount + 5% plan = 25% you pay
        "generic_discount": 0.75  # 75% plan coverage = 25% you pay
    },
    "catastrophic_coverage": {
        "greater_of": {
            "percentage": 0.05,  # 5% coinsurance OR
            "copay_generic": 4.50,  # $4.50 for generic
            "copay_brand": 11.20  # $11.20 for brand name
        }
    }
}


# =============================================================================
# AVERAGE PART D PREMIUMS BY STATE (2025 Estimates)
# =============================================================================

STATE_PART_D_PREMIUMS = {
    # National average
    "US_AVERAGE": 55.00,

    # Top 10 most populous states
    "CA": 58.00,  # California
    "TX": 52.00,  # Texas
    "FL": 56.00,  # Florida
    "NY": 62.00,  # New York
    "PA": 54.00,  # Pennsylvania
    "IL": 56.00,  # Illinois
    "OH": 53.00,  # Ohio
    "GA": 51.00,  # Georgia
    "NC": 52.00,  # North Carolina
    "MI": 55.00,  # Michigan

    # Additional states (alphabetical)
    "AZ": 54.00,
    "CO": 56.00,
    "MA": 60.00,
    "NJ": 61.00,
    "VA": 53.00,
    "WA": 57.00,
}


# =============================================================================
# MEDIGAP (SUPPLEMENT) AVERAGE PREMIUMS BY STATE
# =============================================================================

@dataclass
class MedigapPremiums:
    """Average monthly Medigap premiums by plan type"""
    plan_g: float  # Most popular plan
    plan_n: float  # Lower cost alternative
    plan_f: float  # Only for those eligible before 2020


STATE_MEDIGAP_PREMIUMS = {
    "US_AVERAGE": MedigapPremiums(plan_g=150.00, plan_n=120.00, plan_f=180.00),

    # Varies significantly by state and age
    "CA": MedigapPremiums(plan_g=140.00, plan_n=110.00, plan_f=170.00),
    "TX": MedigapPremiums(plan_g=145.00, plan_n=115.00, plan_f=175.00),
    "FL": MedigapPremiums(plan_g=165.00, plan_n=135.00, plan_f=195.00),
    "NY": MedigapPremiums(plan_g=200.00, plan_n=160.00, plan_f=230.00),  # Community rated
    "PA": MedigapPremiums(plan_g=155.00, plan_n=125.00, plan_f=185.00),
    "IL": MedigapPremiums(plan_g=148.00, plan_n=118.00, plan_f=178.00),
    "OH": MedigapPremiums(plan_g=142.00, plan_n=112.00, plan_f=172.00),
    "GA": MedigapPremiums(plan_g=138.00, plan_n=108.00, plan_f=168.00),
    "NC": MedigapPremiums(plan_g=135.00, plan_n=105.00, plan_f=165.00),
    "MI": MedigapPremiums(plan_g=152.00, plan_n=122.00, plan_f=182.00),
}


# =============================================================================
# MEDICARE ADVANTAGE (PART C) AVERAGE PREMIUMS
# =============================================================================

MEDICARE_ADVANTAGE_DATA = {
    "national_average_premium": 18.00,  # Monthly premium (2025)
    "percent_zero_premium_plans": 0.57,  # 57% of plans have $0 premium
    "average_out_of_pocket_max": 5500,  # Average MOOP
    "typical_copays": {
        "primary_care_visit": 10.00,
        "specialist_visit": 40.00,
        "emergency_room": 90.00,
        "urgent_care": 40.00,
        "inpatient_hospital_per_day": 325.00,
        "generic_drugs_tier1": 5.00,
        "preferred_brand_drugs_tier2": 47.00,
    }
}


# =============================================================================
# MEDICARE SAVINGS PROGRAMS (MSP) INCOME LIMITS
# =============================================================================

MEDICARE_SAVINGS_PROGRAMS_2025 = {
    "QMB": {  # Qualified Medicare Beneficiary
        "name": "Qualified Medicare Beneficiary (QMB)",
        "income_limit_single": 1275,  # Monthly
        "income_limit_married": 1725,
        "asset_limit_single": 9430,
        "asset_limit_married": 14130,
        "covers": ["Part A premium", "Part B premium", "Deductibles", "Coinsurance"]
    },
    "SLMB": {  # Specified Low-Income Medicare Beneficiary
        "name": "Specified Low-Income Medicare Beneficiary (SLMB)",
        "income_limit_single": 1533,
        "income_limit_married": 2070,
        "asset_limit_single": 9430,
        "asset_limit_married": 14130,
        "covers": ["Part B premium"]
    },
    "QI": {  # Qualifying Individual
        "name": "Qualifying Individual (QI)",
        "income_limit_single": 1724,
        "income_limit_married": 2327,
        "asset_limit_single": 9430,
        "asset_limit_married": 14130,
        "covers": ["Part B premium"]
    }
}


# =============================================================================
# EXTRA HELP (LOW INCOME SUBSIDY) FOR PART D
# =============================================================================

EXTRA_HELP_2025 = {
    "full_subsidy": {
        "income_limit_single": 1719,  # Monthly (~150% FPL)
        "income_limit_married": 2318,
        "asset_limit_single": 10930,
        "asset_limit_married": 17130,
        "premium_subsidy": 1.00,  # 100%
        "deductible": 0,
        "copays": {
            "generic": 0,
            "brand": 0
        }
    },
    "partial_subsidy": {
        "income_limit_single": 1911,  # Monthly (~165% FPL)
        "income_limit_married": 2578,
        "asset_limit_single": 16630,
        "asset_limit_married": 33230,
        "premium_subsidy": 0.75,  # 75%
        "deductible": 110,
        "copays": {
            "generic": 4.50,
            "brand": 11.20
        }
    }
}


# =============================================================================
# INFLATION PROJECTIONS FOR MEDICARE COSTS
# =============================================================================

MEDICARE_INFLATION_RATES = {
    "historical_average_part_b": 0.057,  # 5.7% average annual increase
    "conservative_projection": 0.04,  # 4% for conservative planning
    "moderate_projection": 0.05,  # 5% moderate
    "aggressive_projection": 0.065,  # 6.5% aggressive
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_part_d_premium_for_state(state_code: str) -> float:
    """
    Get average Part D premium for a state

    Args:
        state_code: Two-letter state code (e.g., "CA", "TX")

    Returns:
        float: Average monthly Part D premium for that state
    """
    return STATE_PART_D_PREMIUMS.get(state_code.upper(), STATE_PART_D_PREMIUMS["US_AVERAGE"])


def get_medigap_premiums_for_state(state_code: str) -> MedigapPremiums:
    """
    Get average Medigap premiums for a state

    Args:
        state_code: Two-letter state code

    Returns:
        MedigapPremiums: Object with plan G, N, and F premiums
    """
    return STATE_MEDIGAP_PREMIUMS.get(state_code.upper(), STATE_MEDIGAP_PREMIUMS["US_AVERAGE"])


def calculate_medigap_premium_by_age(base_premium: float, age: int) -> float:
    """
    Estimate Medigap premium based on age (attained-age pricing)

    Most Medigap plans use attained-age pricing where premiums increase
    as you get older. This is a simplified model.

    Args:
        base_premium: Base premium at age 65
        age: Current age

    Returns:
        float: Estimated premium for given age
    """
    if age < 65:
        return base_premium  # Not eligible yet

    # Approximate 3-4% increase per year after 65
    years_after_65 = age - 65
    age_factor = (1.035 ** years_after_65)  # 3.5% per year

    return round(base_premium * age_factor, 2)


def project_part_b_premium(
    years_from_now: int,
    starting_premium: float = None,
    inflation_rate: float = None
) -> float:
    """
    Project future Part B premium with inflation

    Args:
        years_from_now: Number of years into the future
        starting_premium: Current premium (default: 2025 rate)
        inflation_rate: Annual increase rate (default: moderate 5%)

    Returns:
        float: Projected premium
    """
    if starting_premium is None:
        starting_premium = HISTORICAL_PART_B_PREMIUMS[2025]

    if inflation_rate is None:
        inflation_rate = MEDICARE_INFLATION_RATES["moderate_projection"]

    projected = starting_premium * ((1 + inflation_rate) ** years_from_now)
    return round(projected, 2)


def get_medicare_cost_summary(
    state_code: str = "US_AVERAGE",
    include_medigap_g: bool = True,
    age: int = 65
) -> Dict:
    """
    Get complete Medicare cost summary for a state

    Args:
        state_code: Two-letter state code
        include_medigap_g: Whether to include Medigap Plan G
        age: Current age (for Medigap pricing)

    Returns:
        dict: Complete cost summary
    """
    part_b = HISTORICAL_PART_B_PREMIUMS[2025]
    part_d = get_part_d_premium_for_state(state_code)

    costs = {
        "part_b_monthly": part_b,
        "part_d_monthly": part_d,
        "medicare_base_monthly": part_b + part_d,
        "medicare_base_annual": (part_b + part_d) * 12,
    }

    if include_medigap_g:
        medigap = get_medigap_premiums_for_state(state_code)
        medigap_premium = calculate_medigap_premium_by_age(medigap.plan_g, age)
        costs["medigap_g_monthly"] = medigap_premium
        costs["total_with_medigap_monthly"] = costs["medicare_base_monthly"] + medigap_premium
        costs["total_with_medigap_annual"] = costs["total_with_medigap_monthly"] * 12

    return costs


# =============================================================================
# TESTING AND EXAMPLES
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MEDICARE DATA REPOSITORY - TEST EXAMPLES")
    print("=" * 70)

    # Example 1: Historical premium trends
    print("\n📊 Historical Part B Premium Trends:")
    print("-" * 70)
    for year, premium in sorted(HISTORICAL_PART_B_PREMIUMS.items()):
        print(f"{year}: ${premium:.2f}/month")

    # Example 2: State-specific costs
    print("\n📊 Medicare Costs by State (Age 65):")
    print("-" * 70)
    for state in ["CA", "FL", "NY", "TX"]:
        costs = get_medicare_cost_summary(state, include_medigap_g=True, age=65)
        print(f"\n{state}:")
        print(f"  Medicare Base: ${costs['medicare_base_monthly']:.2f}/month")
        print(f"  + Medigap Plan G: ${costs['medigap_g_monthly']:.2f}/month")
        print(f"  Total: ${costs['total_with_medigap_monthly']:.2f}/month (${costs['total_with_medigap_annual']:,.2f}/year)")

    # Example 3: Age-based Medigap pricing
    print("\n📊 Medigap Plan G Premium by Age (California):")
    print("-" * 70)
    base_premium = STATE_MEDIGAP_PREMIUMS["CA"].plan_g
    for age in [65, 70, 75, 80, 85]:
        premium = calculate_medigap_premium_by_age(base_premium, age)
        print(f"Age {age}: ${premium:.2f}/month")

    # Example 4: Future projections
    print("\n📊 Projected Part B Premium (5% inflation):")
    print("-" * 70)
    for years in [5, 10, 15, 20]:
        future = project_part_b_premium(years)
        print(f"In {years} years: ${future:.2f}/month")

    print("\n" + "=" * 70)
    print("✅ Medicare Data Repository - Ready for Integration!")
    print("=" * 70)
