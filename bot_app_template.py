import pdb

# from datetime import datetime
import time

import bot_functions as functions
import streamlit as st
from interface import *
from llama_index import StorageContext, load_index_from_storage
from PIL import Image
from streamlit_chat import message
from streamlit_extras.app_logo import add_logo

# streamlit config
st.set_page_config(
    page_title="Office Hog",
    # page_icon=
    layout="wide",
    page_icon=".streamlit/favicon.ico",
    menu_items={
        "Get Help": "https://www.bürohengst.com/help",
        "Report a bug": "https://www.bürohengst.com/bug",
        "About": "# Bürohengst makes german bureaucracy a joy ride. \
        Our robot paper pusher (Chatbot) knows a host of german official \
        documents (they're in a Vector database) and answer your questions.",
    },
)


# Hide the menu button
st.markdown(
    """ <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """,
    unsafe_allow_html=True,
)

# Condense the layout
padding = 0
st.markdown(
    f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """,
    unsafe_allow_html=True,
)

# load custom css styles
with open(".streamlit/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# column 1
with st.sidebar:
    st.title("Office Hog")
    st.subheader("ate the official documents", divider="orange")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Choose a file from your hard drive"):
        uploaded_file = st.file_uploader(
            "",
            type=["docx", "doc", "pdf"],
            accept_multiple_files=True,
        )

        show_progress = False  # Initialize the flag

        # Check if any files were uploaded
        if uploaded_file:
            for file in uploaded_file:
                if len(file.getvalue()) > 0:
                    show_progress = True
                    break

        # Show progress bar only if the flag is set to True
        if show_progress:
            # Show progress bar
            progress_bar = st.progress(0)
            progress_text = st.empty()

            for perc_completed in range(100):
                time.sleep(1)
                progress_bar.progress(perc_completed + 1)

            # Update progress bar and text
            progress_bar.progress(100)

            print(uploaded_file)

            ## Save the file - didn't work
            # functions.save_uploaded_file(uploaded_file)

            st.text("File saved successfully!")

            ## query engine from uploaded file - not working
            # query_engine_to_use = functions.engine_from_upload(uploaded_file)

        else:
            ## query engine from default vector space - also not working
            query_engine_to_use = functions.default_engine()

    st.markdown("<br>", unsafe_allow_html=True)

    # show a selection of stored files
    docs_list = functions.load_docs_list()
    st.markdown("Select the document from our database: ")
    doc_type = st.selectbox("", list(docs_list.keys()))


## Chat
# for different options look into chat.py file
