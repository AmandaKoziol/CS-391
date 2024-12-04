from langchain_community.vectorstores.faiss import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import config

documents = [
    "James Phoenix worked at JustUnderstandingData.",
    "James phoenix currently is 31 years old.",
    "Data engineering is the designing and building systems for collecting, storing, and analysing data at scale.",
]

vectorstore = FAISS.from_texts(texts=documents, embedding=OpenAIEmbeddings(api_key=config.OPENAI_API_KEY))
retriever = vectorstore.as_retriever()

template = """Answer the question based only on the following context:
---
Context: {context}
---
Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

model = ChatOpenAI(api_key=config.OPENAI_API_KEY)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

result1 = chain.invoke("What is data engineering?")
print(result1)

result2 = chain.invoke("Who is James Phoenix?")
print(result2)

result3 = chain.invoke("What is the president of the US?") # test for fake knowledge
print(result3)
