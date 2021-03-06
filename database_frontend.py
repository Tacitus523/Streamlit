import streamlit as st

def handle_search_change():
    st.session_state.product_index = None

def handle_database_change():
    handle_search_change()
    st.session_state.database = None

def handle_addition_change():
    handle_search_change()
    st.session_state.addition_task = True

def display_view_options(options):
    st.header("Datenbank-Optionen")
    option = st.selectbox(
        'Datenbank bearbeiten, einsehen oder zur Ergebnis-Übersicht wechseln?',
        options,
        index = 1,
        on_change = handle_database_change)
    return option

def display_dataset_options(options):
    option = st.selectbox(
        'Bestehende Datenbank laden oder neue Datenbank anlegen?',
        options,
        index = 0,
        on_change = handle_database_change)
    return option

def display_dataset_upload():
    uploaded_database = st.file_uploader(
    "Datenbank-Auswahl",
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
    "Download", 
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
        col1.write(str(x))  # index
        col2.write(detail_df['Produktname'][x])  # Produktname
        col3.write(detail_df['Konzentration'][x])  # Konzentration
        col4.write(detail_df['Temperatur'][x])   # Temperatur
        col5.write(detail_df['Datum'][x]) # Datum
        col6.button("Details", on_click=handle_buttonpress, args = (x,), key=detail_df['Produktname']+str(x))
    
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
    def handle_overview_buttonpress(figure):
        st.session_state.overview.append(figure)
    col1, col2 = st.columns((6, 1))
    with col1:
        st.pyplot(fig = evaluation_graph)
    with col2:
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.button("Zu Übersicht hinzufügen", on_click=handle_overview_buttonpress, args = (evaluation_graph,), key="overview_button")
        
def display_database_deletion(database_dict):
    def handle_delete_buttonpress(product, x):
        database_dict[product].pop(x)
        
    st.header("Datenbank-Eintrag löschen")

    cols = st.columns((1, 2, 1, 1, 1, 1))
    fields = ["Index",'Produktname','Konzentration','Temperatur','Datum']
    for col, field_name in zip(cols, fields):
        col.write(field_name)

    for product in database_dict:
        for entry_index in range(len(database_dict[product])):
            details = database_dict[product][entry_index].get("Details")
            col1, col2, col3, col4, col5, col6 = st.columns((1, 2, 1, 1, 1, 1))
            col1.write(str(entry_index))  # index
            col2.write(details['Produktname'])  # Produktname
            col3.write(details['Konzentration'])  # Konzentration
            col4.write(details['Temperatur'])   # Temperatur
            col5.write(details['Datum']) # Datum
            col6.button("Delete", on_click=handle_delete_buttonpress, args = (product, entry_index), key=product+str(entry_index))