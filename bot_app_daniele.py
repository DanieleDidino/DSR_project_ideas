# from datetime import datetime
import time

# import bot_functions as functions
from bot_utils import default_engine, engine_from_upload, save_uploadedfile
import streamlit as st
# from interface import *
from llama_index import StorageContext, load_index_from_storage
from llama_index import Prompt
# from PIL import Image
from streamlit_chat import message
# from streamlit_extras.app_logo import add_logo
import environ
import openai
import os


# Uncomment this lines when we will ask for the user OpenAI Key
# openai_key = col.text_input('OpenAI Key:')
# os.environ["OPENAI_API_KEY"] = openai_key

# For now I use my key
env = environ.Env()
environ.Env.read_env()
API_KEY = env("OPENAI_API_KEY")
openai.api_key = API_KEY



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


number_top_results = 3 # Number of top results to return
folder_with_index = "vector_db"

# folder_with_index = "vector_db"
# storage_context = StorageContext.from_defaults(persist_dir="vector_db") # rebuild storage context
# index = load_index_from_storage(storage_context) # load index
# number_top_results = 3 # Number of top results to return
# # query_engine = index.as_chat_engine(text_qa_template=qa_template, similarity_top_k=number_top_results)
# query_engine = index.as_query_engine(text_qa_template=qa_template, similarity_top_k=number_top_results)
query_engine_default = default_engine(folder_with_index, qa_template, number_top_results)

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
        use_user_docs = st.toggle('User document(s)', key="my_toggle")
    
        with st.expander("Choose a file from your hard drive"):
            uploaded_file = st.file_uploader(
                "",
                type=["docx", "doc", "pdf"],
                accept_multiple_files=True,
            )
            # uploaded_file = st.file_uploader("", type=['pdf'])
    
            show_progress = False  # Initialize the flag
    
            # Check if any files were uploaded
            if uploaded_file:
                # show_progress = True
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
                    #time.sleep(1)
                    progress_bar.progress(perc_completed + 1)
    
                # Update progress bar and text
                progress_bar.progress(100)
    
                ## Save the file - didn't work
                # functions.save_uploaded_file(uploaded_file)
    
                st.text("File saved successfully!")
    
                ## query engine from uploaded file - not working
                # query_engine_to_use = functions.engine_from_upload(uploaded_file)
                # save_uploadedfile(uploaded_file)
                ## for file in uploaded_file:
                ##     save_uploadedfile(file, folder_user_uploaded_files)
                ## query_engine_user = engine_from_upload(folder_user_uploaded_files, qa_template, number_top_results)
                # query_engine = query_engine_user
    
        st.markdown("<br>", unsafe_allow_html=True)
    
        # show a selection of stored files
        st.markdown("Select the document from our database: ")



if uploaded_file:
    # save_uploadedfile(file, folder_user_uploaded_files)
    for file in uploaded_file:
        save_uploadedfile(file, folder_user_uploaded_files)


## Chat
# for different options look into chat.py file

if use_user_docs:
    if uploaded_file:
        query_engine_user = engine_from_upload(folder_user_uploaded_files, qa_template, number_top_results)
        query_engine = query_engine_user
    elif not uploaded_file:
        query_engine = query_engine_default
        st.write("NO UPLOADED FILE")
else:
    query_engine = query_engine_default

# if uploaded_file:
#     save_uploadedfile(file, folder_user_uploaded_files)
#     query_engine_user = engine_from_upload(folder_user_uploaded_files, qa_template, number_top_results)
#     query_engine = query_engine_user
# else:
#     query_engine = query_engine_default


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Response from llm
    response = query_engine.query(prompt)

    response_text = response.response
    response_metadata = dict()
    # for i, meta_data in enumerate(response.metadata):
    #     key_name = "ref_" + str(i)
    #     response_metadata[key_name] = {
    #         "page": response.metadata[meta_data]["page_label"],
    #         "document":response.metadata[meta_data]["file_name"]
    #     }
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})







    