"""
Roth Conversion Sweet Spot Calculator
======================================
Calculate optimal Roth conversion amounts to minimize lifetime taxes.

Key strategy: Convert traditional IRA/401k to Roth during "gap years"
(after peak earning, before RMDs) to stay within target tax bracket.
"""

from typing import Dict


# =============================================================================
# TAX BRACKET DATA (2025 Federal - Married Filing Jointly)
# =============================================================================

TAX_BRACKETS_MFJ_2025 = {
    "10%": {"min": 0, "max": 23_850, "rate": 0.10},
    "12%": {"min": 23_850, "max": 94_300, "rate": 0.12},
    "22%": {"min": 94_300, "max": 201_050, "rate": 0.22},
    "24%": {"min": 201_050, "max": 383_900, "rate": 0.24},
    "32%": {"min": 383_900, "max": 487_450, "rate": 0.32},
    "35%": {"min": 487_450, "max": 731_200, "rate": 0.35},
    "37%": {"min": 731_200, "max": float('inf'), "rate": 0.37}
}

TAX_BRACKETS_SINGLE_2025 = {
    "10%": {"min": 0, "max": 11_925, "rate": 0.10},
    "12%": {"min": 11_925, "max": 48_475, "rate": 0.12},
    "22%": {"min": 48_475, "max": 103_350, "rate": 0.22},
    "24%": {"min": 103_350, "max": 197_300, "rate": 0.24},
    "32%": {"min": 197_300, "max": 250_525, "rate": 0.32},
    "35%": {"min": 250_525, "max": 626_350, "rate": 0.35},
    "37%": {"min": 626_350, "max": float('inf'), "rate": 0.37}
}


def get_tax_bracket_max(target_bracket: str, filing_status: str = "married") -> float:
    """
    Get the maximum income for a tax bracket.

    Args:
        target_bracket: "12%", "22%", or "24%"
        filing_status: "single" or "married"

    Returns:
        Maximum income before hitting next bracket
    """
    brackets = TAX_BRACKETS_MFJ_2025 if filing_status == "married" else TAX_BRACKETS_SINGLE_2025
    return brackets.get(target_bracket, {}).get("max", 94_300)


def calculate_roth_sweet_spot(
    current_age: int,
    trad_ira_balance: float,
    roth_balance: float,
    current_taxable_income: float,
    target_bracket: str = "22%",
    conversion_start_age: int = None,
    conversion_end_age: int = 72,
    filing_status: str = "married",
    future_rmd_bracket_rate: float = 0.24
) -> Dict:
    """
    Calculate optimal Roth conversion strategy.

    Strategy: Fill up target tax bracket each year with conversions.

    Args:
        current_age: User's current age
        trad_ira_balance: Total traditional IRA/401k balance
        roth_balance: Current Roth IRA balance
        current_taxable_income: Annual taxable income (before retirement)
        target_bracket: Tax bracket to stay within ("12%", "22%", "24%")
        conversion_start_age: When to start conversions (default: current age)
        conversion_end_age: When to stop (default: 72, before RMDs)
        filing_status: "single" or "married"
        future_rmd_bracket_rate: Expected tax rate on RMDs if no conversion (default: 24%)

    Returns:
        Dict with conversion strategy and savings calculations
    """
    if conversion_start_age is None:
        conversion_start_age = max(current_age, 60)  # Start at current age or 60

    # Get bracket ceiling
    bracket_max = get_tax_bracket_max(target_bracket, filing_status)

    # Calculate annual conversion headroom (how much can convert and stay in bracket)
    annual_headroom = max(0, bracket_max - current_taxable_income)

    # Number of conversion years
    conversion_years = max(0, conversion_end_age - conversion_start_age)

    # Total we could convert over the window
    total_convertible = annual_headroom * conversion_years

    # Can't convert more than we have
    total_converted = min(total_convertible, trad_ira_balance)

    # If we can't convert everything, we'll do what we can
    if total_converted < total_convertible:
        # We can convert the full balance
        actual_years_needed = total_converted / annual_headroom if annual_headroom > 0 else 0
    else:
        actual_years_needed = conversion_years

    # Tax calculations
    # Get the rate for the target bracket
    brackets = TAX_BRACKETS_MFJ_2025 if filing_status == "married" else TAX_BRACKETS_SINGLE_2025
    target_rate = brackets.get(target_bracket, {}).get("rate", 0.22)

    # Tax paid now on conversions (at target bracket rate)
    tax_paid_now = total_converted * target_rate

    # Tax that would be paid later on RMDs (assume higher bracket)
    # RMDs are forced distributions that push you into higher brackets
    tax_if_no_conversion = total_converted * future_rmd_bracket_rate

    # Lifetime savings
    lifetime_savings = tax_if_no_conversion - tax_paid_now

    # Additional benefits
    # IRMAA thresholds (Medicare Part B/D surcharges)
    irmaa_threshold_mfj = 206_000  # 2025 threshold
    irmaa_savings_estimate = 0
    if current_taxable_income + (total_converted / conversion_years if conversion_years > 0 else 0) > irmaa_threshold_mfj:
        # Estimate IRMAA avoidance savings
        irmaa_savings_estimate = 2100 * conversion_years  # ~$175/month extra for Part B

    # RMD reduction estimate
    # At age 73, RMD factor is about 26.5 (3.77% withdrawal)
    # At age 80, RMD factor is about 20.2 (4.95% withdrawal)
    remaining_trad_after_conversion = trad_ira_balance - total_converted
    rmd_at_73_if_no_conversion = trad_ira_balance * 0.0377
    rmd_at_73_after_conversion = remaining_trad_after_conversion * 0.0377
    rmd_reduction = rmd_at_73_if_no_conversion - rmd_at_73_after_conversion

    # Percentage of traditional IRA converted
    conversion_percentage = (total_converted / trad_ira_balance * 100) if trad_ira_balance > 0 else 0

    return {
        # Core strategy
        "annual_conversion_amount": annual_headroom,
        "conversion_years": conversion_years,
        "total_converted": total_converted,
        "remaining_traditional": remaining_trad_after_conversion,
        "conversion_percentage": conversion_percentage,

        # Tax impact
        "target_bracket": target_bracket,
        "target_rate": target_rate,
        "tax_paid_now": tax_paid_now,
        "tax_if_no_conversion": tax_if_no_conversion,
        "lifetime_tax_savings": lifetime_savings,

        # Additional benefits
        "rmd_reduction_at_73": rmd_reduction,
        "irmaa_savings_estimate": irmaa_savings_estimate,

        # Total benefits
        "total_lifetime_benefit": lifetime_savings + irmaa_savings_estimate,

        # Strategy details
        "start_age": conversion_start_age,
        "end_age": conversion_end_age,
        "filing_status": filing_status,
        "bracket_ceiling": bracket_max
    }


