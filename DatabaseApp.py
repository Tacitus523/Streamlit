import streamlit as st
from DatabaseAppHelper import *
from DatabaseAppBackend import *

print("Welcome back, Commander")
st.set_page_config(page_title="wfk-Datenbank",layout='centered',menu_items={
         #'Get Help': 'https://www.extremelycoolapp.com/help',
         #'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "This is my *first* project with streamlit. I hope it can help you out."
     })

with open("style.css","r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

if not 'product_index' in st.session_state:
    st.session_state.product_index = None
if not 'database' in st.session_state:
    st.session_state.database = None
if not 'addition_task' in st.session_state:
    st.session_state.addition_task = False
    
database_dict, product_search = display_sidebar()

query_result = display_query_result(database_dict, product_search)

if st.session_state.product_index is None:
    st.stop()
else:
    product_index = st.session_state.product_index

measurements = query_result[product_index]
calibration_data, calibration_amount = retrieve_calibration_data(measurements)
slope, ordinate, r_value, calibration_graph = calculate_calibrations(calibration_data)
measurement_data, blind_data = retrieve_measurement_data(measurements)
protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung = wfk_evaluation(measurements, slope)
evaluation_graph = figure_wfk_evaluation(measurements, protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung)

display_evaluation_graph(evaluation_graph)
display_query_calibration(calibration_data, calibration_amount, slope, ordinate, r_value, calibration_graph)
display_query_measurement(measurement_data, blind_data)


