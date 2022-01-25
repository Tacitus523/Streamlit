from turtle import onclick
import streamlit as st
import pandas as pd
import json
from DatabaseAppHelper import *
from DatabaseAppBackend import *
import time

st.set_page_config(page_title="wfk-Datenbank",layout='centered',menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     })

if 'product_index' not in st.session_state:
    st.session_state.product_index = None
    

uploaded_database, product_search = display_sidebar()

database_dict = load_database(uploaded_database)
display_database_details(database_dict)
display_query_result(database_dict, product_search)


if st.session_state.product_index is None:
    st.stop()
