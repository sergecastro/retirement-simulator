# test_simple_storage.py - SIMPLEST possible test of streamlit-local-storage
"""
Ultra-simple test to verify if streamlit-local-storage library works AT ALL.
No encryption, no complexity - just raw localStorage read/write.
"""

import streamlit as st
from streamlit_local_storage import LocalStorage

st.title("SIMPLE localStorage Test")

# Initialize localStorage
if 'localS' not in st.session_state:
    st.session_state.localS = LocalStorage()
    st.info("LocalStorage initialized")

localS = st.session_state.localS

st.divider()

# SAVE TEST
st.header("1. SAVE Test")
if st.button("Save 'Hello World' to localStorage"):
    try:
        localS.setItem("simple_test", "Hello World from Streamlit!")
        st.success("Called localS.setItem('simple_test', 'Hello World from Streamlit!')")
        st.info("Check DevTools (F12 → Application → Local Storage) for key 'simple_test'")
    except Exception as e:
        st.error(f"ERROR: {e}")
        import traceback
        st.code(traceback.format_exc())

st.divider()

# LOAD TEST
st.header("2. LOAD Test")
if st.button("Load from localStorage"):
    try:
        value = localS.getItem("simple_test")
        if value:
            st.success(f"LOADED (raw): {value}")
            st.write(f"Type: {type(value)}")

            # If it's a dict, extract the value
            if isinstance(value, dict):
                st.info(f"It's a dict! Keys: {list(value.keys())}")
                if "simple_test" in value:
                    actual_value = value["simple_test"]
                    st.success(f"Extracted value: {actual_value}")
        else:
            st.warning("Nothing found (returned None or empty)")
    except Exception as e:
        st.error(f"ERROR: {e}")
        import traceback
        st.code(traceback.format_exc())

st.divider()

st.header("3. Instructions")
st.write("""
**How to test:**

1. Click "Save 'Hello World' to localStorage"
2. Press F12 to open DevTools
3. Go to Application tab → Local Storage → http://localhost:8502
4. **Look for key: `simple_test`**
5. **Does it exist? What's the value?**

If you see `simple_test` key with value, then streamlit-local-storage WORKS!
If you don't see it, then the library is NOT working.
""")
