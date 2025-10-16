# intake_validation.py - Intelligent validation for retirement intake data
"""
Smart validation module with context-aware warnings and helpful suggestions.
Helps users avoid common data entry mistakes.
"""

import streamlit as st
from typing import Dict, List, Tuple, Optional

# ============================================================================
# VALIDATION RULES & RANGES
# ============================================================================

class ValidationRules:
    """Defines reasonable ranges and validation logic for retirement planning"""

    # Age-related rules
    AGE_MIN = 18
    AGE_MAX = 100
    AGE_EARLY_RETIREMENT = 62
    AGE_FULL_RETIREMENT = 67
    AGE_VERY_SENIOR = 85

    # Income rules (monthly)
    INCOME_VERY_LOW = 500
    INCOME_LOW = 1500
    INCOME_MEDIAN = 4500
    INCOME_HIGH = 15000
    INCOME_VERY_HIGH = 50000

    # Social Security rules (monthly, 2024)
    SS_MIN_BENEFIT = 800
    SS_AVERAGE_BENEFIT = 1900
    SS_MAX_BENEFIT = 4900

    # Expense rules (monthly)
    EXPENSE_VERY_LOW = 500
    EXPENSE_LOW = 1500
    EXPENSE_MEDIAN = 4000
    EXPENSE_HIGH = 10000
    EXPENSE_VERY_HIGH = 50000

    # Housing rules (% of income)
    HOUSING_RATIO_WARNING = 0.35  # 35% of income
    HOUSING_RATIO_DANGER = 0.50   # 50% of income

    # Assets rules
    ASSETS_LIQUID_MIN_MONTHS = 3  # 3 months of expenses
    ASSETS_LIQUID_GOOD_MONTHS = 6  # 6 months emergency fund

    # Liabilities rules (debt-to-income)
    DTI_WARNING = 0.40  # 40% debt-to-income
    DTI_DANGER = 0.50   # 50% debt-to-income


# ============================================================================
# PROFILE VALIDATION
# ============================================================================

def validate_age(age: int, is_partner: bool = False) -> Tuple[str, str]:
    """
    Validates age and returns (level, message)
    Levels: 'success', 'info', 'warning', 'error'
    """
    label = "Partner" if is_partner else "Your"

    if age < ValidationRules.AGE_MIN:
        return ('error', f"❌ {label} age must be at least {ValidationRules.AGE_MIN}")

    if age > ValidationRules.AGE_MAX:
        return ('warning', f"⚠️ {label} age over {ValidationRules.AGE_MAX} is very unusual. Please confirm.")

    if age > 95:
        return ('warning', f"⚠️ {label} age over 95 detected. Planning for extreme longevity?")

    if age < ValidationRules.AGE_EARLY_RETIREMENT:
        return ('info', f"ℹ️ {label} age {age} - Early retirement planning. Social Security won't be available until 62.")

    if age >= ValidationRules.AGE_EARLY_RETIREMENT and age < ValidationRules.AGE_FULL_RETIREMENT:
        return ('info', f"ℹ️ Age {age} - You can claim Social Security now, but waiting until {ValidationRules.AGE_FULL_RETIREMENT} increases benefits.")

    if age >= ValidationRules.AGE_FULL_RETIREMENT:
        return ('success', f"✅ Full retirement age reached. Social Security benefits maximized at 70.")

    return ('success', '')


def validate_age_gap(age1: int, age2: int) -> Tuple[str, str]:
    """Validates age gap between partners"""
    gap = abs(age1 - age2)

    if gap > 30:
        return ('warning', f"⚠️ Large age gap ({gap} years) detected. This may impact survivor benefit planning.")

    if gap > 20:
        return ('info', f"ℹ️ Significant age gap ({gap} years). Consider longevity planning for younger spouse.")

    return ('success', '')


# ============================================================================
# INCOME VALIDATION
# ============================================================================

