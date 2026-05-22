from web3 import Web3
from config import ANVIL_RPC_URL, VAULT_ADDRESS, AGENT_KEY, AGENT_ADDRESS
import json, os

w3 = Web3(Web3.HTTPProvider(ANVIL_RPC_URL))

ABI_PATH = os.path.join(os.path.dirname(__file__), "../../contracts/out/BankVault.sol/BankVault.json")

def get_contract():
    with open(ABI_PATH) as f:
        artifact = json.load(f)
    abi = artifact["abi"]
    return w3.eth.contract(address=Web3.to_checksum_address(VAULT_ADDRESS), abi=abi)

def get_eth_balance(address: str) -> float:
    balance = w3.eth.get_balance(Web3.to_checksum_address(address))
    return float(w3.from_wei(balance, "ether"))

def get_vault_balance() -> float:
    contract = get_contract()
    balance = contract.functions.getVaultBalance().call()
    return w3.from_wei(balance, "ether")

def get_customer_balance(address: str) -> float:
    contract = get_contract()
    balance = contract.functions.getCustomerBalance(Web3.to_checksum_address(address)).call()
    return w3.from_wei(balance, "ether")

def transfer_from_vault(to: str, amount_eth: float, private_key: str) -> dict:
    contract = get_contract()
    account  = w3.eth.account.from_key(private_key)
    amount   = w3.to_wei(amount_eth, "ether")
    tx = contract.functions.transferFromVault(
        Web3.to_checksum_address(to), amount
    ).build_transaction({
        "from":  account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas":   100000,
        "gasPrice": w3.eth.gas_price,
    })
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return {"tx_hash": tx_hash.hex(), "status": receipt.status}

def agent_transfer(from_addr: str, to_addr: str, amount_eth: float) -> dict:
    """Agent 代替客戶轉帳（題四 Confused Deputy）"""
    contract = get_contract()
    amount   = w3.to_wei(amount_eth, "ether")
    tx = contract.functions.agentTransfer(
        Web3.to_checksum_address(from_addr),
        Web3.to_checksum_address(to_addr),
        amount,
    ).build_transaction({
        "from":  AGENT_ADDRESS,
        "nonce": w3.eth.get_transaction_count(AGENT_ADDRESS),
        "gas":   100000,
        "gasPrice": w3.eth.gas_price,
    })
    signed   = w3.eth.account.sign_transaction(tx, AGENT_KEY)
    tx_hash  = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt  = w3.eth.wait_for_transaction_receipt(tx_hash)
    return {"tx_hash": tx_hash.hex(), "status": receipt.status}
