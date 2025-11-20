# Plausible Analytics Setup & Troubleshooting
**Family Forecast - Analytics Configuration Guide**

Last Updated: November 20, 2025
Status: ✅ **WORKING - Verified & Tracking**

---

## 🎯 CURRENT CONFIGURATION (WORKING!)

### **Service Details**
- **Analytics Provider:** Plausible Analytics (plausible.io)
- **Account Type:** Plausible Cloud (hosted by Plausible)
- **Domain Being Tracked:** `familyforecast.ai`
- **Installation Method:** CSS injection via Streamlit (proven method)
- **Status:** ✅ Verified by Plausible on Nov 20, 2025

### **Script Configuration**
- **Script URL:** `https://plausible.io/js/script.js` (standard script)
- **Script Type:** Standard (simple, reliable)
- **Domain Attribute:** `data-domain="familyforecast.ai"`
- **Loading Method:** `defer` (proper sequential loading)

### **Location in Code**
- **File:** `config/settings.py`
- **Variable:** `CUSTOM_CSS` (lines 33-36)
- **Injection Method:** `st.markdown(CUSTOM_CSS, unsafe_allow_html=True)`
- **Called From:** `apply_custom_css()` in `initialize_app()`
- **Execution Timing:** Early in page lifecycle (before main content)

---

## 🔧 TECHNICAL IMPLEMENTATION

### **✅ WORKING CODE** (as of Nov 20, 2025 - 8:09 AM)

**File: `config/settings.py`**

```python
CUSTOM_CSS = """
<!-- Plausible Analytics -->
<script defer data-domain="familyforecast.ai" src="https://plausible.io/js/script.js"></script>

<style>
    /* Your CSS styles here... */
</style>
"""

def apply_custom_css():
    """Apply custom CSS styling to the app"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
```

**File: `app.py`**

```python
from config.settings import initialize_app

def main():
    # Initialize app (includes CSS + Plausible injection)
    initialize_app()  # ← This applies CUSTOM_CSS with Plausible script

    # Rest of your app code...
```

### **Why This Implementation Works:**

1. **Early Execution**
   - `initialize_app()` is called at the very start of `main()`
   - Script loads before any page content
   - Ensures Plausible is ready to track immediately

2. **Main Page HTML (Not Iframe)**
   - `st.markdown()` with `unsafe_allow_html=True` injects into main page
   - NOT in an iframe (unlike `st.components.v1.html()`)
   - Plausible verification can detect it

3. **Same Method as CSS**
   - Uses identical injection method as your working CSS
   - Proven reliable in production
   - No experimental techniques

4. **Simple & Standard**
   - Official Plausible one-liner (from their docs)
   - No custom JavaScript
   - No dynamic DOM manipulation
   - Can't fail due to complexity

---

## 🐛 TROUBLESHOOTING HISTORY (Nov 20, 2025)

### **What We Tried (And Why Each Failed):**

#### **Attempt 1: Missing `data-domain` Attribute** ❌
**Problem:**
- Custom proxy script loaded: `pa-3npHKPHg2kmQuG1mgMbMw.js`
- BUT: Missing `data-domain="familyforecast.ai"` attribute
- Script loaded but didn't know which site to track

**Why It Failed:**
- Plausible requires `data-domain` to identify the website
- Without it, script loads but does nothing

**Commit:** `cb07443`
**Lesson:** Always include `data-domain` attribute!

---

#### **Attempt 2: Custom Proxy Script with `data-domain`** ❌
**Problem:**
- Added `data-domain` attribute ✅
- But used custom proxy: `pa-3npHKPHg2kmQuG1mgMbMw.js` ❌
- Plausible verification couldn't detect it

**Why It Failed:**
- Verification tool specifically looks for standard `script.js`
- Custom proxy works for tracking but fails verification
- Proxy is intended to bypass ad blockers (not needed yet)

**Commit:** `cb07443`
**Lesson:** Use standard `script.js` for initial setup and verification!

---

#### **Attempt 3: Standard Script with Dynamic Injection** ❌
**Problem:**
- Switched to standard: `https://plausible.io/js/script.js` ✅
- Used dynamic JavaScript to append to `document.head` ❌
- Complex injection logic ❌

**Code Attempted:**
```javascript
var script = document.createElement('script');
script.defer = true;
script.setAttribute('data-domain', 'familyforecast.ai');
script.src = 'https://plausible.io/js/script.js';
document.head.appendChild(script);
```

