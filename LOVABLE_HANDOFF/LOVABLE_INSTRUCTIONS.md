# ForeCash UI Branding Project

## Brand Identity
- **Name:** ForeCash
- **Domain:** forecash.ai
- **Tagline:** "See Your Financial Future Clearly."

## Colors (CRITICAL - Use These Exactly)
```css
--fc-navy: #003D5B      /* Primary brand color */
--fc-gold: #E8B541      /* Accent/Logo gold */
--fc-light: #E8E6E0     /* Backgrounds */
--fc-gray: #555B66      /* Text/Secondary */
```

## Typography
- **Headlines:** Steibold (bold, confident)
- **Body:** Source Sans Pro (clean, professional)

## Files to Style (Priority Order)

### 1. app.py (HIGHEST PRIORITY)
**Target:** `show_mode_selection_landing_page()` function (lines ~115-230)
**What to brand:**
- Replace welcome box blue (#f0f8ff) with ForeCash light (#E8E6E0)
- Change button colors to ForeCash navy (#003D5B)
- Add ForeCash gold (#E8B541) accents to cards
- Replace green (#d4edda) with gold gradient
- Keep HTML structure, just update colors

### 2. config_settings.py (HIGH PRIORITY)
**Target:** `CUSTOM_CSS` variable (lines ~20-85)
**What to brand:**
- Replace all color values with ForeCash palette
- Update button styles to navy/gold theme
- Add logo styling if needed

### 3. intake_integrated.py (MEDIUM PRIORITY)
**What to brand:**
- Section headers → Navy (#003D5B)
- Progress indicators → Gold (#E8B541)
- Input backgrounds → Light gray (#E8E6E0)
- Success messages → Navy/Gold theme

### 4. Other files (LOWER PRIORITY)
- ui_navigation.py
- ui_results_page.py
- healthcare files

## Logo Integration
Use circular horizon logo:
- Gold top half (#E8B541)
- Navy bottom half (#003D5B)
- White trend line overlay

## Design Goals
✅ Professional financial services aesthetic
✅ Navy + Gold = Trust + Prosperity
✅ Clean, calm, confident
✅ Accessible (WCAG AA contrast)

## What NOT to Change
❌ Python function logic
❌ Session state variables
❌ Import statements
❌ Function names
❌ Data processing code

## Output Format
Return styled versions of files with:
1. ForeCash color palette applied
2. Typography updated (if Streamlit allows)
3. Professional financial UI aesthetic
4. All functionality preserved

---

## Note on Brand Files
Brand asset files (forecash_brand_board.html, forecash-colors.css, forecash-design-tokens.json, forecash_figma_brand_kit.json) were not found in the source directory. Please use the color specifications and typography guidelines above as the definitive brand guide.
