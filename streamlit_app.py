import os
import environ
import time
import pickle
import streamlit as st
# from datetime import datetime
from streamlit_chat import message
from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index import StorageContext, load_index_from_storage
import openai


def save_uploaded_file(uploadedfile, folder_docs="docs"):
    """
    Save in an uploaded file in the folder "folder_docs".

    Args:
        uploadedfile (UploadedFile): A instance of the UploadedFile class with the uploaded file.
        folder_docs (str): Folder in which to save the uploaded files.

    Returns:
        None, save the file in the folder "folder_docs"
    """
    with open(os.path.join(folder_docs, uploadedfile.name),"wb") as f:
        f.write(uploadedfile.getbuffer())


def save_read_write_all_uploaded_files(uploaded_files, folder_docs="docs"):
    """
    This function does 3 things:
    1) Save all uploaded files in the folder "folder_docs".
    2) Read the file using "SimpleDirectoryReader" from "llama_index".
    3) Write the name of the uploaded files to the app.

    Args:
        uploaded_files (list  of UploadedFile): A list with instances of the UploadedFile class (the uploaded files).
        folder_docs (str): Folder in which to save the uploaded files.

    Returns:
        documents: the list of documents read with "SimpleDirectoryReader"
        Also, it saves the uploaded files in the folder "folder_docs", reads them and writes their name to the app.
    """
    if not os.path.exists("./" + folder_docs):
        os.mkdir("./" + folder_docs)
   
    for uploaded_file in uploaded_files:
       save_uploaded_file(uploaded_file)
       st.write("filename: ", uploaded_file.name)
    
    documents = SimpleDirectoryReader(folder_docs).load_data()

    return documents


def create_vector_database(documents, folder_vec_db="vector_db", file_name_vector_db="vect_bd_1.json"):
    """
    Create a vector database with the documents and save them in the folder "folder_vec_db".

    Args:
        documents (list of Document): list of documents created with "SimpleDirectoryReader"
        folder_vec_db (str): Folder in which to save the vector database.
        file_name_vector_db (str): File where to save the vector database.

    Returns:
        index (VectorStoreIndex): Vector database.
        Also, it saves the vector database in the folder "vector_db".
    """
    index = VectorStoreIndex.from_documents(documents)
    # index.save_to_disk(folder_vec_db + '/' + file_name_vector_db)
    index.storage_context.persist(persist_dir=folder_vec_db, docstore_fname=file_name_vector_db)
    return index


def get_response(user_query, query_engine):
    """
    Return the response from the bit (using query_engine) based on the user query.

    Args:
        user_query (str): query from user.
        query_engine: a query_engine created from the index.

    Returns:
        response (str): response from the query_engine.
    """
    response = query_engine.query(user_query)
    return str(response)


def send_message(user_query, messages, query_engine):
    """
    Send the message to the query engine.

    Args:
        user_query (str): query from user.
        messages: chat history.
        query_engine: a query_engine created from the index.

    Returns:
        None, update the chat history (in "messages").
    """
    if user_query:
        messages.append({'user': 'user', 'text': user_query})
        bot_response = get_response(user_query, query_engine)
        messages.append({'user': 'bot', 'text': bot_response})
        st.session_state.messages = messages


def display_messages(messages):
    """
    Display the message in the chat.

    Args:
        messages: chat history.

    Returns:
        None, display the messages in the chat.
    """
    for msg in messages:
        if msg['user'] == 'user':
            # seed: int or str (The seed for choosing the avatar to be used, default is 42)
            message(f"You: {msg['text']}", is_user=True, key=int(time.time_ns()))
        else:
            message(f"Bot: {msg['text']}", key=int(time.time_ns()))


def load_docs_list():
    docs_list_path = "docs_list/docs_list.pkl"
    # file = open(docs_list_path,"rb")
    # docs_list = pickle.load(file)
    # file.close()
    with open(docs_list_path,"rb") as file:
        docs_list = pickle.load(file)
    return docs_list


if __name__ == '__main__':
    
    # Parameters
    num_to_return = 3 # number of results to return (from the similarity search)
    folder_vec_db= "vector_database_1.json" # Folder where to save the vector database
    folder_docs_user = "docs_user" # Folder where to save the uploaded files from the user
    folder_vec_db_user = "vector_db_user" # Folder where to save the vector database from the user

    # For now I use my key
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('OPENAI_API_KEY')
    openai.api_key = API_KEY

    # Uncomment this lines when we will ask for the user OpenAI Key
    # openai_key = col.text_input('OpenAI Key:')
    # os.environ["OPENAI_API_KEY"] = openai_key   

    folder_with_index = "vector_db"
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="vector_db")
    # load index
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine(similarity_top_k=num_to_return)
    
    uploaded_files = st.file_uploader("Upload your files", type=['docx', 'doc', 'pdf'], accept_multiple_files=True)
    if uploaded_files:
        if not os.path.exists(folder_vec_db_user):
            os.mkdir(folder_vec_db_user)
        documents_user = save_read_write_all_uploaded_files(uploaded_files, folder_docs=folder_docs_user)
        index_user = create_vector_database(documents_user, folder_vec_db=folder_vec_db_user, file_name_vector_db="vect_bd_user.json")
        query_engine_user = index_user.as_query_engine(similarity_top_k=num_to_return)

    # Create title
    st.markdown("<h1 style='text-align: center; color: blue;'>German Admin Bot</h1>", unsafe_allow_html=True)

    docs_list = load_docs_list()

    doc_type = st.selectbox('Please select the document: ', list(docs_list.keys()))

    st.write("Document selected: ", doc_type)

    user_query = st.text_input("You: ", "", key= "input")
    send_button = st.button("Send")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if send_button:
        send_message(user_query, st.session_state.messages, query_engine)
        display_messages(st.session_state.messages)

####################################################################################################

# st.title("What are you looking at?!")

# TODO: Display chat messages from history on app rerun (do we need this?)
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# React to user input
# if prompt := st.chat_input("What is up?"):
#     # Display user message in chat message container
#     st.chat_message("user").markdown(prompt)
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
# 
#     response = f"Echo: {prompt}"
#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         st.markdown(response)
#     # Add assistant response to chat history
#     st.session_state.messages.append({"role": "assistant", "content": response})




