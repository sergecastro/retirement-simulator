"""
Healthcare Cost Projector - Legal Disclaimers
==============================================
Comprehensive legal disclaimers for healthcare features including Medicare,
Medigap, Medicare Advantage, and Long-Term Care analysis.

CRITICAL: These disclaimers MUST be displayed to ensure Family Forecast complies
with healthcare and insurance regulatory requirements.

Author: Family Forecast Development Team
Last Updated: October 22, 2025
Legal Review: REQUIRED before production deployment
"""

import streamlit as st
from datetime import datetime


# =============================================================================
# PRIMARY HEALTHCARE DISCLAIMER
# =============================================================================

PRIMARY_HEALTHCARE_DISCLAIMER = """
**🏥 HEALTHCARE COST PROJECTOR - IMPORTANT NOTICE**

Family Forecast's Healthcare Cost Projector provides **general educational information** about
healthcare costs, Medicare, insurance options, and long-term care planning for
**informational and educational purposes only**.

**What This Tool Provides:**
✅ Educational information about Medicare costs and IRMAA calculations
✅ General comparison of healthcare coverage options
✅ Estimated healthcare cost projections based on your inputs
✅ Planning concepts and decision-making frameworks

**What This Tool Does NOT Provide:**
❌ Medical advice or healthcare recommendations
❌ Personalized insurance recommendations or plan selection
❌ Licensed insurance broker or agent services
❌ Legal advice for Medicaid planning or estate planning
❌ Guaranteed accuracy of future healthcare costs
❌ Tax advice related to healthcare decisions

**CRITICAL LIMITATIONS:**

⚠️ **Medicare Rules Are Complex:** Medicare enrollment has strict deadlines, penalties
for late enrollment, and exceptions we cannot fully model

⚠️ **Annual Changes:** Medicare premiums, IRMAA brackets, and plan details change every year

⚠️ **Individual Circumstances:** Your actual costs depend on health status, medications,
providers, and many factors we cannot predict

⚠️ **State Variations:** Medicare Advantage, Medigap, and Medicaid rules vary significantly
by state

⚠️ **Not Real-Time Data:** We use published averages and estimates, not real-time
insurance plan data

**🎯 ALWAYS Consult Qualified Professionals:**
1. **Medicare.gov** - Official Medicare plan finder and information
2. **SHIP (State Health Insurance Assistance Program)** - Free Medicare counseling
3. **Licensed Insurance Agents** - For plan enrollment and selection
4. **Healthcare Providers** - For medical advice and care planning
5. **Tax Professionals** - For tax implications of healthcare decisions
6. **Elder Law Attorneys** - For Medicaid planning and legal matters

**By using this Healthcare Cost Projector, you acknowledge:**
- This is educational information only, not medical or insurance advice
- You will verify all information with official sources and professionals
- You understand healthcare and insurance decisions require professional guidance
- Family Forecast does not act as an insurance broker, agent, or healthcare advisor

**Use this tool to ask better questions of your advisors, NOT to replace them.**
"""


# =============================================================================
# MEDICARE IRMAA CALCULATOR DISCLAIMER
# =============================================================================

