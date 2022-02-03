import logging
import streamlit as st
from database_app_frontend import *
from database_app_backend import *
from excel_import import import_wfk_data_from_excel, prepare_download

with st.sidebar:
    #Laden oder neu anlegen
    options = ('Laden', 'Neu')
    option = display_dataset_options(options)
    if option == options[1]:
        #Neue Datenbank anlegen
        if st.session_state.database is None:
            logging.info("New Database created")
            st.session_state.database = {}
            
    #Bestehende Datenbank laden
    else:
        uploaded_database = display_dataset_upload()
        if uploaded_database is None:
            logging.handlers.clear()
            st.stop()
        elif st.session_state.database is None:
            logging.info("Attempting to load database")
            st.session_state.database, validation_status, validation_comment = load_database(uploaded_database)
            if validation_status == False:
                logging.warning("Attempt to load database failed: " + validation_comment)
                st.write(validation_comment)
                st.session_state.database = None
                logging.handlers.clear()
                st.stop()
            logging.info("Loaded database")
                
    #Datenbank aus session-state laden, um mehrere Erweiterungen zuzulassen             
    database_dict = st.session_state.database
    
    #Vorhandene Einträge von Reiniger-Produkten
    logging.info("Attempting to retrieve unique names")
    unique_names = retrieve_unique_names(database_dict)
    logging.info("Retrieved unique names")
    display_unique_names(unique_names)
    #Reiniger-Eintrag suchen
    product_search = display_product_search()
    
    #Weitere Einträge hinzufügen
    database_addition = display_database_addition()
        
    #Erweiterte Datenbank herunterladen
    if st.session_state.addition_task:
        logging.info("Attempting excel data import")
        succesful_addition = import_wfk_data_from_excel(database_addition, database_dict)
        if succesful_addition:
            logging.info("Imported excel data")
            st.write("Erfolg! Weitere Daten hochladen oder Datenbank herunterladen")
            logging.info("Attempting download preparation")
            database_json = prepare_download(database_dict)
            logging.info("Prepared download")
            display_database_download(database_json)
        else:
            logging.warning("Attempt to import excel data failed")
            st.write("Eintrag falsch formatiert oder bereits vorhanden")
        st.session_state.addition_task = False

if product_search == '':
    logging.handlers.clear()
    st.stop()

logging.info("Attempting query search")
query_result = retrieve_query_result(database_dict, product_search)
logging.info("Searched query")
logging.info("Attempting detail retrieval")
detail_df = retrieve_query_details(query_result)
logging.info("Retrieved details")

display_query_result(detail_df)

if st.session_state.product_index is None:
    logging.handlers.clear()
    st.stop()
    
logging.info("Attempting calculations")
measurements = query_result[st.session_state.product_index]
calibration_data, calibration_amount = retrieve_calibration_data(measurements)
slope, ordinate, r_value, calibration_graph = calculate_calibrations(calibration_data)
measurement_data, blind_data = retrieve_measurement_data(measurements)
protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung = wfk_evaluation(measurements, slope)
evaluation_graph = figure_wfk_evaluation(measurements, protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung)
logging.info("Calculated")

logging.info("Attempting calculation display")
display_evaluation_graph(evaluation_graph)
display_query_calibration(calibration_data, calibration_amount, slope, ordinate, r_value, calibration_graph)
display_query_measurement(measurement_data, blind_data)
logging.info("Displayed calculations")

logging.handlers.clear()
