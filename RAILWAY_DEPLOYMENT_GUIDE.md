# 🚂 Railway Deployment Guide - Flask API for AI Explanations

**Your #1 Priority "Deal-Breaker" Feature**

This guide walks you through deploying the Flask API server to Railway, enabling AI-powered chart explanations on your deployed Streamlit apps.

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ GitHub repository with the code (sergecastro/retirement-simulator)
- ✅ Anthropic API key for Claude
- ✅ Credit card for Railway (required even for free tier, but won't be charged)

---

## 🚀 Step-by-Step Deployment

### Step 1: Create Railway Account

1. Go to **https://railway.app/**
2. Click **"Start a New Project"** or **"Login"**
3. Sign up using your **GitHub account** (easiest option)
4. Verify your email if prompted
5. Add a payment method (Railway requires this even for free tier - you won't be charged unless you exceed free limits)

**Free Tier Limits:**
- $5 of usage per month
- 500 hours of runtime
- Perfect for testing and low-traffic apps

---

### Step 2: Create New Project from GitHub

1. From Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. If first time, authorize Railway to access your GitHub
4. Search for and select: **`sergecastro/retirement-simulator`**
5. Railway will prompt: "Select a branch"
   - Choose: **`feature/merged-app`**
6. Click **"Deploy Now"**

Railway will automatically detect:
- `Procfile` (tells it to run Flask)
- `runtime.txt` (Python 3.11.9)
- `railway.json` (deployment config)

---

### Step 3: Configure Environment Variables

**CRITICAL:** The Flask API needs your Anthropic API key and CORS settings.

1. In Railway dashboard, click on your deployed service
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add these two variables:

**Variable 1: ANTHROPIC_API_KEY**
```
Variable name: ANTHROPIC_API_KEY
Value: [Your Anthropic API key - starts with "sk-ant-..."]
```

**Variable 2: ALLOWED_ORIGINS**
```
Variable name: ALLOWED_ORIGINS
Value: https://ultimate-family-retirement-plan.streamlit.app,https://intake-retirement-simulator.streamlit.app,http://localhost:8501,http://localhost:8505
```

**Note:** Adjust the Streamlit URLs if your app URLs are different.

5. Click **"Add"** for each variable
6. Railway will automatically redeploy with new environment variables

---

### Step 4: Get Your Railway URL

1. Wait for deployment to complete (usually 2-3 minutes)
2. Look for deployment status: **"Success"** with green checkmark
3. In the Railway dashboard, you'll see a **URL** assigned to your service
   - Example: `https://retirement-api-production-abc123.up.railway.app`
   - Or you can set a custom domain

4. **Copy this URL** - you'll need it for Step 6

---

### Step 5: Test Your Railway Deployment

Before connecting to Streamlit, verify the Flask API is working:

1. Open a browser and visit:
   ```
   https://your-railway-url.railway.app/health
   ```

2. You should see a JSON response like:
   ```json
   {
     "status": "healthy",
     "port": 8502,
     "api_key": "configured",
     "allowed_origins": ["https://ultimate-family-retirement-plan.streamlit.app", ...]
   }
   ```

3. **Verify:**
   - `status: "healthy"` ✅
   - `api_key: "configured"` ✅ (NOT "missing")

If you see `"api_key": "missing"`, go back to Step 3 and check your ANTHROPIC_API_KEY.

---

### Step 6: Update Streamlit Apps to Use Railway

Now we need to tell your Streamlit apps to use the Railway API instead of localhost.

1. Open `app.py` in your code editor
2. Find the section that calls the Flask API (search for "8502" or "explain")
3. Look for code like:
   ```python
   API_URL = "http://localhost:8502"
   ```

4. Replace with:
   ```python
   # Railway Flask API for AI explanations
   API_URL = os.getenv("FLASK_API_URL", "https://your-railway-url.railway.app")
   ```

5. **Do the same for any other files that call the Flask API**

**Alternative (Recommended):** Use environment variable in Streamlit Cloud:
- Go to Streamlit Cloud dashboard
- Click your app → Settings → Secrets
- Add:
   ```toml
   FLASK_API_URL = "https://your-railway-url.railway.app"
   ```
- Use in code: `API_URL = st.secrets.get("FLASK_API_URL", "http://localhost:8502")`

---

### Step 7: Deploy Updated Streamlit Apps

1. Commit and push changes to GitHub:
   ```bash
   git add app.py
   git commit -m "Connect Streamlit to Railway Flask API"
   git push
   ```

2. Streamlit Cloud will auto-deploy the update (takes 2-3 minutes)

3. Visit your deployed Streamlit app and test the AI explanations feature:
   - Run a simulation
   - Click the **"?"** button on any chart
   - You should get AI-powered explanations!

---

## 🎉 Success Checklist

- ✅ Railway deployment shows "Success" status
- ✅ `/health` endpoint returns healthy status with `api_key: "configured"`
- ✅ Streamlit apps updated with Railway URL
- ✅ AI chart explanations work on deployed apps
- ✅ No CORS errors in browser console

---

## 💰 Cost & Monitoring

### Railway Free Tier
- **$5 credit per month** (resets monthly)
- **500 execution hours per month**
- Your Flask API uses minimal resources (~$2-3/month estimated)

### To Monitor Usage:
1. Go to Railway dashboard
2. Click **"Usage"** tab
3. See real-time usage of compute, memory, and costs

### To Upgrade (if needed):
- If you exceed free tier, Railway will prompt you to add the **Hobby Plan ($5/month)**
- This gives you 500 hours + $5 credit (basically doubles your free tier)

---

## 🔧 Troubleshooting

### Issue 1: "API key not configured" in /health
**Solution:** Go back to Step 3, verify ANTHROPIC_API_KEY is set correctly, redeploy

### Issue 2: CORS errors in browser console
**Solution:** Check ALLOWED_ORIGINS includes your Streamlit app URLs exactly

### Issue 3: Railway app keeps crashing
**Solution:**
- Check Railway logs (click "Deployments" → latest deployment → "View Logs")
- Verify `requirements.txt` has all dependencies: flask, flask-cors, anthropic, python-dotenv

### Issue 4: "This site can't be reached"
**Solution:**
- Verify Railway deployment is running (not stopped)
- Check if Railway assigned a public URL (some plans require manual domain setup)

### Issue 5: Slow response times
**Solution:**
- Railway free tier apps "sleep" after 15 minutes of inactivity
- First request after sleep takes ~10 seconds to wake up
- Upgrade to Hobby plan for 24/7 uptime

---

## 🎯 Next Steps

Once Railway deployment is working:

1. ✅ **Test thoroughly** - Try all chart explanations
2. ✅ **Monitor costs** - Check Railway dashboard after a few days
3. ✅ **Optimize if needed** - Consider caching responses to reduce API calls
4. ✅ **Move to other priorities**:
   - Hide passwords from URL
   - Improve save/load UX
   - Add auto-save reminders

---

## 📞 Need Help?

**Railway Support:**
- Documentation: https://docs.railway.app/
- Discord: https://discord.gg/railway

**Anthropic API:**
- API Status: https://status.anthropic.com/
- Documentation: https://docs.anthropic.com/

---

**You're deploying your #1 priority "deal-breaker" feature! 🚀**

The AI explanations will transform how users understand their retirement projections.
