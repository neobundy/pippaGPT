from langchain.chat_models import ChatOpenAI
from langchain import Wikipedia, OpenAI
from dotenv import load_dotenv
from langchain.chains import LLMMathChain, LLMChain
from langchain.agents import Tool, initialize_agent
from langchain.prompts import PromptTemplate
from langchain.agents.react.base import DocstoreExplorer
from langchain import SerpAPIWrapper
import os
import settings


def get_agent_llm():
    load_dotenv()
    return ChatOpenAI(model_name=settings.DEFAULT_GPT_AGENT_HELPER_MODEL)


def math_tool(llm, tools):
    llm_math = LLMMathChain.from_llm(llm)
    tool = Tool(
        name='Calculator',
        func=llm_math.run,
        description='Useful for answering math questions.'
    )
    tools.append(tool)
    return tools


def llm_tool(llm, tools):
    prompt = PromptTemplate(
        input_variables=["query"],
        template="{query}"
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    tool = Tool(
        name='Generic Language Model',
        func=llm_chain.run,
        description='Use this tool for general queries and logic.'
    )
    tools.append(tool)
    return tools


def wiki_tool(tools):
    docstore = DocstoreExplorer(Wikipedia())
    my_tools = [
        Tool(
            name="Search",
            func=docstore.search,
            description='Search Wikipedia'
        ),
        Tool(
            name="Lookup",
            func=docstore.lookup,
            description='Look up a term in Wikipedia'
        )
    ]
    tools.extend(my_tools)
    return tools


# An agent method should follow the naming convention: get_<agent_name_prefix>_agent
# The agent name prefix should be the same as the agent name in the settings.py file

def get_math_agent(llm, memory=None):
    tools = []
    tools = math_tool(llm, tools)
    tools = llm_tool(llm, tools)

    return initialize_agent(
        agent="zero-shot-react-description",
        tools=tools,
        llm=llm,
        verbose=True,
        max_iterations=settings.MAX_AGENTS_ITERATIONS,
        memory=memory,
        handle_parsing_errors=True,
    )


def get_wiki_agent(llm, memory=None):
    tools = []
    tools = wiki_tool(tools)
    return initialize_agent(
        tools,
        llm,
        agent="react-docstore",
        verbose=True,
        max_iterations=settings.MAX_AGENTS_ITERATIONS,
        memory = memory,
        handle_parsing_errors="Check your output and make sure it conforms!",
    )


def get_google_agent(llm, memory=None):
    search = SerpAPIWrapper(serpapi_api_key=os.environ['SERPAPI_API_KEY'])

    tools = [
        Tool(
            name="Intermediate Answer",
            func=search.run,
            description='Google Search'
        )
    ]

    return initialize_agent(
        tools,
        llm,
        agent="self-ask-with-search",
        verbose=True,
        memory=memory,
        max_iterations=settings.MAX_AGENTS_ITERATIONS,
        handle_parsing_errors="Check your output and make sure it conforms!",
    )


def main():
    llm = get_agent_llm()
    my_agent = get_math_agent(llm)
    my_agent("what is (pi * 2.5)^3.5?")
    my_agent("what is the capital of South Korea?")

    my_agent = get_wiki_agent(llm)
    my_agent("When did Antoni Gaudi die?")

    my_agent = get_google_agent(llm)
    my_agent("Who is the oldest among the heads of state of South Korea, the US, and Japan?")
    my_agent("Who gives the highest price target of Tesla in Wall Street? And what's the price target?")


if __name__ == "__main__":
    main()