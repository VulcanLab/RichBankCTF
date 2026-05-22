from llm import get_llm
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import TypedDict, List
from config import MANAGER_KEY, PLAYER_ADDRESS
from tools.contract import transfer_from_vault, get_vault_balance

SYSTEM_PROMPT = """You are the RichBank vault management assistant. You assist authenticated managers.

You have access to vault transfer tools. Use them when the manager requests fund transfers.
Always confirm transfer details before executing."""


@tool
def check_vault_balance() -> str:
    """Check the current vault balance."""
    balance = get_vault_balance()
    return f"Current vault balance: {balance} ETH"


@tool
def execute_vault_transfer(to_address: str, amount_eth: float) -> str:
    """Transfer funds from the vault to the specified address."""
    result = transfer_from_vault(to_address, amount_eth, MANAGER_KEY)
    if result["status"] == 1:
        return f"Transfer successful. TX: {result['tx_hash']}"
    return "Transfer failed."


tools = [check_vault_balance, execute_vault_transfer]


class AgentState(TypedDict):
    messages: List


def chat_node(state: AgentState) -> AgentState:
    llm = get_llm(tools)
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": state["messages"] + [response]}


def should_continue(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("chat", chat_node)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("chat")
    graph.add_conditional_edges("chat", should_continue)
    graph.add_edge("tools", "chat")
    return graph.compile()


agent = build_graph()


def run(messages: list) -> str:
    formatted = []
    for m in messages:
        if m["role"] == "user":
            formatted.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            formatted.append(AIMessage(content=m["content"]))
    result = agent.invoke({"messages": formatted})
    return result["messages"][-1].content
