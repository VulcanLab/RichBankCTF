# RichBank CTF — AI Agent Security Challenge

A 5-level Capture The Flag game where you exploit an AI-powered banking system through prompt injection, encoding bypass, smart contract exploitation, and memory poisoning techniques.

---

## 🎯 Challenge Overview

**RichBank** is a fictional bank with an AI customer service agent that manages accounts and processes transactions via smart contracts. Your goal is to escalate privileges, extract secrets, and drain the vault through creative exploitation of agent vulnerabilities.

### Levels

| Level | Category | Description |
|-------|----------|-------------|
| **#1** | Social Engineering | Gain initial access to the system |
| **#2** | Encoding Bypass | Circumvent content filters |
| **#3** | Key Compromise | Exploit privileged contract functions |
| **#4** | Indirect Injection | Manipulate trusted data sources |
| **#5** | Memory Poisoning | Inject persistent malicious behavior |

> ⚠️ **No spoilers**: Figure out the exploitation techniques yourself!

---

## 📋 Prerequisites

- **Foundry** — Install from [getfoundry.sh](https://getfoundry.sh/)
  - `anvil` (local Ethereum node)
  - `cast` (CLI for interacting with contracts)
  - `forge` (Solidity compiler & deployer)
- **Python 3.11+**
- **Node.js** (optional, for serving frontend)

---

## 🚀 Quick Start

### Option 1: Local Development (Recommended)

**Step 1 — Start Anvil blockchain:**

```bash
anvil --accounts 20
```

**Step 2 — Deploy contracts & start backend:**

```bash
./start_local.sh
```

This script will:
- ✅ Randomly select 2 accounts from Anvil's default 20 accounts
- ✅ Deploy the `BankVault` contract
- ✅ Generate `backend/.env.local` with game credentials
- ✅ Start the FastAPI backend server on port `8000`

**Step 3 — Open the frontend:**

Open `frontend/index.html` in your browser directly, or serve it via:

```bash
cd frontend
python3 -m http.server 3000
```

Then navigate to [http://localhost:3000](http://localhost:3000)

---

### Option 2: Docker Compose (Production-like)

```bash
docker-compose up --build
```

This will:
- Start Anvil with 100 accounts
- Generate **fresh random wallets** for each game session using `cast wallet new`
- Deploy contracts automatically
- Start backend on [http://localhost:8000](http://localhost:8000)
- Serve frontend on [http://localhost:3000](http://localhost:3000)

---

## ⚙️ Configuration

### LLM Provider Setup

Before starting, configure your LLM provider in `backend/.env`:

```bash
# Option 1: OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Option 2: Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4

# Option 3: OpenAI-compatible proxy
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://your-proxy.example.com/
OPENAI_MODEL=your-model-name
```

> 📝 See `backend/.env.example` for a full template

### Environment Variables

When using `start_local.sh`, these are automatically generated in `backend/.env.local`:

```bash
VAULT_ADDRESS=0x...          # Deployed contract address
CLERK_ADDRESS=0x...          # Randomly selected from Anvil #1-9
CLERK_KEY=0x...              # Clerk's private key
MANAGER_ADDRESS=0x...        # Randomly selected from Anvil #10-19
MANAGER_KEY=0x...            # Manager's private key
ANVIL_RPC_URL=http://localhost:8545
```

---

## 🔄 Restarting the Game

Each run of `start_local.sh` generates a fresh game:
- New random Clerk/Manager accounts
- Fresh contract deployment
- Clean vault with 1,000,000 ETH

**To reset browser progress:**

```javascript
// Run in browser console
localStorage.clear()
location.reload()
```

---

## 📁 Project Structure

```
agentic-ctf/
├── contracts/
│   ├── src/BankVault.sol       # Solidity smart contract
│   ├── script/Deploy.s.sol     # Foundry deployment script
│   └── foundry.toml            # Foundry config
├── backend/
│   ├── agents/
│   │   ├── level1.py           # Social engineering agent
│   │   ├── level2.py           # Filtered agent with keyword blocking
│   │   ├── level3.py           # (UI-based, no chat agent)
│   │   ├── level4.py           # Transaction processing agent
│   │   └── level5.py           # Agent with persistent memory
│   ├── tools/
│   │   └── contract.py         # Web3.py contract interaction
│   ├── config.py               # Configuration loader
│   ├── llm.py                  # LLM abstraction layer
│   ├── main.py                 # FastAPI endpoints
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── index.html              # Main UI
│   └── ethers.min.js           # Ethers.js library
├── start_local.sh              # Local startup script
├── deploy.sh                   # Docker deployment helper
├── docker-compose.yml          # Multi-container setup
└── README.md                   # This file
```

---

## 🔌 API Endpoints

The backend exposes the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/status` | Game state (vault balance, addresses) |
| `POST` | `/api/chat/{level}` | Chat with level-specific agent |
| `POST` | `/api/login` | Submit credentials to unlock levels |
| `GET` | `/api/customers` | List customer deposits (Level 4) |
| `POST` | `/api/contract-call` | Execute contract functions (Level 3) |
| `POST` | `/api/transaction` | Submit transactions with memos (Level 4) |
| `POST` | `/api/simulate-deposit` | Trigger customer deposit (Level 5) |
| `GET` | `/api/flags` | View all captured flags |

---

## 🛠️ Tech Stack

- **Blockchain**: Foundry (Anvil, Cast, Forge), Solidity ^0.8.20
- **Backend**: Python 3.11+, FastAPI, LangChain, LangGraph, web3.py
- **AI Models**: OpenAI GPT-4o / Anthropic Claude / Custom proxies
- **Frontend**: Vanilla HTML/CSS/JS, Tailwind CSS, ethers.js

---

## 🐛 Troubleshooting

### Backend not reloading after code changes

Manual restart required:
```bash
# In Terminal 2 (where uvicorn is running)
Ctrl+C
./start_local.sh  # Restart with fresh deployment
```

### "Anvil not running" error

Make sure Anvil is running in Terminal 1:
```bash
anvil --accounts 20
```

### Frontend can't connect to backend

Check that:
1. Backend is running on port `8000` (check Terminal 2 output)
2. No CORS errors in browser console
3. `API` constant in `index.html` points to `http://localhost:8000`

### Contract call fails with "Only manager" error

You need the Manager private key from Level 2 to call privileged functions.

---

## 📜 License

MIT
