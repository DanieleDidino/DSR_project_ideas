# from datetime import datetime
import time

import bot_functions as functions
import streamlit as st
import streamlit_functions as sf
from PIL import Image
from streamlit_chat import message
from streamlit_extras.app_logo import add_logo

import numpy as np

# streamlit config
st.set_page_config(
    page_title="Doc Hog",
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

# add logo
sf.add_logo()

# load custom css styles
with open(".streamlit/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# col1.subheader("Your robot paper pusher", divider="orange")

# column 1
with st.sidebar:
    st.title("Doc Hog")
    st.subheader("He eats all your papers")

    with st.expander("Choose a file from your hard drive"):
        uploaded_file = st.file_uploader(
            "",
            type=["docx", "doc", "pdf"],
            accept_multiple_files=True,
        )

    show_progress = False  # Initialize the flag

    # Check if any files are uploaded
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

        # Save the file
        functions.save_uploaded_file(uploaded_file)

        # Update progress bar and text
        progress_bar.progress(100)
        st.text("File saved successfully!")

    query_engine = functions.engine_from_upload(uploaded_file)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # show a selection of stored files
    docs_list = functions.load_docs_list()
    st.markdown("Select the document from our database: ")
    doc_type = st.selectbox("", list(docs_list.keys()))

## Chat

# # avatar - little picture shown instead of the robot
# avatar = np.array(Image.open(".streamlit/hengst.png"))

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("How can I help?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display user message in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Iterate through the messages and generate responses
        for message in st.session_state.messages:
            if message["role"] == "user":
                response = functions.get_response(message["content"], query_engine)
                full_response += response[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")

            # Display the response
            message_placeholder.markdown(full_response)

    # Append to session_state.messages
    st.session_state.messages.append({"role": "assistant", "content": response})


# st.info(
#     "This app is maintained by the deities of paper work.\n"
#     "You can learn more about us at [officegods.com](https://officegods.com).",
#     icon="ℹ️",
# )
