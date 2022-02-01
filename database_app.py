import logging
import streamlit as st
import sys
from database_app_frontend import *
from database_app_backend import *
from excel_import import import_wfk_data_from_excel, prepare_download

my_logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("dataset_logs.log")
file_handler.setLevel(logging.WARNING)
file_formatter = logging.Formatter("[%(asctime)s] {%(levelname)s} %(name)s: #%(lineno)d - %(message)s")
file_handler.setFormatter(file_formatter)
my_logger.addHandler(file_handler)

my_logger.info('''
------------------
---APP STARTED----
------------------
''')

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
    if option == options[1]:
        #Neue Datenbank anlegen
        if st.session_state.database is None:
            my_logger.info("New Database created")
            st.session_state.database = {}
            
    #Bestehende Datenbank laden
    else:
        uploaded_database = display_dataset_upload()
        if uploaded_database is None:
            my_logger.handlers.clear()
            st.stop()
        elif st.session_state.database is None:
            my_logger.info("Attempting to load database")
            st.session_state.database, validation_status, validation_comment = load_database(uploaded_database)
            if validation_status == False:
                my_logger.warning("Attempt to load database failed: " + validation_comment)
                st.write(validation_comment)
                st.session_state.database = None
                my_logger.handlers.clear()
                st.stop()
            my_logger.info("Loaded database")
                
    #Datenbank aus session-state laden, um mehrere Erweiterungen zuzulassen             
    database_dict = st.session_state.database
    
    #Vorhandene Einträge von Reiniger-Produkten
    my_logger.info("Attempting to retrieve unique names")
    unique_names = retrieve_unique_names(database_dict)
    my_logger.info("Retrieved unique names")
    display_unique_names(unique_names)
    #Reiniger-Eintrag suchen
    product_search = display_product_search()
    
    #Weitere Einträge hinzufügen
    database_addition = display_database_addition()
        
    #Erweiterte Datenbank herunterladen
    if st.session_state.addition_task:
        my_logger.info("Attempting excel data import")
        succesful_addition = import_wfk_data_from_excel(database_addition, database_dict)
        if succesful_addition:
            my_logger.info("Imported excel data")
            st.write("Erfolg! Weitere Daten hochladen oder Datenbank herunterladen")
            my_logger.info("Attempting download preparation")
            database_json = prepare_download(database_dict)
            my_logger.info("Prepared download")
            display_database_download(database_json)
        else:
            my_logger.warning("Attempt to import excel data failed")
            st.write("Eintrag falsch formatiert oder bereits vorhanden")
        st.session_state.addition_task = False

if product_search == '':
    my_logger.handlers.clear()
    st.stop()

my_logger.info("Attempting query search")
query_result = retrieve_query_result(database_dict, product_search)
my_logger.info("Searched query")
my_logger.info("Attempting detail retrieval")
detail_df = retrieve_query_details(query_result)
my_logger.info("Retrieved details")

display_query_result(detail_df)

if st.session_state.product_index is None:
    my_logger.handlers.clear()
    st.stop()
    
my_logger.info("Attempting calculations")
measurements = query_result[st.session_state.product_index]
calibration_data, calibration_amount = retrieve_calibration_data(measurements)
slope, ordinate, r_value, calibration_graph = calculate_calibrations(calibration_data)
measurement_data, blind_data = retrieve_measurement_data(measurements)
protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung = wfk_evaluation(measurements, slope)
evaluation_graph = figure_wfk_evaluation(measurements, protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung)
my_logger.info("Calculated")

my_logger.info("Attempting calculation display")
display_evaluation_graph(evaluation_graph)
display_query_calibration(calibration_data, calibration_amount, slope, ordinate, r_value, calibration_graph)
display_query_measurement(measurement_data, blind_data)
my_logger.info("Displayed calculations")

my_logger.handlers.clear()