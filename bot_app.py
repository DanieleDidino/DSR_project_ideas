# from datetime import datetime
import time

import DSR_project_ideas.bot_functions as functions
import streamlit as st
from streamlit_chat import message

st.set_page_config(
    page_title="Bürohengst",
    layout="wide",
    page_icon="🧊",
    menu_items={
        "Get Help": "https://www.bürohengst.com/help",
        "Report a bug": "https://www.bürohengst.com/bug",
        "About": "# Bürohengst makes german bureaucracy a joy ride. \
        Our robot paper pusher (Chatbot) knows a host of german official \
        documents (they're in a Vector database) and answer your questions.",
    },
)

with open(".streamlit/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

col1.title("Bürohengst")
col1.subheader("Your robot paper pusher", divider="orange")


with col1:
    docs_list = functions.load_docs_list()
    doc_type = st.selectbox(
        "Select the document from our database: ", list(docs_list.keys())
    )

    uploaded_file = st.file_uploader(
        "Choose a file from your hard drive",
        type=["docx", "doc", "pdf"],
        accept_multiple_files=True,
    )

    # progress bar
    if uploaded_file is not None:
        # Show progress bar
        progress_bar = st.progress(0)

        for perc_completed in range(100):
            time.sleep(1)
            progress_bar.progress(perc_completed + 1)

            progress_text = st.empty()

        # Save the file
        functions.save_uploaded_file(uploaded_file)

        # Update progress bar and text
        progress_bar.progress(100)
        progress_text.text("File saved successfully!")

        docs_list = functions.embed_docs(uploaded_file)

        doc_type = st.selectbox("Please select the document: ", list(docs_list.keys()))

        st.write("Document selected: ", doc_type)

        user_query = st.text_input("You: ", "", key="input")
        send_button = st.button("Send")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if send_button:
    send_message(user_query, st.session_state.messages, query_engine)
    display_messages(st.session_state.messages)
