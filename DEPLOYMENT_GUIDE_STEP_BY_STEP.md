# 🚀 FORECASH DEPLOYMENT GUIDE - FOOLPROOF STEP-BY-STEP CHECKLIST

**Last Updated:** October 22, 2025
**Version:** 1.0
**Purpose:** Complete deployment process for ForeCash retirement planning app

---

## ⚠️ READ THIS FIRST - IMPORTANT NOTES

**This guide covers:**
1. Deploying Streamlit app to Streamlit Cloud (main app)
2. Configuring Render.com (Flask API for chart explanations)
3. Troubleshooting common issues

**Estimated Time:** 15-20 minutes (if everything goes smoothly)

**Prerequisites:**
- GitHub repository up to date
- Anthropic API key available
- Streamlit Cloud account logged in
- Render.com account logged in

---

## 📊 ARCHITECTURE OVERVIEW (UNDERSTAND THIS FIRST!)

```
┌─────────────────────────────────────────────────────────────┐
│  USER'S BROWSER                                             │
│  https://aiforecash.streamlit.app                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  STREAMLIT CLOUD                                            │
│  • Hosts main app (app.py)                                  │
│  • Needs: ANTHROPIC_API_KEY, FLASK_API_URL                  │
│  • Python 3.11                                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ (Chart explanation requests)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  RENDER.COM (Flask API)                                     │
│  • Hosts explain_api_server.py                              │
│  • Needs: ANTHROPIC_API_KEY, ALLOWED_ORIGINS                │
│  • Python 3.11                                              │
└─────────────────────────────────────────────────────────────┘
```

**KEY POINT:** Both services must be configured correctly for "?" buttons to work!

---

# PART 1: PREPARE FOR DEPLOYMENT

## CHECKLIST BEFORE YOU START:

