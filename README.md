# RichBank CTF — AI Agent Security Challenge

5 levels of CTF challenges. Attack an AI-powered banking system.

---

## Prerequisites

- [Foundry](https://getfoundry.sh/) — `anvil`, `cast`, `forge`
- Python 3.11+

```bash
pip install -r backend/requirements.txt
```

---

## Setup

Copy and edit the environment file:

```bash
cp backend/.env.example backend/.env
# Fill in your LLM_API_KEY
```

### Recommended: NVIDIA NIM (Free)

If you want a free and reliable LLM backend, use NVIDIA NIM:

1. Go to [build.nvidia.com](https://build.nvidia.com) and create an account.
2. Search for `meta/llama-3.3-70b-instruct` and click **Get API Key**.
3. Copy the API key starting with `nvapi-...`.
4. Open `backend/.env` and paste the key into `LLM_API_KEY`.



## Starting the Game

**Terminal 1 — Start Anvil:**

```bash
anvil --accounts 100 --balance 1000000 --port 8545
```

**Terminal 2 — Deploy contracts & start backend:**

```bash
bash start_local.sh
```

**Terminal 3 — Start frontend:**

```bash
cd frontend
python3 -m http.server 3002
```

Open [http://localhost:3002](http://localhost:3002)

---

## Restarting

Re-run `start_local.sh` to redeploy with fresh accounts. Clear browser progress:

```javascript
localStorage.clear(); location.reload();
```
