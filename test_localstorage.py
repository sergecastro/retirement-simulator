# test_localstorage.py - Test localStorage with CookieManager
"""
Simple test app to verify localStorage READ/WRITE works.

Run with: streamlit run test_localstorage.py
"""

import streamlit as st
from streamlit_local_storage import LocalStorage
from utils.encryption import encrypt_data, decrypt_data

st.title("localStorage Test App - AES-256 ENCRYPTED")

st.write("This app tests if localStorage READ/WRITE works after browser close.")
st.success("🔒 Data protected with AES-256-GCM Bank-Grade Encryption!")

# Initialize localStorage INLINE (like the working simple test)
if 'localS' not in st.session_state:
    st.session_state.localS = LocalStorage()

localS = st.session_state.localS

# Show persistent status at top
if 'save_result' in st.session_state or 'load_result' in st.session_state:
    st.success("STATUS INDICATOR IS WORKING - Messages persist across reruns!")

    if 'save_result' in st.session_state:
        st.info(f"Last SAVE: {st.session_state.save_result}")

    if 'load_result' in st.session_state:
        st.info(f"Last LOAD: {st.session_state.load_result}")

# Add a clear button to reset message state
if st.button("Clear Messages"):
    if 'save_result' in st.session_state:
        del st.session_state.save_result
    if 'save_data' in st.session_state:
        del st.session_state.save_data
    if 'load_result' in st.session_state:
        del st.session_state.load_result
    if 'load_data' in st.session_state:
        del st.session_state.load_data
    if 'load_message' in st.session_state:
        del st.session_state.load_message
    st.rerun()

st.divider()

# Test data
test_data = {
    "user_name": "Test User",
    "age": 65,
    "balance": 500000.0,
    "test_timestamp": st.session_state.get('test_timestamp', 'Not set')
}

# Set timestamp on first run
if 'test_timestamp' not in st.session_state:
    from datetime import datetime
    st.session_state.test_timestamp = datetime.now().isoformat()
    test_data["test_timestamp"] = st.session_state.test_timestamp

# SAVE TEST
st.header("SAVE Test")
if st.button("Save to localStorage"):
    with st.spinner("Encrypting and saving..."):
        try:
            # Encrypt data (this generates/loads the encryption key)
            encrypted_string = encrypt_data(test_data, localS)

            # Save encryption key if it's new (to avoid duplicate key error)
            if st.session_state.get('encryption_key_needs_save', False):
                localS.setItem('ff_encryption_key', st.session_state.encryption_key_b64)
                st.session_state.encryption_key_needs_save = False
                print("[OK] Saved encryption key to localStorage")

            # Save encrypted data
            localS.setItem('test_data', encrypted_string)

            st.session_state.save_result = "SUCCESS"
            st.session_state.save_data = test_data
            print(f"[OK] Saved AES-256 encrypted data to browser localStorage: test_data")
        except Exception as e:
            st.session_state.save_result = f"ERROR: {e}"
            print(f"[ERROR] Failed to save: {e}")
            import traceback
            traceback.print_exc()

# Show save result if it exists
if 'save_result' in st.session_state:
    if st.session_state.save_result == "SUCCESS":
        st.success("SAVE SUCCESS! Data encrypted with AES-256-GCM and saved to browser localStorage!")
        st.json(st.session_state.save_data)
        st.info("🔒 Your data is protected with bank-grade encryption!")
        st.info("Now try: 1) Click LOAD button below, 2) Close browser, 3) Reopen and click LOAD")
    elif st.session_state.save_result == "FAILED":
        st.error("Save failed! Check Python console for details.")
    else:
        st.error(st.session_state.save_result)

st.divider()

# LOAD TEST
st.header("LOAD Test")
if st.button("Load from localStorage"):
    with st.spinner("Loading and decrypting..."):
        try:
            # Load encrypted string and decrypt with persistent key
            encrypted_string = localS.getItem('test_data')
            if encrypted_string:
                loaded_data = decrypt_data(encrypted_string, localS)
                if loaded_data:
                    st.session_state.load_result = "SUCCESS"
                    st.session_state.load_data = loaded_data
                    # Compare timestamps
                    if loaded_data.get('test_timestamp') == test_data.get('test_timestamp'):
                        st.session_state.load_message = "CURRENT"
                    else:
                        st.session_state.load_message = f"PREVIOUS: {loaded_data.get('test_timestamp')}"
                    print(f"[OK] Loaded and decrypted AES-256 data from browser localStorage: test_data")
                else:
                    st.session_state.load_result = "DECRYPT_FAILED"
                    print(f"[ERROR] Decryption failed")
            else:
                st.session_state.load_result = "NOT_FOUND"
                print(f"[INFO] No data found in browser localStorage: test_data")
        except Exception as e:
            st.session_state.load_result = f"ERROR: {e}"
            import traceback
            st.session_state.load_traceback = traceback.format_exc()
            print(f"[ERROR] Failed to load: {e}")

# Show load result if it exists
if 'load_result' in st.session_state:
    if st.session_state.load_result == "SUCCESS":
        st.success("LOAD SUCCESS! Data loaded from browser localStorage!")
        st.json(st.session_state.load_data)
        if st.session_state.load_message == "CURRENT":
            st.info("Data matches current session (saved just now)")
        else:
            st.warning(st.session_state.load_message)
            st.success("PERSISTENCE WORKS! Browser localStorage survived browser close!")
    elif st.session_state.load_result == "NOT_FOUND":
        st.error("No data found in localStorage")
        st.warning("This could mean: You haven't saved yet, or you cleared localStorage")
    else:
        st.error(st.session_state.load_result)
        if 'load_traceback' in st.session_state:
            st.code(st.session_state.load_traceback)

st.divider()

# INSTRUCTIONS
st.header("Test Instructions")

st.write("""
**Test Plan:**
1. Click "Save to localStorage" - should see success indicator at top
2. Click "Load from localStorage" - should see same data
3. **Close browser completely**
4. **Reopen browser** to this page
5. Click "Load from localStorage" - should see saved data from previous session!

**Expected Result:**
- Data should persist after browser close
- Timestamp should show data from previous session
""")

st.divider()

st.header("DEBUG: Check Browser localStorage Directly")
st.write("""
If status messages aren't working, you can verify localStorage directly:

**Open Browser DevTools:**
1. Press F12 (or right-click → Inspect)
2. Go to "Application" tab (Chrome) or "Storage" tab (Firefox)
3. Click "Local Storage" in left sidebar
4. Select http://localhost:8502
5. Look for key: `test_data`

**What you should see:**
- Key: `test_data`
- Value: Long encrypted string (base64)

**Test:**
- Click "Save to localStorage" button above
- Check DevTools - should see `test_data` appear
- Refresh page - should still be there
- Close browser completely
- Reopen browser and go back to http://localhost:8502
- Check DevTools - should STILL be there (THIS is persistence!)
""")