- [ ] **Backup complete** (entire project folder)
- [ ] **Git status clean** (all changes committed)
- [ ] **Latest code pushed to GitHub** (on the branch you want to deploy)
- [ ] **Anthropic API key ready** (you'll need this twice)
- [ ] **Both accounts logged in:**
  - [ ] https://share.streamlit.io/ (logged in)
  - [ ] https://dashboard.render.com/ (logged in)

---

# PART 2: DEPLOY TO STREAMLIT CLOUD (MAIN APP)

## SECTION A: CREATE NEW APP (If deploying for first time OR creating fresh deployment)

### Step 1: Go to Streamlit Cloud Dashboard
```
URL: https://share.streamlit.io/
```
**Action:** Login if needed
**Verify:** You see your dashboard with list of apps (if any)

---

### Step 2: Click "Create app" or "New app" Button
**Location:** Top right of the page
**Note:** Button may say "Deploy an app" or "New app" depending on UI version

---

### Step 3: Fill in App Configuration Form

**CRITICAL:** Fill in EXACTLY as shown below:

```
Repository:
  [sergecastro/retirement-simulator]
  (Your GitHub username/repo name)

Branch:
  [master]  ← IMPORTANT: Deploy from master branch
  (Or whatever branch has your latest code)

Main file path:
  [app.py]
  ⚠️ NOTE: Even though app.py is in family_retirement_no_OCR/app.py,
           Streamlit Cloud will find it. Just enter: app.py

  If it doesn't work, try: family_retirement_no_OCR/app.py

App URL (optional):
  [aiforecash]  ← This will become: https://aiforecash.streamlit.app/
  (Choose your custom subdomain)
```

**Action:** Click "Deploy!" button

---

### Step 4: Wait for Initial Deployment Attempt
**What you'll see:** "Deploying..." or loading animation
**Time:** 2-5 minutes
**Expected result:** Will probably FAIL (this is normal!) because secrets aren't configured yet

---

## SECTION B: CONFIGURE APP SETTINGS (CRITICAL!)

### Step 5: Access App Settings
**Option 1 (If you see your app in dashboard):**
1. Find your app in the list: `aiforecash · master · app.py`
2. Click the **3 dots** ⋮ on the RIGHT side of the app
3. Click **"Settings"** from dropdown menu

**What you should see:** Settings panel opens (usually on right side)

---

### Step 6: Configure Python Version
**In Settings Panel:**

1. Look for section: **"Python version"** or **"Advanced settings"**
2. Find dropdown that shows Python version
3. **Change to:** `3.11`
4. **⚠️ CRITICAL:** Must be Python 3.11 (not 3.9, not 3.12)

**Why:** Your app dependencies require Python 3.11

---

### Step 7: Configure Secrets (MOST IMPORTANT STEP!)
**In Settings Panel:**

1. Look for section: **"Secrets"**
2. Click to expand/edit secrets
3. **Copy and paste EXACTLY this (replace with your actual API key):**

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR-ACTUAL-KEY-HERE"
FLASK_API_URL = "https://retirement-simulator.onrender.com"
```

**⚠️ CRITICAL NOTES:**
- Replace `sk-ant-api03-YOUR-ACTUAL-KEY-HERE` with your REAL Anthropic API key
- The FLASK_API_URL must match your Render.com service URL EXACTLY
- Format must be TOML (as shown above, with quotes)
- No trailing spaces or extra characters

**Your Anthropic API Key:**
```
sk-ant-api03-[YOUR-ACTUAL-API-KEY-HERE]
```
*Note: Use your actual Anthropic API key from https://console.anthropic.com/*

---

### Step 8: Save Settings
**Action:** Click **"Save"** button at bottom of Settings panel
**What happens:** App will automatically REDEPLOY with new settings
**Time:** 2-5 minutes

---

### Step 9: Monitor Deployment
**How to check status:**
1. Look at app in dashboard
2. Status will show:
   - "Deploying..." (in progress)
   - "Running" or green indicator (success!)
   - Red indicator (failed - see troubleshooting)

**If it fails:** Check troubleshooting section at end of this guide

---

### Step 10: Verify App is Running
**Action:** Click on app name to open it in browser
**Expected URL:** https://aiforecash.streamlit.app/

**What you should see:**
- Password screen appears
- Enter password: `abcd123` (demo) or your trusted password
- App loads with no errors

**⚠️ NOTE:** "?" buttons may not work YET - that's okay, we'll fix that in Part 3

---

## SECTION C: UPDATE EXISTING APP (If app already exists, just updating code)

### Step 1: Push Latest Code to GitHub
```bash
git status              # Verify all changes committed
git push origin master  # Push to GitHub
```

---

### Step 2: Trigger Redeployment
**Option 1: Automatic (if enabled)**
- Streamlit Cloud will auto-detect GitHub push
- Wait 2-5 minutes for automatic redeployment

**Option 2: Manual Reboot**
1. Go to https://share.streamlit.io/
2. Find your app in list
3. Click **3 dots** ⋮
4. Click **"Reboot"**
5. Wait 2-5 minutes

---

### Step 3: Verify Update
**Action:** Open app in browser
**Expected:** New features/changes are visible

---

# PART 3: CONFIGURE RENDER.COM (FLASK API FOR CHART EXPLANATIONS)

## WHY THIS IS NEEDED:
The "?" buttons on charts send requests to a Flask API hosted on Render.com.
This API must be configured to ALLOW requests from your Streamlit app.

---

## SECTION A: UPDATE ALLOWED ORIGINS (CRITICAL FOR "?" BUTTONS!)

### Step 1: Login to Render.com
```
URL: https://dashboard.render.com/
```
**Action:** Login with your credentials

---

### Step 2: Find Your Flask API Service
**What to look for:** Service named `retirement-api` or similar
**In dashboard:** You should see a list of services
**Action:** Click on the Flask API service (NOT any other services)

**Service Details:**
- Name: retirement-api
- Type: Web Service
- Language: Python 3

---

### Step 3: Open Environment Variables
**In left sidebar, under "Manage" section:**
1. Look for menu option: **"Environment"**
2. Click **"Environment"**

**What you should see:** List of environment variables including:
- `ALLOWED_ORIGINS`
- `ANTHROPIC_API_KEY`

---

### Step 4: Edit ALLOWED_ORIGINS
**Current value (before editing):**
```
https://ultimate-family-retirement-plan.streamlit.app,https://intake-retirement-simulator.streamlit.app
```

**Action:**
1. Click **"Edit"** button (top right)
2. Find the `ALLOWED_ORIGINS` row
3. Click in the **"Value"** field
4. **Go to the END of the text**
5. **Add this at the end:**
   ```
   ,https://aiforecash.streamlit.app
   ```

**New value (after editing):**
```
https://ultimate-family-retirement-plan.streamlit.app,https://intake-retirement-simulator.streamlit.app,https://aiforecash.streamlit.app
```

**⚠️ CRITICAL NOTES:**
- Must start with a comma: `,https://aiforecash.streamlit.app`
- NO SPACES before or after the comma
- URL must match your Streamlit app URL EXACTLY
- Include `https://` (not `http://`)
- NO trailing slash

---

### Step 5: Save Changes
**Action:** Click **"Save Changes"** button
**What happens:** Render.com will automatically REBUILD and REDEPLOY the service
**Time:** 1-2 minutes

---

### Step 6: Monitor Render.com Deployment
**In Render.com service page:**
1. Click **"Logs"** (left sidebar)
2. Watch logs scroll
3. Wait for message: **"Your service is live 🎉"**

**Expected logs (end of deployment):**
```
[INFO] Listening at: http://0.0.0.0:10000
[INFO] Using worker: sync
[INFO] Booting worker with pid: 63
OK: Anthropic API key loaded successfully
==> Your service is live 🎉
==> Available at your primary URL https://retirement-simulator.onrender.com
```

---

### Step 7: Verify Render.com Configuration
**Action:** Open this URL in your browser:
```
https://retirement-simulator.onrender.com/health
```

**Expected response (JSON):**
```json
{
  "status": "healthy",
  "port": 5000,
  "api_key": "configured",
  "allowed_origins": [
    "https://ultimate-family-retirement-plan.streamlit.app",
    "https://intake-retirement-simulator.streamlit.app",
    "https://aiforecash.streamlit.app"
  ]
}
```

**⚠️ VERIFY:** Your new app URL (`https://aiforecash.streamlit.app`) is in the `allowed_origins` list!

**If not showing:** Go back to Step 4 and check you saved correctly

---

# PART 4: FINAL TESTING

## SECTION A: TEST MAIN APP FUNCTIONALITY

### Step 1: Open Your Deployed App
```
URL: https://aiforecash.streamlit.app/
```

---

### Step 2: Test Password Screen
**Action:** Enter password: `abcd123` (or your trusted password)
**Expected:** Password accepted, mode selector appears

---

### Step 3: Test INTAKE Mode
**Action:**
1. Select **"Data Entry Mode"**
2. Navigate through all 8 pages:
   - Profile
   - Income
   - Expenses
   - Custom Expenses
   - Assets
   - Liabilities
   - Family Events
   - Review & Complete
3. Click **"Complete & Go to Analysis Mode"**

**Expected:**
- All pages load without errors
- Balloons appear on completion 🎈
- Transitions to Analysis Mode
- Data auto-loads

---

### Step 4: Test Analysis Mode
**Action:**
1. Enter **"Analysis Mode"** (or should already be there after INTAKE)
2. Verify sidebar shows your data
3. Scroll down to see disclaimers
4. Look for **AI Planning Assistant** section

**Expected:**
- ⚠️ Disclaimers showing properly
- All data visible in sidebar
- No errors in main area

---

### Step 5: Test AI Planning Assistant
**Action:**
1. Find **"AI Planning Assistant"** checkbox in sidebar
2. Enable it (check the box)
3. Ask a question in the chat: "What is my biggest financial risk?"

**Expected:**
- ⚠️ AI disclaimer shows at top of chat
- Chat interface appears
- AI responds within 10-20 seconds
- Response is relevant to your data

**If fails:** Check ANTHROPIC_API_KEY in Streamlit secrets

---

### Step 6: Run a Simulation
**Action:**
1. Scroll to bottom of page
2. Click **"Run Simulation"** button
3. Wait for charts to appear (30-60 seconds)

**Expected:**
- Charts load successfully
- Multiple charts appear (trajectories, Monte Carlo, etc.)
- No error messages

---

### Step 7: Test "?" Chart Explanation Buttons (THE BIG TEST!)
**Action:**
1. After simulation completes, **WAIT 30-40 SECONDS**
2. Look for **RED "?" BUTTONS** on charts
3. **⚠️ IMPORTANT:** Buttons take 30-40 seconds to appear (this is normal!)
4. Click a "?" button on any chart

**Expected:**
- Modal/popup appears
- Shows "Loading explanation..." message
- After 5-10 seconds, AI explanation appears
- Explanation is relevant to the chart data
- ⚠️ Disclaimer appears at bottom of explanation

**If "?" buttons don't appear:**
- Wait 60 seconds (patience!)
- Check browser console for errors (F12)
- See troubleshooting section

**If "?" buttons appear but clicking shows error:**
- Error: "Failed to fetch" → CORS issue, go back to Part 3
- Error: "API key not configured" → Check Render.com has ANTHROPIC_API_KEY
- Error: "500 Internal Server Error" → Check Render.com logs

---

## SECTION B: BROWSER CONSOLE CHECK (FOR ADVANCED USERS)

### Step 1: Open Browser Console
**Action:** Press **F12** (Windows) or **Cmd+Option+I** (Mac)
**Tab:** Click **"Console"** tab

---

### Step 2: Check for Errors
**Look for:**
- ❌ **Red errors** (these are problems)
- ⚠️ **Orange warnings** (usually okay, can ignore)

**Common errors and what they mean:**

| Error Message | Meaning | Fix |
|---------------|---------|-----|
| `Failed to fetch` | CORS issue | Check Part 3 (Render.com ALLOWED_ORIGINS) |
| `404 Not Found: /~/_stcore/health` | Streamlit internal, ignore | No action needed |
| `Access-Control-Allow-Origin` | CORS issue | Check Part 3 (Render.com ALLOWED_ORIGINS) |
| `WebSocket connection failed` | Streamlit reconnecting | Usually auto-resolves, ignore |
| `ANTHROPIC_API_KEY not found` | Missing secret | Check Part 2, Step 7 |

---

### Step 3: Verify Chart Registry
**In console, look for messages like:**
```
[ChartRegistry] Registered financial_trajectories: Object
[ChartRegistry] Registered monte_carlo_simulation: Object
[ChartRegistry] Registered irmaa_magi_trajectory: Object
```

**If you see these:** Chart explanation system is initializing correctly ✅

---

# PART 5: TROUBLESHOOTING COMMON ISSUES

## ISSUE 1: App Won't Deploy / Keeps Failing

### Symptoms:
- Red indicator in Streamlit Cloud dashboard
- App shows error page when opened

### Solutions:

**Check 1: Python Version**
- Go to Settings → Python version
- Must be: **3.11** (not 3.9, 3.10, or 3.12)

**Check 2: Secrets Format**
- Go to Settings → Secrets
- Verify format is TOML (with quotes):
  ```toml
  ANTHROPIC_API_KEY = "sk-ant-..."
  FLASK_API_URL = "https://retirement-simulator.onrender.com"
  ```
- No extra spaces, no typos

**Check 3: Branch and File Path**
- Verify branch exists on GitHub
- Verify app.py exists in repository
- Try both: `app.py` and `family_retirement_no_OCR/app.py`

**Check 4: Requirements.txt**
- Verify `requirements.txt` exists in repository
- All dependencies listed correctly

---

## ISSUE 2: App Loads But Shows Python Errors

### Symptoms:
- App opens but shows error messages
- "ModuleNotFoundError" or "ImportError"

### Solutions:

**Check 1: Missing Dependencies**
- Review error message for missing module name
- Add to `requirements.txt` in GitHub
- Push change and redeploy

**Check 2: Python Version Mismatch**
- Some packages require specific Python versions
- Ensure Python 3.11 is set in Streamlit settings

---

## ISSUE 3: "?" Buttons Don't Appear

### Symptoms:
- Simulation runs successfully
- Charts appear
- But NO "?" buttons show up (even after 60 seconds)

### Solutions:

**Check 1: Wait Longer**
- "?" buttons can take 30-60 seconds to appear
- Be patient! This is normal behavior

**Check 2: Reboot Streamlit App**
- Go to Streamlit Cloud dashboard
- Click 3 dots ⋮ on app
- Click "Reboot"
- Wait 2-3 minutes
- Try again

**Check 3: Hard Refresh Browser**
- Press **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)
- This clears browser cache
- JavaScript will reload