def generate_conversion_timeline(
    current_age: int,
    trad_ira_balance: float,
    annual_conversion: float,
    conversion_start_age: int,
    conversion_end_age: int,
    growth_rate: float = 0.06
) -> list:
    """
    Generate year-by-year conversion timeline.

    Args:
        current_age: User's current age
        trad_ira_balance: Starting traditional IRA balance
        annual_conversion: Amount to convert each year
        conversion_start_age: When to start
        conversion_end_age: When to stop
        growth_rate: Investment growth rate (default: 6%)

    Returns:
        List of dicts with yearly breakdown
    """
    timeline = []
    trad_balance = trad_ira_balance
    roth_balance = 0

    for age in range(current_age, 100):
        year_data = {
            "age": age,
            "year": 2025 + (age - current_age),
            "trad_balance_start": trad_balance,
            "conversion_amount": 0,
            "trad_balance_end": trad_balance,
            "roth_balance": roth_balance
        }

        # During conversion window
        if conversion_start_age <= age < conversion_end_age and trad_balance > 0:
            # Convert up to annual amount (or remaining balance)
            conversion = min(annual_conversion, trad_balance)
            year_data["conversion_amount"] = conversion

            # Update balances
            trad_balance -= conversion
            roth_balance += conversion

        # Apply growth to both accounts
        trad_balance *= (1 + growth_rate)
        roth_balance *= (1 + growth_rate)

        year_data["trad_balance_end"] = trad_balance
        year_data["roth_balance"] = roth_balance

        timeline.append(year_data)

        # Stop after conversion window plus a few years
        if age > conversion_end_age + 5:
            break

    return timeline


def get_bracket_recommendations(current_income: float, filing_status: str = "married") -> list:
    """
    Get recommendations for which bracket to target.

    Args:
        current_income: Current taxable income
        filing_status: "single" or "married"

    Returns:
        List of recommendations with pros/cons
    """
    brackets = TAX_BRACKETS_MFJ_2025 if filing_status == "married" else TAX_BRACKETS_SINGLE_2025

    recommendations = []

    # Check each bracket
    for bracket_name, bracket_info in brackets.items():
        headroom = bracket_info["max"] - current_income

        if headroom > 0 and bracket_name in ["12%", "22%", "24%"]:
            rec = {
                "bracket": bracket_name,
                "headroom": headroom,
                "rate": bracket_info["rate"],
                "max_income": bracket_info["max"]
            }

            # Add recommendation text
            if bracket_name == "12%":
                rec["recommendation"] = "Conservative: Lower tax rate but limited headroom"
                rec["best_for"] = "Lower income retirees, maximize tax-free growth"
            elif bracket_name == "22%":
                rec["recommendation"] = "Balanced: Most popular choice for pre-retirees"
                rec["best_for"] = "Most people - good balance of tax savings and conversion amounts"
            elif bracket_name == "24%":
                rec["recommendation"] = "Aggressive: Higher upfront taxes but more conversion"
                rec["best_for"] = "High net worth, expecting much higher future taxes"

            recommendations.append(rec)

    return recommendations
