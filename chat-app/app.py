"""
Ebra Voice Presence — Chat Test App
FastAPI backend that loads the ebra-call skill system prompt
and lets you chat with the AI agent to test it.
"""

import json
import os
import re
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