**Why It Failed:**
- Streamlit's security might have blocked dynamic injection
- Timing issues (script might execute after page render)
- Overly complex for no benefit

**Commit:** `3b6d7fa`
**Lesson:** Keep it simple - use direct script tag!

---

#### **Attempt 4: Simplified Script via `st.markdown()`** ❌
**Problem:**
- Simplified to one-line: `<script defer data-domain="familyforecast.ai" src="..."></script>` ✅
- Injected via: `st.markdown(ANALYTICS_TRACKING_CODE, unsafe_allow_html=True)` ❌
- Called from `main()` function ❌

**Why It Failed:**
- Executed TOO LATE in page lifecycle
- `main()` runs after page structure is established
- Plausible verification couldn't detect delayed injection

**Commit:** `dd41763`
**Lesson:** Script must load EARLY (during page setup)!

---

#### **Attempt 5: Simple Script via `st.components.v1.html()`** ❌
**Problem:**
- One-line script: `<script defer data-domain="familyforecast.ai" src="..."></script>` ✅
- Changed injection to: `st.components.v1.html(ANALYTICS_TRACKING_CODE, height=0)` ❌

**Why It Failed:**
- **ROOT CAUSE IDENTIFIED!**
- `st.components.v1.html()` creates an **IFRAME**
- Plausible script loaded INSIDE iframe ❌
- Plausible verification checks MAIN page, NOT iframes ❌
- Script invisible to verification tool

**Commit:** `dd41763`
**Critical Discovery:** NEVER use `st.components.v1.html()` for analytics scripts!

---

#### **✅ Attempt 6: Script in CUSTOM_CSS via `st.markdown()`** ✅
**Solution:**
- One-line script: `<script defer data-domain="familyforecast.ai" src="..."></script>` ✅
- Added to: `CUSTOM_CSS` variable in `config/settings.py` ✅
- Injected via: `st.markdown(CUSTOM_CSS, unsafe_allow_html=True)` ✅
- Called from: `initialize_app()` (early in lifecycle) ✅

**Why It Works:**
1. ✅ Same method as your CSS (proven reliable)
2. ✅ Loads EARLY (before main content)
3. ✅ Injects into MAIN page HTML (not iframe)
4. ✅ Plausible verification can detect it
5. ✅ Simple one-line implementation

**Commit:** `a307eed`
**Result:** 🎉 **VERIFIED BY PLAUSIBLE! TRACKING WORKS!**

---

## 🔍 VERIFICATION CHECKLIST

### **Method 1: Plausible Dashboard** ✅
1. Go to https://plausible.io/familyforecast.ai
2. Click **"⚙️ Settings"** → **"Verify Installation"**
3. Should see: ✅ **"We've detected Plausible on your site!"**
4. **Status as of Nov 20, 2025:** ✅ VERIFIED!

### **Method 2: Real-Time Visitor Count** ✅
1. Go to Plausible dashboard
2. Check "Current visitors" at top
3. Visit your site in another tab
4. Should see: **"1 current visitor"** (yourself!)
5. **Status as of Nov 20, 2025:** ✅ WORKING!

### **Method 3: Browser DevTools - Elements** ✅
1. Visit https://familyforecast.ai
2. Press **F12** (open DevTools)
3. **Elements tab** → Search for `plausible`
4. Should see: `<script defer data-domain="familyforecast.ai" src="https://plausible.io/js/script.js"></script>`
5. **Location:** In main page HTML (not in iframe)

### **Method 4: Browser DevTools - Network** ✅
1. DevTools → **Network tab**
2. Reload page
3. Filter by: `script.js`
4. Should see:
   - Request to `https://plausible.io/js/script.js` → Status **200** ✅
   - Request to `https://plausible.io/api/event` → Status **202** ✅ (pageview tracked!)

### **Method 5: Browser DevTools - Console** ✅
1. DevTools → **Console tab**
2. Type: `window.plausible`
3. Should return: `function() { ... }` (NOT `undefined`)
4. Try: `window.plausible('test-event')`
5. Check Plausible dashboard - should see event within 60 seconds

---

## 🐛 COMMON ISSUES & SOLUTIONS

### **Issue 1: "We couldn't detect Plausible on your site"**

**Symptoms:**
- Plausible verification fails
- No visitor data appearing
- Real-time visitors shows 0