**Check 4: Browser Console**
- Press F12, check Console tab
- Look for JavaScript errors
- Look for message: `[ChartRegistry] Registered ...`
- If not showing, JavaScript didn't load

---

## ISSUE 4: "?" Buttons Appear But Show "Failed to Fetch" Error

### Symptoms:
- "?" buttons are visible
- Clicking them shows error: "Could not get explanation: Failed to fetch"

### Solutions:

**Check 1: Render.com ALLOWED_ORIGINS (MOST COMMON)**
- Go to https://dashboard.render.com/
- Open your Flask API service
- Environment → ALLOWED_ORIGINS
- **Verify your Streamlit app URL is in the list:**
  ```
  https://aiforecash.streamlit.app
  ```
- If missing, add it (see Part 3, Step 4)
- Save and wait for redeploy

**Check 2: Render.com Service is Running**
- Open: https://retirement-simulator.onrender.com/health
- Should show: `{"status": "healthy", ...}`
- If shows error or times out → Render service is down
- Go to Render dashboard, check service status
- Click "Manual Deploy" to redeploy if needed

**Check 3: FLASK_API_URL in Streamlit Secrets**
- Go to Streamlit Cloud → Settings → Secrets
- Verify FLASK_API_URL matches your Render.com URL exactly:
  ```toml
  FLASK_API_URL = "https://retirement-simulator.onrender.com"
  ```
