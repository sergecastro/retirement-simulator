# CRITICAL: Lovable → Streamlit Data Flow Problem
## December 15, 2025 - NEED EXTERNAL HELP

---

## Executive Summary

We spent a full day building a beautiful Lovable (React) INTAKE form that collects user financial data. The Streamlit backend handles encryption and Supabase storage. **But we completely missed the fact that the data collected in Lovable NEVER reaches Streamlit for encryption and storage.**

**95% of the work is done. The missing 5% breaks everything.**

---

## The Architecture We Built

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LOVABLE (React/TypeScript)                       │
│  ┌─────────────────────────┐    ┌─────────────────────────────────────┐ │
│  │   LANDING PAGE          │    │   INTAKE                            │ │
│  │   familyforecast.ai     │───▶│   intake.familyforecast.ai/intake   │ │
│  │                         │    │                                     │ │
│  │   - User can register   │    │   - 6 pages of data collection      │ │
│  │   - Creates vault in    │    │   - Saves to Lovable localStorage   │ │
│  │     Supabase (EMPTY)    │    │   - "Continue to Analysis" button   │ │
│  └─────────────────────────┘    └──────────────────┬──────────────────┘ │
└────────────────────────────────────────────────────┼────────────────────┘
                                                     │
                                                     ▼
                                    ?mode=Analysis&vault_id=FF-XXXX-XXXX
                                                     │
┌────────────────────────────────────────────────────┼────────────────────┐
│                         STREAMLIT (Python)         │                    │
│                         app.familyforecast.ai      ▼                    │
│                                                                          │
│   - Receives vault_id ✅                                                │
│   - Prompts for password ✅                                             │
│   - Has encryption code ✅                                              │
│   - Has Supabase sync code ✅                                           │
│                                                                          │
│   BUT: HAS NO DATA TO ENCRYPT! ❌                                       │
│                                                                          │
│   The INTAKE data is stuck in Lovable's localStorage                    │
│   which Streamlit CANNOT access (different domain)                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Technical Problem

### localStorage Is Domain-Specific

```javascript
// Lovable INTAKE (intake.familyforecast.ai) saves:
localStorage.setItem('intake_data', JSON.stringify({
  input_user_name: "John Smith",
  input_age: 65,
  input_salary_wages: 120000,
  // ... 50+ fields
}));

// Streamlit (app.familyforecast.ai) tries to read:
localStorage.getItem('intake_data');  // Returns NULL!

// WHY? Different subdomain = different localStorage bucket
// intake.familyforecast.ai localStorage ≠ app.familyforecast.ai localStorage
```

### What We Have Working

1. **Lovable Landing Page** - Creates empty vault in Supabase ✅
2. **Lovable INTAKE** - Beautiful 6-page form, collects all data ✅
3. **URL Parameter Passing** - vault_id passes to Streamlit ✅
4. **Streamlit Password Prompt** - Asks for password when vault_id present ✅
5. **Streamlit Encryption** - AES-256-GCM with PBKDF2 (600K iterations) ✅
6. **Streamlit Supabase Sync** - Can save/load encrypted data ✅

### What's BROKEN

**The actual user data never leaves Lovable's localStorage.**

When user clicks "Continue to Analysis":
- Lovable sends: `?mode=Analysis&vault_id=FF-XXXX-XXXX`
- Lovable does NOT send: The actual intake data

Streamlit receives the vault_id but has NOTHING to encrypt and save.

---

## The Encryption Architecture (Why We Can't Just "Send Data")

### Our Security Promise

We promise users "zero-knowledge encryption" - data is encrypted BEFORE leaving their device, using their password as the key. We (the server) can NEVER see their financial data.

### The Encryption Code (Python - Streamlit side)

```python
# File: utils/password_crypto.py

SALT_LENGTH = 32
NONCE_LENGTH = 12
KEY_LENGTH = 32
PBKDF2_ITERATIONS = 600_000  # High iteration count for security

def generate_salt() -> str:
    """Generate a random salt for key derivation."""
    salt_bytes = secrets.token_bytes(SALT_LENGTH)
    return base64.b64encode(salt_bytes).decode('utf-8')

def derive_key_from_password(password: str, salt: str) -> bytes:
    """Derive encryption key from password using PBKDF2."""
    salt_bytes = base64.b64decode(salt.encode('utf-8'))

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt_bytes,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )

    return kdf.derive(password.encode('utf-8'))

def encrypt_with_password(plaintext: str, password: str, salt: str) -> str:
    """Encrypt data using password-derived key."""
    key = derive_key_from_password(password, salt)
    nonce = secrets.token_bytes(NONCE_LENGTH)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)

    encrypted_bytes = nonce + ciphertext
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def decrypt_with_password(encrypted_data: str, password: str, salt: str) -> str:
    """Decrypt data using password-derived key."""
    key = derive_key_from_password(password, salt)

    encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
    nonce = encrypted_bytes[:NONCE_LENGTH]
    ciphertext = encrypted_bytes[NONCE_LENGTH:]

    aesgcm = AESGCM(key)
    plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)

    return plaintext_bytes.decode('utf-8')
```

### The Supabase Sync Code (Python - Streamlit side)

