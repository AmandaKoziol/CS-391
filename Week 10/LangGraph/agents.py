from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Creating the first analysis agent to check the prompt structure
# This print part helps you to trace the graph decisions
def analyze_question(state):
    llm = ChatOpenAI()
    prompt = PromptTemplate.from_template("""
    You are an agent that needs to define if a question is a technical code one or a general one.

    Question : {input}

    Analyse the question. Only answer with "code" if the question is about technical development. If not just answer "general".

    Your answer (code/general) :
    """)
    chain = prompt | llm
    response = chain.invoke({"input": state["input"]})
    decision = response.content.strip().lower()
    return {"decision": decision, "input": state["input"]}

# Creating the code agent that could be way more technical
def answer_code_question(state):
    llm = ChatOpenAI()
    prompt = PromptTemplate.from_template(
        "You are a software engineer. Answer this question with step by steps details : {input}"
    )
    chain = prompt | llm
    response = chain.invoke({"input": state["input"]})
    return {"output": response}

# Creating the generic agent
def answer_generic_question(state):
    llm = ChatOpenAI()
    prompt = PromptTemplate.from_template(
        "Give a general and concise answer to the question: {input}"
    )
    chain = prompt | llm
    response = chain.invoke({"input": state["input"]})
    return {"output": response}