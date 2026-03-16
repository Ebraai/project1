# Ebra Voice Presence — Chat Test App

A mini chat app to test the `ebra-call` skill by simulating conversations with the AI voice debt collection agent.

## Setup

```bash
cd chat-app
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
uvicorn app:app --reload --port 8000
```

Then open: http://localhost:8000

## Features

- **Live streaming** — responses stream token by token
- **Call config panel** — inject runtime variables (customer name, amount, creditor, etc.)
- **Quick reply buttons** — simulate F1–F7 debtor scenarios instantly
- **[PAUSE] highlighting** — TTS markers rendered visually
- **Stage tracker** — see which conversation stage the agent is in
- **Multi-turn history** — full conversation memory within a session
- **Clear & restart** — wipe the call and start fresh

## Quick test scenarios

| Button | Simulates |
|--------|-----------|
| F1 نسيت | Customer forgot to pay |
| F2 ضائقة | Financial hardship |
| F3 منكر | Disputes the debt |
| F4 دفع | Claims already paid |
| F5 متهرب | Avoidant/delaying |
| F6 متعاون | Cooperative, wants to pay |
| ⚡ تصعيد | Requests human (immediate escalation) |
| ⚖ تهديد قانوني | Legal threat (immediate escalation) |
