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
    

database_dict, product_search = display_sidebar()


query_result = display_query_result(database_dict, product_search)
display_query_contents(query_result)


