# test_localstorage_read.py
# Manual test to read localStorage WITHOUT triggering rerun loops
import streamlit as st
from streamlit_browser_storage import LocalStorage

st.title("🔬 localStorage Test")
st.write("This test reads localStorage ONLY when you click the button.")
st.write("No automatic reads = no rerun loops.")

st.divider()

# Only create LocalStorage when button is clicked
if st.button("🔍 Read localStorage NOW", type="primary"):
    st.write("Creating LocalStorage instance...")
    ls = LocalStorage(key="test_read_manual")

    st.write("---")
    st.subheader("1. Reading ff_snapshots_index")
    try:
        data = ls.get("ff_snapshots_index")
        st.write(f"**Data type:** `{type(data).__name__}`")
        if data:
            st.write(f"**Data length:** {len(data)} chars")
            st.write(f"**First 300 chars:**")
            st.code(data[:300] if len(data) > 300 else data)
        else:
            st.error("ff_snapshots_index returned None/empty")
    except Exception as e:
        st.error(f"Error reading ff_snapshots_index: {e}")

    st.write("---")
    st.subheader("2. Reading ff_encryption_key")
    try:
        key_data = ls.get("ff_encryption_key")
        st.write(f"**Data type:** `{type(key_data).__name__}`")
        if key_data:
            st.write(f"**Key length:** {len(key_data)} chars")
            st.write(f"**First 50 chars:** `{key_data[:50]}...`")
        else:
            st.error("ff_encryption_key returned None/empty")
    except Exception as e:
        st.error(f"Error reading ff_encryption_key: {e}")

    st.write("---")
    st.subheader("3. Try to decrypt ff_snapshots_index")
    if data and key_data:
        try:
            import base64
            import json
            from cryptography.fernet import Fernet

            # Decode the key
            key_bytes = base64.b64decode(key_data)
            fernet = Fernet(key_bytes)

            # Decrypt the data
            decrypted = fernet.decrypt(data.encode()).decode()
            index = json.loads(decrypted)

            st.success("✅ Decryption successful!")
            st.write(f"**Number of snapshots:** {len(index.get('snapshots', []))}")
            st.write(f"**Current snapshot ID:** {index.get('current_snapshot_id')}")

            st.write("**Snapshots:**")
            for snap in index.get('snapshots', []):
                st.write(f"  - `{snap.get('id')}`: {snap.get('name')}")
        except Exception as e:
            st.error(f"Decryption failed: {e}")
            import traceback
            st.code(traceback.format_exc())

st.divider()
st.caption("Click the button above to manually trigger localStorage read.")
st.caption("If data exists in F12 > Application > localStorage, it should appear here.")
