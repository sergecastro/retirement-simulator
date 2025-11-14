# Future Improvements - Scenario Studio

**Date Identified:** November 14, 2025
**Status:** Documented for future enhancement

---

## 🎯 CRITICAL UX IMPROVEMENT: Scenario Comparison Logic

### Issue #1: Duplicate Scenarios in Comparison
**Problem:** When selecting scenarios to compare, if user has 2 scenarios with same name (e.g., "Conservative Approach"), both appear in comparison even if only selected once.

**Current Behavior:**
- User selects "Conservative Approach" once
- Chart shows "Conservative vs Conservative vs Aggressive"

**Expected Behavior:**
- Only show unique selected scenarios
- Or prevent duplicate scenario names

**Priority:** Medium
**Impact:** Confusing for users, clutters charts

---

## 🎯 MAJOR UX IMPROVEMENT: Always Compare Against Base Plan

### Issue #2: Missing Base Plan in Comparisons
**Problem:** Comparisons only show selected scenarios, NOT the user's actual current data (base plan).

**Current Behavior:**
- User creates "Aggressive Growth" and "Conservative Approach" scenarios
- Comparison shows: Aggressive vs Conservative
- **Missing:** The user's ACTUAL current retirement plan!

**Expected Behavior:**
- **ALWAYS include the base plan (current data) as the first comparison**
- Show it as "Current Plan" or "Base Plan"
- Let users select 1-3 additional scenarios to compare AGAINST their base
- Charts would show: "**Current Plan** vs Aggressive Growth vs Conservative Approach"

**Why This Matters:**
- Users want to see: "How does this hypothetical scenario compare to MY current situation?"
- Without base plan, comparisons are abstract and less meaningful
- The whole point is: "What if I change X, Y, Z from my CURRENT plan?"

**Design Suggestions:**

1. **Visual Hierarchy:**
   ```
   📊 Compare Scenarios

   ✅ Current Plan (YOUR BASELINE - always included)

   Select scenarios to compare against your current plan:
   [ ] Aggressive Growth
   [ ] Conservative Approach
   [ ] Early Retirement
   ```

2. **Chart Design:**
   - Base plan shown in BOLD or different color
   - Label: "Current Plan (You)" vs "Aggressive Growth" vs "Conservative"
   - Make it clear which one is reality vs hypothetical

3. **Table Comparison:**
   ```
   Metric               | Current Plan | Aggressive | Conservative
   ---------------------|--------------|------------|-------------
   Final Savings        | $2.5M        | $3.8M      | $2.1M
   Years Solvent        | 25 years     | 30 years   | 22 years
   Monthly Surplus      | -$900        | $1,200     | -$400
   ```

**Priority:** HIGH - This is a fundamental UX issue
**Impact:** Major - Changes the entire value proposition of scenarios
**Effort:** Medium - Requires refactoring comparison selection logic

---

## 📋 Implementation Notes

### Files to Modify:
- `ui/scenario_studio_page.py` (comparison selection logic, lines 1247-1290)
- `ui/scenario_studio_page.py` (chart generation, lines 1537-1750)
- May need to modify `utils/comparison_scenarios.py` if base plan needs to be loaded differently

### Technical Approach:
1. **Auto-include base plan:**
   - Load current snapshot as "base plan"
   - Always add it as first item in comparison array
   - Mark it with special flag: `is_base_plan: true`

2. **Dedup scenarios:**
   - Check for duplicate IDs in selected scenarios
   - Or use Set instead of List for selection

3. **Visual distinction:**
   - Use different color scheme for base plan in charts
   - Add label "(Current)" or "(Baseline)" to base plan name
   - Consider using solid bar for base vs pattern/hatched bars for scenarios

---

## 🗓️ When to Implement

**Recommendation:** Hold for next major feature sprint

**Reasoning:**
- Current functionality works (users CAN compare scenarios)
- This is a UX enhancement, not a bug
- Requires thoughtful design and testing
- Better to batch with other Scenario Studio improvements

**Alternative Quick Fix:**
- Add prominent message: "💡 Tip: Your current plan is not shown. These are hypothetical scenarios."
- Less ideal but acknowledges the gap

---

## 💭 Serge's Insight

> "LOGICALLY, COMPARISONS NEED TO BE COMPARED WITH THE CORE, BASIC DATA SET... I FEEL LIKE THE USER WANTS TO COMPARE THEIR OWN CURRENT DATA SET WITH AN IMAGINARY SCENARIO"

**This is absolutely correct.** The fundamental use case is:
- "I have my current plan (reality)"
- "What if I retire 2 years earlier? (scenario)"
- "What if I invest more aggressively? (scenario)"
- **SHOW ME: Reality vs Option A vs Option B**

Without the base plan, it's like comparing Option A vs Option B without knowing where you are NOW.

---

**Status:** Documented ✅
**Next Steps:** Review during next planning session