MEDICARE_IRMAA_DISCLAIMER = """
**💰 MEDICARE IRMAA CALCULATOR - IMPORTANT NOTICE**

**What is IRMAA?**
Income-Related Monthly Adjustment Amount (IRMAA) is an additional charge added to
Medicare Part B and Part D premiums based on your Modified Adjusted Gross Income (MAGI)
from **2 years prior**.

**What This Calculator Does:**
✅ Estimates your IRMAA bracket based on income projections
✅ Shows how income changes affect Medicare premiums (2-year lookback)
✅ Models potential impact of Roth conversions on IRMAA costs
✅ Uses official CMS IRMAA brackets updated for 2025

**CRITICAL LIMITATIONS:**

⚠️ **2-Year Lookback Rule:** Your 2025 IRMAA is based on your 2023 income (not current)

⚠️ **MAGI Calculation:** Our MAGI calculator is simplified. Actual MAGI calculations
can be complex and should be verified with a tax professional

⚠️ **Annual Bracket Adjustments:** IRMAA brackets are adjusted annually for inflation by CMS

⚠️ **Life-Changing Events:** You may qualify for IRMAA reduction if you experience
certain life events (marriage, divorce, death of spouse, retirement, etc.)

⚠️ **Tax-Exempt Interest Counts:** Municipal bond interest counts toward MAGI for
IRMAA purposes (even though it's tax-free!)

⚠️ **One-Time Income Spikes:** Large capital gains, Roth conversions, or property
sales can push you into higher brackets for 2 years

**What We DON'T Account For:**
- Exact IRS MAGI calculations (complex tax situations)
- IRMAA appeals and life-changing event exceptions
- State-specific Medicare supplements or programs
- Premium assistance programs (MSP, Extra Help)

**🎯 Before Making Income Decisions Based on IRMAA:**
1. Verify your actual MAGI with a CPA or tax professional
2. Check current year IRMAA brackets on Medicare.gov
3. Consider multi-year tax planning with your financial advisor
4. Understand the 2-year lookback creates a planning window
5. Consider IRMAA appeals for life-changing events

**This calculator is an educational tool. For actual Medicare premium calculations
and tax planning, consult Medicare.gov and your tax advisor.**
"""


# =============================================================================
# MEDIGAP VS MEDICARE ADVANTAGE DISCLAIMER
# =============================================================================

MEDIGAP_ADVANTAGE_DISCLAIMER = """
**🏥 MEDIGAP VS MEDICARE ADVANTAGE - INSURANCE COMPARISON NOTICE**

This comparison provides **general educational information** about differences between
Medigap (Medicare Supplement Insurance) and Medicare Advantage (Part C) plans.

**What This Comparison Shows:**
✅ General features and cost structures of each plan type
✅ Typical premium ranges and out-of-pocket costs
✅ Key decision factors (provider flexibility, travel, predictability)
✅ Long-term cost projections based on usage assumptions

**What This Comparison Does NOT Do:**
❌ Recommend specific insurance plans, carriers, or policies
❌ Show actual plan details, provider networks, or drug formularies
❌ Account for your specific health conditions or medications
❌ Replace the Medicare.gov Plan Finder tool
❌ Act as licensed insurance advice or broker services

**CRITICAL PLAN DIFFERENCES:**

**Medigap (Supplement Insurance):**
- Works WITH Original Medicare (Parts A & B)
- Covers gaps in Original Medicare (deductibles, coinsurance)
- See ANY doctor who accepts Medicare (nationwide)
- More predictable costs (higher premiums, minimal out-of-pocket)
- No provider networks or referrals needed
- May require medical underwriting (varies by state and enrollment period)

**Medicare Advantage (Part C):**
- REPLACES Original Medicare (all-in-one plan)
- Includes Part D (prescriptions) in most plans
- Provider networks (HMO/PPO) - limited to specific doctors/hospitals
- Lower premiums but higher out-of-pocket costs when you use care
- May require referrals to see specialists
- Plans can change networks, costs, and coverage annually

**Important Factors We Simplify:**
⚠️ Your specific prescription drugs and their formulary coverage
⚠️ Your preferred doctors and whether they're in-network
⚠️ Geographic availability (not all plans available in all areas)
⚠️ Plan quality ratings (Star Ratings) and customer satisfaction
⚠️ Special Needs Plans (SNPs) for specific conditions

**Enrollment Rules Are Strict:**
- **Initial Enrollment Period:** 6 months starting when you turn 65 and enroll in Part B
- **Medigap Open Enrollment:** Guaranteed issue rights during initial period only
- **Annual Election Period:** Oct 15 - Dec 7 for Medicare Advantage changes
- **Late Enrollment Penalties:** Apply if you miss deadlines

**🎯 For Actual Plan Selection:**
1. Use **Medicare.gov Plan Finder** for your ZIP code and specific needs
2. Enter your actual medications and preferred doctors
3. Review plan Star Ratings and quality measures
4. Consult **SHIP counselors** (free, unbiased Medicare counseling)
5. Compare multiple carriers and read plan materials carefully
6. Enroll during proper enrollment periods to avoid penalties or coverage gaps

**This tool helps you UNDERSTAND plan types. For actual plan selection and
enrollment, use Medicare.gov and consult licensed insurance professionals.**
"""


