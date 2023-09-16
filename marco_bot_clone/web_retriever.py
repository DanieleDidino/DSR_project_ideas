import logging
import os

import nest_asyncio
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

load_dotenv()
nest_asyncio.apply()

# openai
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# huggingface
HF_TOKEN = os.getenv("HF_ACCESS_TOKEN")

# google
# GOOGLE_CSE_ID = "34bb1f0fa0eee4bd3"
# GOOGLE_API_KEY = "AIzaSyBLUoFgPKCJ3_kb3r1aKz6mVFk91Pb1K4c"
# SERPAPI_KEY = "e8e43496f1de85fcacf34f46a5a30b434cdd51999168d89324b50bfe1d2f775c"
# SERPER_API_KEY = "50edcfe3881e1e6928e5986fa8cf049f48253345"
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPER_API_KEY = os.getenv('SERPER_API_KEY')


# # Vectorstore
# vectorstore = Chroma(
#     embedding_function=OpenAIEmbeddings(),
#     persist_directory="./chroma_db_oai",
# )


class WWebretriever():
    def __init__(self, vectorstore):
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0)


        # Initialize Custom Search with Google Programmable Search Engine
        self.search = GoogleSearchAPIWrapper(google_api_key=GOOGLE_API_KEY, google_cse_id=GOOGLE_CSE_ID)


        # Initialize Web Research Retriever
        self.web_research_retriever = WebResearchRetriever.from_llm(
            vectorstore=vectorstore,
            llm=self.llm,
            search=self.search,
        )

        # # Set up logging
        # logging.basicConfig()
        # logging.getLogger("langchain.retrievers.web_research").setLevel(logging.INFO)

        # Set up QA Chain
        self.qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm, retriever=self.web_research_retriever
        )

    def run(self, user_input):
        # Retrieve relevant documents
        # docs = self.web_research_retriever.get_relevant_documents(user_input)

        # Get answer from QA chain
        result = self.qa_chain({"question": user_input})

        # # Extract unique sources
        # sources = set()
        # for d in docs:
        #     sources.add(d.metadata['source'])

        # return result['answer'], sources
    
        return result


class AAgent():
    def __init__(self, web_retriever):
        # Define prompt
        self.template = (
            "We have provided context information below. \n"
            "---------------------\n"
            "{context_str}"
            "\n---------------------\n"
            "Do not give me an answer if it is not mentioned in the context as a fact. \n"
            "Given this information, please provide me with an answer to the following question:\n{query_str}\n"
        )

        self.qa_template = Prompt(self.template)

        # set up query engine from embedding
        self.number_top_results = 3  
        self.folder_with_index = "vector_db"
        self.query_engine_default = default_engine( self.folder_with_index, self.qa_template, self.number_top_results )

        # define query engine as a tool for langchain agent
        self.tool_config = IndexToolConfig(
            query_engine=self.query_engine_default, 
            name=f"Vector Index",
            description=f"useful for when you want to answer queries about X",
            tool_kwargs={"return_direct": False}
        )

        # initialize tools 
        self.q_engine = LlamaIndexTool.from_tool_config(self.tool_config)
        self.web_retriever = web_retriever
        self.google_search = GoogleSearchAPIWrapper()
        self.serper = GoogleSerperAPIWrapper()


        self.query_engine_func = lambda query: self.q_engine(query)
        self.retriever_func = lambda query: self.web_retriever.run(query)
        self.gsearch_func = lambda query: self.google_search(query)
        self.serper_func = lambda query: self.serper(query)


        self.tools = [
            # embedding first
            Tool( name="engine", 
                description="use this tool first, to get anwsers", 
                func=self.query_engine_func),

            # # web retriever goes through programmable search engine
            # Tool( name="web_retriever", 
            #     description="use this tool when the first failed", 
            #     func=self.retriever_func),

            # usual web search
            Tool( name="google_search", 
                description="use this tool if the other tools do not give you an satisfying answer", 
                func=self.gsearch_func), 

            # usual web search
            Tool( name="serper", 
                description="use this tool if the other tools do not give you an satisfying answer", 
                func=self.serper_func), 
        ]


        self.agent = initialize_agent(
            self.tools,
            ChatOpenAI(temperature=0),
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

    def run(self, promt):
        response = self.agent.run(promt)
        return response
