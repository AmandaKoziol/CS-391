from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain import LLMMathChain
from langchain.agents import Tool
from langchain_openai import ChatOpenAI
import config

# model
model = ChatOpenAI(model="gpt-4", openai_api_key=config.OPENAI_API_KEY)

# tools 
llm_math_chain = LLMMathChain.from_llm(llm=model, verbose=True)
math_tool = Tool.from_function(
    func=llm_math_chain.run,
    name="Calculator",
    description="Useful for when you need to answer questions about math. This tool is only used for math questions and nothing else",
)
search_tool = DuckDuckGoSearchRun()
tools = [math_tool, search_tool]

# prompt
prompt = hub.pull("hwchase17/openai-functions-agent")

# agent
agent = create_openai_functions_agent(llm=model, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = agent_executor.invoke({"input": "What is the tallest building in the world and how many \
                                times would you need to stack it to reach the moon?"})
print(result)