# =============================================================================
# LONG-TERM CARE DISCLAIMER
# =============================================================================

LONG_TERM_CARE_DISCLAIMER = """
**🏥 LONG-TERM CARE COST ANALYSIS - PLANNING NOTICE**

This analysis provides **general educational information** about long-term care (LTC)
costs, probability estimates, and funding strategies for **planning purposes only**.

**What This Analysis Shows:**
✅ Average LTC costs by region and care setting (nursing home, assisted living, home care)
✅ Statistical probability of needing LTC based on age and demographic factors
✅ Comparison of funding strategies (self-insure, LTC insurance, hybrid policies, Medicaid)
✅ Monte Carlo simulations of potential LTC cost scenarios

**What This Analysis Does NOT Do:**
❌ Predict YOUR specific health outcomes or care needs
❌ Recommend specific LTC insurance policies, carriers, or products
❌ Provide Medicaid planning or legal advice
❌ Guarantee accuracy of cost projections or probability estimates
❌ Replace elder law attorneys, insurance specialists, or care planners

**CRITICAL LIMITATIONS:**

⚠️ **Highly Individual:** Your actual care needs depend on health factors, family history,
lifestyle, and medical conditions we cannot predict

⚠️ **Wide Cost Variations:** LTC costs vary dramatically by:
- Geographic location (urban vs rural, state differences)
- Facility quality and amenities
- Level of care needed (skilled nursing vs assisted living vs home care)
- Inflation in healthcare costs (historically 4-6% annually)

⚠️ **Probability vs Reality:** Statistics show ~70% of people over 65 need some LTC,
but YOUR individual probability may be very different

⚠️ **Insurance Limitations:** LTC insurance has:
- Strict age limits for purchase (typically max age 75-80)
- Medical underwriting (pre-existing conditions may disqualify you)
- Premium increases (carriers can raise rates on entire classes)
- Benefit triggers (specific criteria to receive benefits)
- Elimination periods (waiting periods before coverage begins)

⚠️ **Medicaid Complexity:** Medicaid LTC coverage involves:
- 5-year lookback period for asset transfers
- Asset and income limits (vary by state)
- Estate recovery (state may claim assets after death)
- Spend-down requirements
- Complex legal rules requiring attorney guidance

**Understanding LTC Probabilities:**
- ~70% of people over 65 need some form of long-term care (industry statistic)
- Average duration is ~3.5 years, but range is wide (20% need 5+ years)
- Women typically need more care than men (longer lifespan)
- Statistics are averages and do NOT predict YOUR individual situation
- Health history, genetics, lifestyle significantly affect your personal risk

**Funding Strategy Considerations:**

**1. Self-Insure:**
- Requires substantial liquid assets ($200K-$500K+)
- Risk: One extended care event can deplete entire retirement savings
- Benefit: No premiums, full control, any care setting

**2. Traditional LTC Insurance:**
- Age limits (typically max 75-80 for new policies)
- Medical underwriting required
- Premiums can increase over time
- Use-it-or-lose-it (no benefit if you don't need care)
- Tax benefits available in some cases

**3. Hybrid Life/LTC Policies:**
- Combination of life insurance and LTC benefits
- More expensive upfront but guaranteed benefits
- Death benefit if LTC not needed
- Complex products requiring careful analysis

**4. Medicaid Planning:**
- Must meet strict asset and income limits
- 5-year lookback for asset transfers
- Requires elder law attorney guidance
- Limited facility choices in some areas
- Estate recovery considerations

**🎯 For Actual LTC Planning:**
1. **Elder Law Attorney** - For Medicaid planning, asset protection, legal strategies
2. **LTC Insurance Specialist** - For policy comparison, underwriting assessment, cost analysis
3. **Fee-Only Financial Planner** - For comprehensive funding strategy and retirement integration
4. **Geriatric Care Manager** - For care needs assessment and resource navigation
5. **State Medicaid Office** - For eligibility rules, application assistance, program details

**This tool helps you UNDERSTAND LTC planning concepts and explore scenarios.
For actual LTC planning decisions, you MUST consult qualified professionals
in elder law, insurance, and financial planning.**
"""


