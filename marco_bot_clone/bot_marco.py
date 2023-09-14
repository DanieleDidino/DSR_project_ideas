import pickle

# import os
from pathlib import Path

# from streamlit_extras.app_logo import add_logo
import environ
import openai
import streamlit as st
from bot_utils_marco import ( default_engine, engine_from_upload, get_filename_from_title, save_uploadedfile, )

# from llama_index import StorageContext, load_index_from_storage
from llama_index import Prompt

from streamlit_chat import message

# For now I use my key
env = environ.Env()
environ.Env.read_env()
API_KEY = env("OPENAI_API_KEY")
openai.api_key = API_KEY


# Load dictionary with the title of the pdf files.
with open(Path("pdf_titles", "pdf_dictionary.pkl"), "rb") as f:
    pdf_dict = pickle.load(f)

folder_user_uploaded_files = "data_streamlit"

# Define prompt
template = (
    "We have provided context information below. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "Given this information, please answer the question and each answer should start with code word Response: {query_str}\n"
)

qa_template = Prompt(template)

number_top_results = 3  # Number of top results to return
folder_with_index = "vector_db"
query_engine_default = default_engine( folder_with_index, qa_template, number_top_results )

####################################################################################
# Config streamlit

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

 ####################################################################################
# Left column (first part)

sidebar = st.sidebar

with sidebar:

    # Custom page title and subtitle
    st.title("Office Hog")
    st.subheader("Ate the official documents", divider="orange")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Get OpenAI ley from user
    st.markdown("Enter your [OpenAi key](https://platform.openai.com/account/api-keys)")
    OPENAI_KEY = st.text_input(label="OpenAI Key:", type="password", help="Enter your OpenAi key")
    
    # openai.api_key = OPENAI_KEY # TODO: Uncomment this lines when we will ask for the user OpenAI Key
    
    # This toggle define whether we use the default query engine (based on our documents) or
    # the query engine created from the user uploaded documents
    toggle_help = 'If "on" the responses are based on the uploaded file(s)'
    use_user_docs = st.toggle('User document(s)', key="my_toggle", help=toggle_help)
    st.write(f"User context is {use_user_docs}") # TODO: This info is only for us, delete before demo day
    
    # Expander for file uploading
    with st.expander("Choose a file from your hard drive"):
        uploaded_file = st.file_uploader("", type=["docx", "doc", "pdf"], accept_multiple_files=True)

        # NEW: show only when a file was saved
        if uploaded_file:
            st.text("File saved successfully!")
    
    # Add space between elements of the column
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Initialize list downloadable files
    if "list_file_download" not in st.session_state:
        st.session_state.list_file_download = []
    
    # Save the uploaded file
    if uploaded_file:
        for file in uploaded_file:
            save_uploadedfile(file, folder_user_uploaded_files)



####################################################################################
# Chat

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if use_user_docs:
    if uploaded_file:
        query_engine_user = engine_from_upload(folder_user_uploaded_files, qa_template, number_top_results)
        query_engine = query_engine_user
    elif not uploaded_file:
        query_engine = query_engine_default
        st.write("NO UPLOADED FILE")
else:
    query_engine = query_engine_default

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)
    
# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Response from llm
    response = query_engine.query(prompt)
    # Get response as string
    response_text = response.response
    # If the user uploaded a file and switched to "query_user_engine"
    if use_user_docs and uploaded_file:
        response_for_user = response_text
    # If we use our "query_engine_default"
    else:
        # Create first part of the source section (i.e., section of the response message with source documents)
        response_metadata_message = f'There are {len(response.metadata)} source files.'
        # Loop over all documents used as source
        for i, meta_data in enumerate(response.metadata):
            # Extract title from dictionary with {"file_name":"title"}, given a file name
            document_title = pdf_dict[response.metadata[meta_data]["file_name"]]
            # Append the title, if title is not in the list of used sources
            if document_title not in st.session_state.list_file_download:
                st.session_state.list_file_download.append(document_title)
            # Update the source section with the source metadata
            response_metadata_message += f'<br>**Source {i+1}**: page {response.metadata[meta_data]["page_label"]} from file *{document_title}*.'
        # Add response_metadata_message (i.e., source section) after the LLM response text
        response_for_user = (f"{response_text}<br><br>{response_metadata_message}")
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response_for_user, unsafe_allow_html=True)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_for_user})


####################################################################################
# Left column (second part)

with sidebar:
    # Selectbox with the list of titles used as source
    selected_file = st.selectbox("Select a source file to download", options=st.session_state.list_file_download)
    # Prepare the file for downloading, if a file is selected in the selectbox
    if selected_file:
        # Get the name of the file from the selected title
        file_name_to_download = get_filename_from_title(pdf_dict, selected_file)
        # Define path to file to download
        path_file_download = Path("documents_pdf", file_name_to_download)
        # Open and read the file
        with open(path_file_download, "rb") as pdf_file:
            PDFbyte = pdf_file.read()
        # Make the file available for download
        st.download_button(
            label="Download",
            data=PDFbyte,
            file_name=file_name_to_download,
            mime='application/octet-stream')
        


with sidebar:
    "[View the source code](https://github.com/DanieleDidino/DSR_project_ideas/blob/master/bot_app_marco.py)"









# # avatar - little picture shown instead of the robot
# avatar = np.array(Image.open(".streamlit/hengst.png"))
