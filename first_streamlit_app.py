import streamlit as st
import pandas as pd
import json

st.markdown('''
## Hello World

This is my first streamlit app

*Italic*

**Bold**

***Bold and italic***

''')

st.sidebar.header("A Header")

uploaded_file = st.sidebar.file_uploader("Choose a databank")
if uploaded_file is not None:
    data = json.load(uploaded_file)
    st.header("wfk-Daten")
    st.write(pd.DataFrame(data["Neodisher Gigazyme"][0]["Details"],index=pd.RangeIndex(0,1)))
