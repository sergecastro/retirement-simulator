# test_localstorage_keys.py
import streamlit as st
import json
from streamlit_javascript import st_javascript

st.title("localStorage Keys Inspector")

# Always run this - it will auto-rerun once to get the value
result = st_javascript("""
    JSON.stringify(Object.keys(localStorage))
""")

st.write("**All localStorage keys:**")

if result == 0:
    st.warning("Waiting for JS to execute... (will auto-refresh)")
else:
    try:
        keys = json.loads(result)
        for key in keys:
            st.write(f"- `{key}`")
        st.success(f"Found {len(keys)} keys")
    except:
        st.code(result)

st.divider()

# Show specific values we care about
st.write("**Cloud backup credentials:**")
email = st_javascript("localStorage.getItem('ff_user_email')")
vault = st_javascript("localStorage.getItem('ff_vault_id')")

if email != 0:
    st.write(f"- ff_user_email: `{email}`")
if vault != 0:
    st.write(f"- ff_vault_id: `{vault}`")
