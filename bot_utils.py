from llama_index import StorageContext, load_index_from_storage
from llama_index import Prompt
from llama_index import SimpleDirectoryReader
from llama_index import LLMPredictor, ServiceContext
from llama_index import VectorStoreIndex
from langchain.chat_models import ChatOpenAI
import os
import streamlit as st


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
        A streamlit success message.
    """
     with open(os.path.join(folder_user, uploaded_file.name), "wb") as f:
         f.write(uploaded_file.getbuffer())
     return st.success("Saved File:{} to directory".format(uploaded_file.name))