def validate_total_income(total: float, age: int) -> Tuple[str, str]:
    """Validates total monthly income with age context"""

    if total < ValidationRules.INCOME_VERY_LOW:
        return ('warning', f"⚠️ Total income ${total:,.0f}/month seems very low. Please verify all income sources are included.")

    if total < ValidationRules.INCOME_LOW and age >= ValidationRules.AGE_FULL_RETIREMENT:
        return ('warning', f"⚠️ Low income for retirement age. Have you included Social Security and pension benefits?")

    if total > ValidationRules.INCOME_VERY_HIGH:
        return ('info', f"ℹ️ High income detected (${total:,.0f}/month). Confirm amounts are MONTHLY not ANNUAL.")

    if total >= ValidationRules.INCOME_MEDIAN:
        return ('success', f"✅ Income ${total:,.0f}/month - Good financial foundation")

    return ('success', '')


def validate_social_security(ss_amount: float, age: int) -> Tuple[str, str]:
    """Validates Social Security benefit amount"""

    if ss_amount == 0 and age >= ValidationRules.AGE_EARLY_RETIREMENT:
        return ('info', f"ℹ️ No Social Security entered. If you're eligible, benefits range ${ValidationRules.SS_MIN_BENEFIT}-${ValidationRules.SS_MAX_BENEFIT}/month.")

    if ss_amount > 0 and age < ValidationRules.AGE_EARLY_RETIREMENT:
        return ('warning', f"⚠️ Social Security entered but you're under 62. You won't be eligible for {ValidationRules.AGE_EARLY_RETIREMENT - age} more years.")

    if ss_amount > ValidationRules.SS_MAX_BENEFIT:
        return ('warning', f"⚠️ Social Security ${ss_amount:,.0f} exceeds 2024 maximum (${ValidationRules.SS_MAX_BENEFIT}). Please verify.")

    if ss_amount > 0 and ss_amount < ValidationRules.SS_MIN_BENEFIT:
        return ('warning', f"⚠️ Social Security ${ss_amount:,.0f} is below typical minimum (${ValidationRules.SS_MIN_BENEFIT}). Please verify.")

    if ss_amount >= ValidationRules.SS_AVERAGE_BENEFIT:
        return ('success', f"✅ Social Security ${ss_amount:,.0f}/month - At or above average benefit")

    return ('success', '')


def validate_income_mix(salary: float, pension: float, ss: float, total: float, age: int) -> Tuple[str, str]:
    """Validates income source mix makes sense for age"""

    work_income = salary
    retirement_income = pension + ss

    if age >= 70 and work_income > retirement_income:
        return ('info', f"ℹ️ Age {age} with significant work income. Are you still working? Consider delaying Social Security for higher benefits.")

    if age >= ValidationRules.AGE_FULL_RETIREMENT and retirement_income == 0:
        return ('warning', f"⚠️ Age {age} with no pension or Social Security. Have you applied for retirement benefits?")

    return ('success', '')


# ============================================================================
# EXPENSE VALIDATION
# ============================================================================

def validate_total_expenses(total: float) -> Tuple[str, str]:
    """Validates total monthly expenses"""

    if total < ValidationRules.EXPENSE_VERY_LOW:
        return ('warning', f"⚠️ Total expenses ${total:,.0f}/month seems very low. Please verify all expenses are included.")

    if total > ValidationRules.EXPENSE_VERY_HIGH:
        return ('info', f"ℹ️ High expenses detected (${total:,.0f}/month). Confirm amounts are MONTHLY not ANNUAL.")

    if total >= ValidationRules.EXPENSE_MEDIAN and total <= ValidationRules.EXPENSE_HIGH:
        return ('success', f"✅ Expenses ${total:,.0f}/month - Typical range for retirees")

    return ('success', '')


