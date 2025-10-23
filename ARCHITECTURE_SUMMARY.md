# ForeCash Architecture Summary

**Created:** October 23, 2025 @ 11:30 AM
**For:** Claude.ai deployment coordination
**Purpose:** Crystal-clear architecture reference

---

## 🎯 **THE ANSWER: Option C - Streamlit Only**

### **Current Architecture**

```
┌─────────────────────────────────────────┐
│                                         │
│    ForeCash Application                 │
│    (Single Streamlit Service)           │
│                                         │
│  Entry Point: app.py                    │
│  Port: $PORT (Render sets this)         │
│  AI: Direct Anthropic API calls         │
│                                         │
└─────────────────────────────────────────┘
         │
         ├─→ Uses Anthropic API directly
         ├─→ No separate Flask service needed
         └─→ All features in one service
```

---

## 🚀 **Render Deployment Configuration**

### **Build Command:**
```bash
pip install -r requirements.txt
```

### **Start Command:**
```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### **Environment Variables:**
```
ANTHROPIC_API_KEY=sk-ant-...
DEMO_PASSWORD=<set_your_password>
TRUSTED_USERS=serge@emiramed.com,other@email.com
```

### **Port Configuration:**
- **Render sets:** `$PORT` environment variable automatically
- **Streamlit uses:** `--server.port=$PORT` flag
- **You do nothing:** Port is automatic

---

## 📁 **Repository Details**

| Setting | Value |
|---------|-------|
| **GitHub URL** | https://github.com/sergecastro/retirement-simulator |
| **Branch** | `refactor/modular-app-structure` |
| **Root Directory** | `/family_retirement_no_OCR` |
| **Main File** | `app.py` |
| **Requirements** | `requirements.txt` |

---

## 🔧 **What About Flask?**

### **Flask Server Exists But Is Optional**

**File:** `explain_api_server.py`
**Purpose:** Chart explanations (optional feature)
**Status:** NOT NEEDED for main app

**Why it exists:**
- Original design had separate Flask API
- AI Advisor now uses direct Anthropic API instead
- Flask code kept for potential future use
- Main app works perfectly without it

**Do NOT deploy Flask server to Render!**

---

## ✅ **Key Points for Deployment**

1. **Single Service** - Deploy only Streamlit app
2. **One Command** - `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
3. **Three Variables** - ANTHROPIC_API_KEY, DEMO_PASSWORD, TRUSTED_USERS
4. **Automatic Port** - Render sets $PORT, Streamlit uses it
5. **No Flask** - Not needed, don't deploy it

---

## 🏗️ **Application Structure**

```
family_retirement_no_OCR/
│
├── app.py                    ← MAIN ENTRY POINT (Streamlit)
├── requirements.txt          ← Dependencies
│
├── config/                   ← Configuration
│   ├── settings.py          (App initialization)
│   └── auth.py              (Authentication)
│
├── ui/                      ← UI Components
│   ├── navigation.py        (Navigation/features)
│   └── results_page.py      (Results display)
│
├── pages/                   ← Data Collection
│   ├── user_inputs.py
│   ├── financial_inputs.py
│   └── family_inputs.py
│
├── visualization/           ← Charts & Graphs
│   ├── charts_basic.py
│   ├── charts_advanced.py
│   ├── timeline.py
│   └── longevity_analysis.py
│
├── healthcare/              ← Healthcare Module (DISABLED)
│   └── (not imported)
│
├── ai_advisor.py            ← AI Advisor (Direct Anthropic API)
├── simulation_core.py       ← Simulation Engine
├── monte_carlo.py           ← Monte Carlo Simulations
├── financial_utils.py       ← Financial Calculations
│
└── explain_api_server.py    ← Flask Server (OPTIONAL - NOT USED)
```

---

## 🎨 **How AI Advisor Works**

### **Current Implementation (Direct API)**

```python
# ai_advisor.py (line 2)
"Direct Claude API integration (no Flask server needed)"

# How it works:
1. User clicks "Ask AI Advisor"
2. Streamlit sends request directly to Anthropic API
3. Response comes back to Streamlit
4. Display in UI

# NO intermediate Flask server needed!
```

### **Old Implementation (Flask - NOT USED)**

```
❌ User → Streamlit → Flask API → Anthropic → Flask → Streamlit → User
✅ User → Streamlit → Anthropic → Streamlit → User
```

**We use the ✅ direct method!**

---

## 📋 **Render Deployment Checklist**

### **Step-by-Step**

