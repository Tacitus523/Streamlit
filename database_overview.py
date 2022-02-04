import streamlit as st

def database_overview_view():
    def handle_delete_buttonpress(index):
        st.session_state.index = index
    
    if st.session_state.index is not None:
        st.session_state.overview.pop(st.session_state.index)
        st.session_state.index = None
        
    columns = st.columns((7,1))
    columns[0].header("Übersicht")
    if len(st.session_state.overview) == 0:
        st.write("Noch keine Abbildung zur Übersicht hinzugefügt.")
        st.write("Unter \"Einsicht\" können Abbildungen zur Übersicht hinzugefügt werden.")
    
    for index, figure in enumerate(st.session_state.overview):
        columns = st.columns((6,1))
        col_num = index % int(len(columns)/2)
        figure_column = columns[col_num]
        figure_column.pyplot(figure)
        button_column = columns[col_num+1]
        button_column.write("")
        button_column.write("")
        button_column.write("")
        button_column.write("")
        button_column.write("")
        button_column.write("")
        button_column.write("")
        button_column.write("")
        button_column.button("Löschen", on_click=handle_delete_buttonpress, args = (index,), key="index "+str(index))
        