def validate_housing_ratio(housing: float, total_income: float) -> Tuple[str, str]:
    """Validates housing costs as percentage of income"""

    if total_income == 0:
        return ('success', '')

    ratio = housing / total_income

    if ratio > ValidationRules.HOUSING_RATIO_DANGER:
        return ('error', f"🚨 Housing is {ratio*100:.0f}% of income! Recommended: under 35%. This may cause financial stress.")

    if ratio > ValidationRules.HOUSING_RATIO_WARNING:
        return ('warning', f"⚠️ Housing is {ratio*100:.0f}% of income. Recommended: under 35%. Consider ways to reduce housing costs.")

    if ratio <= 0.25:
        return ('success', f"✅ Housing is only {ratio*100:.0f}% of income - Excellent!")

    return ('success', f"✅ Housing is {ratio*100:.0f}% of income - Good")


def validate_income_vs_expenses(income: float, expenses: float) -> Tuple[str, str]:
    """Validates income covers expenses with surplus"""

    surplus = income - expenses

    if surplus < 0:
        return ('error', f"🚨 Monthly deficit: ${abs(surplus):,.0f}. Expenses exceed income! You're drawing down savings.")

    if surplus < 500:
        return ('warning', f"⚠️ Small surplus: ${surplus:,.0f}/month. Very tight budget - consider increasing income or reducing expenses.")

    if surplus >= 500 and surplus < 2000:
        return ('info', f"ℹ️ Surplus: ${surplus:,.0f}/month. Good cushion for unexpected expenses.")

    if surplus >= 2000:
        return ('success', f"✅ Surplus: ${surplus:,.0f}/month. Excellent savings potential!")

    return ('success', '')


# ============================================================================
# ASSET VALIDATION
# ============================================================================

def validate_liquid_assets(liquid: float, monthly_expenses: float) -> Tuple[str, str]:
    """Validates liquid assets against monthly expenses (emergency fund)"""

    if monthly_expenses == 0:
        return ('success', '')

    months_covered = liquid / monthly_expenses

    if months_covered < ValidationRules.ASSETS_LIQUID_MIN_MONTHS:
        return ('error', f"🚨 Liquid assets only cover {months_covered:.1f} months of expenses. Recommended: at least 3-6 months.")

    if months_covered < ValidationRules.ASSETS_LIQUID_GOOD_MONTHS:
        return ('warning', f"⚠️ Liquid assets cover {months_covered:.1f} months of expenses. Aim for 6+ months emergency fund.")

    if months_covered >= 12:
        return ('success', f"✅ Liquid assets cover {months_covered:.1f} months of expenses - Excellent emergency fund!")

    return ('success', f"✅ Liquid assets cover {months_covered:.1f} months - Good safety net")


def validate_retirement_accounts(ira: float, k401: float, age: int) -> Tuple[str, str]:
    """Validates retirement account balances"""

    total_retirement = ira + k401

    if age >= 65 and total_retirement < 100000:
        return ('warning', f"⚠️ Retirement accounts total ${total_retirement:,.0f}. This may not be sufficient for retirement.")

    if total_retirement > 1000000:
        return ('success', f"✅ Retirement accounts: ${total_retirement:,.0f} - Strong retirement savings!")

    if total_retirement > 500000:
        return ('success', f"✅ Retirement accounts: ${total_retirement:,.0f} - Good retirement foundation")

    return ('success', '')


# ============================================================================
# LIABILITY VALIDATION
# ============================================================================

def validate_debt_to_income(total_liabilities: float, monthly_income: float) -> Tuple[str, str]:
    """Validates debt-to-income ratio"""

    if monthly_income == 0:
        return ('success', '')

    # Estimate monthly debt payment (rough: 3% of total liability per month)
    estimated_monthly_debt = total_liabilities * 0.03
    dti = estimated_monthly_debt / monthly_income

    if dti > ValidationRules.DTI_DANGER:
        return ('error', f"🚨 Debt payments ~{dti*100:.0f}% of income. This is very high and may cause financial stress.")

    if dti > ValidationRules.DTI_WARNING:
        return ('warning', f"⚠️ Debt payments ~{dti*100:.0f}% of income. Recommended: under 40%. Consider debt reduction strategies.")

    if dti < 0.20:
        return ('success', f"✅ Low debt burden (~{dti*100:.0f}% of income) - Excellent!")

    return ('success', f"✅ Manageable debt load (~{dti*100:.0f}% of income)")


