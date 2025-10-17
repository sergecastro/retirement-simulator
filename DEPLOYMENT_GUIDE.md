# 🚀 Deployment Guide - Streamlit Community Cloud

**Date:** October 17, 2025
**App:** Ultimate Family Retirement Plus
**Target:** Beta testing with friends/family (Oren and others)

---

## ✅ Pre-Deployment Checklist

- [x] Remove all debug output (print statements, tracebacks)
- [x] Add professional dashboard with key metrics
- [x] Apply professional CSS styling
- [x] Test both apps locally (INTAKE + Main simulator)
- [x] Create requirements.txt with all dependencies
- [x] Create .streamlit/config.toml for styling
- [x] Commit all changes to git
- [ ] Push to GitHub
- [ ] Deploy main app to Streamlit Cloud
- [ ] Deploy INTAKE app to Streamlit Cloud (separate deployment)
- [ ] Configure secrets (ANTHROPIC_API_KEY)
- [ ] Share URL with beta testers

---

## 🎯 Deployment Options

### **Option 1: Streamlit Community Cloud (RECOMMENDED for Beta)**

**What Works:**
- ✅ Main retirement simulator app (app.py)
- ✅ INTAKE data entry app (intake_app.py)
- ✅ All visualizations and analysis features
- ✅ Free hosting for public repos
- ✅ Automatic updates from GitHub

**What Doesn't Work:**
- ❌ Flask API server (explain_api_server.py) - Streamlit Cloud only runs Streamlit apps
- ❌ AI-powered chart explanations (requires Flask server)

**Solution for AI Explanations:**
- **Short-term (Beta):** Disable AI explanations for deployed version
- **Long-term:** Deploy Flask server to Heroku, Railway, or Render (free tiers available)

---

## 📝 Step-by-Step Deployment

### **Step 1: Push to GitHub**

```bash
# Make sure you're on the right branch
git status

# Push to GitHub
git push origin feature/custom-fields

# Or push to main/master if that's your deployment branch
git push origin main
```

### **Step 2: Create Streamlit Cloud Account**

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Authorize Streamlit Cloud to access your repositories

### **Step 3: Deploy Main App**

1. Click "New app" in Streamlit Cloud dashboard
2. Select your repository: `retirement-simulator`
3. Select branch: `feature/custom-fields` (or main)
4. Main file path: `family_retirement_no_OCR/app.py`
5. Click "Deploy!"

**App URL will be:** `https://your-username-retirement-simulator-app-random.streamlit.app`

### **Step 4: Deploy INTAKE App (Separate Deployment)**

1. Click "New app" again
2. Same repository and branch
3. Main file path: `family_retirement_no_OCR/intake_app.py`
4. Click "Deploy!"

**App URL will be:** `https://your-username-retirement-simulator-intake-random.streamlit.app`

### **Step 5: Configure Secrets (IMPORTANT)**

For each deployed app:

1. Go to app settings (⋮ menu → Settings)
2. Click "Secrets" tab
3. Add this configuration:

```toml
# For AI features (if deploying Flask separately)
ANTHROPIC_API_KEY = "your-actual-api-key-here"
```

**Note:** Get your Anthropic API key from: https://console.anthropic.com/

---

## 🔧 Handling Flask Server for AI Explanations

### **Option A: Disable for Beta (Easiest)**

Edit `app.py` and `intake_app.py` to disable AI explanations:

```python
# In app.py, comment out Flask server check
# CHECK FLASK SERVER CONNECTION (does NOT auto-start)
# ... (comment out entire section)

# Skip AI explanation initialization
# inject_explain_visual_system()
```

### **Option B: Deploy Flask to Heroku (Free Tier)**

1. Create a `Procfile` in the project root:
```
web: python explain_api_server.py
```

2. Deploy to Heroku:
```bash
heroku create retirement-app-api
git push heroku main
```

3. Update environment variable in both Streamlit apps:
```toml
FLASK_API_URL = "https://retirement-app-api.herokuapp.com"
```

### **Option C: Deploy Flask to Railway (Recommended)**

1. Go to https://railway.app/
2. Connect GitHub repository
3. Select `explain_api_server.py` as entry point
4. Railway will auto-detect Python and install requirements
5. Copy deployed URL
6. Add to Streamlit secrets:
```toml
FLASK_API_URL = "https://your-app.railway.app"
```

**Cost:** Free for <500 hours/month

---

## 🧪 Testing Your Deployment

### **Test Checklist:**

1. **Main App:**
   - [ ] Opens without errors
   - [ ] Dashboard displays correctly
   - [ ] Financial inputs work
   - [ ] Simulation runs successfully
   - [ ] Charts render properly
   - [ ] Data manager (save/load) works
   - [ ] INTAKE import works (if files uploaded)

2. **INTAKE App:**
   - [ ] Opens without errors
   - [ ] Validation warnings appear correctly
   - [ ] Two-path workflow accessible
   - [ ] Export to JSON works
   - [ ] Document parser functional (if enabled)