# =============================================================================
# DATA SOURCE DISCLAIMER
# =============================================================================

DATA_SOURCE_DISCLAIMER = """
**📊 DATA SOURCES & ACCURACY DISCLAIMER**

**Data Sources:**
- **IRMAA Brackets:** Centers for Medicare & Medicaid Services (CMS) published rates
- **Medicare Premiums:** CMS official announcements and historical data
- **State Cost Data:** Kaiser Family Foundation, AARP, industry surveys
- **LTC Costs:** Genworth Cost of Care Survey, AARP studies
- **Probability Data:** Published actuarial studies and longevity research

**Data Limitations:**
⚠️ **Point-in-Time:** All data is current as of October 2025 and will become outdated
⚠️ **Estimates & Averages:** Regional costs and probabilities are estimates, not guarantees
⚠️ **Simplified Models:** We use simplified assumptions for complex real-world situations
⚠️ **No Real-Time Plans:** We do NOT pull real-time insurance plan data or pricing

**Annual Updates Required:**
- Medicare premiums and IRMAA brackets change every year (announced in October/November)
- State insurance costs fluctuate
- Tax laws and regulations change
- Healthcare costs inflate at varying rates

**🎯 Always Verify With Official Sources:**
- Medicare.gov for current premiums and plan details
- SSA.gov for Social Security and Medicare information
- CMS.gov for official IRMAA brackets and Medicare rules
- State insurance departments for Medicaid and local programs

**This tool uses the best available data but cannot guarantee accuracy for
your specific situation or future years.**
"""


# =============================================================================
# ROTH CONVERSION TAX DISCLAIMER
# =============================================================================

ROTH_CONVERSION_TAX_DISCLAIMER = """
**💰 ROTH CONVERSION & IRMAA - TAX PLANNING NOTICE**

**Important Context:**
This tool shows how Roth IRA conversions can affect Medicare IRMAA surcharges.
However, this is just ONE factor in a complex tax decision.

**What We Show:**
✅ How conversion income increases MAGI
✅ Which IRMAA bracket you'd move into
✅ Additional Medicare costs for 2 years (due to lookback)

**What We DON'T Show (Consult Tax Professional!):**
❌ Federal and state income tax on the conversion
❌ Effect on Social Security taxation
❌ Impact on other means-tested benefits (ACA subsidies, etc.)
❌ Net present value of tax savings vs costs
❌ Optimal conversion timing and amounts
❌ Required Minimum Distribution (RMD) implications
❌ Estate planning considerations

**Critical Tax Considerations:**
⚠️ Roth conversions are TAXABLE income in the year of conversion
⚠️ May push you into higher tax brackets (federal + state)
⚠️ Can trigger IRMAA surcharges for 2 years
⚠️ May affect taxation of Social Security benefits
⚠️ Timing matters (early retirement vs late career)

**Multi-Year Strategy Required:**
- Roth conversions are typically done over multiple years
- Requires coordination with tax professional
- Consider "filling up" tax brackets strategically
- Account for IRMAA cliffs and bracket thresholds

**🎯 For Roth Conversion Planning:**
1. **CPA or Tax Professional** - Calculate total tax impact
2. **Financial Advisor** - Multi-year optimization strategy
3. **Coordinate:** Tax planning + Medicare planning + Social Security timing

**This tool shows IRMAA impact only. ALWAYS consult a tax professional
before executing Roth conversions.**
"""


