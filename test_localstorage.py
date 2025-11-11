import streamlit as st
from streamlit_browser_storage import LocalStorage

localS = LocalStorage(key="test_key")

if st.button("Set value"):
    localS.set("my_key", "my_value")
    st.write("Set")

value = localS.get("my_key")
st.write("Value:", value)