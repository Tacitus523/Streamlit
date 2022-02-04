import logging
import streamlit as st
from database_frontend import *
from database_backend import *

def database_selection_view():
    with st.sidebar:
        #Bestehende Datenbank laden
        uploaded_database = display_dataset_upload()
        if uploaded_database is None:
            st.stop()
        elif st.session_state.database is None:
            logging.info("Attempting to load database")
            st.session_state.database, validation_status, validation_comment = load_database(uploaded_database)
            if validation_status == False:
                logging.warning("Attempt to load database failed: " + validation_comment)
                st.write(validation_comment)
                st.session_state.database = None
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

    if product_search == '':
        st.stop()

    logging.info("Attempting query search")
    query_result = retrieve_query_result(database_dict, product_search)
    logging.info("Searched query")
    logging.info("Attempting detail retrieval")
    detail_df = retrieve_query_details(query_result)
    logging.info("Retrieved details")

    display_query_result(detail_df)

    if st.session_state.product_index is None:
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
