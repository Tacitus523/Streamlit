import streamlit as st
from DatabaseAppBackend import *

def display_sidebar():
    def handle_change():
        st.session_state.product_index = None
    
    with st.sidebar:
        st.header("Datenbank-Auswahl")
        sidebar_col_1, sidebar_col_2 = st.columns([3,1])
        with sidebar_col_1:
            uploaded_database = st.file_uploader("",type="json", on_change = handle_change)
        with sidebar_col_2:
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            new_databank = st.button("Neu")
        if new_databank is False:
            pass
        if uploaded_database is None:
            st.stop()
        database_dict = load_database(uploaded_database)
        product_search = st.text_input('Produktnamen suchen', on_change = handle_change)
        with st.expander("Eingetragene Produktnamen"):
            unique_names = retrieve_unique_names(database_dict)
            st.write(unique_names.to_string(index = False))
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
    calibration_data = retrieve_calibration_data(measurements)
    slope, ordinate, r_value, f = calculate_calibrations(calibration_data)
    with st.expander("Kalibrierung"):
        col1, col2 = st.columns((1,1))
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
    measurement_data = retrieve_measurement_data(measurements)
    protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung = wfk_evaluation(measurements, slope)
    f = grafik_wfk_auswertung(measurements, protein_gehälter, protein_gehälter_mittelwert, protein_gehälter_standardabweichung)
    with st.expander("Messungen"):
        st.table(measurement_data.style.format({
            "Reinigungszeit [min]": "{:.0f}",
            "OPA-Extinktion 1": "{:.3f}",
            "OPA-Extinktion 2": "{:.3f}",
            "OPA-Extinktion 3": "{:.3f}",
            "Eigen-absorption 1": "{:.3f}",
            "Eigen-absorption 2": "{:.3f}",
            "Eigen-absorption 3": "{:.3f}"}))

    st.pyplot(fig=f, clear_figure=True)    