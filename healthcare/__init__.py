"""
Family Forecast Healthcare Cost Projector
==================================

Medicare premium calculation and healthcare cost projection tools.

Modules:
- healthcare_disclaimers: Legal disclaimers and acknowledgment system
- medicare_data: Historical Medicare data and state-specific premiums
- medicare_irmaa_calculator: IRMAA calculation engine for Medicare premiums
- medicare_calculator_ui: Streamlit UI for Medicare IRMAA calculator
- medicare_charts: Plotly visualization library for Medicare costs
- healthcare_main: Main navigation hub for healthcare planning tools

Author: Family Forecast Development Team
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
    PART_A_COST_SHARING_2026,
    PART_B_COST_SHARING_2026,
    PART_D_COST_STRUCTURE_2026,
    MEDICARE_SAVINGS_PROGRAMS_2026,
    EXTRA_HELP_2026,
    MEDICARE_INFLATION_RATES,
    MedigapPremiums,
    get_part_d_premium_for_state,
    get_medigap_premiums_for_state,
    calculate_medigap_premium_by_age,
    project_part_b_premium,
    get_medicare_cost_summary,
    # Data freshness functions
    DATA_VERSION,
    DATA_YEAR,
    get_data_version_info,
    check_data_freshness,
    get_data_update_instructions
)

from .medicare_irmaa_calculator import (
    IRMAABracket,
    MedicarePremiun,
    MedicareIRMAACalculator,
    calculate_medicare_cost
)

# UI Components (optional imports - require streamlit/plotly)
try:
    from .medicare_calculator_ui import show_calculator_page
    from .medicare_charts import (
        create_irmaa_waterfall_chart,
        create_irmaa_bracket_heatmap,
        create_bracket_threshold_chart,
        create_stacked_area_projection,
        create_cumulative_cost_chart,
        create_roth_conversion_multi_scenario_chart,
        create_conversion_breakeven_chart,
        create_medicare_cost_gauge,
        create_cost_breakdown_pie
    )
    from .healthcare_main import main as healthcare_main
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False

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
    "PART_A_COST_SHARING_2026",
    "PART_B_COST_SHARING_2026",
    "PART_D_COST_STRUCTURE_2026",
    "MEDICARE_SAVINGS_PROGRAMS_2026",
    "EXTRA_HELP_2026",
    "MEDICARE_INFLATION_RATES",
    "MedigapPremiums",
    "get_part_d_premium_for_state",
    "get_medigap_premiums_for_state",
    "calculate_medigap_premium_by_age",
    "project_part_b_premium",
    "get_medicare_cost_summary",
    # Data Freshness
    "DATA_VERSION",
    "DATA_YEAR",
    "get_data_version_info",
    "check_data_freshness",
    "get_data_update_instructions",
    # Calculator
    "IRMAABracket",
    "MedicarePremiun",
    "MedicareIRMAACalculator",
    "calculate_medicare_cost",
    # UI Components (if available)
    "UI_AVAILABLE",
]

# Conditionally add UI exports if available
if UI_AVAILABLE:
    __all__.extend([
        "show_calculator_page",
        "create_irmaa_waterfall_chart",
        "create_irmaa_bracket_heatmap",
        "create_bracket_threshold_chart",
        "create_stacked_area_projection",
        "create_cumulative_cost_chart",
        "create_roth_conversion_multi_scenario_chart",
        "create_conversion_breakeven_chart",
        "create_medicare_cost_gauge",
        "create_cost_breakdown_pie",
        "healthcare_main",
    ])