- [ ] 1. Go to render.com
- [ ] 2. Click "New" → "Web Service"
- [ ] 3. Connect GitHub: `sergecastro/retirement-simulator`
- [ ] 4. Select branch: `refactor/modular-app-structure`
- [ ] 5. Set Root Directory: `family_retirement_no_OCR`
- [ ] 6. Set Build Command: `pip install -r requirements.txt`
- [ ] 7. Set Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- [ ] 8. Add Environment Variables:
  - `ANTHROPIC_API_KEY` = sk-ant-...
  - `DEMO_PASSWORD` = (your password)
  - `TRUSTED_USERS` = serge@emiramed.com
- [ ] 9. Click "Create Web Service"
- [ ] 10. Wait for deployment (3-5 minutes)
- [ ] 11. Copy Render URL (e.g., `forcash-abc123.onrender.com`)
- [ ] 12. Test URL in browser

---

## 🌐 **DNS Configuration (After Render Works)**

### **GoDaddy DNS Settings**

| Type | Host | Points To | TTL |
|------|------|-----------|-----|
| CNAME | @ | `forcash-abc123.onrender.com` | 600 |

**Or if CNAME doesn't work for @:**

| Type | Host | Points To | TTL |
|------|------|-----------|-----|
| A | @ | (Get from Render support) | 600 |
| CNAME | www | `forcash-abc123.onrender.com` | 600 |

**Wait:** 15-30 minutes for DNS propagation

---

## 🧪 **Post-Deployment Testing**

### **Test URLs**

1. ✅ Render URL works: `https://forcash-abc123.onrender.com`
2. ✅ Custom domain works: `https://forcash.ai`
3. ✅ SSL certificate valid (green padlock)

### **Test Features**

- [ ] Home page loads
- [ ] Can select INTAKE mode
- [ ] Can select Analysis mode
- [ ] Charts display correctly
- [ ] AI Advisor responds
- [ ] Scenario save/load works
- [ ] Authentication works

---

## ❓ **Common Questions**

### **Q: Do we need to deploy Flask separately?**
**A:** NO! Flask server not needed. Streamlit handles everything.

### **Q: What port should we use?**
**A:** Use `$PORT` - Render sets this automatically. Don't hardcode a port.

### **Q: How does AI Advisor work without Flask?**
**A:** Direct Anthropic API calls from Streamlit. See `ai_advisor.py` line 2.

### **Q: Why is Flask in requirements.txt if we don't use it?**
**A:** `explain_api_server.py` uses it, but that's an optional feature we're not deploying.

### **Q: Should we remove Flask from requirements.txt?**
**A:** No need - it doesn't hurt to have it. We just don't run the Flask server.

### **Q: Can we deploy on one service or need multiple?**
**A:** ONE SERVICE ONLY - Just the Streamlit app.

---

## 🔍 **Verification Commands**

### **Check if Deployment is Working**

```bash
# Health check (should return 200 OK)
curl https://forcash-abc123.onrender.com

# Check if Streamlit is running
curl -I https://forcash-abc123.onrender.com

# Expected response:
HTTP/2 200
server: streamlit
...
```

---

## 📊 **Architecture Comparison**

### **What We DON'T Have**

```
❌ Separate Flask service
❌ Multiple services
❌ Microservices architecture
❌ Docker containers
❌ Load balancer
❌ Separate AI API
```

### **What We DO Have**

```
✅ Single Streamlit app
✅ Direct Anthropic API integration
✅ Simple deployment
✅ One service, one port
✅ Automatic SSL from Render
✅ Environment variables for secrets
```

---

## 🚨 **Critical Information**

### **DO:**
- ✅ Deploy ONE Streamlit service to Render
- ✅ Use `--server.port=$PORT` in start command
- ✅ Set ANTHROPIC_API_KEY environment variable
- ✅ Point forcash.ai to Render URL via DNS

### **DON'T:**
- ❌ Deploy Flask server separately
- ❌ Hardcode port numbers
- ❌ Skip environment variables
- ❌ Deploy multiple services

---

## 📞 **Quick Reference**

| Item | Value |
|------|-------|
| **Service Type** | Web Service (Streamlit) |
| **Runtime** | Python 3.12 |
| **Framework** | Streamlit 1.36.0 |
| **Entry Point** | `app.py` |
| **Build** | `pip install -r requirements.txt` |
| **Start** | `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0` |
| **Port** | Auto ($PORT from Render) |
| **Domain** | forcash.ai (GoDaddy) |

---

## ✅ **Summary**

**Architecture:** Single Streamlit service
**Deployment:** One service to Render
**AI:** Direct Anthropic API (no Flask)
**Port:** Automatic from Render
**SSL:** Automatic from Render
**DNS:** Point forcash.ai to Render URL

**That's it! Simple, single-service deployment.**

---

**Last Updated:** October 23, 2025 @ 11:30 AM
**Author:** Claude Code
**Status:** Ready for deployment
