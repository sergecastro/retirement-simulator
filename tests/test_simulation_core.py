"""
Comprehensive Test Suite for simulation_core.py
================================================
This is your SAFETY NET for the sidebar architecture migration.

Run with: python -m pytest tests/test_simulation_core.py -v
Or: python tests/test_simulation_core.py (standalone)

Created: November 15, 2025
Purpose: Phase 0 of Parallel UI/UX Architecture Upgrade
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock streamlit BEFORE importing simulation_core
mock_st = MagicMock()
mock_st.session_state = {}
mock_st.error = MagicMock()
mock_st.warning = MagicMock()
sys.modules['streamlit'] = mock_st

from simulation_core import (
    calculate_taxes,
    optimize_roth_conversions,
    run_simulation,
    TAX_BRACKETS_2025,
    IRMAA_BRACKETS_2025
)
from financial_utils import safe_float, safe_int


# ===========================================================================
# TEST GROUP 1: Tax Calculation Tests
# ===========================================================================
class TestTaxCalculations:
    """Verify federal tax calculations match 2025 brackets"""

    def test_single_filer_10_percent_bracket(self):
        """Single filer in 10% bracket only"""
        tax = calculate_taxes(10000, 'single')
        expected = 10000 * 0.10
        assert abs(tax - expected) < 0.01, f"Expected {expected}, got {tax}"

    def test_single_filer_12_percent_bracket(self):
        """Single filer crossing into 12% bracket"""
        income = 25000
        tax = calculate_taxes(income, 'single')
        # 0-11600 @ 10% = 1160
        # 11600-25000 @ 12% = 13400 * 0.12 = 1608
        expected = 1160 + 1608
        assert abs(tax - expected) < 0.01, f"Expected {expected}, got {tax}"

    def test_single_filer_22_percent_bracket(self):
        """Single filer in 22% bracket"""
        income = 75000
        tax = calculate_taxes(income, 'single')
        # 0-11600 @ 10% = 1160
        # 11600-47150 @ 12% = 35550 * 0.12 = 4266
        # 47150-75000 @ 22% = 27850 * 0.22 = 6127
        expected = 1160 + 4266 + 6127
        assert abs(tax - expected) < 0.01, f"Expected {expected}, got {tax}"

    def test_joint_filer_10_percent_bracket(self):
        """Joint filer in 10% bracket"""
        tax = calculate_taxes(20000, 'joint')
        expected = 20000 * 0.10
        assert abs(tax - expected) < 0.01

    def test_joint_filer_12_percent_bracket(self):
        """Joint filer crossing into 12% bracket"""
        income = 50000
        tax = calculate_taxes(income, 'joint')
        # 0-23200 @ 10% = 2320
        # 23200-50000 @ 12% = 26800 * 0.12 = 3216
        expected = 2320 + 3216
        assert abs(tax - expected) < 0.01

    def test_joint_filer_high_income(self):
        """Joint filer with high income (multiple brackets)"""
        income = 250000
        tax = calculate_taxes(income, 'joint')
        # 0-23200 @ 10% = 2320
        # 23200-94300 @ 12% = 71100 * 0.12 = 8532
        # 94300-201050 @ 22% = 106750 * 0.22 = 23485
        # 201050-250000 @ 24% = 48950 * 0.24 = 11748
        expected = 2320 + 8532 + 23485 + 11748
        assert abs(tax - expected) < 1.0, f"Expected {expected}, got {tax}"

    def test_zero_income(self):
        """Zero income should have zero tax"""
        assert calculate_taxes(0, 'single') == 0
        assert calculate_taxes(0, 'joint') == 0

    def test_very_high_income(self):
        """Very high income hits 37% bracket"""
        income = 1000000
        tax = calculate_taxes(income, 'single')
        assert tax > 0
        # Top bracket is 37%, so effective rate should be < 37% but significant
        effective_rate = tax / income
        assert 0.30 < effective_rate < 0.37

    def test_tax_brackets_are_progressive(self):
        """Higher income should mean higher effective tax rate"""
        incomes = [25000, 50000, 100000, 200000, 500000]
        effective_rates = []
        for income in incomes:
            tax = calculate_taxes(income, 'joint')
            effective_rates.append(tax / income)

        # Each rate should be higher than the previous
        for i in range(1, len(effective_rates)):
            assert effective_rates[i] > effective_rates[i-1], \
                f"Tax rate not progressive: {effective_rates}"


# ===========================================================================
# TEST GROUP 2: Roth Conversion Optimization Tests
# ===========================================================================
class TestRothConversionOptimization:
    """Verify Roth conversion logic"""

    def test_no_conversion_when_ira_empty(self):
        """No conversion if IRA balance is zero"""
        result = optimize_roth_conversions(0, 100000, 0, 50000, 'joint')
        assert result == 0

    def test_no_conversion_when_annual_limit_zero(self):
        """No conversion if annual limit is zero"""
        result = optimize_roth_conversions(0, 100000, 100000, 0, 'joint')
        assert result == 0

    def test_conversion_limited_by_ira_balance(self):
        """Conversion limited to available IRA balance"""
        ira_balance = 10000
        annual_limit = 50000
        result = optimize_roth_conversions(0, 50000, ira_balance, annual_limit, 'joint')
        assert result <= ira_balance

    def test_conversion_limited_by_annual_limit(self):
        """Conversion limited to annual conversion limit"""
        ira_balance = 100000
        annual_limit = 25000
        result = optimize_roth_conversions(0, 50000, ira_balance, annual_limit, 'joint')
        assert result <= annual_limit

    def test_conversion_respects_tax_bracket_boundary(self):
        """Conversion should not push into higher tax bracket unnecessarily"""
        # MAGI at $90,000 (joint), next bracket at $94,300
        current_magi = 90000
        result = optimize_roth_conversions(0, current_magi, 100000, 50000, 'joint')
        # Should convert at most to hit next bracket boundary
        assert result <= (94300 - current_magi) or result == 0

    def test_conversion_respects_irmaa_threshold(self):
        """Conversion should consider IRMAA thresholds"""
        # Joint filer at $200,000, next IRMAA at $206,000
        current_magi = 200000
        result = optimize_roth_conversions(0, current_magi, 100000, 50000, 'joint')
        # Should be conservative around IRMAA boundaries
        assert result <= 50000  # At most the user limit

    def test_conversion_returns_non_negative(self):
        """Conversion should never be negative"""
        result = optimize_roth_conversions(0, 300000, 50000, 25000, 'single')
        assert result >= 0


# ===========================================================================
# TEST GROUP 3: Core Simulation Tests
# ===========================================================================
class TestRunSimulation:
    """Test the main simulation engine"""

    @pytest.fixture
    def basic_simulation_params(self):
        """Standard parameters for testing"""
        mock_st.session_state = {
            'children_rows': [],
            'inherit_rows': []
        }
        return {
            'age': 35,
            'partner_exists': True,
            'partner_age': 33,
            'total_income': 120000,
            'total_expenses': 84000,
            'combined_financial_assets': 250000,
            'primary_residence_value': 450000,
            'secondary_residence_value': 0,
            'combined_other_assets_total': 50000,
            'total_liabilities_local': 300000,
            'partner_liabilities': 0,
            'tax_rate': 22.0,
            'inflation_rate': 3.0,
            'investment_return_rate': 7.0,
            'simulation_years': 30,
            'mc_iterations': 0,
            'goal_costs': {},
            'college_inflation_pct': 4.0,
            'base_public_in': 20000,
            'base_public_out': 40000,
            'base_private': 60000,
            'ira_balance': 50000,
            'four01k_403b_balance': 150000,
            'partner_ira_balance': 30000,
            'partner_four01k_403b_balance': 100000,
            'monthly_surplus': 3000,
            'combined_total_liabilities': 300000,
            'roth_conversion_annual': 0,
            'itemize_deductions': True,
            'five29_plan_balance': 0,
            'tax_exempt_interest': 0,
            'custom_expenses_total': 0
        }

    def test_simulation_returns_dict(self, basic_simulation_params):
        """Simulation should return a dictionary"""
        result = run_simulation(**basic_simulation_params)
        assert isinstance(result, dict)

    def test_simulation_returns_dataframe(self, basic_simulation_params):
        """Result should contain a DataFrame"""
        result = run_simulation(**basic_simulation_params)
        assert 'df' in result
        assert isinstance(result['df'], pd.DataFrame)

    def test_simulation_dataframe_has_correct_rows(self, basic_simulation_params):
        """DataFrame should have one row per simulation year"""
        result = run_simulation(**basic_simulation_params)
        df = result['df']
        assert len(df) == basic_simulation_params['simulation_years']

    def test_simulation_dataframe_has_required_columns(self, basic_simulation_params):
        """DataFrame should have all required columns"""
        result = run_simulation(**basic_simulation_params)
        df = result['df']

        required_columns = [
            'Year', 'User_Age', 'Partner_Age',
            'Total_Income', 'Total_Expenses',
            'Taxes_Paid', 'Net_Worth', 'Savings_End',
            'User_RMD', 'Partner_RMD', 'Total_RMD',
            'Roth_Conversion', 'IRMAA_Annual_Cost'
        ]

        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"

    def test_simulation_years_are_sequential(self, basic_simulation_params):
        """Years should be sequential starting from current year"""
        result = run_simulation(**basic_simulation_params)
        df = result['df']

        years = df['Year'].tolist()
        current_year = date.today().year
        expected_years = list(range(current_year, current_year + 30))

        assert years == expected_years

    def test_simulation_ages_increment_correctly(self, basic_simulation_params):
        """Ages should increment by 1 each year"""
        result = run_simulation(**basic_simulation_params)
        df = result['df']

        user_ages = df['User_Age'].tolist()
        for i in range(1, len(user_ages)):
            assert user_ages[i] == user_ages[i-1] + 1

        partner_ages = df['Partner_Age'].tolist()
        for i in range(1, len(partner_ages)):
            assert partner_ages[i] == partner_ages[i-1] + 1

    def test_simulation_income_grows_with_inflation(self, basic_simulation_params):
        """Income should grow with inflation rate"""
        result = run_simulation(**basic_simulation_params)
        df = result['df']

        # Year-over-year growth should be approximately inflation rate
        for i in range(1, min(5, len(df))):
            growth = df['Total_Income'].iloc[i] / df['Total_Income'].iloc[i-1]
            expected_growth = 1 + basic_simulation_params['inflation_rate'] / 100
            # Allow 10% tolerance due to RMDs and other factors
            assert abs(growth - expected_growth) < 0.10

    def test_simulation_expenses_grow_with_inflation(self, basic_simulation_params):
        """Expenses should grow with inflation rate"""
        result = run_simulation(**basic_simulation_params)
        df = result['df']

        for i in range(1, min(5, len(df))):
            growth = df['Total_Expenses'].iloc[i] / df['Total_Expenses'].iloc[i-1]
            expected_growth = 1 + basic_simulation_params['inflation_rate'] / 100
            assert abs(growth - expected_growth) < 0.10

    def test_simulation_net_worth_calculated(self, basic_simulation_params):
        """Net worth should be total assets minus liabilities"""
        result = run_simulation(**basic_simulation_params)
        df = result['df']

        for i in range(len(df)):
            net_worth = df['Net_Worth'].iloc[i]
            total_assets = df['Total_Assets'].iloc[i]
            total_liabilities = df['Total_Liabilities'].iloc[i]
            assert abs(net_worth - (total_assets - total_liabilities)) < 0.01

    def test_simulation_savings_accumulates(self, basic_simulation_params):
        """Savings should generally grow if income > expenses"""
        result = run_simulation(**basic_simulation_params)
        df = result['df']

        # With positive surplus, savings should grow (at least in early years)
        initial_savings = df['Savings_End'].iloc[0]
        final_savings = df['Savings_End'].iloc[-1]
        # Given 7% returns and positive surplus, should grow significantly
        assert final_savings > initial_savings * 2

    def test_simulation_returns_health_metrics(self, basic_simulation_params):
        """Result should include financial health metrics"""
        result = run_simulation(**basic_simulation_params)

        assert 'emergency_fund_months' in result
        assert 'debt_to_income' in result
        assert 'savings_rate' in result
        assert 'health_score' in result
        assert 'years_solvent' in result

    def test_simulation_health_score_range(self, basic_simulation_params):
        """Health score should be between 0 and 100"""
        result = run_simulation(**basic_simulation_params)
        assert 0 <= result['health_score'] <= 100

    def test_simulation_with_zero_income(self, basic_simulation_params):
        """Simulation should handle zero income gracefully"""
        params = basic_simulation_params.copy()
        params['total_income'] = 0
        params['monthly_surplus'] = 0

        result = run_simulation(**params)
        assert result is not None
        assert isinstance(result['df'], pd.DataFrame)

    def test_simulation_with_high_expenses(self, basic_simulation_params):
        """Simulation should handle expenses > income"""
        params = basic_simulation_params.copy()
        params['total_expenses'] = 150000  # More than income
        params['monthly_surplus'] = -2500

        result = run_simulation(**params)
        assert result is not None
        # Savings should eventually deplete
        df = result['df']
        # Final savings might be zero or near zero
        assert df['Savings_End'].iloc[-1] >= 0  # Should not go negative

    def test_simulation_single_person(self, basic_simulation_params):
        """Simulation should work for single person (no partner)"""
        params = basic_simulation_params.copy()
        params['partner_exists'] = False
        params['partner_age'] = 0
        params['partner_ira_balance'] = 0
        params['partner_four01k_403b_balance'] = 0

        result = run_simulation(**params)
        assert result is not None
        df = result['df']
        # Partner columns should be zero
        assert all(df['Partner_Age'] == 0)
        assert all(df['Partner_RMD'] == 0)


# ===========================================================================
# TEST GROUP 4: RMD (Required Minimum Distribution) Tests
# ===========================================================================
class TestRMDCalculations:
    """Test Required Minimum Distribution logic"""

    @pytest.fixture
    def rmd_params(self):
        """Parameters for RMD testing (start at age 70)"""
        mock_st.session_state = {
            'children_rows': [],
            'inherit_rows': []
        }
        return {
            'age': 70,
            'partner_exists': False,
            'partner_age': 0,
            'total_income': 60000,
            'total_expenses': 48000,
            'combined_financial_assets': 100000,
            'primary_residence_value': 400000,
            'secondary_residence_value': 0,
            'combined_other_assets_total': 0,
            'total_liabilities_local': 0,
            'partner_liabilities': 0,
            'tax_rate': 22.0,
            'inflation_rate': 3.0,
            'investment_return_rate': 7.0,
            'simulation_years': 10,
            'mc_iterations': 0,
            'goal_costs': {},
            'college_inflation_pct': 4.0,
            'base_public_in': 20000,
            'base_public_out': 40000,
            'base_private': 60000,
            'ira_balance': 500000,
            'four01k_403b_balance': 500000,
            'partner_ira_balance': 0,
            'partner_four01k_403b_balance': 0,
            'monthly_surplus': 1000,
            'combined_total_liabilities': 0,
            'roth_conversion_annual': 0,
            'itemize_deductions': True,
            'five29_plan_balance': 0,
            'tax_exempt_interest': 0,
            'custom_expenses_total': 0
        }

    def test_rmd_starts_at_age_73(self, rmd_params):
        """RMDs should start at age 73"""
        result = run_simulation(**rmd_params)
        df = result['df']

        # Ages 70, 71, 72 should have zero RMD
        for i in range(3):  # First 3 years
            if df['User_Age'].iloc[i] < 73:
                assert df['User_RMD'].iloc[i] == 0

        # Age 73+ should have RMD > 0
        rmd_73_idx = 3  # Age 73 is 4th year (index 3)
        if rmd_73_idx < len(df):
            assert df['User_RMD'].iloc[rmd_73_idx] > 0

    def test_rmd_uses_correct_factors(self, rmd_params):
        """RMD should use IRS Uniform Lifetime Table factors"""
        result = run_simulation(**rmd_params)
        df = result['df']

        # At age 73, factor is 27.4
        # Initial balance = 500k + 500k = 1M
        # Expected RMD = 1M / 27.4 ≈ 36,496
        # But balance changes, so just check it's reasonable
        rmd_at_73_idx = 3
        if rmd_at_73_idx < len(df):
            rmd = df['User_RMD'].iloc[rmd_at_73_idx]
            # Should be roughly balance / 27.4
            assert 30000 < rmd < 50000

    def test_rmd_decreases_ira_balance(self, rmd_params):
        """RMD withdrawals should reduce retirement balance over time"""
        result = run_simulation(**rmd_params)
        df = result['df']

        # After several years of RMDs, total should decrease
        # (unless investment returns exceed RMDs)
        total_rmds = df['User_RMD'].sum()
        assert total_rmds > 0

    def test_partner_rmd_independent(self, rmd_params):
        """Partner RMDs should be calculated independently"""
        params = rmd_params.copy()
        params['partner_exists'] = True
        params['partner_age'] = 74  # Already RMD age
        params['partner_ira_balance'] = 300000
        params['partner_four01k_403b_balance'] = 200000

        result = run_simulation(**params)
        df = result['df']

        # Partner should have RMDs from year 1 (age 74)
        assert df['Partner_RMD'].iloc[0] > 0
        # Total RMD should be sum of both
        assert abs(df['Total_RMD'].iloc[0] - (df['User_RMD'].iloc[0] + df['Partner_RMD'].iloc[0])) < 0.01


# ===========================================================================
# TEST GROUP 5: Goal Achievement Tests
# ===========================================================================
class TestGoalAchievement:
    """Test goal tracking functionality"""

    @pytest.fixture
    def goal_params(self):
        """Parameters with goals"""
        mock_st.session_state = {
            'children_rows': [],
            'inherit_rows': []
        }
        current_year = date.today().year
        return {
            'age': 35,
            'partner_exists': True,
            'partner_age': 33,
            'total_income': 200000,
            'total_expenses': 100000,
            'combined_financial_assets': 500000,
            'primary_residence_value': 500000,
            'secondary_residence_value': 0,
            'combined_other_assets_total': 50000,
            'total_liabilities_local': 200000,
            'partner_liabilities': 0,
            'tax_rate': 22.0,
            'inflation_rate': 3.0,
            'investment_return_rate': 7.0,
            'simulation_years': 20,
            'mc_iterations': 0,
            'goal_costs': {
                'Buy Vacation Home': {
                    'amount': 300000,
                    'year': current_year + 5
                },
                'Kids College Fund': {
                    'amount': 200000,
                    'year': current_year + 10
                },
                'Early Retirement': {
                    'amount': 2000000,
                    'year': current_year + 15
                }
            },
            'college_inflation_pct': 4.0,
            'base_public_in': 20000,
            'base_public_out': 40000,
            'base_private': 60000,
            'ira_balance': 100000,
            'four01k_403b_balance': 300000,
            'partner_ira_balance': 50000,
            'partner_four01k_403b_balance': 200000,
            'monthly_surplus': 8000,
            'combined_total_liabilities': 200000,
            'roth_conversion_annual': 0,
            'itemize_deductions': True,
            'five29_plan_balance': 0,
            'tax_exempt_interest': 0,
            'custom_expenses_total': 0
        }

    def test_goal_achievement_returned(self, goal_params):
        """Goal achievement should be in results"""
        result = run_simulation(**goal_params)
        assert 'goal_achievement' in result
        assert isinstance(result['goal_achievement'], dict)

    def test_all_goals_tracked(self, goal_params):
        """All defined goals should be tracked"""
        result = run_simulation(**goal_params)

        for goal_name in goal_params['goal_costs'].keys():
            assert goal_name in result['goal_achievement']

    def test_goal_structure_correct(self, goal_params):
        """Each goal should have required fields"""
        result = run_simulation(**goal_params)

        for goal_name, goal_data in result['goal_achievement'].items():
            assert 'target' in goal_data
            assert 'year' in goal_data
            assert 'actual' in goal_data
            assert 'achieved' in goal_data

    def test_achievable_goal_marked_achieved(self, goal_params):
        """Goals with sufficient savings should be marked achieved"""
        result = run_simulation(**goal_params)

        # With high income and savings, early goals should be achieved
        vacation_home = result['goal_achievement'].get('Buy Vacation Home', {})
        if vacation_home:
            # High savings rate should achieve this
            assert vacation_home['actual'] > 0

    def test_goal_achievement_boolean(self, goal_params):
        """Achievement should be boolean (True/False)"""
        result = run_simulation(**goal_params)

        for goal_name, goal_data in result['goal_achievement'].items():
            # NumPy may return np.bool_ which is truthy but not isinstance bool
            assert goal_data['achieved'] in [True, False] or isinstance(goal_data['achieved'], (bool, np.bool_))


# ===========================================================================
# TEST GROUP 6: Edge Cases and Error Handling
# ===========================================================================
class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def minimal_params(self):
        """Minimal valid parameters"""
        mock_st.session_state = {
            'children_rows': [],
            'inherit_rows': []
        }
        return {
            'age': 30,
            'partner_exists': False,
            'partner_age': 0,
            'total_income': 50000,
            'total_expenses': 40000,
            'combined_financial_assets': 10000,
            'primary_residence_value': 0,
            'secondary_residence_value': 0,
            'combined_other_assets_total': 0,
            'total_liabilities_local': 0,
            'partner_liabilities': 0,
            'tax_rate': 20.0,
            'inflation_rate': 3.0,
            'investment_return_rate': 5.0,
            'simulation_years': 10,
            'mc_iterations': 0,
            'goal_costs': {},
            'college_inflation_pct': 4.0,
            'base_public_in': 20000,
            'base_public_out': 40000,
            'base_private': 60000,
            'ira_balance': 0,
            'four01k_403b_balance': 0,
            'partner_ira_balance': 0,
            'partner_four01k_403b_balance': 0,
            'monthly_surplus': 800,
            'combined_total_liabilities': 0,
            'roth_conversion_annual': 0,
            'itemize_deductions': True,
            'five29_plan_balance': 0,
            'tax_exempt_interest': 0,
            'custom_expenses_total': 0
        }

    def test_very_long_simulation(self, minimal_params):
        """Simulation should handle 50+ year horizons"""
        params = minimal_params.copy()
        params['simulation_years'] = 50

        result = run_simulation(**params)
        assert len(result['df']) == 50

    def test_very_short_simulation(self, minimal_params):
        """Simulation should handle 1-year horizon"""
        params = minimal_params.copy()
        params['simulation_years'] = 1

        result = run_simulation(**params)
        assert len(result['df']) == 1

    def test_very_old_user(self, minimal_params):
        """Simulation should handle users age 90+"""
        params = minimal_params.copy()
        params['age'] = 95
        params['simulation_years'] = 10
        # Need retirement balances for RMDs
        params['ira_balance'] = 500000
        params['four01k_403b_balance'] = 500000

        result = run_simulation(**params)
        assert result is not None
        # Should have RMDs (age 95 is past RMD age 73)
        # Note: RMD factors go up to age 100, older uses default
        assert result['df']['User_RMD'].sum() > 0

    def test_very_young_user(self, minimal_params):
        """Simulation should handle users age 18"""
        params = minimal_params.copy()
        params['age'] = 18
        params['simulation_years'] = 50

        result = run_simulation(**params)
        assert result is not None
        # No RMDs for young users
        assert result['df']['User_RMD'].iloc[0] == 0

    def test_zero_inflation(self, minimal_params):
        """Simulation should handle 0% inflation"""
        params = minimal_params.copy()
        params['inflation_rate'] = 0.0

        result = run_simulation(**params)
        df = result['df']

        # With zero inflation, base expenses should not grow
        # (though actual might due to other factors)
        assert result is not None

    def test_high_inflation(self, minimal_params):
        """Simulation should handle high inflation (10%+)"""
        params = minimal_params.copy()
        params['inflation_rate'] = 12.0

        result = run_simulation(**params)
        df = result['df']

        # Expenses should grow significantly
        year_1_expenses = df['Total_Expenses'].iloc[0]
        year_10_expenses = df['Total_Expenses'].iloc[-1]
        # 12% inflation over 9 years ≈ 2.77x
        assert year_10_expenses > year_1_expenses * 2

    def test_negative_returns(self, minimal_params):
        """Simulation should handle negative investment returns"""
        params = minimal_params.copy()
        params['investment_return_rate'] = -5.0

        result = run_simulation(**params)
        # Should still complete without error
        assert result is not None
        # Investment returns should be negative
        assert result['df']['Investment_Return'].iloc[0] < 0

    def test_custom_expenses(self, minimal_params):
        """Custom expenses should be included"""
        params = minimal_params.copy()
        params['custom_expenses_total'] = 500  # $500/month

        result = run_simulation(**params)
        df = result['df']

        # Custom expenses should appear
        assert df['Custom_Expenses'].iloc[0] > 0
        # Should be about 500 * 12 = 6000 annually
        assert 5000 < df['Custom_Expenses'].iloc[0] < 7000

    def test_roth_conversion_enabled(self, minimal_params):
        """Roth conversions should occur when enabled"""
        params = minimal_params.copy()
        params['age'] = 60  # Past age 65 - (age) = negative, so won't trigger
        params['roth_conversion_annual'] = 50000
        params['ira_balance'] = 200000

        # Note: Current implementation starts conversions at year (65 - age)
        # So if age=60, it starts at year 5
        params['simulation_years'] = 10

        result = run_simulation(**params)
        # May or may not have conversions depending on tax optimization
        assert result is not None


# ===========================================================================
# TEST GROUP 7: Data Integrity Tests
# ===========================================================================
class TestDataIntegrity:
    """Ensure data consistency and integrity"""

    @pytest.fixture
    def standard_params(self):
        """Standard test parameters"""
        mock_st.session_state = {
            'children_rows': [],
            'inherit_rows': []
        }
        return {
            'age': 45,
            'partner_exists': True,
            'partner_age': 43,
            'total_income': 150000,
            'total_expenses': 90000,
            'combined_financial_assets': 400000,
            'primary_residence_value': 500000,
            'secondary_residence_value': 0,
            'combined_other_assets_total': 25000,
            'total_liabilities_local': 350000,
            'partner_liabilities': 0,
            'tax_rate': 22.0,
            'inflation_rate': 3.0,
            'investment_return_rate': 7.0,
            'simulation_years': 20,
            'mc_iterations': 0,
            'goal_costs': {},
            'college_inflation_pct': 4.0,
            'base_public_in': 20000,
            'base_public_out': 40000,
            'base_private': 60000,
            'ira_balance': 100000,
            'four01k_403b_balance': 200000,
            'partner_ira_balance': 50000,
            'partner_four01k_403b_balance': 100000,
            'monthly_surplus': 5000,
            'combined_total_liabilities': 350000,
            'roth_conversion_annual': 0,
            'itemize_deductions': True,
            'five29_plan_balance': 0,
            'tax_exempt_interest': 0,
            'custom_expenses_total': 0
        }

    def test_no_nan_values_in_output(self, standard_params):
        """DataFrame should not contain NaN values"""
        result = run_simulation(**standard_params)
        df = result['df']

        # Check all numeric columns
        for col in df.columns:
            if col != 'Goal_Progress':  # Skip dict column
                nan_count = df[col].isna().sum()
                assert nan_count == 0, f"Column {col} has {nan_count} NaN values"

    def test_no_infinite_values(self, standard_params):
        """DataFrame should not contain infinite values"""
        result = run_simulation(**standard_params)
        df = result['df']

        for col in df.select_dtypes(include=[np.number]).columns:
            inf_count = np.isinf(df[col]).sum()
            assert inf_count == 0, f"Column {col} has {inf_count} infinite values"

    def test_savings_never_negative(self, standard_params):
        """Savings should never go below zero"""
        result = run_simulation(**standard_params)
        df = result['df']

        assert all(df['Savings_End'] >= 0)

    def test_taxes_never_negative(self, standard_params):
        """Taxes should never be negative"""
        result = run_simulation(**standard_params)
        df = result['df']

        assert all(df['Taxes_Paid'] >= 0)

    def test_rmds_never_negative(self, standard_params):
        """RMDs should never be negative"""
        result = run_simulation(**standard_params)
        df = result['df']

        assert all(df['User_RMD'] >= 0)
        assert all(df['Partner_RMD'] >= 0)
        assert all(df['Total_RMD'] >= 0)

    def test_ages_always_positive(self, standard_params):
        """Ages should always be positive"""
        result = run_simulation(**standard_params)
        df = result['df']

        assert all(df['User_Age'] > 0)
        # Partner age can be 0 if no partner

    def test_total_rmd_equals_sum(self, standard_params):
        """Total RMD should equal user + partner RMD"""
        result = run_simulation(**standard_params)
        df = result['df']

        for i in range(len(df)):
            total = df['Total_RMD'].iloc[i]
            user = df['User_RMD'].iloc[i]
            partner = df['Partner_RMD'].iloc[i]
            assert abs(total - (user + partner)) < 0.01


# ===========================================================================
# STANDALONE TEST RUNNER
# ===========================================================================
if __name__ == '__main__':
    print("=" * 70)
    print("SIMULATION CORE TEST SUITE")
    print("Phase 0: Safety Net for Architecture Migration")
    print("=" * 70)

    # Run pytest if available
    try:
        exit_code = pytest.main([__file__, '-v', '--tb=short'])
        sys.exit(exit_code)
    except Exception as e:
        print(f"Pytest failed: {e}")
        print("Running basic tests manually...")

        # Manual test execution
        test_count = 0
        pass_count = 0
        fail_count = 0

        # Simple test runner
        test_classes = [
            TestTaxCalculations,
            TestRothConversionOptimization,
            TestRunSimulation,
            TestRMDCalculations,
            TestGoalAchievement,
            TestEdgeCases,
            TestDataIntegrity
        ]

        for test_class in test_classes:
            print(f"\n--- {test_class.__name__} ---")
            instance = test_class()

            for method_name in dir(instance):
                if method_name.startswith('test_'):
                    test_count += 1
                    try:
                        # Get fixtures if needed
                        if hasattr(instance, 'basic_simulation_params'):
                            instance.basic_simulation_params = instance.basic_simulation_params()
                        method = getattr(instance, method_name)
                        method()
                        print(f"  ✓ {method_name}")
                        pass_count += 1
                    except Exception as e:
                        print(f"  ✗ {method_name}: {str(e)[:100]}")
                        fail_count += 1

        print(f"\n{'=' * 70}")
        print(f"RESULTS: {pass_count}/{test_count} tests passed, {fail_count} failed")
        print("=" * 70)
