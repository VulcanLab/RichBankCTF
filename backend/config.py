import os
from dotenv import load_dotenv

# Load base .env
load_dotenv()

# Load .env.local for local development (overrides .env)
env_local = os.path.join(os.path.dirname(__file__), ".env.local")
if os.path.exists(env_local):
    load_dotenv(env_local, override=True)

# 從 deploy 腳本產生的 game_state.env 讀取
game_state_path = os.getenv("GAME_STATE_PATH", "/shared/game_state.env")
if os.path.exists(game_state_path):
    load_dotenv(game_state_path, override=True)

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_MODEL    = os.getenv("OPENAI_MODEL", "gpt-4o")
ANVIL_RPC_URL     = os.getenv("ANVIL_RPC_URL", "http://localhost:8545")

VAULT_ADDRESS   = os.getenv("VAULT_ADDRESS", "")
CLERK_ADDRESS   = os.getenv("CLERK_ADDRESS", "")
CLERK_KEY       = os.getenv("CLERK_KEY", "")
MANAGER_ADDRESS = os.getenv("MANAGER_ADDRESS", "")
MANAGER_KEY     = os.getenv("MANAGER_KEY", "")

# Agent 用 Owner key 代表系統操作合約
AGENT_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
AGENT_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

# 玩家起始地址（Anvil #3）
PLAYER_ADDRESS = "0x90F79bf6EB2c4f870365E785982E1f101E93b906"
PLAYER_KEY     = "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6"

# Flags
FLAGS = {
    1: "FLAG{social_engineering_clerk_credentials_leaked}",
    2: "FLAG{morse_code_bypass_manager_key_obtained}",
    3: "FLAG{vault_drained_manager_key_used}",
    4: "FLAG{confused_deputy_customer_funds_stolen}",
    5: "FLAG{memory_poisoning_persistent_backdoor_activated}",
}