def validate_mortgage_in_retirement(mortgage: float, age: int) -> Tuple[str, str]:
    """Validates carrying mortgage into retirement"""

    if mortgage > 0 and age >= 70:
        return ('info', f"ℹ️ Mortgage balance ${mortgage:,.0f} at age {age}. Consider: can you pay this off before retirement for lower expenses?")

    if mortgage > 500000 and age >= 65:
        return ('warning', f"⚠️ Large mortgage (${mortgage:,.0f}) in retirement. This increases required monthly income.")

    return ('success', '')


# ============================================================================
# CROSS-FIELD VALIDATION
# ============================================================================

def validate_complete_picture(data: Dict) -> List[Tuple[str, str]]:
    """
    Validates the complete financial picture with cross-field checks.
    Returns list of (level, message) tuples.
    """
    messages = []

    # Extract key values
    age = data.get('input_age', 65)
    total_income = data.get('input_total_income', 0)
    total_expenses = data.get('input_total_expenses', 0)
    liquid_assets = data.get('input_cash', 0) + data.get('input_savings', 0) + data.get('input_brokerage', 0)
    total_liabilities = data.get('input_mortgage_balance', 0) + data.get('input_credit_card_debt', 0) + data.get('input_other_debt', 0)

    # Net worth check
    total_assets = liquid_assets + data.get('input_ira_balance', 0) + data.get('input_four01k_403b_balance', 0)
    net_worth = total_assets - total_liabilities

    if net_worth < 0:
        messages.append(('warning', f"⚠️ Negative net worth: ${net_worth:,.0f}. You have more debt than assets. Focus on debt reduction."))
    elif net_worth < 100000 and age >= 60:
        messages.append(('warning', f"⚠️ Net worth ${net_worth:,.0f} at age {age} may be low for retirement. Consider savings strategies."))
    elif net_worth > 1000000:
        messages.append(('success', f"✅ Net worth: ${net_worth:,.0f} - Strong financial position!"))

    # Sustainability check
    if total_income > 0 and total_expenses > 0:
        monthly_surplus = total_income - total_expenses
        if monthly_surplus < 0:
            months_until_broke = liquid_assets / abs(monthly_surplus) if monthly_surplus != 0 else 0
            if months_until_broke < 12:
                messages.append(('error', f"🚨 At current deficit rate (${abs(monthly_surplus):,.0f}/month), liquid assets depleted in {months_until_broke:.1f} months!"))
            elif months_until_broke < 36:
                messages.append(('warning', f"⚠️ Monthly deficit ${abs(monthly_surplus):,.0f}. Liquid assets will last ~{months_until_broke:.0f} months. Action needed!"))

    return messages


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def show_validation_message(level: str, message: str):
    """Display validation message with appropriate Streamlit styling"""
    if not message:
        return

    if level == 'error':
        st.error(message)
    elif level == 'warning':
        st.warning(message)
    elif level == 'info':
        st.info(message)
    elif level == 'success':
        st.success(message)


def show_all_validations(validations: List[Tuple[str, str]]):
    """Display all validation messages"""
    for level, message in validations:
        if message:  # Only show non-empty messages
            show_validation_message(level, message)


def convert_annual_to_monthly(annual: float) -> float:
    """Helper to convert annual amounts to monthly"""
    return annual / 12


def convert_monthly_to_annual(monthly: float) -> float:
    """Helper to convert monthly amounts to annual"""
    return monthly * 12
