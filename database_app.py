import streamlit as st
from database_app_frontend import *
from database_app_backend import *

st.set_page_config(page_title="wfk-Datenbank",layout='centered',menu_items={
         'Get Help': 'https://github.com/Tacitus523/Streamlit',
         'Report a bug': "https://github.com/Tacitus523/Streamlit",
         'About': '''
This is my *first* project with streamlit. I hope it can help you out.
You should check out the ReadMe under the Get Help link to get examples
for the required formatting of excel-imports and example json-databases.
'''
     })

with open("style.css","r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

if not 'product_index' in st.session_state:
    st.session_state.product_index = None
if not 'database' in st.session_state:
    st.session_state.database = None
if not 'addition_task' in st.session_state:
    st.session_state.addition_task = False


with st.sidebar:
    #Laden oder neu anlegen
    options = ('Laden', 'Neu')
    option = display_dataset_options(options)
    #Neue Datenbank anlegen
    if option == options[1]:
        if st.session_state.database is None:
            st.session_state.database = {}
    #Bestehende Datenbank laden
    else:
        uploaded_database = display_dataset_upload()
        if uploaded_database is None:
            st.stop()
        elif st.session_state.database is None:
            st.session_state.database, validation_result, validation_comment = load_database(uploaded_database)
            if validation_result == False:
                st.write(validation_comment)
                st.session_state.database = None
                st.stop()
                
    #Datenbank aus session-state laden, um mehrere Erweiterungen zuzulassen             
    database_dict = st.session_state.database
    
    #Vorhandene Einträge von Reiniger-Produkten
    unique_names = retrieve_unique_names(database_dict)
    display_unique_names(unique_names)
    
    #Reiniger-Eintrag suchen
    product_search = display_product_search()
    
    #Weitere Einträge hinzufügen
    database_addition = display_database_addition()
        
    #Erweiterte Datenbank herunterladen
    if st.session_state.addition_task:
        succesful_addition = import_wfk_data_from_excel(database_addition, database_dict)
        if succesful_addition:
            st.write("Datensatz erfolgreich hinzugefügt! Weitere Daten hochladen oder Datenbank herunterladen")
            database_json = prepare_download(database_dict)
            display_database_download(database_json)
        else:
            st.write("Eintrag falsch formatiert oder bereits vorhanden")
        st.session_state.addition_task = False

if product_search == '':
    st.stop()
    
query_result = retrieve_query_result(database_dict, product_search)
detail_df = retrieve_query_details(query_result)

display_query_result(detail_df)

if st.session_state.product_index is None:
    st.stop()
    
measurements = query_result[st.session_state.product_index]
calibration_data, calibration_amount = retrieve_calibration_data(measurements)
slope, ordinate, r_value, calibration_graph = calculate_calibrations(calibration_data)
measurement_data, blind_data = retrieve_measurement_data(measurements)
protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung = wfk_evaluation(measurements, slope)
evaluation_graph = figure_wfk_evaluation(measurements, protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung)

display_evaluation_graph(evaluation_graph)
display_query_calibration(calibration_data, calibration_amount, slope, ordinate, r_value, calibration_graph)
display_query_measurement(measurement_data, blind_data)


