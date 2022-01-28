import streamlit as st
from DatabaseAppBackend import *
from excel_import import import_wfk_data_from_excel, prepare_download

def display_sidebar():
    def handle_change():
        st.session_state.product_index = None
    
    with st.sidebar:
        st.header("Datenbank-Auswahl")
        #Laden oder neu anlegen
        options = ('Laden', 'Neu')
        option = st.selectbox(
            'Bestehende Datenbank laden oder neue Datenbank anlegen?',
            options,
            index = 0,
            on_change = handle_change)
        
        #Neue Datenbank anlegen
        if option == options[1]:
            database_dict = {}
        
        #Bestehende Datenbank laden  
        else:
            uploaded_database = st.file_uploader(
                "",
                type="json",
                on_change = handle_change,
                key = "database_upload")
            if uploaded_database is None:
                st.stop()
            database_dict = load_database(uploaded_database)
        
        #Alle einzigartigen Produktnamen
        with st.expander("Eingetragene Produktnamen"):
            unique_names = retrieve_unique_names(database_dict)
            if unique_names:
                st.write(unique_names.to_string(index = False))
            else:
                st.write("Keine Einträge")
        
        #Reiniger-Eintragen suchen
        product_search = st.text_input('Produktnamen suchen', on_change = handle_change)
        
        #Weitere Einträge hinzufügen
        st.header("Datenbank-Erweiterung")
        database_addition = st.file_uploader(
            "Korrekt formatierte Excel-Datei auswählen",
            type="xlsx",
            on_change = handle_change,
            key = "addition_upload",
            accept_multiple_files = True)

        #Erweiterte Datenbank herunterladen
        if database_addition:
            succesful_addition = import_wfk_data_from_excel(database_addition[-1], database_dict)
            if succesful_addition:
                st.write("Datensatz erfolgreich hinzugefügt! Weitere Daten hochladen oder Datenbank herunterladen")
                database_json = prepare_download(database_dict)
                st.download_button("Datenbank-Download", database_json, file_name="wfk-Datenbank.json", mime="text/plain", help="Datenbank als .json")
            else:
                st.write("Eintrag falsch formatiert oder bereits vorhanden")
        
        return database_dict, product_search

def display_query_result(database_dict, product_search):
    def handle_buttonpress(x):
        st.session_state.product_index = x

    if product_search == '':
        st.stop()
    
    st.header("wfk-Daten")
    query_result = retrieve_query_result(database_dict, product_search)
    detail_df = retrieve_query_details(query_result)
    if detail_df is None:
        st.write("Keine Daten verfügbar")
        st.stop()

    cols = st.columns((1, 2, 1, 1, 1, 1))
    fields = ["Index",'Produktname','Konzentration','Temperatur','Datum']
    for col, field_name in zip(cols, fields):
        col.write(field_name)

    for x in range(len(detail_df)):
        col1, col2, col3, col4, col5, col6 = st.columns((1, 2, 1, 1, 1, 1))
        col1.write(x)  # index
        col2.write(detail_df['Produktname'][x])  # Produktname
        col3.write(detail_df['Konzentration'][x])  # Konzentration
        col4.write(detail_df['Temperatur'][x])   # Temperatur
        col5.write(detail_df['Datum'][x]) # Datum
        button_phold = col6.empty()  # create a placeholder
        button_phold.button("Details",on_click=handle_buttonpress, args = (x,), key=x)
    return query_result
    
def display_query_calibration(measurements):
    calibration_data, calibration_amount = retrieve_calibration_data(measurements)
    if calibration_data is None:
        st.write("Keine Kalibrierung gefunden")
        st.stop()
    slope, ordinate, r_value, f = calculate_calibrations(calibration_data)
    with st.expander("Kalibrierung"):
        col1, col2 = st.columns((1,1))
        st.write(f"Mittelwert aus {calibration_amount} {'Messreihe' if calibration_amount == 1 else 'Messreihen'}")
        with col1:
            st.table(calibration_data.style.format({
                "BSA-Konzentration [µg/ml]": "{:.0f}",
                "OPA-Extinktion": "{:.3f}",
                "Eigenabsorption": "{:.3f}"}))
        with col2:
            st.markdown(f"Steigung: {slope:.5f}")
            st.markdown(f"Ordinate: {ordinate:.1f}")
            st.markdown(f"Bestimmtheit: {r_value:.4f}")
            st.pyplot(fig=f, clear_figure=True)
    return slope

def display_query_measurement(measurements, slope):
    measurement_data, blind_data = retrieve_measurement_data(measurements)
    if measurement_data is None:
        st.write("Keine Messungen gefunden")
        st.stop()
    protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung = wfk_evaluation(measurements, slope)
    f = figure_wfk_evaluation(measurements, protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung)
    with st.expander("Messungen"):
        st.table(measurement_data.style.format({
            "Reinigungszeit [min]": "{:.0f}",
            "OPA-Extinktion 1": "{:.3f}",
            "OPA-Extinktion 2": "{:.3f}",
            "OPA-Extinktion 3": "{:.3f}",
            "Eigen-absorption 1": "{:.3f}",
            "Eigen-absorption 2": "{:.3f}",
            "Eigen-absorption 3": "{:.3f}"}))
        st.table(blind_data.style.format({
            "OPA-Blindwert": "{:.3f}",
            "Eigenabsorption-Blindwert": "{:.3f}"
        }))

    st.pyplot(fig=f, clear_figure=True)