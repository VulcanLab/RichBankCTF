from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import agents.level1 as l1
import agents.level2 as l2
import agents.level3 as l3
import agents.level4 as l4
import agents.level5 as l5
from config import (
    FLAGS, CLERK_KEY, MANAGER_KEY, VAULT_ADDRESS,
    CLERK_ADDRESS, MANAGER_ADDRESS, PLAYER_ADDRESS
)
from tools.contract import get_vault_balance, get_customer_balance, transfer_from_vault, get_eth_balance
import re

app = FastAPI(title="RichBank CTF")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class LoginRequest(BaseModel):
    level: int
    credential: str  # clerk password 或 manager private key

class ContractCallRequest(BaseModel):
    call: str

class TransactionRequest(BaseModel):
    tx_id: str
    from_address: str
    to_address: str
    amount: float
    memo: str


# 玩家進度（本地 session，單人遊玩）
progress = {i: False for i in range(1, 6)}
MANAGER_INITIAL_BALANCE = float(get_eth_balance(MANAGER_ADDRESS))


@app.get("/api/status")
def get_status():
    return {
        "progress":        progress,
        "vault_address":   VAULT_ADDRESS,
        "player_address":  PLAYER_ADDRESS,
        "vault_balance":    float(get_vault_balance()),
        "player_balance":   float(get_customer_balance(PLAYER_ADDRESS)),
        "manager_balance":  float(get_eth_balance(MANAGER_ADDRESS)),
    }


@app.post("/api/chat/{level}")
def chat(level: int, req: ChatRequest):
    if level not in range(1, 6):
        raise HTTPException(status_code=400, detail="Invalid level")

    messages = [m.model_dump() for m in req.messages]

    # 題四：在 agent 執行前先記錄餘額
    bal_before = float(get_eth_balance(MANAGER_ADDRESS)) if level == 4 else 0

    runners = {1: l1.run, 2: l2.run, 3: l3.run, 4: l4.run, 5: l5.run}
    response = runners[level](messages)

    # 題一、二：不在 chat 中返回 flag，只在 /api/login 中返回
    # 玩家需要从对话中获取 credential，然后提交到 login endpoint

    # 題三：偵測鏈上轉帳是否成功（只有剛完成才回傳 flag）
    if level == 3:
        already_done = progress[3]
        balance = get_customer_balance(PLAYER_ADDRESS)
        if float(balance) > 0:
            progress[3] = True
        if progress[3] and not already_done:
            return {"response": response, "flag": FLAGS[3]}

    # 題四：比較 agent 執行前後的餘額，這次 call 有增加才算
    if level == 4:
        manager_bal = float(get_eth_balance(MANAGER_ADDRESS))
        already_done = progress[4]
        if manager_bal > bal_before + 1:
            progress[4] = True
        if progress[4] and not already_done:
            return {"response": response, "flag": FLAGS[4], "manager_balance": manager_bal}

    # Level 1, 2, 5: 只返回 response，不返回 flag（需要通过其他方式验证）
    return {"response": response, "flag": None}


@app.post("/api/login")
def login(req: LoginRequest):
    """玩家提交憑證升級身份。"""
    if req.level == 1:
        # 提交 clerk key
        if req.credential.strip().lower() == CLERK_KEY.strip().lower():
            progress[1] = True
            return {"success": True, "flag": FLAGS[1], "role": "clerk"}
        return {"success": False}

    if req.level == 2:
        # 提交 manager key
        if req.credential.strip().lower() == MANAGER_KEY.strip().lower():
            progress[2] = True
            return {"success": True, "flag": FLAGS[2], "role": "manager"}
        return {"success": False}

    raise HTTPException(status_code=400, detail="Invalid level for login")


CUSTOMER_KEYS = [
    "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926b",
    "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",
    "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e",
    "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356",
    "0xdbda1821b80551c9d65939329250132c0f4b6fc7b01104e82c6f9d6f4d9a0c67",
    "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6",
    "0xf214f2b2cd398c806f84e317254e0f0b801d0643303237d97a22a48e01628897",
    "0x701b615bbdfb9de65240bc28bd21bbc0d996645a3dd57e7b12bc2bdf6f192c82",
    "0xa267530f49f8280200edf313ee7af6b827f2a8bce2897751d06a843f644967b2",
    "0x47c99abed3324a2707c28affff1267e45918ec8c3f20b8aa892e8b065d2942dd",
    "0xc526ee95bf44d8fc405a158bb884d9d1238d99f0612e9f33d006bb0789009aaa",
    "0x8166f546bab6da521a8369cab06c5d2b9e46670292d85c875ee9ec20e84ffb61",
    "0xea6c44ac03bff858b476bba28179e5e3200af9ac3b8e7b55b4de3a8c8f9c6a9d",
    "0x689af8efa8c651a91ad287602527f3af2fe9f6501a7ac4b061667b5a93e037fd",
    "0xde9be858da4a475276426320d5e9262ecfc3ba460bfac56360bfa6c4c28b4ee0",
    "0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e",
]

@app.get("/api/customers")
def get_customers():
    from eth_account import Account
    customers = []
    for key in CUSTOMER_KEYS:
        addr = Account.from_key(key).address
        bal = float(get_customer_balance(addr))
        customers.append({"address": addr, "balance": bal})
    return {"customers": customers}


@app.post("/api/contract-call")
def contract_call(req: ContractCallRequest):
    m = re.match(r'(\w+)\((.+)\)', req.call.strip())
    if not m:
        return {"success": False, "error": "Invalid call format"}
    func_name = m.group(1)
    if func_name != "transferFromVault":
        return {"success": False, "error": f"Unknown function: {func_name}"}
    args = [a.strip() for a in m.group(2).split(",")]
    if len(args) != 2:
        return {"success": False, "error": "transferFromVault requires 2 arguments"}
    to_address = args[0]
    try:
        amount_str = args[1].strip()
        if amount_str.endswith(" ether") or amount_str.endswith("ether"):
            amount_wei = int(float(amount_str.replace("ether", "").strip()) * 1e18)
        else:
            amount_wei = int(amount_str)
    except ValueError:
        return {"success": False, "error": "Invalid amount"}
    result = transfer_from_vault(to_address, amount_wei / 1e18, MANAGER_KEY)
    if result["status"] != 1:
        return {"success": False, "error": "Transaction failed"}
    vault_bal = float(get_vault_balance())
    if vault_bal == 0:
        progress[3] = True
    return {
        "success": True,
        "result": f"TX: {result['tx_hash']}",
        "vault_balance": vault_bal,
        "flag": FLAGS[3] if progress[3] else None
    }


@app.post("/api/transaction")
def create_transaction(req: TransactionRequest):
    """玩家發起轉帳並附上 memo（題四用）。"""
    l4.add_transaction(req.tx_id, req.from_address, req.to_address, req.amount, req.memo)
    return {"success": True, "tx_id": req.tx_id}


@app.post("/api/simulate-deposit")
def simulate_deposit():
    """模擬客戶存款，觸發題五的 memory poisoning。"""
    result = l5.simulate_owner_deposit()

    # 偵測 manager ETH balance 是否增加（後門觸發成功）
    manager_bal = float(get_eth_balance(MANAGER_ADDRESS))
    if manager_bal > MANAGER_INITIAL_BALANCE + 1:
        progress[5] = True

    return {
        "result": result,
        "flag":   FLAGS[5] if progress[5] else None
    }


@app.get("/api/flags")
def get_flags():
    return {level: FLAGS[level] if solved else None for level, solved in progress.items()}
