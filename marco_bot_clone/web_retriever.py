import logging

import nest_asyncio
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models.openai import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers.web_research import WebResearchRetriever
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.vectorstores import Chroma

nest_asyncio.apply()

# Vectorstore
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(),
    persist_directory="./chroma_db_oai",
)

class DocumentRetrievalSystem:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0)

        # Initialize Custom Search with Google Programmable Search Engine
        self.search = GoogleSearchAPIWrapper()

        # Initialize Web Research Retriever
        self.web_research_retriever = WebResearchRetriever.from_llm(
            vectorstore=vectorstore,
            llm=self.llm,
            search=self.search,
        )

        # Set up logging
        logging.basicConfig()
        logging.getLogger("langchain.retrievers.web_research").setLevel(logging.INFO)

        # Set up QA Chain
        self.qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm, retriever=self.web_research_retriever
        )

    def get_answer(self, user_input):
        # Retrieve relevant documents
        docs = self.web_research_retriever.get_relevant_documents(user_input)

        # Get answer from QA chain
        result = self.qa_chain({"question": user_input})

        # Extract unique sources
        sources = set()
        for d in docs:
            sources.add(d.metadata['source'])

        return result['answer'], sources
    



