"""
Medicare IRMAA Calculator
=========================
Calculates Medicare Part B and Part D premiums including Income-Related
Monthly Adjustment Amounts (IRMAA) based on Modified Adjusted Gross Income (MAGI).

Author: Family Forecast Development Team
Last Updated: October 22, 2025
Data Source: CMS 2025 IRMAA Tables
"""

from typing import Dict, Tuple, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IRMAABracket:
    """Represents an IRMAA income bracket with associated surcharges"""
    bracket_name: str
    single_min: float
    single_max: float
    married_min: float
    married_max: float
    part_b_surcharge: float
    part_d_surcharge: float
    description: str


@dataclass
class MedicarePremiun:
    """Results of Medicare premium calculation"""
    base_part_b: float
    part_b_surcharge: float
    total_part_b: float
    base_part_d: float
    part_d_surcharge: float
    total_part_d: float
    total_monthly: float
    total_annual: float
    irmaa_bracket: str
    magi_used: float


class MedicareIRMAACalculator:
    """
    Calculator for Medicare premiums including IRMAA surcharges

    IRMAA (Income-Related Monthly Adjustment Amount) is an extra charge
    added to Medicare Part B and Part D premiums for higher-income beneficiaries.

    Key Facts:
    - IRMAA is based on MAGI (Modified Adjusted Gross Income) from 2 years prior
    - Income thresholds adjust annually for inflation
    - Applies to both single filers and married filing jointly
    """

    # 2025 CMS Standard Premiums (these change annually)
    BASE_PART_B_PREMIUM = 174.70  # 2025 standard Part B premium
    BASE_PART_D_PREMIUM = 55.00   # 2025 estimated average Part D premium

    # 2025 IRMAA Brackets (Based on CMS guidelines)
    # NOTE: These are updated annually by CMS for inflation
    IRMAA_BRACKETS_2025 = [
        IRMAABracket(
            bracket_name="Standard (No IRMAA)",
            single_min=0,
            single_max=106000,
            married_min=0,
            married_max=212000,
            part_b_surcharge=0,
            part_d_surcharge=0,
            description="Standard Medicare premiums - no additional charges"
        ),
        IRMAABracket(
            bracket_name="IRMAA Bracket 1",
            single_min=106001,
            single_max=133000,
            married_min=212001,
            married_max=266000,
            part_b_surcharge=69.90,
            part_d_surcharge=12.90,
            description="First IRMAA tier - modest surcharge"
        ),
        IRMAABracket(
            bracket_name="IRMAA Bracket 2",
            single_min=133001,
            single_max=167000,
            married_min=266001,
            married_max=334000,
            part_b_surcharge=174.70,
            part_d_surcharge=33.30,
            description="Second IRMAA tier - medium surcharge"
        ),
        IRMAABracket(
            bracket_name="IRMAA Bracket 3",
            single_min=167001,
            single_max=200000,
            married_min=334001,
            married_max=400000,
            part_b_surcharge=279.50,
            part_d_surcharge=53.80,
            description="Third IRMAA tier - high surcharge"
        ),
        IRMAABracket(
            bracket_name="IRMAA Bracket 4",
            single_min=200001,
            single_max=500000,
            married_min=400001,
            married_max=750000,
            part_b_surcharge=384.30,
            part_d_surcharge=74.20,
            description="Fourth IRMAA tier - very high surcharge"
        ),
        IRMAABracket(
            bracket_name="IRMAA Bracket 5 (Maximum)",
            single_min=500001,
            single_max=float('inf'),
            married_min=750001,
            married_max=float('inf'),
            part_b_surcharge=419.30,
            part_d_surcharge=81.00,
            description="Highest IRMAA tier - maximum surcharge"
        ),
    ]

    def __init__(self, year: int = 2025):
        """
        Initialize calculator for specific year

        Args:
            year: Tax year for IRMAA calculation (default: 2025)
        """
        self.year = year
        self.brackets = self.IRMAA_BRACKETS_2025  # In future, load year-specific brackets

    def calculate_magi_simple(
        self,
        adjusted_gross_income: float,
        tax_exempt_interest: float = 0,
        excluded_foreign_income: float = 0
    ) -> float:
        """
        Calculate Modified Adjusted Gross Income (MAGI) for IRMAA purposes

        SIMPLIFIED CALCULATION:
        MAGI = AGI + Tax-Exempt Interest + Excluded Foreign Income

        NOTE: This is a simplified calculation. Actual MAGI can be more complex.
        Users should verify with tax professional.

        Args:
            adjusted_gross_income: AGI from tax return (Line 11 of Form 1040)
            tax_exempt_interest: Municipal bond interest (Line 2a of Form 1040)
            excluded_foreign_income: Foreign earned income exclusion (Form 2555)

        Returns:
            float: Calculated MAGI
        """
        magi = adjusted_gross_income + tax_exempt_interest + excluded_foreign_income
        return round(magi, 2)

    def calculate_magi_from_retirement_income(
        self,
        social_security: float = 0,
        pension: float = 0,
        ira_withdrawals: float = 0,
        roth_conversions: float = 0,
        investment_income: float = 0,
        capital_gains: float = 0,
        rental_income: float = 0,
        other_income: float = 0,
        tax_exempt_interest: float = 0,
        deductions: float = 0
    ) -> float:
        """
        Calculate MAGI from typical retirement income sources

        This is a more detailed calculation that breaks down retirement income.

        Args:
            social_security: Taxable portion of Social Security benefits
            pension: Pension and annuity income
            ira_withdrawals: Traditional IRA/401k withdrawals
            roth_conversions: Roth IRA conversion amounts (counts toward MAGI!)
            investment_income: Dividends, interest from taxable accounts
            capital_gains: Realized capital gains (including from sales)
            rental_income: Net rental income
            other_income: Any other taxable income
            tax_exempt_interest: Municipal bond interest (COUNTS for IRMAA!)
            deductions: Above-the-line deductions (not itemized)

        Returns:
            float: Calculated MAGI
        """
        # Calculate AGI
        agi = (
            social_security +
            pension +
            ira_withdrawals +
            roth_conversions +  # Conversions count as income!
            investment_income +
            capital_gains +
            rental_income +
            other_income -
            deductions
        )

        # Add back tax-exempt interest for IRMAA purposes
        magi = agi + tax_exempt_interest

        return round(magi, 2)

    def find_irmaa_bracket(
        self,
        magi: float,
        filing_status: str = "single"
    ) -> IRMAABracket:
        """
        Find the appropriate IRMAA bracket for given MAGI and filing status

        Args:
            magi: Modified Adjusted Gross Income
            filing_status: "single" or "married" (married filing jointly)

        Returns:
            IRMAABracket: The applicable IRMAA bracket
        """
        filing_status = filing_status.lower()

        for bracket in self.brackets:
            if filing_status == "single":
                if bracket.single_min <= magi <= bracket.single_max:
                    return bracket
            else:  # married
                if bracket.married_min <= magi <= bracket.married_max:
                    return bracket

        # If we get here, return highest bracket (shouldn't happen with inf max)
        return self.brackets[-1]

    def calculate_premiums(
        self,
        magi: float,
        filing_status: str = "single",
        include_part_d: bool = True
    ) -> MedicarePremiun:
        """
        Calculate total Medicare premiums including IRMAA surcharges

        Args:
            magi: Modified Adjusted Gross Income
            filing_status: "single" or "married"
            include_part_d: Whether to include Part D premium (default: True)

        Returns:
            MedicarePremiun: Complete premium calculation results
        """
        # Find applicable IRMAA bracket
        bracket = self.find_irmaa_bracket(magi, filing_status)

        # Calculate Part B
        total_part_b = self.BASE_PART_B_PREMIUM + bracket.part_b_surcharge

        # Calculate Part D (if included)
        if include_part_d:
            total_part_d = self.BASE_PART_D_PREMIUM + bracket.part_d_surcharge
        else:
            total_part_d = 0

        # Calculate totals
        total_monthly = total_part_b + total_part_d
        total_annual = total_monthly * 12

        return MedicarePremiun(
            base_part_b=self.BASE_PART_B_PREMIUM,
            part_b_surcharge=bracket.part_b_surcharge,
            total_part_b=total_part_b,
            base_part_d=self.BASE_PART_D_PREMIUM if include_part_d else 0,
            part_d_surcharge=bracket.part_d_surcharge if include_part_d else 0,
            total_part_d=total_part_d,
            total_monthly=total_monthly,
            total_annual=total_annual,
            irmaa_bracket=bracket.bracket_name,
            magi_used=magi
        )

    def calculate_roth_conversion_impact(
        self,
        current_magi: float,
        conversion_amount: float,
        filing_status: str = "single"
    ) -> Dict:
        """
        Calculate how a Roth conversion would impact Medicare premiums

        CRITICAL: Roth conversions count as income and can push you into
        higher IRMAA brackets for 2 years!

        Args:
            current_magi: Current MAGI without conversion
            conversion_amount: Amount to convert to Roth
            filing_status: "single" or "married"

        Returns:
            dict: Comparison of premiums with and without conversion
        """
        # Calculate current premiums
        current = self.calculate_premiums(current_magi, filing_status)

        # Calculate premiums with conversion
        new_magi = current_magi + conversion_amount
        with_conversion = self.calculate_premiums(new_magi, filing_status)

        # Calculate the difference (2-year impact due to lookback)
        annual_increase = with_conversion.total_annual - current.total_annual
        two_year_cost = annual_increase * 2  # IRMAA lookback is 2 years

        return {
            "current_magi": current_magi,
            "new_magi": new_magi,
            "conversion_amount": conversion_amount,
            "current_bracket": current.irmaa_bracket,
            "new_bracket": with_conversion.irmaa_bracket,
            "current_annual_premium": current.total_annual,
            "new_annual_premium": with_conversion.total_annual,
            "annual_increase": annual_increase,
            "two_year_total_cost": two_year_cost,
            "monthly_increase": round(annual_increase / 12, 2),
            "bracket_changed": current.irmaa_bracket != with_conversion.irmaa_bracket
        }

    def project_premiums_multi_year(
        self,
        starting_year: int,
        magi_by_year: Dict[int, float],
        filing_status: str = "single",
        inflation_rate: float = 0.03
    ) -> List[Dict]:
        """
        Project Medicare premiums over multiple years

        NOTE: IRMAA uses 2-year lookback, so 2025 premiums based on 2023 MAGI

        Args:
            starting_year: First year of projection
            magi_by_year: Dictionary mapping years to MAGI amounts
            filing_status: "single" or "married"
            inflation_rate: Expected annual increase in premiums (default 3%)

        Returns:
            List of dictionaries with yearly projections
        """
        projections = []

        # Adjust base premiums for inflation each year
        current_part_b = self.BASE_PART_B_PREMIUM
        current_part_d = self.BASE_PART_D_PREMIUM

        for year in sorted(magi_by_year.keys()):
            # IRMAA lookback: Use MAGI from 2 years prior
            lookback_year = year - 2

            if lookback_year in magi_by_year:
                magi = magi_by_year[lookback_year]
                bracket = self.find_irmaa_bracket(magi, filing_status)
            else:
                # No historical data, use current year
                magi = magi_by_year[year]
                bracket = self.find_irmaa_bracket(magi, filing_status)

            # Calculate premiums with inflated base
            years_from_base = year - starting_year
            inflated_part_b = current_part_b * ((1 + inflation_rate) ** years_from_base)
            inflated_part_d = current_part_d * ((1 + inflation_rate) ** years_from_base)

            total_part_b = inflated_part_b + bracket.part_b_surcharge
            total_part_d = inflated_part_d + bracket.part_d_surcharge
            total_monthly = total_part_b + total_part_d

            projections.append({
                "year": year,
                "lookback_year": lookback_year,
                "magi": magi,
                "irmaa_bracket": bracket.bracket_name,
                "base_part_b": round(inflated_part_b, 2),
                "part_b_surcharge": bracket.part_b_surcharge,
                "total_part_b": round(total_part_b, 2),
                "total_part_d": round(total_part_d, 2),
                "total_monthly": round(total_monthly, 2),
                "total_annual": round(total_monthly * 12, 2)
            })

        return projections

    def get_all_brackets_summary(
        self,
        filing_status: str = "single"
    ) -> List[Dict]:
        """
        Get summary of all IRMAA brackets for display/education

        Args:
            filing_status: "single" or "married"

        Returns:
            List of dictionaries with bracket information
        """
        summary = []

        for bracket in self.brackets:
            if filing_status == "single":
                income_min = bracket.single_min
                income_max = bracket.single_max if bracket.single_max != float('inf') else "No limit"
            else:
                income_min = bracket.married_min
                income_max = bracket.married_max if bracket.married_max != float('inf') else "No limit"

            total_part_b = self.BASE_PART_B_PREMIUM + bracket.part_b_surcharge
            total_part_d = self.BASE_PART_D_PREMIUM + bracket.part_d_surcharge
            total_monthly = total_part_b + total_part_d

            summary.append({
                "bracket_name": bracket.bracket_name,
                "income_range": f"${income_min:,.0f} - ${income_max:,.0f}" if isinstance(income_max, (int, float)) else f"${income_min:,.0f}+",
                "part_b_monthly": f"${total_part_b:.2f}",
                "part_d_monthly": f"${total_part_d:.2f}",
                "total_monthly": f"${total_monthly:.2f}",
                "total_annual": f"${total_monthly * 12:,.2f}",
                "description": bracket.description
            })

        return summary


