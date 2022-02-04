import logging
import streamlit as st
from database_frontend import display_dataset_options, display_dataset_upload, display_database_addition, display_database_download, display_database_deletion
from database_backend import load_database
from excel_import import import_wfk_data_from_excel, prepare_download

def database_edit_view():
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
    
    
    #Weitere Einträge hinzufügen
    database_addition = display_database_addition()
        
    #Erweiterte Datenbank herunterladen
    if st.session_state.addition_task:
        logging.info("Attempting excel data import")
        succesful_addition = import_wfk_data_from_excel(database_addition, database_dict)
        if succesful_addition:
            logging.info("Imported excel data")
            st.write("Erfolg! Weitere Daten hochladen oder Datenbank herunterladen")
        else:
            logging.warning("Attempt to import excel data failed")
            st.write("Eintrag falsch formatiert oder bereits vorhanden")
        st.session_state.addition_task = False
    
    display_database_deletion(database_dict)
    
    st.header("Datenbank-Download")
    columns = st.columns((2,1,2))
    with columns[1]:
        logging.info("Attempting download preparation")
        database_json = prepare_download(database_dict)
        logging.info("Prepared download")
        display_database_download(database_json)