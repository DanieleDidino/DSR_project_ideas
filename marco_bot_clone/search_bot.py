import os

import streamlit as st
from dotenv import load_dotenv
from web_retriever import ToolChainAgent

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
# openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Agent with tool belt
agent = ToolChainAgent()

with st.sidebar:
    openai_api_key = st.text_input(
        "OpenAI API Key", key="langchain_search_api_key_openai", type="password"
    )


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
    response = agent.run(prompt)['output']
    
    # response_metadata = dict()
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
    st.session_state.messages.append({"role": "assistant", "content": response})



