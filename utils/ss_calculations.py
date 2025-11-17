"""
Social Security Benefits Calculator
=====================================
Core calculation engine for SS benefit optimization.

Based on SSA rules as of 2025:
- Full Retirement Age (FRA): 67 for those born 1960+
- Early claiming: As early as 62 (reduced benefits)
- Delayed credits: Up to age 70 (increased benefits)
- Spousal benefits: Up to 50% of primary earner's FRA benefit
"""

from datetime import date
from typing import Dict, Tuple, Optional


# =============================================================================
# CONSTANTS (2025 SSA RULES)
# =============================================================================

# Full Retirement Age by birth year
FRA_BY_BIRTH_YEAR = {
    range(1943, 1955): 66.0,
    range(1955, 1956): 66.167,  # 66 + 2 months
    range(1956, 1957): 66.333,  # 66 + 4 months
    range(1957, 1958): 66.5,    # 66 + 6 months
    range(1958, 1959): 66.667,  # 66 + 8 months
    range(1959, 1960): 66.833,  # 66 + 10 months
    range(1960, 2100): 67.0,    # 67 for 1960+
}

# Reduction/increase factors
EARLY_REDUCTION_FIRST_36_MONTHS = 5/9 / 100  # 0.555% per month
EARLY_REDUCTION_AFTER_36_MONTHS = 5/12 / 100  # 0.417% per month
DELAYED_CREDIT_PER_YEAR = 0.08  # 8% per year (0.667% per month)

# Benefit limits
MIN_CLAIMING_AGE = 62
MAX_CLAIMING_AGE = 70
SPOUSAL_BENEFIT_PCT = 0.50  # 50% of spouse's FRA benefit


# =============================================================================
# CORE CALCULATION FUNCTIONS
# =============================================================================

def get_fra(birth_year: int) -> float:
    """
    Get Full Retirement Age based on birth year.

    Args:
        birth_year: Year of birth

    Returns:
        FRA in years (e.g., 67.0)
    """
    for year_range, fra in FRA_BY_BIRTH_YEAR.items():
        if birth_year in year_range:
            return fra
    # Default for anyone born before 1943
    if birth_year < 1943:
        return 65.0
    # Default for future births
    return 67.0


def calculate_benefit_at_age(
    pia: float,
    claiming_age: float,
    birth_year: int
) -> float:
    """
    Calculate monthly SS benefit based on claiming age.

    Args:
        pia: Primary Insurance Amount (benefit at FRA)
        claiming_age: Age at which to claim benefits (62-70)
        birth_year: Year of birth

    Returns:
        Monthly benefit amount
    """
    fra = get_fra(birth_year)

    if claiming_age < MIN_CLAIMING_AGE:
        claiming_age = MIN_CLAIMING_AGE
    if claiming_age > MAX_CLAIMING_AGE:
        claiming_age = MAX_CLAIMING_AGE

    # Calculate months difference from FRA
    months_diff = int((claiming_age - fra) * 12)

    if months_diff == 0:
        # Claiming at FRA
        return pia
    elif months_diff < 0:
        # Early claiming (reduction)
        months_early = abs(months_diff)

        # First 36 months: reduce by 5/9 of 1% per month
        first_36_reduction = min(months_early, 36) * EARLY_REDUCTION_FIRST_36_MONTHS * pia

        # Months beyond 36: reduce by 5/12 of 1% per month
        if months_early > 36:
            additional_reduction = (months_early - 36) * EARLY_REDUCTION_AFTER_36_MONTHS * pia
        else:
            additional_reduction = 0

        total_reduction = first_36_reduction + additional_reduction
        return pia - total_reduction
    else:
        # Delayed claiming (increase)
        years_delayed = months_diff / 12
        increase_pct = years_delayed * DELAYED_CREDIT_PER_YEAR
        return pia * (1 + increase_pct)