**Possible Causes & Solutions:**

**A) Script Not in Main Page HTML** ❌
- **Check:** DevTools → Elements → Search for `plausible`
- **If NOT found:** Script might be in iframe or not loading at all
- **Solution:** Ensure script is in `CUSTOM_CSS` (config/settings.py)
- **Verify:** Script should appear in main `<body>` or near `<style>` tags

**B) Script Loading in Iframe** ❌
- **Check:** DevTools → Elements → Look for `<iframe>` tags
- **If found:** Check inside iframe for Plausible script
- **Problem:** Verification can't see inside iframes
- **Solution:** NEVER use `st.components.v1.html()` for Plausible!
- **Use Instead:** `st.markdown(CUSTOM_CSS, unsafe_allow_html=True)`

**C) Missing `data-domain` Attribute** ❌
- **Check:** Find Plausible script tag in Elements
- **Look for:** `data-domain="familyforecast.ai"` attribute
- **If missing:** Script loads but doesn't track
- **Solution:** Add attribute to script tag in CUSTOM_CSS

**D) Wrong Script URL** ❌
- **Check:** Script src should be `https://plausible.io/js/script.js`
- **NOT:** Custom proxy like `pa-3npHKPHg2kmQuG1mgMbMw.js` (fails verification)
- **Solution:** Use standard script.js for initial setup

**E) Render Hasn't Deployed** ⏱️
- **Check:** Render dashboard for latest commit hash
- **Should match:** `a307eed` (or later)
- **If not:** Wait for deploy or manually trigger
- **Time needed:** 3-5 minutes after push

---

### **Issue 2: Script Not Loading at All**

**Symptoms:**
- DevTools → Network shows no request to plausible.io
- `window.plausible` is `undefined`
- No script tag in page source

**Diagnosis Steps:**

**Step 1: Check File Content**
```bash
# Verify CUSTOM_CSS has Plausible script
grep -A 2 "Plausible Analytics" config/settings.py

# Should output:
# <!-- Plausible Analytics -->
# <script defer data-domain="familyforecast.ai" src="https://plausible.io/js/script.js"></script>
```

**Step 2: Check Git Commit**
```bash
# Verify latest commit includes the fix
git log --oneline -1

# Should show: a307eed or later
```

**Step 3: Check Render Deployment**
- Render dashboard → Check current commit
- Should be: `a307eed` or later
- If older: Manually trigger deploy

**Step 4: Clear All Caches**
- Browser: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Cloudflare: If using CDN, purge cache
- Browser: Clear site data (DevTools → Application → Clear storage)

**Step 5: Check Console Errors**
- DevTools → Console tab
- Look for errors mentioning "plausible" or "script"
- Check for CSP (Content Security Policy) errors

---

### **Issue 3: Tracking Works Locally But Not in Production**

**Symptoms:**
- Works on `localhost` ✅
- Fails on `familyforecast.ai` ❌

**Possible Causes:**

**A) Domain Mismatch**
- **Problem:** `data-domain` doesn't match production domain
- **Check:** Script should have `data-domain="familyforecast.ai"`
- **NOT:** `data-domain="localhost"` or `data-domain="www.familyforecast.ai"`
- **Solution:** Ensure exact match with your Plausible dashboard domain

**B) Different Code Deployed**
- **Problem:** Local changes not pushed or not deployed
- **Check:** Compare local file with GitHub, GitHub with Render
- **Solution:** Ensure changes are committed, pushed, and deployed

**C) Browser Extension Blocking**
- **Problem:** Ad blocker or privacy extension blocks plausible.io
- **Test:** Try in Incognito/Private mode (disables extensions)
- **Solution:** Whitelist plausible.io or test without extensions

---

### **Issue 4: Double Counting / Multiple Pageviews**

**Symptoms:**
- One visit shows as 2-3 pageviews
- Duplicate events in dashboard

**Root Cause:**
- Script injected multiple times (Streamlit re-renders)

**Solution:**
- Current implementation prevents this (script in CUSTOM_CSS, loaded once)
- If happens: Check for multiple `<script>` tags with same src in DevTools

---

### **Issue 5: Zero Historical Visitors**

**Symptoms:**
- Verification passes ✅
- Real-time tracking works ✅
- But "Last 30 days" shows 0 visitors

