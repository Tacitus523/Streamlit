import logging
import streamlit as st
from database_edit import database_edit_view
from database_overview import database_overview_view
from database_selection import database_selection_view
from database_frontend import display_view_options

logging.info("""
------------------
---APP STARTED----
------------------
""")

#Streamlit configurations
st.set_page_config(page_title="wfk-Datenbank", layout="centered", menu_items={
"Get Help": "https://github.com/Tacitus523/Streamlit",
"Report a bug": "https://github.com/Tacitus523/Streamlit",
"About": """
This is my *first* project with streamlit. I hope it can help you out.
You should check out the ReadMe under the Get Help link to get examples
for the required formatting of excel-imports and example json-databases.
"""})

#Import custom CSS-Styles
with open("style.css","r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

#Preparte Session-State-Variables
if not "product_index" in st.session_state:
    st.session_state.product_index = None
if not "database" in st.session_state:
    st.session_state.database = None
if not "addition_task" in st.session_state:
    st.session_state.addition_task = False
if not "overview" in st.session_state:
    st.session_state.overview = []
if not "index" in st.session_state:
    st.session_state.index = None

with st.sidebar:
    view_options = ("Bearbeitung", "Einsicht", "Übersicht")
    option = display_view_options(view_options)
if option == view_options[0]:
    database_edit_view()
elif option == view_options[1]:
    database_selection_view()
elif option == view_options[2]:
    database_overview_view()