- No trailing slash, correct domain

**Check 4: CORS Headers**
- Open browser console (F12)
- Look for error mentioning: "CORS policy" or "Access-Control-Allow-Origin"
- This confirms ALLOWED_ORIGINS issue
- Fix: Update Render.com ALLOWED_ORIGINS (Part 3)

---

## ISSUE 5: Chart Explanations Load But Are Generic/Wrong

### Symptoms:
- "?" buttons work
- Modal opens, explanation loads
- But explanation doesn't match the chart data

### Solutions:

**Check 1: Wait for Full Chart Load**
- Make sure simulation fully completes before clicking "?"
- Charts need to be fully rendered with data

**Check 2: Plotly Charts Fully Loaded**
- The JavaScript extracts data from Plotly chart objects
- If Plotly hasn't finished rendering, data may be incomplete
- Wait 10-15 seconds after charts appear, then click "?"

**This is a known limitation - explanations improve once charts fully render**

---

## ISSUE 6: AI Planning Assistant Not Working

### Symptoms:
- Checkbox shows in sidebar
- But clicking it shows nothing or error

### Solutions:

**Check 1: ANTHROPIC_API_KEY in Streamlit**
- Go to Settings → Secrets
- Verify ANTHROPIC_API_KEY is set correctly
- Must be valid Anthropic API key

