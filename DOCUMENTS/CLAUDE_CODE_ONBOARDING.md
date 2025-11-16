# CLAUDE CODE ONBOARDING - READ THIS FIRST
## How to Start a New Session on the Sidebar Architecture Project

**COPY AND PASTE THIS ENTIRE FILE to any new Claude Code session to restore context.**

---

## QUICK START (Copy this exact text to new Claude Code)

```
Hi Claude Code! I'm working on a retirement planning simulator and we're in the middle of a PARALLEL UI/UX ARCHITECTURE MIGRATION.

PLEASE READ THESE FILES FIRST (in this order):
1. DOCUMENTS/PARALLEL_UI_UX_UPGRADE_REPORT.md - Our master plan
2. DOCUMENTS/GIT_BRANCHING_GUIDE.md - How we're doing safe parallel development
3. GEMINI-Architecting a Modular Retirement Planning SaaS.txt - The architectural blueprint we're following

CURRENT STATUS:
- Phase 0 (Tests) = COMPLETED - 56 tests all passing
- Phase 1 (Sidebar Navigation) = [INSERT YOUR STATUS HERE]
- Production app = Running on master branch (DO NOT TOUCH)

MY REQUEST TODAY:
[INSERT WHAT YOU WANT TO WORK ON]

CRITICAL REMINDERS:
- All new work happens on feature/sidebar-architecture branch
- Never modify master branch
- Run tests after changes: python -m pytest tests/test_simulation_core.py -v
- Test suite is our safety net

Please confirm you've read the context files before proceeding.
```

---

## WHAT TO DO WHEN STARTING PHASE 1

When you're ready to start Phase 1 (after Sunday, November 22), paste this:

```
Hi Claude Code! I need you to start Phase 1 of our sidebar architecture migration.

PLEASE READ FIRST:
- DOCUMENTS/PARALLEL_UI_UX_UPGRADE_REPORT.md
- DOCUMENTS/GIT_BRANCHING_GUIDE.md

CURRENT STATUS:
- Phase 0 (Tests) = COMPLETED
- Phase 1 (Sidebar Navigation) = NOT STARTED

MY REQUEST:
Please create the Git feature branch for sidebar architecture:
1. Tag current master as v1.0-pre-sidebar
2. Create branch: feature/sidebar-architecture
3. Confirm we're on the new branch
4. Then start implementing the sidebar navigation shell

DO NOT touch master branch. All work on the feature branch only.
```

---

## WHAT TO DO IF BRANCH ALREADY EXISTS

If you've already created the branch in a previous session:

```
Hi Claude Code! Continuing Phase 1 of sidebar architecture migration.

PLEASE READ FIRST:
- DOCUMENTS/PARALLEL_UI_UX_UPGRADE_REPORT.md

CURRENT STATUS:
- Branch feature/sidebar-architecture already created
- Currently on Phase 1, Step: [INSERT WHAT YOU LAST DID]

MY REQUEST TODAY:
[DESCRIBE SPECIFIC TASK]

IMPORTANT:
- We're on feature/sidebar-architecture branch (not master)
- Run tests after changes: python -m pytest tests/test_simulation_core.py -v
```

---

## PROJECT QUICK FACTS

**Codebase:**
- 76 Python files, 57,000+ lines
- Streamlit-based retirement planning app
- Encrypted localStorage for user data
- Heavy use of st.session_state (100+ keys)

**Key Files:**
- `app.py` - Main entry point (762 lines)
- `simulation_core.py` - Core calculations (533 lines)
- `tests/test_simulation_core.py` - Safety net tests (56 tests)
- `intake_integrated.py` + `intake_review.py` - Data entry (2,427 lines)
- `ui/results_page.py` - Analysis dashboard (706 lines)

**Architecture Migration Goal:**
- FROM: Four-card dashboard navigation
- TO: Persistent left-hand sidebar navigation
- METHOD: Parallel development (production untouched)

**Phases:**
1. Sidebar Navigation Shell (current focus)
2. Healthcare Hub Migration
3. Scenario Studio 3-Panel Layout
4. Tax Optimizer Module (NEW)
5. Social Security Module (NEW)
6. Feature Gating System

---

## EMERGENCY COMMANDS

**Check which branch you're on:**
```bash
git branch
```

**Switch to production (if needed):**
```bash
git checkout master
```

**Switch to development:**
```bash
git checkout feature/sidebar-architecture
```

**Run safety net tests:**
```bash
python -m pytest tests/test_simulation_core.py -v
```

**See what files changed:**
```bash
git status
```

---

## WARNINGS FOR NEW CLAUDE CODE SESSIONS

**ALWAYS TELL CLAUDE CODE:**
- We're doing PARALLEL development
- Master branch is PRODUCTION - DO NOT MODIFY
- All work on feature/sidebar-architecture branch
- Session state key names must NOT change
- Run tests after code changes

**NEVER LET CLAUDE CODE:**
- Push to master branch
- Change st.session_state key names
- Delete existing functionality
- Skip the test suite
- Modify encryption or snapshot format

---

## HOW TO UPDATE THIS DOCUMENT

After each session, update the "CURRENT STATUS" section above with:
- Which phase you're on
- Which step within that phase
- Any blockers or issues
- What was completed

This document becomes your "memory" between sessions.

---

*Document created: November 15, 2025*
*Last updated: [UPDATE THIS DATE AFTER EACH SESSION]*
*Current Phase: 0 (Tests) - COMPLETED*
*Next Phase: 1 (Sidebar Navigation) - Ready to start after Nov 22*
