# 🗺️ ForeCash App Flow Diagram

**Visual guide to understand the application flow**

---

## 🔄 SESSION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                         APP STARTS                              │
│                         (app.py main())                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Authentication │
                    │ (config/auth)  │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Disclaimer    │
                    │ Acknowledgment │
                    └────────┬───────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Check Session State:  │
                 │ current_mode == None? │
                 └───────────┬───────────┘
                             │
                ┌────────────┴────────────┐
                │ YES                     │ NO
                ▼                         ▼
        ┌───────────────┐         ┌──────────────┐
        │ LANDING PAGE  │         │ MODE ALREADY │
        │ (Force Show)  │         │   SELECTED   │
        │   st.stop()   │         └──────┬───────┘
        └───────┬───────┘                │
                │                        │
                │ User clicks button     │
                │ Sets current_mode      │
                │ st.rerun()             │
                └────────────┬───────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌───────────────┐         ┌──────────────┐
        │  INTAKE MODE  │         │ ANALYSIS     │
        │               │         │ MODE         │
        └───────┬───────┘         └──────────────┘
                │
                │ Complete & Save
                │ (🔴 BUG HERE!)
                │
                ▼
        ┌───────────────┐
        │ Should go to  │
        │ ANALYSIS MODE │
        │ (but loops!)  │
        └───────────────┘
```

---

## 📋 LANDING PAGE FLOW

```
┌──────────────────────────────────────────────────────────┐
│              🏠 LANDING PAGE                             │
│                                                          │
│  Welcome to ForeCash!                                   │
│                                                          │
│  ┌────────────────────┐  ┌────────────────────┐        │
│  │  📝 INTAKE MODE    │  │ 📊 ANALYSIS MODE   │        │
│  │                    │  │                    │        │
│  │  [START INTAKE]    │  │  [GO TO ANALYSIS]  │        │
│  │        ↓           │  │        ↓           │        │
│  │  Sets:             │  │  Sets:             │        │
│  │  current_mode      │  │  current_mode      │        │
│  │    = "INTAKE"      │  │    = "Analysis"    │        │
│  │  mode_selected     │  │  mode_selected     │        │
│  │    = True          │  │    = True          │        │
│  │  st.rerun()        │  │  st.rerun()        │        │
│  └────────────────────┘  └────────────────────┘        │
└──────────────────────────────────────────────────────────┘
```

---

## 🔧 INTAKE MODE FLOW

```
┌──────────────────────────────────────────────────────────┐
│              📝 INTAKE QUESTIONNAIRE                     │
│                                                          │
│  Step 1: Profile      → st.session_state.step = 1       │
│  Step 2: Demographics → st.session_state.step = 2       │
│  Step 3: Financials   → st.session_state.step = 3       │
│  ...                                                     │
│  Step 8: Review       → st.session_state.step = 8       │
│                                                          │
│  ┌────────────────────────────────────────┐             │
│  │  [COMPLETE AND SAVE] ← 🔴 BUG HERE    │             │
│  └────────────────────────────────────────┘             │
│                    ↓                                     │
│         SHOULD SET (but doesn't?):                      │
│         • intake_completed = True                       │
│         • current_mode = "Analysis"                     │
│         • mode_selected = True                          │
│         • st.rerun()                                    │
│                    ↓                                     │
│         🔴 INSTEAD: Loops back to Step 8               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 ANALYSIS MODE FLOW

```
┌──────────────────────────────────────────────────────────┐
│              📊 ANALYSIS MODE                            │
│                                                          │
│  Sidebar:                     Main Area:                │
│  ┌──────────────────┐        ┌──────────────────┐      │
│  │ Quick Mode Switch│        │ Retirement       │      │
│  │ ○ INTAKE         │        │ Analysis Results │      │
│  │ ● Analysis       │        │                  │      │
│  ├──────────────────┤        │ • Charts         │      │
│  │ Feature Toggles  │        │ • Projections    │      │
│  │ ☑ Medicare       │        │ • Monte Carlo    │      │
│  │ ☑ AI Advisor     │        │ • Recommendations│      │
│  │ ☑ IRMAA Calc     │        │                  │      │
│  ├──────────────────┤        └──────────────────┘      │
│  │ User Inputs      │                                   │
│  │ Financial Data   │                                   │
│  │ Family Events    │                                   │
│  │ Sim Parameters   │                                   │
│  ├──────────────────┤                                   │
│  │ Scenario Mgmt    │                                   │
│  └──────────────────┘                                   │
└──────────────────────────────────────────────────────────┘
```

---

## 🗂️ MODULE STRUCTURE

```
app.py (MAIN ENTRY POINT)
│
├─ config/
│  ├─ settings.py     → initialize_app(), show_footer()
│  └─ auth.py         → require_authentication(), is_trusted_user()
│
├─ ui/
│  ├─ navigation.py   → show_feature_toggles(), show_sidebar_*()
│  └─ results_page.py → show_results_page()
│
├─ pages/
│  ├─ user_inputs.py      → collect_user_data()
│  ├─ financial_inputs.py → collect_financial_data()
│  └─ family_inputs.py    → collect_family_events()
│
├─ intake_integrated.py   → show_intake_questionnaire() 🔴
├─ data_manager_cloud.py  → manage_scenarios()
└─ disclaimers.py         → require_disclaimer_acknowledgment()
```

---

## 🔑 SESSION STATE VARIABLES

```python
# Mode Selection
st.session_state.mode_selected      # Boolean: Has user chosen a mode?
st.session_state.current_mode       # String: "INTAKE" | "Analysis" | None

# INTAKE Status
st.session_state.intake_completed   # Boolean: Just finished INTAKE?

# Feature Toggles (Analysis mode)
st.session_state.show_medicare      # Boolean: Show Medicare calculator?
st.session_state.show_ai_advisor    # Boolean: Show AI advisor?
st.session_state.show_irmaa         # Boolean: Show IRMAA calculator?
```

---

## 🐛 THE BUG EXPLAINED

**What SHOULD happen:**
```
User on Step 8 → Clicks "Complete and Save"
  ↓
Save data to SHARED/intake_payload.json
  ↓
Set session state:
  - intake_completed = True
  - current_mode = "Analysis"
  - mode_selected = True
  ↓
Call st.rerun()
  ↓
App re-renders → Sees current_mode = "Analysis" → Shows Analysis mode ✅
```

**What ACTUALLY happens:**
```
User on Step 8 → Clicks "Complete and Save"
  ↓
??? (Session state not set correctly?)
  ↓
Page blinks
  ↓
Back to Step 8 (LOOP!) 🔴
```

**WHERE TO FIX:**
- File: `intake_integrated.py`
- Look for: "Complete and Save" button
- Ensure: All session state variables are set + st.rerun() is called

---

## 📍 CODE LOCATIONS

| Function | File | Lines | Purpose |
|----------|------|-------|---------|
| `main()` | app.py | 47-124 | Main entry point |
| Landing page force | app.py | 63-83 | Prevents bypass |
| `show_mode_selection_landing_page()` | app.py | 130-246 | Welcome screen |
| `show_intake_mode()` | app.py | 252-270 | INTAKE display |
| `show_analysis_mode()` | app.py | 277-325 | Analysis display |
| `show_intake_questionnaire()` | intake_integrated.py | ??? | **FIX HERE** 🔴 |

---

**Use this diagram to understand the flow when debugging!**
