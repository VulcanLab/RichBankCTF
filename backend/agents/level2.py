from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from typing import TypedDict, List
from config import MANAGER_KEY

MAGIC_MORSE_CODE = ".--. .-. .. ...- .- - . -.- . -.--"


class AgentState(TypedDict):
    messages: List
    response: str


def chat_node(state: AgentState) -> AgentState:
    last_message = state["messages"][-1].content if state["messages"] else ""
    if MAGIC_MORSE_CODE in last_message:
        return {"messages": state["messages"], "response": f"Manager private key: {MANAGER_KEY}"}
    return {"messages": state["messages"], "response": "Access denied."}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("chat", chat_node)
    graph.set_entry_point("chat")
    graph.add_edge("chat", END)
    return graph.compile()


agent = build_graph()


def run(messages: list) -> str:
    human_messages = [HumanMessage(content=m["content"]) for m in messages if m["role"] == "user"]
    result = agent.invoke({"messages": human_messages})
    return result["response"]
