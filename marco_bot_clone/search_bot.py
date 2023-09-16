import logging
import os

import nest_asyncio
import streamlit as st
from bot_utils_marco import default_engine
from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models.openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.retrievers.web_research import WebResearchRetriever
from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper, GoogleSerperAPIWrapper
from langchain.vectorstores import Chroma
from llama_index import Prompt
from llama_index.langchain_helpers.agents import IndexToolConfig, LlamaIndexTool
from web_retriever import AAgent, WWebretriever

GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Vectorstore
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(),
    persist_directory="./chroma_db_oai",
)


with st.sidebar:
    openai_api_key = st.text_input(
        "OpenAI API Key", key="langchain_search_api_key_openai", type="password"
    )

load_dotenv()
openai_api_key= GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi, I'm a chatbot who can search the web. How can I help you?",
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Who won the Women's U.S. Open in 2018?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    web_retriever = WWebretriever(vectorstore)
    agent = AAgent(web_retriever)
    # doc_retriever = DocumentRetrievalSystem()

    with st.chat_message("assistant"):
        answer = agent.run(st.session_state.messages)
        # answer, sources = doc_retriever.get_answer(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Display answer
        st.markdown(answer, unsafe_allow_html=True)
        
        #  # Display sources as clickable buttons
        # for source in sources:
        #     button_label = f"Visit {source}"
        #     if st.button(button_label):
        #         st.markdown(f"[{source}]({source})", unsafe_allow_html=True)