# =============================================================================
# HELPER FUNCTIONS TO DISPLAY DISCLAIMERS
# =============================================================================

def show_primary_healthcare_disclaimer(location="header"):
    """
    Display primary healthcare disclaimer

    Args:
        location: "header", "sidebar", or "expander"
    """
    if location == "header":
        st.warning(PRIMARY_HEALTHCARE_DISCLAIMER)
    elif location == "sidebar":
        with st.sidebar:
            with st.expander("⚕️ Healthcare Disclaimer", expanded=False):
                st.markdown(PRIMARY_HEALTHCARE_DISCLAIMER)
    elif location == "expander":
        with st.expander("⚕️ IMPORTANT: Healthcare Tool Disclaimer", expanded=True):
            st.markdown(PRIMARY_HEALTHCARE_DISCLAIMER)


def show_medicare_irmaa_disclaimer():
    """Display Medicare IRMAA calculator disclaimer"""
    with st.expander("💰 Medicare IRMAA Calculator - Read This First", expanded=False):
        st.info(MEDICARE_IRMAA_DISCLAIMER)


def show_medigap_advantage_disclaimer():
    """Display Medigap vs Medicare Advantage comparison disclaimer"""
    with st.expander("🏥 Medigap vs Medicare Advantage - Important Information", expanded=False):
        st.info(MEDIGAP_ADVANTAGE_DISCLAIMER)


def show_long_term_care_disclaimer():
    """Display Long-Term Care analysis disclaimer"""
    with st.expander("🏥 Long-Term Care Analysis - Planning Notice", expanded=False):
        st.warning(LONG_TERM_CARE_DISCLAIMER)


def show_data_source_disclaimer():
    """Display data source and accuracy disclaimer"""
    with st.expander("📊 Data Sources & Limitations", expanded=False):
        st.info(DATA_SOURCE_DISCLAIMER)


def show_roth_conversion_disclaimer():
    """Display Roth conversion tax disclaimer"""
    with st.expander("💰 Roth Conversion & Tax Planning Notice", expanded=False):
        st.warning(ROTH_CONVERSION_TAX_DISCLAIMER)


def show_all_healthcare_disclaimers():
    """Display all healthcare disclaimers in sequence"""
    show_primary_healthcare_disclaimer(location="header")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        show_medicare_irmaa_disclaimer()
        show_long_term_care_disclaimer()
        show_roth_conversion_disclaimer()
    with col2:
        show_medigap_advantage_disclaimer()
        show_data_source_disclaimer()


def require_healthcare_disclaimer_acknowledgment():
    """
    Require user to acknowledge healthcare disclaimers before using features

    Returns:
        bool: True if acknowledged, False if not yet acknowledged
    """
    if 'healthcare_disclaimer_acknowledged' not in st.session_state:
        st.session_state.healthcare_disclaimer_acknowledged = False

    if not st.session_state.healthcare_disclaimer_acknowledged:
        st.title("⚕️ Healthcare Cost Projector - Important Notice")

        st.markdown(PRIMARY_HEALTHCARE_DISCLAIMER)

        st.markdown("---")

        st.markdown("### 📋 Additional Important Information:")

        col1, col2 = st.columns(2)
        with col1:
            with st.expander("Medicare IRMAA Information"):
                st.markdown(MEDICARE_IRMAA_DISCLAIMER)
            with st.expander("Long-Term Care Information"):
                st.markdown(LONG_TERM_CARE_DISCLAIMER)

        with col2:
            with st.expander("Medigap vs Medicare Advantage"):
                st.markdown(MEDIGAP_ADVANTAGE_DISCLAIMER)
            with st.expander("Data Sources"):
                st.markdown(DATA_SOURCE_DISCLAIMER)

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            acknowledge = st.checkbox(
                "✅ I understand this is an educational planning tool and does NOT provide "
                "medical advice, insurance recommendations, or legal guidance. I will consult "
                "qualified professionals (Medicare.gov, SHIP counselors, insurance agents, "
                "tax professionals, elder law attorneys) before making healthcare decisions.",
                key="healthcare_disclaimer_checkbox"
            )

            if st.button("Continue to Healthcare Cost Projector", disabled=not acknowledge, type="primary"):
                st.session_state.healthcare_disclaimer_acknowledged = True
                st.rerun()

        st.stop()

    return True


