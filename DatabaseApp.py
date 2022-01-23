from turtle import onclick
import streamlit as st
import pandas as pd
import json
from DatabaseAppHelper import *

if 'product_index' not in st.session_state:
    st.session_state.product_index = None
    
def handle_buttonpress(x):
    st.session_state.product_index = x

with st.sidebar:
    st.header("Datenbank-Auswahl")
    uploaded_file = st.file_uploader("Datenbank auswählen",type="json")
    product_search = st.text_input('Produkt suchen')
    
if uploaded_file is None or product_search is None:
    st.stop()
    
st.header("wfk-Daten")
data = json.load(uploaded_file)
query_result = data.get(product_search)
if query_result is None:
    st.write("Keine Daten verfügbar")
    st.stop()

detail_data = [pd.DataFrame(query_result[i].get("Details"),index=[i]) for i in range(len(query_result))]
detail_df = pd.concat(detail_data)

# # Show user table 
colms = st.columns((1, 2, 1, 1, 1, 1))
fields = ["Index",'Produktname','Konzentration','Temperatur','Datum']
for col, field_name in zip(colms, fields):
    # header
    col.write(field_name)

for x, email in enumerate(detail_df['Produktname']):
    col1, col2, col3, col4, col5, col6 = st.columns((1, 2, 1, 1, 1, 1))
    col1.write(x)  # index
    col2.write(detail_df['Produktname'][x])  # Produktname
    col3.write(detail_df['Konzentration'][x])  # Konzentration
    col4.write(detail_df['Temperatur'][x])   # Temperatur
    col5.write(detail_df['Datum'][x]) # Datum
    button_phold = col6.empty()  # create a placeholder
    do_action = button_phold.button("Details",on_click=handle_buttonpress, args = (x,), key=x)
    if do_action:
        pass


if st.session_state.product_index is None:
    st.stop()
st.write(st.session_state.product_index)