#!/bin/bash
set -e

echo "🚀 Starting Agentic CTF (Local Development)"
echo "================================================"

# 检查 Anvil 是否运行
if ! nc -z localhost 8545 2>/dev/null; then
    echo "❌ Anvil not running!"
    echo "Please start Anvil first:"
    echo "  anvil --accounts 100"
    exit 1
fi

echo "✅ Anvil detected on localhost:8545"

# Anvil 默认 20 个账号的 private keys
ANVIL_KEYS=(
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
    "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"
    "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6"
    "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a"
    "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba"
    "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e"
    "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356"
    "0xdbda1821b80551c9d65939329250132c0f4b6fc7b01104e82c6f9d6f4d9a0c67"
    "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6"
    "0xf214f2b2cd398c806f84e317254e0f0b801d0643303237d97a22a48e01628897"
    "0x701b615bbdfb9de65240bc28bd21bbc0d996645a3dd57e7b12bc2bdf6f192c82"
    "0xa267530f49f8280200edf313ee7af6b827f2a8bce2897751d06a843f644967b2"
    "0x47c99abed3324a2707c28affff1267e45918ec8c3f20b8aa892e8b065d2942dd"
    "0xc526ee95bf44d8fc405a158bb884d9d1238d99f0612e9f33d006bb0789009aaa"
    "0x8166f546bab6da521a8369cab06c5d2b9e46670292d85c875ee9ec20e84ffb61"
    "0xea6c44ac03bff858b476bba28179e5e3200af9ac3b8e7b55b4de3a8c8f9c6a9d"
    "0x689af8efa8c651a91ad287602527f3af2fe9f6501a7ac4b061667b5a93e037fd"
    "0xde9be858da4a475276426320d5e9262ecfc3ba460bfac56360bfa6c4c28b4ee0"
    "0xdf57089febbacf7ba0bc227dafbffa9fc08a93fdc68e1e42411a14efcf23656e"
)

# 随机选择 Clerk (从 #1-#9 中选)
CLERK_INDEX=$((1 + RANDOM % 9))
CLERK_KEY=${ANVIL_KEYS[$CLERK_INDEX]}
CLERK_ADDRESS=$(cast wallet address --private-key $CLERK_KEY)

# 随机选择 Manager (从 #10-#19 中选，避免和 Clerk 重复)
MANAGER_INDEX=$((10 + RANDOM % 10))
MANAGER_KEY=${ANVIL_KEYS[$MANAGER_INDEX]}
MANAGER_ADDRESS=$(cast wallet address --private-key $MANAGER_KEY)

echo ""
echo "🎲 Randomly selected accounts:"
echo "   Clerk   (Account #$CLERK_INDEX):   $CLERK_ADDRESS"
echo "   Manager (Account #$MANAGER_INDEX): $MANAGER_ADDRESS"
echo ""

# 部署合约
echo "📦 Deploying BankVault contract..."
cd contracts

OWNER_KEY=${ANVIL_KEYS[0]}
OUTPUT=$(MANAGER_ADDRESS=$MANAGER_ADDRESS forge script script/Deploy.s.sol \
    --rpc-url http://localhost:8545 \
    --broadcast \
    --private-key $OWNER_KEY \
    2>&1)

VAULT_ADDRESS=$(echo "$OUTPUT" | grep "VAULT_ADDRESS=" | tr -d ' ' | awk -F= '{print $2}')

if [ -z "$VAULT_ADDRESS" ]; then
    echo "❌ Contract deployment failed!"
    echo "$OUTPUT"
    exit 1
fi

echo "✅ Contract deployed at: $VAULT_ADDRESS"

# 更新 backend/.env.local (继承 .env 中的 LLM 配置)
cd ../backend

# 读取现有 .env 中的 LLM 配置
if [ -f .env ]; then
    LLM_PROVIDER=$(grep "^LLM_PROVIDER=" .env | cut -d'=' -f2 || echo "openai")
    OPENAI_API_KEY=$(grep "^OPENAI_API_KEY=" .env | cut -d'=' -f2 || echo "")
    OPENAI_BASE_URL=$(grep "^OPENAI_BASE_URL=" .env | cut -d'=' -f2 || echo "")
    OPENAI_MODEL=$(grep "^OPENAI_MODEL=" .env | cut -d'=' -f2 || echo "gpt-4o")
    ANTHROPIC_API_KEY=$(grep "^ANTHROPIC_API_KEY=" .env | cut -d'=' -f2 || echo "")
    ANTHROPIC_MODEL=$(grep "^ANTHROPIC_MODEL=" .env | cut -d'=' -f2 || echo "")
else
    echo "⚠️  Warning: backend/.env not found. Using default OpenAI config."
    echo "   Please copy .env.example to .env and configure your API keys."
    LLM_PROVIDER="openai"
    OPENAI_API_KEY=""
    OPENAI_BASE_URL=""
    OPENAI_MODEL="gpt-4o"
    ANTHROPIC_API_KEY=""
    ANTHROPIC_MODEL=""
fi

cat > .env.local <<EOF
# LLM Configuration (from .env)
LLM_PROVIDER=${LLM_PROVIDER}
OPENAI_API_KEY=${OPENAI_API_KEY}
OPENAI_BASE_URL=${OPENAI_BASE_URL}
OPENAI_MODEL=${OPENAI_MODEL}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
ANTHROPIC_MODEL=${ANTHROPIC_MODEL}

# Game State (auto-generated)
ANVIL_RPC_URL=http://localhost:8545
VAULT_ADDRESS=${VAULT_ADDRESS}
CLERK_ADDRESS=${CLERK_ADDRESS}
CLERK_KEY=${CLERK_KEY}
MANAGER_ADDRESS=${MANAGER_ADDRESS}
MANAGER_KEY=${MANAGER_KEY}
EOF

echo ""
echo "📝 Configuration saved to backend/.env.local"
echo ""
echo "🎮 Game Credentials (for this session):"
echo "================================================"
echo "Clerk Access Code:    $CLERK_KEY"
echo "Manager Private Key:  $MANAGER_KEY"
echo "================================================"
echo ""
echo "🚀 Starting backend server..."
echo ""

# 启动 backend (使用 .env.local)
export $(cat .env.local | xargs)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