def calculate_lifetime_benefits(
    monthly_benefit: float,
    claiming_age: float,
    life_expectancy: int,
    inflation_rate: float = 0.02,  # COLA adjustment
    discount_rate: float = 0.03   # Present value discount
) -> Dict[str, float]:
    """
    Calculate total lifetime benefits with present value.

    Args:
        monthly_benefit: Monthly SS benefit
        claiming_age: Age when benefits start
        life_expectancy: Expected age at death
        inflation_rate: Annual COLA (cost of living adjustment)
        discount_rate: Discount rate for present value calculation

    Returns:
        Dict with nominal and present value totals
    """
    total_nominal = 0.0
    total_present_value = 0.0

    years_receiving = life_expectancy - claiming_age

    if years_receiving <= 0:
        return {
            'nominal_total': 0,
            'present_value': 0,
            'years_receiving': 0,
            'annual_at_start': monthly_benefit * 12,
            'annual_at_end': 0
        }

    annual_benefit = monthly_benefit * 12
    annual_at_end = annual_benefit

    for year in range(int(years_receiving)):
        # Apply COLA increase
        if year > 0:
            annual_benefit *= (1 + inflation_rate)

        total_nominal += annual_benefit

        # Present value calculation
        pv_factor = 1 / ((1 + discount_rate) ** year)
        total_present_value += annual_benefit * pv_factor

        annual_at_end = annual_benefit

    return {
        'nominal_total': total_nominal,
        'present_value': total_present_value,
        'years_receiving': years_receiving,
        'annual_at_start': monthly_benefit * 12,
        'annual_at_end': annual_at_end
    }


def calculate_break_even_age(
    pia: float,
    birth_year: int,
    early_age: float = 62,
    delayed_age: float = 70,
    inflation_rate: float = 0.02
) -> float:
    """
    Calculate break-even age between two claiming strategies.

    Args:
        pia: Primary Insurance Amount
        birth_year: Year of birth
        early_age: Earlier claiming age
        delayed_age: Later claiming age
        inflation_rate: Annual COLA

    Returns:
        Age at which cumulative benefits are equal
    """
    early_benefit = calculate_benefit_at_age(pia, early_age, birth_year)
    delayed_benefit = calculate_benefit_at_age(pia, delayed_age, birth_year)

    # Calculate cumulative benefits year by year
    early_cumulative = 0.0
    delayed_cumulative = 0.0

    early_annual = early_benefit * 12
    delayed_annual = delayed_benefit * 12

    # Start from age of delayed claiming
    for age in range(int(delayed_age), 100):
        # Early strategy
        years_early = age - early_age
        if years_early > 0:
            # Apply COLA
            early_this_year = early_annual * ((1 + inflation_rate) ** (years_early - 1))
            early_cumulative += early_this_year

        # Delayed strategy (only starts at delayed_age)
        years_delayed = age - delayed_age
        if years_delayed > 0:
            delayed_this_year = delayed_annual * ((1 + inflation_rate) ** (years_delayed - 1))
            delayed_cumulative += delayed_this_year

        # Check for break-even
        if delayed_cumulative >= early_cumulative:
            return float(age)

    # No break-even found within 100 years
    return 100.0


def calculate_spousal_benefit(
    primary_pia: float,
    spouse_claiming_age: float,
    spouse_birth_year: int,
    spouse_own_pia: float = 0
) -> float:
    """
    Calculate spousal SS benefit.

    Spouse gets the HIGHER of:
    - Their own benefit, OR
    - 50% of primary earner's PIA (reduced if taken early)

    Args:
        primary_pia: Primary earner's PIA
        spouse_claiming_age: Age when spouse claims
        spouse_birth_year: Spouse's birth year
        spouse_own_pia: Spouse's own PIA (if any)

    Returns:
        Monthly spousal benefit
    """
    # Calculate spouse's own benefit
    spouse_own_benefit = calculate_benefit_at_age(
        spouse_own_pia, spouse_claiming_age, spouse_birth_year
    ) if spouse_own_pia > 0 else 0

    # Calculate spousal benefit (50% of primary's FRA amount)
    spousal_amount = primary_pia * SPOUSAL_BENEFIT_PCT

    # Apply early claiming reduction to spousal benefit
    fra = get_fra(spouse_birth_year)
    if spouse_claiming_age < fra:
        months_early = int((fra - spouse_claiming_age) * 12)
        # Spousal benefits reduce differently: 25/36 of 1% for first 36 months
        first_36_reduction = min(months_early, 36) * (25/36/100) * spousal_amount
        if months_early > 36:
            additional_reduction = (months_early - 36) * (5/12/100) * spousal_amount
        else:
            additional_reduction = 0
        spousal_amount -= (first_36_reduction + additional_reduction)

    # Return the higher of own benefit or spousal benefit
    return max(spouse_own_benefit, spousal_amount)


