# SCENARIO STUDIO - Implementation Plan
**Created:** November 13, 2025 @ 12:15 PM PST
**Branch:** `feature/scenario-studio`
**Based On:** `feature/scenario-comparison-enhanced` (Sub-Phase 2A ✅)

---

## 🎯 Overview

Creating **Card #4** on landing page - a dedicated mode for scenario comparison and "what-if" analysis.

**Vision:** Separate comparison features from ANALYSIS mode into a premium, focused experience.

---

## 🏆 Goals

1. **Separate Concerns** - Comparison features get their own dedicated mode
2. **Clean UX** - Focused experience for scenario exploration
3. **Premium Foundation** - Pattern for future monetization features
4. **Proven Pattern** - Following Healthcare Hub success model

---

## 🏗️ Architecture

### **Files to Create**

1. **`ui/scenario_studio_page.py`** (NEW)
   - Main Scenario Studio page
   - Multi-scenario selection interface
   - Comparison controls

2. **`ui/components/scenario_comparison_table.py`** (NEW)
   - Side-by-side comparison table
   - Adjustable columns for each scenario
   - Visual diff highlighting

### **Files to Modify**

1. **`app.py`**
   - Add `scenario_studio` mode routing
   - Import scenario_studio_page
   - Add mode handler

2. **`ui/landing_page.py`**
   - Add 4th card after Healthcare Hub
   - Card title: "🎬 Scenario Studio"
   - Card description: "Compare multiple what-if scenarios side-by-side"

3. **`ui/navigation.py`**
   - Add Scenario Studio menu item
   - Icon: 🎬 or 🎯
   - Position: After Healthcare Hub

4. **`ui/results_page.py`** (CLEANUP)
   - Remove old comparison section
   - Keep only base simulation
   - Add link: "Try Scenario Studio for comparisons"

### **Files to Reference (DON'T CHANGE)**

1. **`healthcare/healthcare_hub.py`**
   - Pattern for new mode structure
   - Reference for landing card design
   - Menu item pattern

2. **`utils/comparison_scenarios.py`**
   - Already working perfectly ✅
   - Use as-is for data loading
   - Don't modify storage logic

---

## 🛡️ Safety Measures

- ✅ **New Branch:** `feature/scenario-studio`
- ✅ **Incremental Commits:** After each step
- ✅ **Test After Each Change:** Verify nothing breaks
- ✅ **Can Rollback:** `git checkout feature/scenario-comparison-enhanced`

---

## ⏱️ Time Estimate

| Step | Task | Time |
|------|------|------|
| 1 | Add landing card | 30 min |
| 2 | Add mode routing | 15 min |
| 3 | Create basic page | 45 min |
| 4 | Build comparison table | 1 hour |
| 5 | Polish & test | 30 min |
| **TOTAL** | | **2.5-3 hours** |

---

## ✅ Success Criteria

- [ ] 4th card appears on landing page
- [ ] Card styling matches Healthcare Hub
- [ ] Clicking card opens Scenario Studio mode
- [ ] Can select 2-4 saved scenarios
- [ ] Side-by-side comparison table displays
- [ ] Comparison shows: Adjustments, Results, Diff
- [ ] ANALYSIS mode is cleaner (old comparison section removed)
- [ ] No regressions in existing features

---

## 📋 Implementation Steps

### **Step 1: Landing Card (30 min)**
**File:** `ui/landing_page.py`

Add 4th card after Healthcare Hub:
```python
# Card 4: Scenario Studio
col4 = st.columns(1)[0]
with col4:
    with st.container():
        st.markdown("### 🎬 Scenario Studio")
        st.markdown("Compare multiple what-if scenarios side-by-side")
        if st.button("Open Scenario Studio", key="open_scenario_studio", use_container_width=True):
            st.session_state.mode = "scenario_studio"
            st.rerun()
```

**Test:** Card appears, button works
**Commit:** `"Step 1: Add Scenario Studio card to landing page"`

---

### **Step 2: Mode Routing (15 min)**
**File:** `app.py`

Add routing logic:
```python
# Import
from ui.scenario_studio_page import scenario_studio_page

# In main()
elif st.session_state.mode == "scenario_studio":
    scenario_studio_page()
```

**Test:** Mode switches without errors
**Commit:** `"Step 2: Add Scenario Studio mode routing"`

---

### **Step 3: Basic Page (45 min)**
**File:** `ui/scenario_studio_page.py` (NEW)

Create basic structure:
```python
import streamlit as st
from utils.comparison_scenarios import get_comparisons_index, load_comparison_scenario

def scenario_studio_page():
    st.title("🎬 Scenario Studio")
    st.markdown("Compare multiple what-if scenarios side-by-side")

    # Get all saved comparisons
    all_comparisons = get_comparisons_index()

    if not all_comparisons:
        st.info("💡 Save some comparison scenarios in ANALYSIS mode first!")
        return

    # Multi-select for scenarios
    st.subheader("Select Scenarios to Compare")
    selected = st.multiselect(
        "Choose 2-4 scenarios",
        options=[c['name'] for c in all_comparisons],
        max_selections=4
    )

    if len(selected) >= 2:
        st.success(f"✅ Selected {len(selected)} scenarios")
        # Comparison table will go here
    else:
        st.warning("⚠️ Select at least 2 scenarios to compare")
```

