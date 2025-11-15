# 🚨 LEFTOVERS - MUST FIX BEFORE LAUNCH 🚨

**Created:** November 15, 2025
**Last Updated:** November 15, 2025
**Status:** 5 ITEMS PENDING

---

## ⚠️ EVERY SESSION: Review this list FIRST! ⚠️

These are NOT new features - they are **INCOMPLETE WORK** that makes the app feel unfinished.

---

## CRITICAL LEFTOVERS (User Experience Issues)

### 1. ❌ Show Existing Goals in INTAKE (30-60 min)
**Problem:** User saves goals, comes back to INTAKE, can't see or edit them
**Impact:** CONFUSING - "Where did my goals go?"
**Fix:** Load `goals_list` into form when page loads

### 2. ❌ Show Existing Custom Expenses in INTAKE (30-60 min)
**Problem:** User saves custom expenses, can't see or edit them later
**Impact:** CONFUSING - "I know I added HELP TO KIDS $1500/month but I can't see it"
**Fix:** Load `custom_expenses` into form when page loads

### 3. ❌ Comparison Table Disappears with 3+ Scenarios + BASE (1-2 hours)
**Problem:** Table shows for 1+BASE or 2 scenarios, but NOT 3+BASE
**Impact:** ANNOYING - Charts work but table is missing
**Fix:** Debug DataFrame building logic for 3+ scenarios

---

## ENHANCEMENT LEFTOVERS (Nice to Have)

### 4. ❌ Goal Year Ranges (2026-2030) (2-3 hours)
**Problem:** Must add 5 separate goals for "Travel 2026-2030"
**Impact:** TEDIOUS - User has to click 5 times for same recurring goal
**Fix:** Add "Repeat for years" option in goal form

### 5. ❌ Healthcare Hub - Full Medigap Comparison (10-15 hours)
**Problem:** Only MVP IRMAA calculator exists
**Impact:** INCOMPLETE - Users expect full Medicare plan comparison
**Fix:** Build complete plan comparison feature (BIG PROJECT)

---

## PRIORITY ORDER FOR CLEARING LEFTOVERS

**Quick Wins First (Clean up the mess):**
1. Show existing goals in INTAKE (~45 min) ⭐
2. Show existing custom expenses in INTAKE (~45 min) ⭐
3. Fix 3+ scenario comparison table (~1.5 hours)

**Then Enhancements:**
4. Goal year ranges (~2.5 hours)
5. Full Medigap (10-15 hours) - Maybe phase 2?

**ESTIMATED TOTAL:** 4-5 hours for items 1-4, then 10-15 for Medigap

---

## TRACKING PROGRESS

| Item | Status | Time Est | Assigned Session | Completed |
|------|--------|----------|------------------|-----------|
| Goals in INTAKE | ❌ PENDING | 45 min | | |
| Custom Expenses in INTAKE | ❌ PENDING | 45 min | | |
| 3+ Scenario Table | ❌ PENDING | 1.5 hr | | |
| Goal Year Ranges | ❌ PENDING | 2.5 hr | | |
| Full Medigap | ❌ PENDING | 10-15 hr | | |

---

## 🚨 NAGGING RULES 🚨

1. **EVERY SESSION** starts with: "What leftovers should we clear today?"
2. **Before new features**: Clear at least ONE leftover
3. **Friday rule**: Dedicate at least 2 hours to leftovers
4. **95% milestone**: ALL leftovers must be cleared before Supabase migration

---

## WHY THIS MATTERS

**Leftovers create:**
- User confusion
- Support requests
- Bad first impressions
- Technical debt
- Lost momentum

**Clean code = Happy users = Successful launch!**

---

*Review this file at the START of every session!*
*Check off items as they're completed!*
*Don't let leftovers pile up!*

🎯 **GOAL: Zero leftovers by 95% completion!** 🎯
