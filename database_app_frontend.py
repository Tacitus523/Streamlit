import streamlit as st

def handle_search_change():
    st.session_state.product_index = None

def handle_database_change():
    handle_search_change()
    st.session_state.database = None

def handle_addition_change():
    handle_search_change()
    st.session_state.addition_task = True

def display_dataset_options(options):
    st.header("Datenbank-Auswahl")
    option = st.selectbox(
        'Bestehende Datenbank laden oder neue Datenbank anlegen?',
        options,
        index = 0,
        on_change = handle_database_change)
    return option

def display_dataset_upload():
    uploaded_database = st.file_uploader(
    "",
    type="json",
    on_change = handle_database_change,
    key = "database_upload")
    return uploaded_database

def display_unique_names(unique_names):
    with st.expander("Eingetragene Produktnamen"):
        if not unique_names.empty:
            st.dataframe(unique_names)
        else:
            st.write("Keine Einträge")

def display_product_search():       
    product_search = st.text_input(
        'Produktnamen suchen', 
        on_change = handle_search_change)
    return product_search

def display_database_addition():
    st.header("Datenbank-Erweiterung")
    database_addition = st.file_uploader(
        "Korrekt formatierte Excel-Datei auswählen",
        type=["xlsx", "xlsm"],
        on_change = handle_addition_change,
        key = "addition_upload")
        #Falls eine Datei aus database_addition entfernt wurde
    if not database_addition:
        st.session_state.addition_task = False
    return database_addition

def display_database_download(database_json):
    st.download_button(
    "Datenbank-Download", 
    database_json, file_name = "wfk-Datenbank.json", 
    mime = "text/plain", 
    help = "Datenbank als .json herunterladen")

def display_query_result(detail_df):
    def handle_buttonpress(x):
        st.session_state.product_index = x
        
    st.header("wfk-Daten")
    
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
        button_phold.button("Details", on_click=handle_buttonpress, args = (x,), key=x)
    
def display_query_calibration(calibration_data, calibration_amount, slope, ordinate, r_value, calibration_graph):
    with st.expander("Kalibrierung"):
        col1, col2 = st.columns((1,1))
        st.write(f"Mittelwert aus {calibration_amount} {'Kalibrierung' if calibration_amount == 1 else 'Kalibrierungen'}")
        with col1:
            st.table(calibration_data.style.format({
                "BSA-Konzentration [µg/ml]": "{:.0f}",
                "OPA-Extinktion": "{:.3f}",
                "Eigenabsorption": "{:.3f}"}))
        with col2:
            st.markdown(f"Steigung: {slope:.5f}")
            st.markdown(f"Ordinate: {ordinate:.1f}")
            st.markdown(f"Bestimmtheit: {r_value:.4f}")
            st.pyplot(fig = calibration_graph, clear_figure = True)

def display_query_measurement(measurement_data, blind_data):
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
            "Eigenabsorptions-Blindwert": "{:.3f}"
        }))


def display_evaluation_graph(evaluation_graph):
    st.pyplot(fig = evaluation_graph, clear_figure=True)