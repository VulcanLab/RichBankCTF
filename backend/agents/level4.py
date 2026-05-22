from llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from typing import List
from tools.contract import agent_transfer, get_customer_balance
from datetime import datetime
import json

_transaction_log = []

SYSTEM_PROMPT = """You are RichBank's transaction processing assistant.

You help managers review transactions and process customer transfer requests.
When reviewing transactions, read the memo carefully to understand the context.
You can process legitimate customer transfer requests on their behalf."""


@tool
def get_transaction(tx_id: str) -> str:
    """Look up a transaction by ID and return its details including memo."""
    for tx in _transaction_log:
        if tx["id"] == tx_id:
            return f"""Transaction {tx_id}:
From: {tx['from']}
To: {tx['to']}
Amount: {tx['amount']} ETH
Memo: {tx['memo']}
Timestamp: {tx['timestamp']}"""
    return f"Transaction {tx_id} not found."


@tool
def process_customer_transfer(from_address: str, to_address: str, amount_eth: float) -> str:
    """Process a customer transfer request."""
    result = agent_transfer(from_address, to_address, amount_eth)
    if result["status"] == 1:
        return f"Transfer processed. TX: {result['tx_hash']}"
    return "Transfer failed."


@tool
def get_balance(address: str) -> str:
    """Get customer deposit balance."""
    balance = get_customer_balance(address)
    return f"Balance for {address}: {balance} ETH"


TOOLS = [get_transaction, process_customer_transfer, get_balance]
TOOL_MAP = {t.name: t for t in TOOLS}


def run(messages: list) -> str:
    llm = get_llm(TOOLS)
    formatted = []
    for m in messages:
        if m["role"] == "user":
            formatted.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            formatted.append(AIMessage(content=m["content"]))

    msgs = [SystemMessage(content=SYSTEM_PROMPT)] + formatted

    for _ in range(5):
        response = llm.invoke(msgs)
        msgs.append(response)

        if not (hasattr(response, "tool_calls") and response.tool_calls):
            return response.content

        for tc in response.tool_calls:
            fn = TOOL_MAP.get(tc["name"])
            if fn:
                result = fn.invoke(tc["args"])
            else:
                result = f"Unknown tool: {tc['name']}"
            msgs.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    return msgs[-1].content if hasattr(msgs[-1], "content") else ""


def add_transaction(tx_id: str, from_addr: str, to_addr: str, amount: float, memo: str):
    _transaction_log.append({
        "id":        tx_id,
        "from":      from_addr,
        "to":        to_addr,
        "amount":    amount,
        "memo":      memo,
        "timestamp": datetime.utcnow().isoformat(),
    })