**Check 2: AI Disclaimer Shows**
- When you enable AI Assistant checkbox
- Should immediately show disclaimer box
- If not, app.py may have issue with disclaimers.py import

**Check 3: API Key Has Credits**
- Login to Anthropic console: https://console.anthropic.com/
- Check if API key has available credits
- If depleted, explanations will fail

---

## ISSUE 7: Render.com Service Shows "Sleeping" or Cold Start

### Symptoms:
- First "?" button click takes 30-60 seconds
- Subsequent clicks are faster
- Render logs show service was sleeping

### Solution:

**This is normal on Render.com Free tier!**
- Free tier services sleep after inactivity
- First request wakes them up (30-60 seconds)

**To avoid (if on paid tier):**
- You're on Render Starter tier ($7/month)
- This should NOT happen
- If it does, check service settings:
  - Instance Type: Should be "Starter" (not "Free")

---

## ISSUE 8: Disclaimers Not Showing

### Symptoms:
- App works but no legal disclaimers appear
- No disclaimer acknowledgment screen

### Solutions:

**Check 1: disclaimers.py Deployed**
- Verify file exists in GitHub repository
- Path: `family_retirement_no_OCR/disclaimers.py`
- If missing, must be added and pushed

**Check 2: app.py Imports Disclaimers**
- Open app.py in GitHub
- Check line ~30: `import disclaimers`
- Check line ~164: `disclaimers.require_disclaimer_acknowledgment()`

