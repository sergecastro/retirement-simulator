# Medicare Data Update Guide

## 📅 Update Schedule
**When:** Annually in October/November
**Effective:** January 1st of following year
**Who:** CMS (Centers for Medicare & Medicaid Services)

## 🔔 Update Triggers
1. CMS announces new Medicare premiums (usually mid-October)
2. CMS announces new IRMAA brackets (usually October/November)
3. New year begins (January 1st - data becomes outdated)

## 📊 What to Update

### Step 1: Update IRMAA Brackets
**File:** `healthcare/medicare_irmaa_calculator.py`
**Lines:** 25-90 (IRMAA_BRACKETS_2025 constant)

**Source:** https://www.cms.gov/medicare/health-plans/medigap/irmaa

Update all 6 brackets:
- `single_min` / `single_max` (income thresholds)
- `married_min` / `married_max` (income thresholds)
- `part_b_surcharge` (monthly surcharge)
- `part_d_surcharge` (monthly surcharge)

### Step 2: Update Standard Premiums
**File:** `healthcare/medicare_irmaa_calculator.py`
**Lines:** 23-24

**Source:** https://www.medicare.gov/basics/costs/medicare-costs
```python
BASE_PART_B_PREMIUM = 174.70  # Update with new year
BASE_PART_D_PREMIUM = 55.00   # Update with new year estimate
```

### Step 3: Update Historical Data
**File:** `healthcare/medicare_data.py`
**Line:** ~45+ (HISTORICAL_PART_B_PREMIUMS)

Add new year:
```python
HISTORICAL_PART_B_PREMIUMS = {
    2020: 144.60,
    2021: 148.50,
    # ... existing years
    2026: XXX.XX,  # Add new year
}
```

### Step 4: Update Data Version Tracking
**File:** `healthcare/medicare_data.py`
**Lines:** 18-24
```python
DATA_VERSION = "2026.1"  # Increment year
DATA_YEAR = 2026  # New year
DATA_LAST_UPDATED = "2025-11-15"  # Today's date
DATA_VALID_THROUGH = "2026-12-31"  # End of new year
DATA_SOURCE_DATE = "2025-11-15"  # When you verified CMS data
NEXT_UPDATE_EXPECTED = "2026-11-01"  # Following year
NEXT_DATA_EFFECTIVE = "2027-01-01"  # Following year
```

## ✅ Testing Checklist

### 1. Run Unit Tests
```bash
python -m healthcare.medicare_irmaa_calculator
```

**Expected output:**
- Example calculations run without errors
- Premium amounts look reasonable
- IRMAA brackets match CMS.gov

### 2. Test Calculator UI
1. Start Streamlit app
2. Navigate to Healthcare → Medicare Calculator
3. Check that data version shows current year
4. Test calculation with $80,000 MAGI
5. Test calculation with $175,000 MAGI
6. Verify IRMAA brackets match CMS

### 3. Verify Warnings
1. Check that "data current" message shows
2. Temporarily change `DATA_VALID_THROUGH` to past date
3. Verify warning appears
4. Revert `DATA_VALID_THROUGH`

## 📝 Commit & Deploy
```bash
# Commit changes
git add healthcare/
git commit -m "Update Medicare data for [YEAR] - CMS [YEAR] rates"

# Tag the update
git tag -a "medicare-data-[YEAR]" -m "Medicare data updated for [YEAR]"

# Push to GitHub
git push origin main
git push origin --tags
```

## 🔗 Official Sources

### Primary Sources (Use These!)
- **CMS IRMAA:** https://www.cms.gov/medicare/health-plans/medigap/irmaa
- **Medicare Costs:** https://www.medicare.gov/basics/costs/medicare-costs
- **CMS Newsroom:** https://www.cms.gov/newsroom

### Verification Sources
- **Social Security (IRMAA):** https://www.ssa.gov/medicare/
- **KFF (Kaiser):** https://www.kff.org/medicare/
- **AARP Medicare:** https://www.aarp.org/health/medicare-insurance/

## ⏰ Timeline Example

**October 15, 2025:** CMS announces 2026 rates
**October 16, 2025:** You update ForeCash data
**October 17, 2025:** Test & deploy
**October 18 - Dec 31, 2025:** Users see "update period" warning
**January 1, 2026:** New rates effective, old data expires

## 🆘 Troubleshooting

**Problem:** CMS hasn't announced rates yet
**Solution:** Wait until mid-October, or use inflation estimate (+3-5%)

**Problem:** Brackets changed structure
**Solution:** Review CMS documentation, may need code changes

**Problem:** State costs outdated
**Solution:** Update from KFF/AARP reports (less critical)