**Explanation:**
- **Normal!** Plausible only tracks AFTER installation
- No historical data before Nov 20, 2025 (when we fixed it)
- Past visitors NOT counted (Plausible doesn't track retroactively)

**What to Expect:**
- **Day 1 (Nov 20):** Shows today's visitors only
- **Day 2 (Nov 21):** Shows 2 days of data
- **Day 30 (Dec 20):** Shows full 30-day history

**Current Status (Nov 20, 2025):**
- ✅ Tracking started today
- ✅ Real-time works (shows 1 current visitor)
- ✅ Historical data will accumulate going forward

---

## 📊 WHAT DATA PLAUSIBLE TRACKS

### **Automatically Tracked (No Code Needed)**
- ✅ **Pageviews** - Every page load
- ✅ **Unique visitors** - Counted by IP + User Agent hash (privacy-friendly)
- ✅ **Bounce rate** - Percentage leaving after one page
- ✅ **Visit duration** - How long visitors stay
- ✅ **Referrer sources** - Where visitors come from (Google, Facebook, direct, etc.)
- ✅ **Countries** - Visitor locations (by IP geolocation)
- ✅ **Devices** - Desktop, Mobile, Tablet breakdown
- ✅ **Operating Systems** - Windows, Mac, Linux, iOS, Android
- ✅ **Browsers** - Chrome, Safari, Firefox, Edge, etc.
- ✅ **Pages** - Which URLs are visited most

### **Custom Events (Requires Code)**

To track custom events (button clicks, form submissions, etc.):

```javascript
// From JavaScript:
window.plausible('Download', {props: {method: 'PDF', filename: 'report.pdf'}});
window.plausible('Signup', {props: {plan: 'Free'}});
window.plausible('Button_Click', {props: {button: 'Save_Snapshot'}});
```

**From Streamlit (Python):**
```python
# Add to any button callback:
st.markdown("""
<script>
if (window.plausible) {
    window.plausible('Button_Click', {props: {button: 'Historical_Tracking'}});
}
</script>
""", unsafe_allow_html=True)
```

**View Custom Events:**
- Plausible Dashboard → Settings → Goals
- Click "Add Goal" → "Custom Event"
- Enter event name (e.g., "Download", "Signup")

---

## 🔐 PRIVACY FEATURES (Why We Use Plausible)

### **What Plausible DOESN'T Do:**
- ❌ **No cookies** - GDPR/CCPA compliant by default
- ❌ **No personal data** - Completely anonymized
- ❌ **No cross-site tracking** - Only tracks your domain
- ❌ **No data selling** - You own 100% of your data
- ❌ **No persistent identifiers** - Can't track individuals across sessions

### **What This Means:**
- ✅ **No consent banners needed** - Privacy-first design
- ✅ **GDPR compliant** - Out of the box
- ✅ **Lightweight** - Script is < 1KB (vs Google Analytics 45KB)
- ✅ **Fast** - Doesn't slow down your site
- ✅ **Transparent** - Open source, auditable code

---

## 🚨 EMERGENCY TROUBLESHOOTING WORKFLOW

### **If Tracking Suddenly Stops Working:**

**Step 1: Check Plausible Service Status** ⏱️ *30 seconds*
- Visit: https://plausible.io/status
- Verify: All systems operational
- If down: Wait for Plausible to fix (nothing you can do)

**Step 2: Verify Script Still in Page** ⏱️ *1 minute*
```bash
# Option A: Check live site
# Visit familyforecast.ai → F12 → Elements → Search "plausible"

# Option B: Check code
grep -A 2 "Plausible Analytics" config/settings.py
```
- **If missing:** Someone removed it (restore from git)
- **If present:** Continue to Step 3

**Step 3: Check Network Request** ⏱️ *1 minute*
- DevTools → Network tab → Reload page
- Filter: `script.js`
- **Status 200:** Script loading ✅ (continue to Step 4)
- **Status 404:** Script URL broken ❌ (fix URL)
- **No request:** Script tag not in page ❌ (back to Step 2)

**Step 4: Check Browser Console** ⏱️ *1 minute*
```javascript
window.plausible  // Should return function
```
- **Returns function:** Script loaded ✅ (continue to Step 5)
- **Returns undefined:** Script failed to load ❌ (check for CSP errors)

**Step 5: Test Manual Event** ⏱️ *2 minutes*
```javascript
// In console:
window.plausible('test-event');
```
- Check Plausible dashboard after 60 seconds
- **Event appears:** Tracking works! ✅ (false alarm)
- **No event:** Script not communicating ❌ (continue to Step 6)

**Step 6: Check Recent Deployments** ⏱️ *2 minutes*
```bash
# Check recent commits affecting settings.py
git log --oneline -10 -- config/settings.py

# Look for changes to CUSTOM_CSS
git diff HEAD~5 config/settings.py
```
- **CUSTOM_CSS changed:** Revert bad changes
- **No changes:** Continue to Step 7

**Step 7: Contact Plausible Support** ⏱️ *varies*
- Email: hello@plausible.io
- Provide:
  - Domain: familyforecast.ai
  - Issue: "Verification passed, script loads, but events not tracking"
  - DevTools screenshots (Network tab, Console)
  - Typically respond within 24 hours

---

## 📝 COMPLETE CHANGE HISTORY

### **November 20, 2025 - 8:09 AM - ✅ FINAL FIX (WORKING!)**
**Commit:** `a307eed`
**Change:** Moved Plausible script to `CUSTOM_CSS` in `config/settings.py`
**Method:** Inject via `st.markdown(CUSTOM_CSS, unsafe_allow_html=True)` in `initialize_app()`
**Result:** ✅ Verification passed! Real-time tracking working!
**Root Cause:** Previous methods used iframe or loaded too late in page lifecycle
**Why This Works:** Same method as CSS (proven), loads early, main page HTML

---

### **November 20, 2025 - 7:59 AM - Attempt 5 (Failed)**
**Commit:** `dd41763`
**Change:** Simplified to one-line script, used `st.components.v1.html()`
**Result:** ❌ Verification failed
**Root Cause:** `st.components.v1.html()` creates iframe - Plausible can't detect scripts inside iframes
**Lesson:** Never use `st.components.v1.html()` for analytics scripts!

---

### **November 20, 2025 - 7:47 AM - Attempt 4 (Failed)**
**Commit:** `dd41763`
**Change:** Simplified to one-line script, kept `st.markdown()`
**Result:** ❌ Verification failed
**Root Cause:** Script loaded too late in page lifecycle (from `main()` function)
**Lesson:** Analytics must load EARLY (during page setup, not main content)

---

### **November 20, 2025 - 7:38 AM - Attempt 3 (Failed)**
**Commit:** `3b6d7fa`
**Change:** Switched to standard `script.js`, added `data-domain` attribute
**Result:** ❌ Verification failed
**Root Cause:** Complex dynamic JavaScript injection - Streamlit might have blocked it
**Lesson:** Keep implementation simple - direct script tag is best

---

### **November 20, 2025 - 7:23 AM - Attempt 2 (Failed)**
**Commit:** `cb07443`
**Change:** Added `data-domain="familyforecast.ai"` attribute to custom proxy script
**Result:** ❌ Verification failed
**Root Cause:** Custom proxy script not recognized by Plausible verification tool
**Lesson:** Use standard `script.js` for initial setup and verification

---

### **November 20, 2025 - 7:10 AM - Attempt 1 (Failed)**
**Discovery:** Custom proxy script (`pa-3npHKPHg2kmQuG1mgMbMw.js`) was loading but missing `data-domain` attribute
**Result:** ❌ Script loaded but didn't track anything
**Lesson:** `data-domain` attribute is CRITICAL - script won't track without it

---

### **November 17, 2025 - FIX: Inject script into HEAD**
**Commit:** `7ec9ca5`
**Change:** Dynamic JavaScript to append script to `document.head`
**Result:** ❌ Partial - script loaded but verification failed
**Note:** This was before Nov 20 debugging session

---

### **November 17, 2025 - LAUNCH: Activate Plausible**
**Commit:** `3bc244c`
**Change:** Initial Plausible setup with custom proxy script
**Result:** ❌ Incomplete - missing critical `data-domain` attribute
**Note:** This was the starting point before Nov 20 fixes

---

## 🔗 USEFUL LINKS

- **Plausible Dashboard:** https://plausible.io/familyforecast.ai
- **Plausible Documentation:** https://plausible.io/docs
- **Installation Guide:** https://plausible.io/docs/plausible-script
- **Custom Events:** https://plausible.io/docs/custom-event-goals
- **Service Status:** https://plausible.io/status
- **Support Email:** hello@plausible.io
- **GitHub Issues:** https://github.com/plausible/analytics/issues

---

## 💡 TIPS FOR MARKETING

### **Using Analytics Data:**

**1. Track Campaign Success:**
```
# Add UTM parameters to your marketing links:
https://familyforecast.ai?utm_source=reddit&utm_campaign=launch&utm_medium=post

# View in Plausible:
Dashboard → Sources → See which campaigns drive traffic
```

**2. Identify Popular Pages:**
- Dashboard → Top Pages
- Focus marketing on features users engage with most
- If "Historical Tracking" gets lots of views → promote that feature!

**3. Understand Your Audience:**
- Dashboard → Locations → Target ads to those countries
- Dashboard → Devices → Optimize for desktop vs mobile
- Dashboard → Browsers → Ensure compatibility with top browsers

**4. Monitor Referrals:**
- Dashboard → Referrers
- See which marketing channels work best
- Double down on what's working, stop what's not

**5. Set Goals & Track Conversions:**
```
# Plausible → Settings → Goals → Add Goal
# Track important actions:
- Signups
- Snapshot saves
- Report downloads
- Button clicks
```

---

## ✅ CURRENT STATUS SUMMARY

**As of November 20, 2025 - 8:15 AM:**

### **Working:**
- ✅ Plausible installed and verified
- ✅ Script loading correctly in main page HTML
- ✅ Real-time tracking active (1 current visitor = you!)
- ✅ `data-domain` attribute present and correct
- ✅ Standard `script.js` (reliable, verifiable)
- ✅ Early execution (via `initialize_app()`)
- ✅ Privacy-compliant (no cookies, GDPR friendly)

### **Expected Behavior:**
- ✅ New visitors will be tracked immediately
- ✅ Pageviews accumulating going forward
- ✅ Historical data starting from today (Nov 20, 2025)
- ✅ Zero historical data before today (correct - wasn't tracking before)
- ✅ Real-time dashboard updates within 60 seconds

### **Next Steps:**
1. **Monitor for 24 hours** - Ensure consistent tracking
2. **Check tomorrow** - Verify historical data accumulating
3. **Share with team** - Start analyzing visitor patterns
4. **Set up goals** - Track important user actions
5. **Add to monitoring** - Check Plausible weekly

---

## 🎉 LESSONS LEARNED

### **Top 3 Critical Lessons:**

**1. iframe = Invisible to Verification** 🔴
- **Never** use `st.components.v1.html()` for analytics scripts
- Plausible (and most analytics tools) can't detect scripts inside iframes
- **Always** use `st.markdown()` with `unsafe_allow_html=True`

**2. Timing is Everything** ⏰
- Analytics scripts must load EARLY in page lifecycle
- Loading from `main()` is too late
- **Always** inject during app initialization (e.g., `initialize_app()`)

**3. Keep It Simple** 💡
- Complex = More ways to fail
- One-line script tag > Dynamic JavaScript injection
- Standard script > Custom proxy (for initial setup)
- **Always** start with simplest implementation

### **Debugging Methodology:**

**What Worked:**
1. ✅ Systematic testing (eliminate one variable at a time)
2. ✅ Check actual live site (not just local)
3. ✅ Use DevTools extensively (Elements, Network, Console)
4. ✅ Test in production after EVERY deploy
5. ✅ Hard refresh (clear cache) before testing

**What Didn't Work:**
1. ❌ Assuming deploy = instant live (takes 3-5 minutes)
2. ❌ Testing without hard refresh (cached old version)
3. ❌ Complex implementations (dynamic injection, custom logic)
4. ❌ Giving up after 2-3 attempts (took 6 attempts to succeed!)

---

## 📞 NEED HELP?

**Priority Order:**

1. **Check this document first** (covers 95% of issues)
2. **Check browser DevTools** (Elements, Network, Console)
3. **Check Plausible Status** (https://plausible.io/status)
4. **Review recent git commits** (someone might have broken it)
5. **Ask Claude Code** (has full context of this implementation)
6. **Contact Plausible Support** (hello@plausible.io)

---

**Document maintained by: Claude Code**
**Last verified working: November 20, 2025 at 8:15 AM**
**Next review: December 20, 2025 (after 30 days of data)**

---

*"Persistence beats complexity. The simplest solution, applied correctly, wins every time."*
— Lessons from 6 debugging attempts on Nov 20, 2025
