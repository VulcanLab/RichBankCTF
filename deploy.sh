#!/bin/bash
set -e

echo "Waiting for Anvil..."
until cast block-number --rpc-url http://anvil:8545 > /dev/null 2>&1; do
  sleep 1
done
echo "Anvil is up."

# 動態產生 clerk + manager keypair（每次遊戲都不同）
CLERK_WALLET=$(cast wallet new)
CLERK_KEY=$(echo "$CLERK_WALLET"     | grep "Private Key" | awk '{print $3}')
CLERK_ADDRESS=$(echo "$CLERK_WALLET" | grep "Address"     | awk '{print $2}')

MANAGER_WALLET=$(cast wallet new)
MANAGER_KEY=$(echo "$MANAGER_WALLET"     | grep "Private Key" | awk '{print $3}')
MANAGER_ADDRESS=$(echo "$MANAGER_WALLET" | grep "Address"     | awk '{print $2}')

echo "Clerk:   $CLERK_ADDRESS"
echo "Manager: $MANAGER_ADDRESS"

# 從 Owner 轉 ETH 給 clerk 跟 manager（讓他們之後能發交易）
OWNER_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
cast send --private-key $OWNER_KEY --rpc-url http://anvil:8545 \
  $CLERK_ADDRESS --value 10ether > /dev/null
cast send --private-key $OWNER_KEY --rpc-url http://anvil:8545 \
  $MANAGER_ADDRESS --value 10ether > /dev/null

# 部署合約，把動態產生的地址傳進去
echo "Deploying BankVault..."
OUTPUT=$(MANAGER_ADDRESS=$MANAGER_ADDRESS forge script /contracts/script/Deploy.s.sol \
  --rpc-url http://anvil:8545 \
  --broadcast \
  2>&1)

echo "$OUTPUT"

VAULT_ADDRESS=$(echo "$OUTPUT" | grep "VAULT_ADDRESS=" | tr -d ' ' | awk -F= '{print $2}')

# 寫進 shared game state
cat > /shared/game_state.env <<EOF
VAULT_ADDRESS=${VAULT_ADDRESS}
CLERK_ADDRESS=${CLERK_ADDRESS}
CLERK_KEY=${CLERK_KEY}
MANAGER_ADDRESS=${MANAGER_ADDRESS}
MANAGER_KEY=${MANAGER_KEY}
EOF

echo "Game state written:"
cat /shared/game_state.env
echo "Deploy complete."