# Convenience function for quick calculations
def calculate_medicare_cost(
    magi: float,
    filing_status: str = "single",
    year: int = 2025
) -> MedicarePremiun:
    """
    Quick function to calculate Medicare premiums

    Args:
        magi: Modified Adjusted Gross Income
        filing_status: "single" or "married"
        year: Tax year (default: 2025)

    Returns:
        MedicarePremiun: Premium calculation results
    """
    calculator = MedicareIRMAACalculator(year=year)
    return calculator.calculate_premiums(magi, filing_status)


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("MEDICARE IRMAA CALCULATOR - TEST EXAMPLES")
    print("=" * 70)

    calculator = MedicareIRMAACalculator()

    # Example 1: Standard Medicare (no IRMAA)
    print("\n📊 Example 1: Retiree with $80,000 MAGI (Single)")
    print("-" * 70)
    result1 = calculator.calculate_premiums(magi=80000, filing_status="single")
    print(f"MAGI: ${result1.magi_used:,.2f}")
    print(f"IRMAA Bracket: {result1.irmaa_bracket}")
    print(f"Part B: ${result1.total_part_b:.2f}/month")
    print(f"Part D: ${result1.total_part_d:.2f}/month")
    print(f"Total Monthly: ${result1.total_monthly:.2f}")
    print(f"Total Annual: ${result1.total_annual:,.2f}")

    # Example 2: High income with IRMAA
    print("\n📊 Example 2: High-Income Retiree with $175,000 MAGI (Single)")
    print("-" * 70)
    result2 = calculator.calculate_premiums(magi=175000, filing_status="single")
    print(f"MAGI: ${result2.magi_used:,.2f}")
    print(f"IRMAA Bracket: {result2.irmaa_bracket}")
    print(f"Part B: ${result2.total_part_b:.2f}/month (Base: ${result2.base_part_b:.2f} + Surcharge: ${result2.part_b_surcharge:.2f})")
    print(f"Part D: ${result2.total_part_d:.2f}/month (Base: ${result2.base_part_d:.2f} + Surcharge: ${result2.part_d_surcharge:.2f})")
    print(f"Total Monthly: ${result2.total_monthly:.2f}")
    print(f"Total Annual: ${result2.total_annual:,.2f}")
    print(f"💰 Extra cost due to IRMAA: ${result2.total_annual - result1.total_annual:,.2f}/year")

    # Example 3: Roth conversion impact
    print("\n📊 Example 3: Impact of $50,000 Roth Conversion")
    print("-" * 70)
    impact = calculator.calculate_roth_conversion_impact(
        current_magi=100000,
        conversion_amount=50000,
        filing_status="single"
    )
    print(f"Current MAGI: ${impact['current_magi']:,.2f}")
    print(f"New MAGI (with conversion): ${impact['new_magi']:,.2f}")
    print(f"Current Bracket: {impact['current_bracket']}")
    print(f"New Bracket: {impact['new_bracket']}")
    print(f"Annual Premium Increase: ${impact['annual_increase']:,.2f}")
    print(f"⚠️ 2-Year Total Cost (due to lookback): ${impact['two_year_total_cost']:,.2f}")
    print(f"Bracket Changed: {'YES ⚠️' if impact['bracket_changed'] else 'NO ✅'}")

    print("\n" + "=" * 70)
    print("✅ Medicare IRMAA Calculator Module - Ready for Integration!")
    print("=" * 70)
