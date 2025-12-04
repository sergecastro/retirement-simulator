"""
Test script for safe localStorage read.
Run with: streamlit run test_safe_read.py

SIMPLE - just read one value, no JSON complexity
"""

import streamlit as st
from streamlit_javascript import st_javascript

st.title("Safe localStorage Read Test")

st.divider()

# Read just test_key first - simplest possible
st.subheader("Reading test_key:")
test_val = st_javascript("localStorage.getItem('test_key')")
st.write(f"test_key = `{test_val}` (type: {type(test_val).__name__})")

st.subheader("Reading ff_user_email:")
email_val = st_javascript("localStorage.getItem('ff_user_email')")
st.write(f"ff_user_email = `{email_val}` (type: {type(email_val).__name__})")

st.subheader("Reading ff_vault_id:")
vault_val = st_javascript("localStorage.getItem('ff_vault_id')")
st.write(f"ff_vault_id = `{vault_val}` (type: {type(vault_val).__name__})")

st.divider()

# Summary
if test_val != 0 and email_val != 0 and vault_val != 0:
    st.success("All reads complete!")
    if email_val or vault_val:
        st.success("User has backup credentials!")
else:
    st.warning("Some values still loading (showing 0)... click anywhere or wait")