**Check 3: Clear Browser Cache**
- Hard refresh: Ctrl+Shift+R
- Or clear all browser cache for the site

---

# PART 6: POST-DEPLOYMENT CHECKLIST

## After Successful Deployment:

- [ ] **Test password screen** (both demo and trusted passwords)
- [ ] **Test INTAKE mode** (all 8 pages)
- [ ] **Test Analysis mode** (data loads correctly)
- [ ] **Test AI Planning Assistant** (at least one question)
- [ ] **Run simulation** (charts appear)
- [ ] **Test "?" buttons** (at least 2-3 charts)
- [ ] **Test on different browser** (Chrome, Firefox, Safari)
- [ ] **Test on mobile device** (optional but recommended)
- [ ] **Document any issues** encountered
- [ ] **Update this guide** if you discovered new steps/issues

---

# PART 7: UPDATING AFTER INITIAL DEPLOYMENT

## When You Make Code Changes:

### Process:
1. Make changes locally
2. Test locally: `streamlit run app.py`
3. Commit changes: `git add . && git commit -m "message"`
4. Push to GitHub: `git push origin master`
5. **Streamlit Auto-Deploys** (wait 2-5 minutes)
6. Test deployed app
7. If issues, check Streamlit logs (in dashboard)

### If Secrets Changed:
- Go to Streamlit Settings → Secrets
- Update secrets
- Click Save (auto-redeploys)

### If Render.com Code Changed:
- Render auto-deploys when you push to GitHub
- Or click "Manual Deploy" in Render dashboard

---

# PART 8: MAINTENANCE & MONITORING

## Regular Checks (Weekly):

- [ ] **Check Streamlit app is accessible**
  - URL: https://aiforecash.streamlit.app/
  - Verify loads without errors

- [ ] **Check Render.com service is running**
  - URL: https://retirement-simulator.onrender.com/health
  - Should return `{"status": "healthy", ...}`

- [ ] **Check API credits**
  - Anthropic console: https://console.anthropic.com/
  - Verify credits available

- [ ] **Check for Streamlit/Render errors**
  - Streamlit dashboard: Check for any red indicators
  - Render dashboard: Check logs for errors

## Monthly Reviews:

- [ ] **Review Streamlit usage metrics**
  - Analytics in Streamlit dashboard
  - Track user count, session duration

- [ ] **Review Render.com usage**
  - Check Render metrics
  - CPU, memory, request count

- [ ] **Update dependencies** (if needed)
  - Check for security updates
  - Update requirements.txt
  - Test thoroughly before deploying

---

# PART 9: EMERGENCY PROCEDURES

## If App Goes Down:

### Step 1: Identify Which Service Failed
- **Test Streamlit:** Open https://aiforecash.streamlit.app/
  - If fails: Streamlit issue (go to Step 2A)
- **Test Render:** Open https://retirement-simulator.onrender.com/health
  - If fails: Render issue (go to Step 2B)

### Step 2A: Streamlit Down
1. Go to Streamlit dashboard
2. Check app status (red = down)
3. Click 3 dots ⋮ → "Reboot"
4. Wait 2-3 minutes
5. If still down, check logs for errors
6. If critical, contact Streamlit support

### Step 2B: Render Down
1. Go to Render dashboard
2. Check service status
3. Click "Manual Deploy" to redeploy
4. Check logs for errors
5. If critical, contact Render support

