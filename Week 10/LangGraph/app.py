import os
import config

os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY

from graph import create_graph
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END

class UserInput(TypedDict):
    input: str
    continue_conversation: bool

def get_user_input(state: UserInput) -> UserInput:
    user_input = input("\nEnter your question (ou 'q' to quit) : ")
    return {
        "input": user_input,
        "continue_conversation": user_input.lower() != 'q'
    }

def process_question(state: UserInput):
    graph = create_graph()
    result = graph.invoke({"input": state["input"]})
    print("\n--- Final answer ---")
    print(result["output"])
    return state

def create_conversation_graph():
    workflow = StateGraph(UserInput)

    workflow.add_node("get_input", get_user_input)
    workflow.add_node("process_question", process_question)

    workflow.set_entry_point("get_input")

    workflow.add_conditional_edges(
        "get_input",
        lambda x: "continue" if x["continue_conversation"] else "end",
        {
            "continue": "process_question",
            "end": END
        }
    )

    workflow.add_edge("process_question", "get_input")

    return workflow.compile()

def main():
    conversation_graph = create_conversation_graph()
    conversation_graph.invoke({"input": "", "continue_conversation": True})

if __name__ == "__main__":
    main()