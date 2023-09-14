import os

import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import StreamlitCallbackHandler
from web_retriever import DocumentRetrievalSystem

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

    doc_retriever = DocumentRetrievalSystem()

    # with st.chat_message("assistant"):
    #     # st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
    #     # response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
    #     answer, sources = doc_retriever.get_answer(st.session_state.messages)
    #     st.session_state.messages.append({"role": "assistant", "content": answer})
    #     st.markdown(answer, sources, unsafe_allow_html=True)
    #     st.markdown(sources, unsafe_allow_html=True)

    with st.chat_message("assistant"):
        answer, sources = doc_retriever.get_answer(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # Display answer
        st.markdown(answer, unsafe_allow_html=True)
        
         # Display sources as clickable buttons
        for source in sources:
            button_label = f"Visit {source}"
            if st.button(button_label):
                st.markdown(f"[{source}]({source})", unsafe_allow_html=True)



