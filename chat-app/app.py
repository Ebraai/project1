"""
Ebra Voice Presence — Chat Test App
FastAPI backend that loads the ebra-call skill system prompt
and lets you chat with the AI agent to test it.
"""

import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv(Path(__file__).parent / ".env")
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ─── Paths ────────────────────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).parent.parent / "ebra-call"
SYSTEM_PROMPT_PATH = SKILL_DIR / "references" / "system-prompt.md"
STATIC_DIR = Path(__file__).parent / "static"
UPDATES_FILE = Path(__file__).parent / "pending_updates.json"
LIVE_SKILL_DIR = Path("/root/.claude/skills/ebra-call")

SKILL_FILE_MAP = {
    "SKILL.md": SKILL_DIR / "SKILL.md",
    "references/system-prompt.md": SKILL_DIR / "references" / "system-prompt.md",
    "references/compliance-rules.md": SKILL_DIR / "references" / "compliance-rules.md",
    "references/objection-library.md": SKILL_DIR / "references" / "objection-library.md",
}

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(title="Ebra Voice Presence — Test Chat")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ─── Models ───────────────────────────────────────────────────────────────────

class CallConfig(BaseModel):
    customer_name: str = "أحمد العتيبي"
    creditor_name: str = "بنك الرياض"
    amount: str = "٣٥٠٠"
    due_date: str = "٢٠٢٤/١٢/٠١"
    product_type: str = "بطاقة ائتمانية"
    attempt_number: str = "٢"
    payment_link: str = "https://pay.example.com/abc123"
    call_id: str = "CALL-TEST-001"


class ChatRequest(BaseModel):
    message: str
    history: list[dict]
    config: CallConfig


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_system_prompt(config: CallConfig) -> str:
    """Load system prompt and inject runtime variables."""
    if not SYSTEM_PROMPT_PATH.exists():
        raise FileNotFoundError(f"System prompt not found at {SYSTEM_PROMPT_PATH}")

    raw = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    # Strip the markdown file header (everything before the first --- separator
    # that marks the actual prompt block)
    # Find the second "---" separator which starts the deployable block
    parts = raw.split("---")
    # The deployable prompt is after the heading block
    # parts[0] = header comment, parts[1] = first section, parts[2] = actual prompt...
    # We want everything from "SYSTEM PROMPT (deploy this block)" section
    deploy_marker = "## SYSTEM PROMPT (deploy this block)"
    if deploy_marker in raw:
        prompt_section = raw[raw.index(deploy_marker) + len(deploy_marker):]
        # Remove the closing --- at the end of that block
        if "---" in prompt_section:
            prompt_section = prompt_section[:prompt_section.rindex("---")]
        system_prompt = prompt_section.strip()
    else:
        system_prompt = raw

    # Inject runtime variables
    replacements = {
        "{{CUSTOMER_NAME}}": config.customer_name,
        "{{CREDITOR_NAME}}": config.creditor_name,
        "{{AMOUNT}}": config.amount,
        "{{DUE_DATE}}": config.due_date,
        "{{PRODUCT_TYPE}}": config.product_type,
        "{{ATTEMPT_NUMBER}}": config.attempt_number,
        "{{PAYMENT_LINK}}": config.payment_link,
        "{{CALL_ID}}": config.call_id,
    }
    for placeholder, value in replacements.items():
        system_prompt = system_prompt.replace(placeholder, value)

    return system_prompt


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


@app.get("/api/skill-info")
async def skill_info():
    """Return skill metadata for the UI."""
    return {
        "skill_path": str(SKILL_DIR),
        "system_prompt_exists": SYSTEM_PROMPT_PATH.exists(),
        "model": "claude-opus-4-6",
    }


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """Stream a response from the ebra-call agent."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY environment variable not set."
        )

    try:
        system_prompt = load_system_prompt(req.config)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Build message history
    messages = []
    for turn in req.history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": req.message})

    client = anthropic.Anthropic(api_key=api_key)

    async def generate() -> AsyncGenerator[str, None]:
        try:
            with client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=2048,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    # Send as SSE
                    yield f"data: {json.dumps({'type': 'text', 'text': text})}\n\n"

                final = stream.get_final_message()
                # Send the stop reason
                yield f"data: {json.dumps({'type': 'done', 'stop_reason': final.stop_reason})}\n\n"

        except anthropic.AuthenticationError:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Invalid API key.'})}\n\n"
        except anthropic.APIError as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ─── Update store helpers ─────────────────────────────────────────────────────

def load_updates() -> list:
    if UPDATES_FILE.exists():
        return json.loads(UPDATES_FILE.read_text(encoding="utf-8"))
    return []


def save_updates(updates: list):
    UPDATES_FILE.write_text(json.dumps(updates, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_skill_change(file_key: str, old_text: str, new_text: str) -> bool:
    """Replace old_text with new_text in skill file. Syncs to live skill dir."""
    path = SKILL_FILE_MAP.get(file_key)
    if not path or not path.exists():
        return False
    content = path.read_text(encoding="utf-8")
    if old_text not in content:
        return False
    updated = content.replace(old_text, new_text, 1)
    path.write_text(updated, encoding="utf-8")
    live_path = LIVE_SKILL_DIR / file_key
    if live_path.parent.exists():
        live_path.write_text(updated, encoding="utf-8")
    return True


# ─── Analysis models ──────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    transcript: list[dict]
    call_json: dict | None = None
    config: CallConfig


# ─── Analysis & update routes ─────────────────────────────────────────────────

@app.post("/api/analyze-call")
async def analyze_call(req: AnalyzeRequest):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set")

    skill_context = {
        k: p.read_text(encoding="utf-8")
        for k, p in SKILL_FILE_MAP.items()
        if p.exists()
    }

    transcript_lines = []
    for turn in req.transcript:
        label = "VP (الوكيل)" if turn["role"] == "assistant" else "العميل"
        transcript_lines.append(f"**{label}:** {turn['content']}")
    transcript_text = "\n\n".join(transcript_lines)

    analyzer_user = f"""## المحادثة:
{transcript_text}

