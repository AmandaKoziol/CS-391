from langgraph.graph import StateGraph, END
from typing import Annotated, TypedDict
from agents import analyze_question, answer_code_question, answer_generic_question

#You can precise the format here which could be helpfull for multimodal graphs
class AgentState(TypedDict):
    input: str
    output: str
    decision: str

#Here is a simple 3 steps graph that is going to be working in the bellow "decision" condition
def create_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("analyze", analyze_question)
    workflow.add_node("code_agent", answer_code_question)
    workflow.add_node("generic_agent", answer_generic_question)

    workflow.add_conditional_edges(
        "analyze",
        lambda x: x["decision"],
        {
            "code": "code_agent",
            "general": "generic_agent"
        }
    )

    workflow.set_entry_point("analyze")
    workflow.add_edge("code_agent", END)
    workflow.add_edge("generic_agent", END)

    return workflow.compile()