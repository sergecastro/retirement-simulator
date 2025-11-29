# TROUBLESHOOTING REPORT: Family Data Not Saving (Nov 28-29, 2025)

## Problem Summary
Family page data (Children, Inheritances, Goals) was not being saved when clicking NEXT to go to Review page. Data appeared in the UI but showed as empty (0 items) on the Review page and in Analysis.

## Duration
~14+ hours of debugging across Nov 28-29, 2025

## Root Cause
Between Nov 14 and Nov 27, the `show_family_page` function in `intake_review.py` was rewritten to use `st.data_editor` instead of individual input widgets.

### OLD Working Code (Nov 14 - commit ffc9652):
- Used individual `st.text_input`, `st.number_input`, `st.selectbox` widgets
- Each widget bound DIRECTLY to `st.session_state.temp_children[idx]["field"]`
- Data saved immediately on every keystroke
- "➕ Add Child" button with explicit `st.rerun()`
- Function was 453 lines

### BROKEN Code (Nov 27+):
- Used `st.data_editor` with `num_rows="dynamic"`
- Data converted via `edited_children.to_dict("records")`
- `st.data_editor` returned empty DataFrame even when data was visible in UI
- Debug showed: `added_rows: []` even after adding rows
- Function was 264 lines (shorter but broken)

## Why st.data_editor Failed
1. The widget displayed data visually but did NOT return it to Python
2. `edited_children.empty = True` even when rows were visible on screen
3. The widget's internal state `{'edited_rows': {}, 'added_rows': [], 'deleted_rows': []}` stayed empty
4. Root cause likely: interaction between st.data_editor and other session_state manipulations

## The Fix
Restored the ORIGINAL `show_family_page` function from commit ffc9652 (Nov 14, 2025) which uses individual input widgets instead of st.data_editor.

### Files Changed:
- `intake_review.py` - Replaced lines 416-679 with original function (now lines 416-868)

### Commits:
- `7c81517` - "Restore working show_family_page with individual input widgets"
- Backup branch: `backup-before-family-restore-nov29`

## Verification Steps
1. Start app: `streamlit run app.py`
2. Navigate through Pages 1-6
3. On Page 7 (Family): Click "➕ Add Child", fill in fields
4. Click NEXT to Page 8 (Review)
5. Verify child data appears in Review
6. Continue to Analysis - verify data persists

## Lessons Learned
1. **Don't replace working code with "cleaner" alternatives** - The st.data_editor looked more modern but was unreliable
2. **Individual input widgets are more reliable** - Direct binding to session_state works consistently
3. **Test thoroughly after refactoring** - The broken code was shorter but didn't work
4. **Keep backups and commit frequently** - We had the working code in git history
5. **Compare with ORIGINAL working code** - Not just recent commits, go back to launch version

## Debug Prints Added (Can Be Removed Later)
- Lines with `[DF DEBUG]` - DataFrame creation
- Lines with `[FORM DEBUG]` - data_editor output
- Lines with `[WIDGET DEBUG]` - widget state
- Lines with `[PAGE7 DEBUG]` - NEXT button execution
- Lines with `[HUNT DEBUG]` - hunt_for_data searches

## Related Fixes in Same Session
1. Widget key cleanup disabled (was deleting user data)
2. Blocklist approach for NEXT button save (prevents widget key errors)
3. localStorage null checks across 5 files

## Prevention
- NEVER replace individual input widgets with st.data_editor for critical data entry
- Always compare with launch/working code when debugging
- Test data persistence end-to-end after any UI changes