## JSON المكالمة:
{json.dumps(req.call_json, ensure_ascii=False, indent=2) if req.call_json else "غير متوفر"}

## ملفات الـ Skill الحالية:
{json.dumps(skill_context, ensure_ascii=False)}

## المطلوب:
حلل المحادثة وأعد JSON فقط بهذا التنسيق بالضبط (بدون أي نص خارجه):
{{
  "summary": "ملخص الأداء في جملة أو جملتين",
  "score": <رقم من 1 إلى 10>,
  "issues": ["مشكلة محددة لاحظتها"],
  "proposals": [
    {{
      "id": "p1",
      "file": "references/system-prompt.md",
      "description": "وصف قصير للتغيير",
      "old_text": "النص الحالي بالضبط كما هو في الملف",
      "new_text": "النص المقترح",
      "reason": "لماذا هذا التغيير يحسن الأداء"
    }}
  ]
}}

قواعد مهمة:
- old_text يجب أن يكون موجوداً بالضبط في الملف المذكور
- لا تقترح تغييرات إذا لم تكن هناك مشاكل حقيقية
- ركز على مشاكل ظهرت في هذه المحادثة تحديداً"""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="أنت محلل متخصص في تحسين وكلاء الذكاء الاصطناعي لتحصيل الديون. أعد JSON فقط بدون أي نص خارجه.",
        messages=[{"role": "user", "content": analyzer_user}],
    )

    raw = response.content[0].text.strip()
    if "```json" in raw:
        raw = raw[raw.index("```json") + 7:]
        raw = raw[:raw.rindex("```")]
    elif raw.startswith("```"):
        raw = raw[3:raw.rindex("```")]

    try:
        analysis = json.loads(raw.strip())
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Parse error: {e}. Raw: {raw[:300]}")

    for i, p in enumerate(analysis.get("proposals", [])):
        p["id"] = p.get("id", f"p{i+1}")
        p["status"] = "pending"

    update = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "call_id": req.config.call_id,
        "overall_status": "pending",
        "summary": analysis.get("summary", ""),
        "score": analysis.get("score", 0),
        "issues": analysis.get("issues", []),
        "proposals": analysis.get("proposals", []),
    }

    updates = load_updates()
    updates.append(update)
    save_updates(updates)
    return update


@app.get("/api/updates")
async def get_updates():
    return load_updates()


@app.post("/api/updates/{update_id}/proposals/{proposal_id}/approve")
async def approve_proposal(update_id: str, proposal_id: str):
    updates = load_updates()
    update = next((u for u in updates if u["id"] == update_id), None)
    if not update:
        raise HTTPException(status_code=404, detail="Update not found")
    proposal = next((p for p in update["proposals"] if p["id"] == proposal_id), None)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    success = apply_skill_change(proposal["file"], proposal["old_text"], proposal["new_text"])
    proposal["status"] = "approved" if success else "failed"
    if not success:
        proposal["error"] = "old_text not found in file — may have already been applied"
    save_updates(updates)
    return {"status": proposal["status"]}


@app.post("/api/updates/{update_id}/proposals/{proposal_id}/reject")
async def reject_proposal(update_id: str, proposal_id: str):
    updates = load_updates()
    update = next((u for u in updates if u["id"] == update_id), None)
    if not update:
        raise HTTPException(status_code=404, detail="Update not found")
    proposal = next((p for p in update["proposals"] if p["id"] == proposal_id), None)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    proposal["status"] = "rejected"
    save_updates(updates)
    return {"status": "rejected"}


@app.get("/api/system-prompt-preview")
async def system_prompt_preview(
    customer_name: str = "أحمد العتيبي",
    creditor_name: str = "بنك الرياض",
    amount: str = "٣٥٠٠",
    due_date: str = "٢٠٢٤/١٢/٠١",
    product_type: str = "بطاقة ائتمانية",
    attempt_number: str = "٢",
    payment_link: str = "https://pay.example.com/abc123",
    call_id: str = "CALL-TEST-001",
):
    """Preview the rendered system prompt with injected variables."""
    config = CallConfig(
        customer_name=customer_name,
        creditor_name=creditor_name,
        amount=amount,
        due_date=due_date,
        product_type=product_type,
        attempt_number=attempt_number,
        payment_link=payment_link,
        call_id=call_id,
    )
    try:
        prompt = load_system_prompt(config)
        return {"system_prompt": prompt, "length": len(prompt)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