### Step 3: Rollback to Previous Version
**If new deployment caused issues:**

**Streamlit:**
1. Go to Settings
2. Change branch back to previous working version
3. Or change commit hash if available
4. Save (redeploys)

**Render:**
1. Go to service page
2. Click "Deploys" (left menu)
3. Find previous working deploy
4. Click "Redeploy" button next to it

---

# PART 10: CONTACTS & RESOURCES

## Support Contacts:

**Streamlit Cloud Support:**
- Dashboard: https://share.streamlit.io/
- Docs: https://docs.streamlit.io/
- Forum: https://discuss.streamlit.io/
- Email: support@streamlit.io

**Render.com Support:**
- Dashboard: https://dashboard.render.com/
- Docs: https://render.com/docs
- Community: https://community.render.com/
- Email: support@render.com

**Anthropic API Support:**
- Console: https://console.anthropic.com/
- Docs: https://docs.anthropic.com/
- Support: support@anthropic.com

## Key URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| **Production App** | https://aiforecash.streamlit.app/ | Main user-facing app |
| **Streamlit Dashboard** | https://share.streamlit.io/ | Manage deployments |
| **Render Dashboard** | https://dashboard.render.com/ | Manage Flask API |
| **Render API Health** | https://retirement-simulator.onrender.com/health | Check API status |
| **GitHub Repo** | https://github.com/sergecastro/retirement-simulator | Source code |
| **Anthropic Console** | https://console.anthropic.com/ | API key & credits |

---

# APPENDIX A: SECRETS TEMPLATES

## Streamlit Secrets (secrets.toml format):

```toml
# Anthropic API Key for AI features
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR-KEY-HERE"

# Flask API URL for chart explanations
FLASK_API_URL = "https://retirement-simulator.onrender.com"
```

## Render.com Environment Variables:

```
Key: ALLOWED_ORIGINS
Value: https://ultimate-family-retirement-plan.streamlit.app,https://intake-retirement-simulator.streamlit.app,https://aiforecash.streamlit.app

Key: ANTHROPIC_API_KEY
Value: sk-ant-api03-YOUR-KEY-HERE
```

---

# APPENDIX B: COMMON CONSOLE ERRORS (AND WHAT THEY MEAN)

## Safe to Ignore:

```
GET /~/_stcore/host-config 404 (Not Found)
GET /~/_stcore/health 404 (Not Found)
WebSocket connection failed
[Violation] 'requestAnimationFrame' handler took <N>ms
```
**Meaning:** Streamlit internal, doesn't affect functionality

## Needs Attention:

```
Access to fetch at 'https://retirement-simulator.onrender.com/explain'
has been blocked by CORS policy
```
**Meaning:** Render.com ALLOWED_ORIGINS needs updating (Part 3, Step 4)

```
Failed to fetch
```
**Meaning:** API request failed - check Render.com is running

```
ANTHROPIC_API_KEY not found
```
**Meaning:** Missing secret in Streamlit or Render.com

---

# APPENDIX C: VERSION HISTORY OF THIS GUIDE

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 22, 2025 | Initial comprehensive guide created after successful deployment |

---

# FINAL NOTES:

**🎯 KEY TAKEAWAYS:**
1. **Python 3.11** is required (both Streamlit and Render)
2. **Secrets must be configured** before app works
3. **ALLOWED_ORIGINS** on Render.com is critical for "?" buttons
4. **"?" buttons take 30-40 seconds to appear** (this is normal!)
5. **Test thoroughly** after every deployment

**💪 YOU GOT THIS!**

If you followed this guide step-by-step, your deployment should succeed!

If you encounter issues not covered here:
1. Check browser console (F12)
2. Check Streamlit logs (in dashboard)
3. Check Render logs (in dashboard)
4. Update this guide with what you learned!

**Good luck! 🚀**

---

**Document End**
**Total Steps:** 50+ detailed steps across 10 parts
**Estimated Time to Complete:** 15-20 minutes (first time), 5-10 minutes (subsequent deployments)
