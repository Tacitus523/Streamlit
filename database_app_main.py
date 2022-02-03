import logging
import streamlit as st
from database_app_frontend import *
from database_app_backend import *
from excel_import import import_wfk_data_from_excel, prepare_download

#Initialize Filelogger, Streamlogger is handled by Streamlit
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

#Streamlit configurations
st.set_page_config(page_title="wfk-Datenbank",layout='centered',menu_items={
         'Get Help': 'https://github.com/Tacitus523/Streamlit',
         'Report a bug': "https://github.com/Tacitus523/Streamlit",
         'About': '''
This is my *first* project with streamlit. I hope it can help you out.
You should check out the ReadMe under the Get Help link to get examples
for the required formatting of excel-imports and example json-databases.
'''
     })

#Import custom CSS-Styles
with open("style.css","r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

#Preparte Session-State-Variables
if not 'product_index' in st.session_state:
    st.session_state.product_index = None
if not 'database' in st.session_state:
    st.session_state.database = None
if not 'addition_task' in st.session_state:
    st.session_state.addition_task = False
if not 'overview' in st.session_state:
    st.session_state.overview = []

with st.sidebar:
    view_options = ("Auswahl", "Bearbeitung", "Übersicht")
    option = display_view_options(view_options)
    if option == view_options[0]:
        database_selection()
    elif option == view_options[1]:
        database_editing()
    elif option == view_options[2]:
        database_overview()
    
