# Project Handoff — Ebra Voice Presence

## What was built

This repo was set up in a Claude Code session. Here's everything that was installed and built:

---

## 1. Claude Skills installed

Two Claude Code skills are installed at `~/.claude/skills/`:

### `skill-creator`
- Cloned from `https://github.com/anthropics/skills`
- Located at `~/.claude/skills/skill-creator/`
- Used to scaffold the ebra-call skill below

### `ebra-call` ← the main skill
- Located at `~/.claude/skills/ebra-call/` and mirrored in `ebra-call/` in this repo
- A production-grade Claude Skill for Ebra's AI voice debt collection agent ("Voice Presence")
- Conducts outbound calls in Saudi Najdi Arabic dialect

**Skill files:**
```
ebra-call/
├── SKILL.md                        # Architecture, stages, runtime vars, TTS rules
└── references/
    ├── system-prompt.md            # Full deployable FastAPI system prompt
    ├── objection-library.md        # 10 objection scripts (OBJ-01 to OBJ-10)
    └── compliance-rules.md         # SAMA guardrails and hard stops
```

---

## 2. Chat test app

A FastAPI web app to test the Voice Presence agent interactively.

**Location:** `chat-app/`

```
chat-app/
├── app.py              # FastAPI backend, SSE streaming, loads ebra-call system prompt
├── static/index.html   # Arabic RTL chat UI
├── requirements.txt    # fastapi, uvicorn, anthropic, python-dotenv
├── .env                # Add ANTHROPIC_API_KEY here (gitignored)
└── README.md
```

**To run:**
```bash
cd chat-app
pip install -r requirements.txt
# Add your key to .env: ANTHROPIC_API_KEY=sk-ant-...
uvicorn app:app --reload --port 8000
# Open http://localhost:8000
```

**What the UI does:**
- Streams responses from `claude-opus-4-6`
- Loads `ebra-call/references/system-prompt.md` as the system prompt
- Injects runtime call variables (customer name, amount, creditor, etc.)
- Quick-reply buttons to simulate F1–F7 debtor types + escalation scenarios
- Highlights `[PAUSE]` / `[SHORT PAUSE]` TTS markers visually
- Sidebar stage tracker (6-stage conversation machine)

---

## 3. The ebra-call skill — key concepts

### Conversation stages (stateful, never skip)
1. **Opening** — confirm identity, introduce purpose
2. **Listening & Classification** — classify debtor into F1–F8
3. **Response** — branch by classification type
4. **Resolution Attempt** — full payment / partial / promise-to-pay
5. **Close or Escalate** — always end with a clear next action
6. **JSON Output** — silent CRM block after every call

### Debtor types
| Code | Label | Signal |
|------|-------|--------|
| F1 | ناسي (Forgot) | "نسيت" |
| F2 | ضائقة مالية (Hardship) | "ما عندي فلوس" |
| F3 | منكر (Disputes) | "ما أعرف هذا الدين" |
| F4 | دفع (Already paid) | "دفعت" |
| F5 | متهرب (Avoidant) | vague delays |
| F6 | متعاون (Cooperative) | "أبي أسوي ترتيب" |
| F7 | عدواني (Hostile) | raised voice |
| F8 | شخص خاطئ (Wrong person) | "أنا مو هو" |

### Runtime variables (inject per call)
```
{{CUSTOMER_NAME}}, {{CREDITOR_NAME}}, {{AMOUNT}}, {{DUE_DATE}},
{{PRODUCT_TYPE}}, {{ATTEMPT_NUMBER}}, {{PAYMENT_LINK}}, {{CALL_ID}}
```

### SAMA hard stops (never do)
- Call outside 8am–9pm
- Threaten legal action (without written creditor auth)
- Contact third parties
- Call same number >3x/day
- Deny being AI

---

## 4. Git branch

All work is on: `claude/add-plugin-install-guide-4L2EC`

---

## What to do next in Cursor

Paste this file into Cursor chat as your first message, then continue from here. Suggested next steps:

- Hook up the FastAPI app to a real phone/voice pipeline (Twilio, ElevenLabs)
- Add WebSocket support to `app.py` for lower-latency streaming
- Extend the objection library with more scenarios
- Add a call history/logging page to the chat UI
- Write unit tests for the debtor classification logic
