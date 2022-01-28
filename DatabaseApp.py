import streamlit as st
from DatabaseAppHelper import *
from DatabaseAppBackend import *

st.set_page_config(page_title="wfk-Datenbank",layout='centered',menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     })

with open("style.css","r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)



if 'product_index' not in st.session_state:
    st.session_state.product_index = None
    

database_dict, product_search = display_sidebar()


query_result = display_query_result(database_dict, product_search)
if st.session_state.product_index is None:
    st.stop()
else:
    product_index = st.session_state.product_index
slope = display_query_calibration(query_result[product_index])
display_query_measurement(query_result[product_index], slope)