**Test:** Page loads, multi-select works
**Commit:** `"Step 3: Create basic Scenario Studio page"`

---

### **Step 4: Comparison Table (1 hour)**
**File:** `ui/components/scenario_comparison_table.py` (NEW)

Build comparison table component:
```python
import streamlit as st
import pandas as pd

def display_comparison_table(scenarios_data):
    """Display side-by-side comparison of scenarios"""

    # Build comparison DataFrame
    comparison_rows = []

    # Row 1: Scenario Name
    comparison_rows.append({
        'Metric': 'Scenario Name',
        **{f'Scenario {i+1}': s['name'] for i, s in enumerate(scenarios_data)}
    })

    # Row 2-5: Adjustments
    for key, label in [
        ('adjusted_income', 'Annual Income'),
        ('adjusted_expenses', 'Annual Expenses'),
        ('adjusted_return_rate', 'Return Rate'),
        ('adjusted_inflation_rate', 'Inflation Rate')
    ]:
        row = {'Metric': label}
        for i, s in enumerate(scenarios_data):
            value = s['adjustments'].get(key, 'N/A')
            row[f'Scenario {i+1}'] = format_value(key, value)
        comparison_rows.append(row)

    # Row 6-9: Results
    for key, label in [
        ('final_savings', 'Final Savings'),
        ('final_net_worth', 'Final Net Worth'),
        ('years_solvent', 'Years Solvent'),
        ('health_score', 'Health Score')
    ]:
        row = {'Metric': label}
        for i, s in enumerate(scenarios_data):
            value = s.get('simulation_results', {}).get(key, 'N/A')
            row[f'Scenario {i+1}'] = format_value(key, value)
        comparison_rows.append(row)

    df = pd.DataFrame(comparison_rows)
    st.dataframe(df, use_container_width=True)

def format_value(key, value):
    """Format values based on type"""
    if value == 'N/A':
        return 'N/A'

    if 'rate' in key:
        return f"{value * 100:.1f}%"
    elif 'savings' in key or 'worth' in key or 'income' in key or 'expenses' in key:
        return f"${value:,.0f}"
    else:
        return str(value)
```

**Test:** Comparison table displays correctly
**Commit:** `"Step 4: Add side-by-side comparison table"`

---

### **Step 5: Polish & Navigation (30 min)**

**File:** `ui/navigation.py`

Add menu item:
```python
# After Healthcare Hub menu item
if st.sidebar.button("🎬 Scenario Studio", key="nav_scenario_studio", use_container_width=True):
    st.session_state.mode = "scenario_studio"
    st.rerun()
```

**File:** `ui/results_page.py` (CLEANUP)

Remove old comparison section, add link:
```python
st.info("💡 **Want to compare scenarios?** Try the new [Scenario Studio](#) for side-by-side comparisons!")
```

**Test:** Navigation works, old section removed
**Commit:** `"Step 5: Add navigation and clean up ANALYSIS mode"`

---

## 🔄 Rollback Plan

**If anything breaks:**
```bash
git checkout feature/scenario-comparison-enhanced
```

All Sub-Phase 2A functionality preserved and working.

---

## 📊 Testing Checklist

Before marking complete:

- [ ] Landing page loads without errors
- [ ] Scenario Studio card appears (4th card)
- [ ] Clicking card switches to Scenario Studio mode
- [ ] Scenario Studio page loads
- [ ] Multi-select shows saved comparisons
- [ ] Selecting 2+ scenarios shows comparison table
- [ ] Table displays adjustments correctly
- [ ] Table displays simulation results correctly
- [ ] Navigation menu item works
- [ ] Can return to ANALYSIS mode
- [ ] ANALYSIS mode no longer has old comparison section
- [ ] All existing features still work (INTAKE, ANALYSIS, Healthcare Hub)

---

## 🎉 Success Metrics

**Phase 2B Complete When:**
1. ✅ Scenario Studio is a standalone mode
2. ✅ Users can compare 2-4 scenarios side-by-side
3. ✅ Comparison table is clear and useful
4. ✅ ANALYSIS mode is cleaner (focused on single simulation)
5. ✅ Pattern established for future premium features

---

## 📝 Notes

- This builds on Sub-Phase 2A (save/load comparisons) ✅
- Uses disk cache storage (reliable) ✅
- Follows Healthcare Hub pattern (proven) ✅
- Separate mode = easier to monetize later
- Foundation for Phase 2C (What-If Presets)

---

**Created by:** Serge + Claude Code
**Ready to Build:** ✅
**Let's make this a masterpiece!** 🎨
