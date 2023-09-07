import pickle
import os
from datetime import datetime
from pathlib import Path
from llama_index import SimpleDirectoryReader
from llama_index import VectorStoreIndex
import openai
import environ

env = environ.Env()
environ.Env.read_env()
API_KEY = env('OPENAI_API_KEY')
openai.api_key = API_KEY


# Dictionary with this structure:
# {"subfolder_name": "name_to_show_to_user"}
# This must be updated every time a new subfodler is added
ui_dict = {
    "merkblatt_fuer_arbeitslose": "Merkblatt für Arbeitslose",
    "wohnungsaufsichtsgesetz": "Wohnungsaufsichtsgesetz",
    "gewobag_hausordnung": "Gewobag Hausordnung",
    "wohnberechtigungsschein": "Wohnberechtigungsschein"
}


def create_documents_dict(ui_dict, folder_with_subfolders = "docs", folder_dict_path = "docs_list/docs_list.pkl"):
    """
    List the subfolders in the folder "folder_with_subfolders" (each subfolder must contain 
    a pdf file) and then create a dictionary with the structure:
    {
        'Document_name_1 for user': {
            'folder_pdf': 'subfolder_with_file_1',
            'pdf': 'file_1.pdf',
            'json': 'file_1.json'
        },
        'Document_name_2 for user': {
            'folder_pdf': 'subfolder_with_file_2',
            'pdf': 'file_2.pdf',
            'json': 'file_2.json'
        },
        ...
    }

    Args:
        ui_dict (dict): Dictionary with "subfolder_name":"name_to_show_to_user".
        folder_with_subfolders (str): Folder where to read the list of subfolders (each subfolder contains a pdf file).
        folder_dict_path (str): Folder where to save the dictionary.
    
    Returns:
        documents_dict: A dictionary with the structure showed above.
        Also, save the dictionary in the folder "folder_dict_path".
    """

    # Create a list with the subfolders
    folders_list = os.listdir(folder_with_subfolders)

    # empy dictionary
    documents_dict = {}

    for folder in folders_list:
        file_pdf = os.listdir("docs" + "/" + folder)
        documents_dict[ui_dict[folder]] = {
            "folder_pdf": folder,
            "pdf": file_pdf[0],
            "json": Path(*file_pdf).stem + ".json"
        }
    
    with open(folder_dict_path,"wb") as file:
        pickle.dump(documents_dict, file)
    
    return documents_dict


def save_documents_embedding(documents_dict, filename_vector_db):
    """
    Save the embedding for the documents. The argument has the following structure:
    documents_dict = {
        'Document_name_1 for user': {
            'folder_pdf': 'subfolder_with_file_1',
            'pdf': 'file_1.pdf',
            'json': 'file_1.json'
        },
        'Document_name_2 for user': {
            'folder_pdf': 'subfolder_with_file_2',
            'pdf': 'file_2.pdf',
            'json': 'file_2.json'
        },
        ...
    }

    Args:
        documents_dict (dict): Dictionary with the structure described above.
        filename_vector_db (str): File where to save the vector database.
    
    Returns:
        None, save the dictionary in the folder "folder_dict_path".
    """

    # Create a list with the paths to the pdf files
    doc_paths = []
    for file in documents_dict.values():
        doc_paths.append(Path("docs", file["folder_pdf"], file["pdf"]))
    
    print("Start loading documents")
    docs = load_data(doc_paths)
    print("Finished")
    
    print("Start creating embeddings")
    index = create_embedding(docs)
    print("Finished")

    print("Start saving embeddings")
    save_vector_database(
        index=index,
        # folder_vec_db="vector_db",
        filename_vector_db=filename_vector_db
    )
    print("Finished")

    return None
    

def load_data(doc_path):
    """
    Load documents using "SimpleDirectoryReader" from "llama_index".
    
    Args:
        doc_path (list): List with the paths to the pdf files.
    
    Returns:
        docs: the list of documents read with "SimpleDirectoryReader"
    """
    docs = SimpleDirectoryReader(input_files=doc_path).load_data()
    return docs


def create_embedding(docs):
    """
    Create a vector database with the documents in "docs.

    Args:
        docs (list of Document): list of documents created with "SimpleDirectoryReader"

    Returns:
        index (VectorStoreIndex): Vector database.
    """
    index = VectorStoreIndex.from_documents(docs)
    return index


def save_vector_database(index, folder_vec_db="vector_db", filename_vector_db="vector_database"):
    """
    Save a vector database  in the folder "folder_vec_db" with the name "filename_vector_db".

    Args:
        index (VectorStoreIndex): Vector database.
        folder_vec_db (str): Folder in which to save the vector database.
        filename_vector_db (str): File where to save the vector database (if "vector_database" adds the datetime at the end of the name).

    Returns:
        None, saves the vector database in the folder "vector_db".
    """
    if filename_vector_db == "vector_database":
        filename_vector_db = "vector_database" + datetime.now().strftime("_%Y_%m_%d__%H_%M") + ".json"
    # index.storage_context.persist(persist_dir=folder_vec_db, docstore_fname=filename_vector_db)
    index.storage_context.persist(persist_dir=folder_vec_db)
    return None


if __name__ == '__main__':

    print("Start crearting docs_list/docs_list.pkl")
    documents_dict = create_documents_dict(ui_dict)
    print("Finished")

    filename_vector_db = "vector_database_1.json"
    save_documents_embedding(documents_dict, filename_vector_db)