def optimize_claiming_strategy(
    user_pia: float,
    user_birth_year: int,
    user_life_expectancy: int,
    partner_pia: float = 0,
    partner_birth_year: int = None,
    partner_life_expectancy: int = None
) -> Dict:
    """
    Find optimal claiming strategy for individual or couple.

    Returns the claiming age(s) that maximize lifetime benefits.

    Args:
        user_pia: User's Primary Insurance Amount
        user_birth_year: User's birth year
        user_life_expectancy: User's expected lifespan
        partner_pia: Partner's PIA (optional)
        partner_birth_year: Partner's birth year (optional)
        partner_life_expectancy: Partner's expected lifespan (optional)

    Returns:
        Dict with optimal strategy and comparison data
    """
    # Test all claiming ages for user
    strategies = []

    for claiming_age in range(62, 71):
        monthly = calculate_benefit_at_age(user_pia, claiming_age, user_birth_year)
        lifetime = calculate_lifetime_benefits(monthly, claiming_age, user_life_expectancy)

        strategies.append({
            'claiming_age': claiming_age,
            'monthly_benefit': monthly,
            'annual_benefit': monthly * 12,
            'lifetime_nominal': lifetime['nominal_total'],
            'lifetime_pv': lifetime['present_value'],
            'years_receiving': lifetime['years_receiving']
        })

    # Find optimal (max present value)
    optimal = max(strategies, key=lambda x: x['lifetime_pv'])

    # Calculate comparison to FRA
    fra = get_fra(user_birth_year)
    fra_benefit = calculate_benefit_at_age(user_pia, fra, user_birth_year)

    # Partner optimization if applicable
    partner_optimal = None
    if partner_pia and partner_birth_year and partner_life_expectancy:
        partner_strategies = []
        for claiming_age in range(62, 71):
            monthly = calculate_benefit_at_age(partner_pia, claiming_age, partner_birth_year)
            lifetime = calculate_lifetime_benefits(monthly, claiming_age, partner_life_expectancy)
            partner_strategies.append({
                'claiming_age': claiming_age,
                'monthly_benefit': monthly,
                'annual_benefit': monthly * 12,
                'lifetime_nominal': lifetime['nominal_total'],
                'lifetime_pv': lifetime['present_value'],
                'years_receiving': lifetime['years_receiving']
            })
        partner_optimal = max(partner_strategies, key=lambda x: x['lifetime_pv'])

    return {
        'optimal_strategy': optimal,
        'all_strategies': strategies,
        'fra': fra,
        'fra_benefit': fra_benefit,
        'partner_optimal': partner_optimal
    }


def estimate_pia_from_income(annual_income: float, years_worked: int = 35) -> float:
    """
    Rough estimate of PIA from annual income.

    This is a SIMPLIFIED estimation. Actual PIA calculation is complex
    and based on AIME (Average Indexed Monthly Earnings).

    Args:
        annual_income: Current annual income
        years_worked: Years of work history

    Returns:
        Estimated monthly PIA
    """
    # Simplified bend points (2024 values, adjusted annually)
    # Actual formula:
    # - 90% of first $1,174 of AIME
    # - 32% of AIME between $1,174 and $7,078
    # - 15% of AIME above $7,078

    monthly_income = annual_income / 12

    # Rough AIME calculation (simplified)
    aime = monthly_income * 0.9  # Account for lower earning years

    # Apply bend points
    if aime <= 1174:
        pia = aime * 0.90
    elif aime <= 7078:
        pia = (1174 * 0.90) + ((aime - 1174) * 0.32)
    else:
        pia = (1174 * 0.90) + ((7078 - 1174) * 0.32) + ((aime - 7078) * 0.15)

    # Apply work history factor (35 years is full credit)
    work_factor = min(years_worked / 35, 1.0)

    return pia * work_factor


def generate_claiming_comparison_table(
    pia: float,
    birth_year: int,
    life_expectancy: int = 85
) -> list:
    """
    Generate comparison table for all claiming ages.

    Args:
        pia: Primary Insurance Amount
        birth_year: Year of birth
        life_expectancy: Expected age at death

    Returns:
        List of dicts with comparison data for each age
    """
    fra = get_fra(birth_year)
    fra_benefit = calculate_benefit_at_age(pia, fra, birth_year) * 12

    table = []

    for age in range(62, 71):
        monthly = calculate_benefit_at_age(pia, age, birth_year)
        annual = monthly * 12
        lifetime = calculate_lifetime_benefits(monthly, age, life_expectancy)

        # Calculate % of FRA benefit
        pct_of_fra = (annual / fra_benefit * 100) if fra_benefit > 0 else 0

        # Calculate break-even vs age 62
        if age > 62:
            break_even = calculate_break_even_age(pia, birth_year, 62, age)
        else:
            break_even = None

        table.append({
            'claiming_age': age,
            'monthly_benefit': monthly,
            'annual_benefit': annual,
            'pct_of_fra': pct_of_fra,
            'lifetime_total': lifetime['nominal_total'],
            'lifetime_pv': lifetime['present_value'],
            'break_even_vs_62': break_even,
            'years_receiving': lifetime['years_receiving']
        })

    return table