```python
# File: utils/supabase_sync.py

def create_anonymous_vault(password: str, data: dict) -> Tuple[str, str]:
    """Create an anonymous vault with encrypted data."""
    client = get_supabase_client()

    # Generate vault ID and salt
    vault_id = generate_vault_id()  # "FF-XXXX-XXXX" format
    salt = generate_salt()

    # Encrypt the data
    json_data = json.dumps(data)
    encrypted_data = encrypt_with_password(json_data, password, salt)

    # Calculate expiration
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()

    # Store in Supabase
    result = client.table('anonymous_vaults').insert({
        'vault_id': vault_id,
        'salt': salt,
        'encrypted_data': encrypted_data,
        'expires_at': expires_at
    }).execute()

    return vault_id, f"Vault created! Expires in 30 days."

def auto_sync_to_cloud(data: dict) -> Tuple[bool, str]:
    """Automatically sync data to cloud if user has credentials."""
    password = st.session_state.get('cloud_password')
    if not password:
        return True, "No cloud backup configured"

    vault_id = st.session_state.get('vault_id')
    if vault_id:
        success, message = update_anonymous_vault(vault_id, password, data)
        return success, message

    return False, "No vault configured"
```

---

## Options We Considered (And Why They Don't Work)

### Option 1: Pass Data via URL Parameters ❌

```
https://app.familyforecast.ai?mode=Analysis&vault_id=XXX&data=BASE64_JSON
```

**Problems:**
- URL length limit (~2000 chars, our data is 5000+ chars)
- Sensitive financial data in URL (appears in browser history, server logs)
- Violates our security promise

### Option 2: Implement JavaScript Encryption in Lovable ❌

We could write the same encryption in JavaScript:

```javascript
// Would need to match Python EXACTLY:
// - PBKDF2 with 600,000 iterations
// - Same salt format (base64 encoded 32 bytes)
// - Same nonce extraction (first 12 bytes)
// - Same AES-GCM parameters
// - Same base64 encoding

// If ANY of these differ by even 1 bit → DATA LOSS
```

**Problems:**
- High risk of encryption mismatch between Python and JavaScript
- Two codebases to maintain for crypto (security nightmare)
- If they ever diverge, users lose access to their data

### Option 3: Keep Using Streamlit INTAKE ❌

Just don't use Lovable INTAKE at all.

**Problems:**
- Wasted all the Lovable work
- Users hated Streamlit INTAKE (high bounce rate)
- That's why we built Lovable INTAKE in the first place

---

## What We Need Help With

We need a secure way to:

1. **Transfer intake data from Lovable to Streamlit** across different subdomains
2. **Without exposing sensitive data** in URLs or unencrypted requests
3. **While keeping encryption in Python** (single source of truth)

### Possible Approaches to Explore

**A. Supabase as Intermediary (Temporary Unencrypted Storage)**
- Lovable saves raw data to Supabase "pending_intake" table
- Streamlit reads it, encrypts it, moves to encrypted vault
- Delete pending data immediately after encryption
- Risk: Brief window of unencrypted data in Supabase

**B. Streamlit API Endpoint**
- Streamlit exposes a POST endpoint
- Lovable POSTs data to Streamlit
- Streamlit encrypts and stores
- Challenge: Streamlit isn't designed for API endpoints

**C. Shared Cookie/Session**
- Use a parent domain cookie (familyforecast.ai)
- Both subdomains can read it
- Challenge: Cookie size limits, complexity

**D. PostMessage with iframe**
- Embed Streamlit in Lovable iframe temporarily
- Use postMessage to transfer data
- Challenge: CSP issues, complexity

**E. Server-Side Session (Redis/Supabase)**
- Generate session token on Lovable
- Store data server-side with token
- Streamlit retrieves by token
- Then encrypts and stores properly

---

## Files to Review

### Lovable Side (React/TypeScript)
We don't have direct access to Lovable code from this repository. The Lovable projects are:
- Landing Page: familyforecast.ai
- INTAKE: intake.familyforecast.ai

### Streamlit Side (Python)

**Critical files:**

1. `utils/password_crypto.py` - Encryption/decryption functions
2. `utils/supabase_sync.py` - Supabase operations
3. `app.py` - URL parameter handling (lines 345-400)
4. `ui/cloud_backup_modal.py` - Password prompt modal

---

## Current Supabase Schema

```sql
-- Anonymous vaults table
CREATE TABLE anonymous_vaults (
    id SERIAL PRIMARY KEY,
    vault_id VARCHAR(15) UNIQUE NOT NULL,  -- "FF-XXXX-XXXX"
    salt VARCHAR(64) NOT NULL,              -- Base64 encoded 32 bytes
    encrypted_data TEXT,                    -- AES-256-GCM encrypted JSON
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);

-- User accounts table
CREATE TABLE user_data (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email VARCHAR(255) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    encrypted_data TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Summary

| Component | Status |
|-----------|--------|
| Lovable Landing Page | ✅ Working |
| Lovable INTAKE (data collection) | ✅ Working |
| Lovable → Streamlit redirect | ✅ Working |
| URL credential passing (vault_id) | ✅ Working |
| Streamlit password prompt | ✅ Working |
| Streamlit encryption code | ✅ Working |
| Streamlit Supabase sync | ✅ Working |
| **DATA TRANSFER BETWEEN APPS** | ❌ **BROKEN** |

The data sits in Lovable's localStorage and never reaches Streamlit for encryption.

---

## Our Security Requirements

1. **Zero-knowledge encryption** - Server never sees plaintext data
2. **Password-based encryption** - User's password is the only key
3. **Single encryption codebase** - Python only (no JS crypto)
4. **HTTPS everywhere** - All data in transit is TLS encrypted
5. **No sensitive data in URLs** - No financial data in browser history

---

## Question for External Help

**How can we securely transfer ~5KB of JSON data from Lovable (intake.familyforecast.ai) to Streamlit (app.familyforecast.ai) so that Streamlit can encrypt it and store it in Supabase?**

Constraints:
- Cannot use URL parameters (too long, security risk)
- Cannot implement JS encryption (mismatch risk)
- Must maintain zero-knowledge promise
- Preferably no major architectural changes

---

## Contact

This document was created by Claude Code for the Family Forecast project.
Date: December 15, 2025

The development team has been working on this integration for a full day and needs a fresh perspective on the data transfer problem.