3. **Cross-App Integration:**
   - [ ] Can export from INTAKE
   - [ ] Can import into Main app
   - [ ] Data transfers correctly

---

## 🐛 Common Deployment Issues

### **Issue 1: "ModuleNotFoundError"**
**Solution:** Ensure all imports are in requirements.txt

### **Issue 2: "FileNotFoundError" for SHARED folder**
**Solution:** Create SHARED folder structure in deployment:
```python
# Add to app.py startup
import os
os.makedirs("SHARED/scenarios", exist_ok=True)
os.makedirs("SHARED/session_states", exist_ok=True)
```

### **Issue 3: Charts not rendering**
**Solution:** Plotly version mismatch. Lock to exact version in requirements.txt

### **Issue 4: API key not found**
**Solution:** Verify secrets.toml is configured in Streamlit Cloud settings

---

## 📧 Sharing with Beta Testers

### **Email Template:**

```
Subject: Beta Access - Family Retirement Planning Tool

Hi [Name],

You're invited to beta test our new retirement planning tool!

🏠 Main App: https://your-app-url.streamlit.app
📝 Data Entry: https://your-intake-app-url.streamlit.app

QUICK START:
1. Start with the Data Entry app to input your financial info
2. Export your data (JSON file)
3. Open the Main App and import your data
4. Run simulations and explore visualizations

NOTE: This is a beta version. Some features (AI explanations) are still in development.

FEEDBACK: Please share any bugs, confusing UI, or feature requests!

Thanks for helping us test!
```

---

## 🔐 Security Considerations

### **For Public Deployment:**

1. **No Secrets in Code:** ✅ All API keys in secrets.toml
2. **No Personal Data Storage:** ✅ All data in session state (ephemeral)
3. **No Database:** ✅ Local files only (SHARED folder)
4. **Rate Limiting:** Consider adding for API calls (future)

### **For Private Beta:**

- Option 1: Keep repo private (Streamlit Community allows this)
- Option 2: Add password protection:
```python
import streamlit as st

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        password = st.text_input("Beta Access Password:", type="password")
        if st.button("Login"):
            if password == "your-beta-password":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        st.stop()

check_password()
```

---

## 💰 Cost Analysis

### **Streamlit Community Cloud (FREE):**
- ✅ Unlimited public apps
- ✅ 1GB resources per app
- ✅ GitHub integration
- ✅ Custom subdomains
- ❌ Can't run background services (Flask)

### **If You Need More:**

**Streamlit Cloud Pro ($20/month):**
- ✅ Private apps
- ✅ More resources (4GB RAM)
- ✅ Priority support
- ❌ Still can't run Flask

**Railway (FREE → $5/month):**
- ✅ Flask API hosting
- ✅ 500 free hours/month
- ✅ $5/month for unlimited
- ✅ Auto-deploy from GitHub

**Total Cost for Full Deployment:**
- Beta (no AI): $0/month
- Beta (with AI): $0-5/month
- Production: $20-25/month

---

## 🎯 Recommended Deployment Strategy

### **Phase 0: Local Testing (NOW)**
- ✅ Test with Oren and 2-3 close friends
- ✅ Use local servers (no deployment)
- ✅ All features work (including AI)

### **Phase 1: Beta (Week 2)**
- Deploy main app to Streamlit Cloud
- Deploy INTAKE to Streamlit Cloud
- **Disable AI explanations** (not critical for beta)
- Share with 10-20 beta testers
- Collect feedback

### **Phase 2: Public Beta (Month 2)**
- Keep Streamlit Cloud for main apps
- Deploy Flask to Railway ($0 or $5/month)
- Enable AI explanations
- Launch on Reddit, Product Hunt

### **Phase 3: Production (Month 3-4)**
- Upgrade to Streamlit Pro ($20/month) if needed
- Keep Railway for Flask ($5/month)
- Add user analytics
- Consider custom domain

---

## 📋 Next Steps

1. **Today:** Push code to GitHub
2. **Today:** Deploy main app to Streamlit Cloud
3. **Today:** Test deployment with dummy data
4. **Tomorrow:** Share link with Oren for first feedback
5. **Week 2:** Share with 5-10 more beta testers
6. **Week 3:** Iterate based on feedback

---

## 🆘 Need Help?

**Streamlit Docs:** https://docs.streamlit.io/streamlit-community-cloud
**Railway Docs:** https://docs.railway.app/
**Anthropic API:** https://docs.anthropic.com/claude/reference/getting-started-with-the-api

**Deployment Support:**
- Streamlit Community Forum: https://discuss.streamlit.io/
- Railway Discord: https://discord.gg/railway

---

**Created by:** Claude Code
**Date:** October 17, 2025
**Status:** Ready for deployment!
**Estimated Time:** 30-60 minutes for first deployment
