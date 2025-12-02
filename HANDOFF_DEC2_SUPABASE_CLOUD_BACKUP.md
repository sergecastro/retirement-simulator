# HANDOFF DOCUMENT - December 2, 2025 @ 7:45 PM PST
# SUPABASE CLOUD BACKUP FEATURE (IN PROGRESS)

---

## 🎯 WHAT WE'RE TRYING TO DO

### The Problem
Family Forecast stores all user data in **browser localStorage only**. This means:
- Data is lost if user clears browser cache
- Data can't be accessed from another device/browser
- No recovery option if device is lost

### The Solution
Add **optional cloud backup** using Supabase (PostgreSQL + Auth):
1. **Anonymous Vault** - 30-day trial, no email, just vault ID + password
2. **Free Account** - Unlimited, email-based, password recovery available

### Zero-Knowledge Encryption
- User's password encrypts data BEFORE it leaves the browser
- Supabase stores only encrypted blobs
- We (Family Forecast) can NEVER see user's financial data
- Same encryption standard as 1Password, Bitwarden, etc.

---

## 📊 CURRENT STATUS

### Branch: `feature/supabase-cloud-backup`
**NOT merged to master - safe to experiment**

### Commits on this branch:
```
a87bc7f End of day Dec 2 - cloud backup UI added to welcome
8c8dfc9 Remove accidental file
30c9bb7 Add supabase_sync module - TESTED WORKING
9740fbf Add password_crypto module - TESTED WORKING
```

### Files Created:

| File | Lines | Status | Purpose |
|------|-------|--------|---------|
| `utils/password_crypto.py` | 166 | ✅ TESTED | Password-based encryption (PBKDF2 + AES-256-GCM) |
| `utils/supabase_sync.py` | 369 | ✅ TESTED | Supabase API wrapper (create/load/update vaults) |
| `ui/cloud_backup_modal.py` | 329 | ✅ SYNTAX OK | UI modal for backup signup/restore |
| `requirements.txt` | +1 line | ✅ | Added `supabase>=2.0.0` |
| `app.py` | +45 lines | ⚠️ PARTIAL | Cloud backup section added to welcome screen |

### Supabase Database Ready:
- **URL:** `https://ebhzvauommuhqlcswdil.supabase.co`
- **Tables created:** `anonymous_vaults`, `user_vaults`
- **Test vault created:** `FF-ACTY-CJZ6` (proves connection works!)

---

## ✅ WHAT'S WORKING

1. **Password Crypto Module** - Fully tested
   - `generate_vault_id()` → `FF-X7K9-M2PL` format
   - `encrypt_with_password()` / `decrypt_with_password()`
   - Wrong password correctly rejected

2. **Supabase Sync Module** - Fully tested
   - `create_anonymous_vault()` → Creates encrypted vault in Supabase
   - `load_anonymous_vault()` → Retrieves and decrypts
   - Connection to Supabase confirmed working

3. **Cloud Backup Modal UI** - Component created
   - Multi-step flow: Choose → Anonymous/Account → Success
   - Restore modal for returning users

---

## ⏳ WHAT'S INCOMPLETE

### 1. Welcome Screen Integration (Partially Done)
The cloud backup section was added to `app.py` but the buttons don't DO anything yet:
```python
if st.button("Try Anonymous", key="welcome_anonymous"):
    st.session_state.show_backup_signup = 'anonymous'
    st.rerun()
```
**Missing:** The code to actually SHOW the signup modal when button is clicked.

### 2. Returning Users Can't See Cloud Backup
**Problem:** The welcome screen with cloud backup options is only shown to NEW users.
Returning users (who have localStorage data) skip directly to Analysis mode.

**Options:**
- A) Add "Cloud Backup" to sidebar (always visible)
- B) Add to Settings/Preferences page
- C) Add "Sync to Cloud" button on INTAKE Page 8 (Save section)
- D) Show a one-time "Enable Cloud Backup?" prompt after first save

### 3. Auto-Sync on Save Not Implemented
**Desired flow:**
1. User saves plan locally (existing behavior)
2. IF user has cloud backup enabled → automatically sync to Supabase
3. Show "Synced ☁️" indicator

### 4. Account Creation Flow
The `create_user_account()` function exists but:
- Email verification not tested
- Sign-in flow not fully wired up

---

## 🔧 ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                           │
├─────────────────────────────────────────────────────────────┤
│  1. User enters password                                    │
│  2. PBKDF2 derives encryption key (600,000 iterations)      │
│  3. AES-256-GCM encrypts data                               │
│  4. Only ENCRYPTED blob sent to Supabase                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SUPABASE (Cloud)                         │
├─────────────────────────────────────────────────────────────┤
│  anonymous_vaults table:                                    │
│  - vault_id (FF-XXXX-XXXX)                                  │
│  - salt (for key derivation)                                │
│  - encrypted_data (we can NEVER decrypt this)               │
│  - expires_at (30 days for trial)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 OPTIONS FOR TOMORROW

### Option A: Complete the Welcome Screen Flow
1. Wire up "Try Anonymous" button → show anonymous signup modal
2. Wire up "Create Free Account" button → show account creation modal
3. Wire up restore expander → actually restore data to session_state
4. Test full flow: New user → Anonymous backup → Get vault ID

### Option B: Add Cloud Backup to INTAKE Page 8
Add cloud backup option AFTER the local save:
```
[SAVE PLAN] button (existing)
    ↓
"Plan saved locally!"
    ↓
[☁️ Also backup to cloud?] (new)
```
This way ALL users see it, not just new users.

### Option C: Add Cloud Backup to Sidebar
Add a persistent "☁️ Cloud Backup" section in sidebar:
- For users without backup: "Enable Cloud Backup"
- For users with backup: "Last synced: Dec 2, 2025"

### Option D: Defer and Focus on Other Launch Blockers
The cloud backup is a NICE-TO-HAVE, not a launch blocker.
Could complete other items first:
- SS Reset Button
- SS Taxation accuracy
- Medigap Comparison polish

---

## ⚠️ IMPORTANT NOTES FOR NEXT SESSION

1. **Branch Safety:** We're on `feature/supabase-cloud-backup`, NOT master
2. **Master has unpushed commits:** Security fix + handoff doc (2 commits ahead)
3. **Supabase credentials are in the code** - This is the ANON key (public, safe)
4. **Test vault exists:** `FF-ACTY-CJZ6` with password `TestPass123`

---

## 🔒 MASTER BRANCH STATUS

Master has 2 unpushed commits:
```
b73e81e Before Supabase integration - Dec 2 2025 5:32 PM (landing page disclosures)
63ea900 SECURITY FIX: Disable disk cache on production - localhost only
```

**These should be pushed before merging any new features.**

---

## 📞 QUESTIONS FOR SERGE

1. Which option for tomorrow? (A, B, C, or D)
2. Should we push master's security fix to production first?
3. Priority: Cloud backup vs other launch blockers?

---

## END OF HANDOFF

**Document Created:** December 2, 2025 @ 7:45 PM PST
**Branch:** feature/supabase-cloud-backup
**Author:** Claude Code
