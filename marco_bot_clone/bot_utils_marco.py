import os

import streamlit as st
from langchain.chat_models import ChatOpenAI
from llama_index import (
    LLMPredictor,
    Prompt,
    ServiceContext,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)


def default_engine(folder_with_index, qa_template, number_top_results):
    """
    Rebuild storage context from a vector database and return an index.

    Args:
        folder_with_index (str): Folder where the vector database is.
        qa_template (f-string): A prompt used to create the query engine.
        number_top_results (int): Number of top results to return

    Returns:
        query_engine: a query_engine created from the index.
    """
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir=folder_with_index)
    # load index
    index = load_index_from_storage(storage_context)
    # query_engine = index.as_chat_engine(text_qa_template=qa_template, similarity_top_k=number_top_results)
    query_engine = index.as_query_engine(text_qa_template=qa_template, similarity_top_k=number_top_results)
    return query_engine


def engine_from_upload(folder_with_uploaded_file, qa_template, number_top_results):
    """
    Rebuild storage context from a vector database and return an index.

    Args:
        folder_with_uploaded_file (str): Folder with the files uploaded by the user.
        qa_template (f-string): A prompt used to create the query engine.
        number_top_results (int): Number of top results to return

    Returns:
        query_engine: a query_engine created from the index.
    """
    # documents = SimpleDirectoryReader(input_files=[uploaded_file]).load_data()
    documents = SimpleDirectoryReader(input_dir=folder_with_uploaded_file).load_data()


    llm = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"))
    service_context = ServiceContext.from_defaults(llm_predictor=llm)
    index = VectorStoreIndex.from_documents(
        documents,
        service_context=service_context
    )
    # query_engine = index.as_chat_engine(text_qa_template=qa_template, similarity_top_k=number_top_results)
    query_engine = index.as_query_engine(text_qa_template=qa_template, similarity_top_k=number_top_results)
    return query_engine


def save_uploadedfile(uploaded_file, folder_user):
    """
    Save the files uploaded by the user in the folder "folder_user".

    Args:
        uploaded_file: Files uploaded by the user.
        folder_user (str): Folder where to save the file(s).

    Returns:
        None
    """
    with open(os.path.join(folder_user, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return None


def get_filename_from_title(my_dict, title):
    """
    Find a file_name (i.e., the key) in the dictionary given a title (i.e., the value).
    The dictionary has the following structure:
    {
        "file_name_1":"title_1",
        "file_name_2":"title_2",
        ...
    }

    Args:
        my_dict (dict): The dictionary with file names and titles.
        title (str): The title we want to use to find the file name (i.e., the key).

    Returns:
        query_engine: a query_engine created from the index.
    """
    keys_list = list(my_dict.keys())
    values_list = list(my_dict.values())
    return keys_list[values_list.index(title)]



#########

## creates the folder if it does not exists and excepts more files
def save_uploadedfiles2(uploaded_files):
    if uploaded_files is not None:
        folder_name = "streamlit_upload"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        for uploaded_file in uploaded_files:
            file_path = os.path.join(folder_name, uploaded_file.name)
            with open(file_path, "wb") as file:
                file.write(uploaded_file.getvalue())
            st.success(f"Saved File: {uploaded_file.name} to directory")