# =============================================================================
# DISCLAIMER VERSION TRACKING
# =============================================================================

DISCLAIMER_VERSION = "1.0.0"
DISCLAIMER_LAST_UPDATED = "October 22, 2025"
DISCLAIMER_NEXT_REVIEW = "January 2026"


def get_disclaimer_metadata():
    """Get disclaimer version and update information"""
    return {
        "version": DISCLAIMER_VERSION,
        "last_updated": DISCLAIMER_LAST_UPDATED,
        "next_review": DISCLAIMER_NEXT_REVIEW,
        "reviewed_by": "Legal team review REQUIRED before production"
    }


# =============================================================================
# USAGE EXAMPLES & INTEGRATION GUIDE
# =============================================================================

"""
INTEGRATION GUIDE FOR HEALTHCARE FEATURES:
------------------------------------------

1. AT TOP OF HEALTHCARE MODULE (Required):
   from healthcare.healthcare_disclaimers import require_healthcare_disclaimer_acknowledgment

   require_healthcare_disclaimer_acknowledgment()  # Shows disclaimer wall

2. IN MEDICARE IRMAA CALCULATOR PAGE:
   from healthcare.healthcare_disclaimers import show_medicare_irmaa_disclaimer

   st.title("Medicare IRMAA Calculator")
   show_medicare_irmaa_disclaimer()  # Shows specific disclaimer
   # ... rest of calculator

3. IN MEDIGAP VS ADVANTAGE COMPARISON:
   from healthcare.healthcare_disclaimers import show_medigap_advantage_disclaimer

   st.title("Medigap vs Medicare Advantage")
   show_medigap_advantage_disclaimer()
   # ... rest of comparison

4. IN LONG-TERM CARE ANALYSIS:
   from healthcare.healthcare_disclaimers import show_long_term_care_disclaimer

   st.title("Long-Term Care Cost Analysis")
   show_long_term_care_disclaimer()
   # ... rest of analysis

5. IN ROTH CONVERSION IRMAA IMPACT:
   from healthcare.healthcare_disclaimers import show_roth_conversion_disclaimer

   st.title("Roth Conversion IRMAA Impact")
   show_roth_conversion_disclaimer()
   # ... rest of calculator

6. IN SIDEBAR (Optional):
   show_primary_healthcare_disclaimer(location="sidebar")
   show_data_source_disclaimer()
"""


if __name__ == "__main__":
    print("=" * 70)
    print("✅ HEALTHCARE DISCLAIMERS MODULE")
    print("=" * 70)
    print(f"\nVersion: {DISCLAIMER_VERSION}")
    print(f"Last Updated: {DISCLAIMER_LAST_UPDATED}")
    print(f"Next Review: {DISCLAIMER_NEXT_REVIEW}")
    print("\nDisclaimers Included:")
    print("  ✅ Primary Healthcare Disclaimer")
    print("  ✅ Medicare IRMAA Calculator Disclaimer")
    print("  ✅ Medigap vs Medicare Advantage Disclaimer")
    print("  ✅ Long-Term Care Analysis Disclaimer")
    print("  ✅ Data Sources & Accuracy Disclaimer")
    print("  ✅ Roth Conversion Tax Disclaimer")
    print("\n⚠️  CRITICAL: Legal review REQUIRED before production!")
    print("=" * 70)
