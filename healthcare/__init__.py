"""
ForeCash Healthcare Cost Projector
==================================

Medicare premium calculation and healthcare cost projection tools.

Modules:
- healthcare_disclaimers: Legal disclaimers and acknowledgment system
- medicare_data: Historical Medicare data and state-specific premiums
- medicare_irmaa_calculator: IRMAA calculation engine for Medicare premiums

Author: ForeCash Development Team
Last Updated: October 22, 2025
"""

from .healthcare_disclaimers import (
    PRIMARY_HEALTHCARE_DISCLAIMER,
    show_primary_healthcare_disclaimer,
    show_medicare_irmaa_disclaimer,
    show_medigap_advantage_disclaimer,
    show_long_term_care_disclaimer,
    show_data_source_disclaimer,
    show_roth_conversion_disclaimer,
    require_healthcare_disclaimer_acknowledgment
)

from .medicare_data import (
    HISTORICAL_PART_B_PREMIUMS,
    HISTORICAL_PART_D_BASE_PREMIUMS,
    IRMAA_BRACKETS_HISTORY,
    STATE_PART_D_PREMIUMS,
    STATE_MEDIGAP_PREMIUMS,
    MEDICARE_ADVANTAGE_DATA,
    PART_A_COST_SHARING_2025,
    PART_B_COST_SHARING_2025,
    PART_D_COST_STRUCTURE_2025,
    MEDICARE_SAVINGS_PROGRAMS_2025,
    EXTRA_HELP_2025,
    MEDICARE_INFLATION_RATES,
    MedigapPremiums,
    get_part_d_premium_for_state,
    get_medigap_premiums_for_state,
    calculate_medigap_premium_by_age,
    project_part_b_premium,
    get_medicare_cost_summary
)

from .medicare_irmaa_calculator import (
    IRMAABracket,
    MedicarePremiun,
    MedicareIRMAACalculator,
    calculate_medicare_cost
)

__version__ = "1.0.0"
__all__ = [
    # Disclaimers
    "PRIMARY_HEALTHCARE_DISCLAIMER",
    "show_primary_healthcare_disclaimer",
    "show_medicare_irmaa_disclaimer",
    "show_medigap_advantage_disclaimer",
    "show_long_term_care_disclaimer",
    "show_data_source_disclaimer",
    "show_roth_conversion_disclaimer",
    "require_healthcare_disclaimer_acknowledgment",
    # Data
    "HISTORICAL_PART_B_PREMIUMS",
    "HISTORICAL_PART_D_BASE_PREMIUMS",
    "IRMAA_BRACKETS_HISTORY",
    "STATE_PART_D_PREMIUMS",
    "STATE_MEDIGAP_PREMIUMS",
    "MEDICARE_ADVANTAGE_DATA",
    "PART_A_COST_SHARING_2025",
    "PART_B_COST_SHARING_2025",
    "PART_D_COST_STRUCTURE_2025",
    "MEDICARE_SAVINGS_PROGRAMS_2025",
    "EXTRA_HELP_2025",
    "MEDICARE_INFLATION_RATES",
    "MedigapPremiums",
    "get_part_d_premium_for_state",
    "get_medigap_premiums_for_state",
    "calculate_medigap_premium_by_age",
    "project_part_b_premium",
    "get_medicare_cost_summary",
    # Calculator
    "IRMAABracket",
    "MedicarePremiun",
    "MedicareIRMAACalculator",
    "calculate_medicare_cost",
]
