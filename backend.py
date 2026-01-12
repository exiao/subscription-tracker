"""
Subscription Tracker - FastAPI + OpenRouter/Gemini Flash with Structured Outputs
"""

import os, uuid, pdfplumber
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openrouter import OpenRouter
from pydantic import BaseModel, Field

app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
sessions: dict = {}


# Pydantic models for structured LLM output
class SubscriptionItem(BaseModel):
    name: str = Field(description="Name of the subscription service (e.g. Netflix, Spotify)")
    amount: float = Field(description="Amount charged per billing cycle")
    frequency: str = Field(description="Billing frequency: monthly, yearly, or weekly")
    last_charged: str = Field(description="Date of most recent charge (YYYY-MM-DD)")
    count: int = Field(description="Number of times this subscription appears in the statement")
    cancel_url: str = Field(default="", description="URL to cancel the subscription")


class SubscriptionList(BaseModel):
    subscriptions: list[SubscriptionItem] = Field(description="List of ALL recurring subscriptions found")


# Internal model with computed fields
class Sub(BaseModel):
    id: str
    name: str
    amount: float
    frequency: str
    last_charged: str
    count: int
    category: str = "pending"
    monthly: float = 0.0
    yearly: float = 0.0
    cancel_url: str = ""


PROMPT = """Extract ALL recurring subscriptions from this bank statement.

Known services (with cancel URLs):
- Netflix (netflix.com/cancelplan), Spotify (spotify.com/account), YouTube Premium, Hulu, Disney+, HBO Max, Amazon Prime (amazon.com/prime/manage), Apple/iCloud (apple.com/account)
- ChatGPT Plus (chat.openai.com/settings), Claude Pro (claude.ai/settings), GitHub (github.com/settings/billing), Cursor, Midjourney
- Notion (notion.so/my-account), Dropbox, Adobe (account.adobe.com), Microsoft 365, 1Password, Google One
- X Premium, Discord Nitro (discord.com/settings/subscriptions), LinkedIn Premium
- NYTimes, WSJ, Substack, Planet Fitness, Equinox, Peloton, ClassPass

Include EVERY recurring subscription. Do not skip any.

Bank statement:
"""


def parse(content: bytes, filename: str) -> list[Sub] | str:
    """Returns list of subscriptions, or error string"""
    # Extract text
    if filename.lower().endswith('.pdf'):
        text = ""
        try:
            with pdfplumber.open(BytesIO(content)) as pdf:
                for p in pdf.pages:
                    if t := p.extract_text(): text += t + "\n"
        except: pass
    else:
        try: text = content.decode('utf-8')
        except: text = content.decode('latin-1')
    
    if not text.strip(): return "Could not read file contents"
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key: return "OPENROUTER_API_KEY not set. Run: export OPENROUTER_API_KEY='your-key'"
    
    try:
        with OpenRouter(api_key=api_key) as client:
            # Use structured outputs with Pydantic schema
            resp = client.chat.send(
                model="google/gemini-2.0-flash-001",
                messages=[{"role": "user", "content": PROMPT + text[:50000]}],
                temperature=0.1,
                max_tokens=8000,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "subscriptions",
                        "strict": True,
                        "schema": SubscriptionList.model_json_schema()
                    }
                }
            )
            
            # Parse with Pydantic validation
            result = resp.choices[0].message.content.strip()
            data = SubscriptionList.model_validate_json(result)
            
            subs = []
            for i, s in enumerate(data.subscriptions):
                freq = s.frequency.lower()
                monthly = s.amount if freq == "monthly" else s.amount/12 if freq == "yearly" else s.amount*4.33
                yearly = s.amount*12 if freq == "monthly" else s.amount if freq == "yearly" else s.amount*52
                subs.append(Sub(
                    id=f"s{i}", name=s.name, amount=s.amount, frequency=freq,
                    last_charged=s.last_charged, count=s.count,
                    monthly=round(monthly, 2), yearly=round(yearly, 2),
                    cancel_url=s.cancel_url
                ))
            return subs
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    sid = str(uuid.uuid4())
    sessions[sid] = []
    return templates.TemplateResponse("index.html", {"request": request, "sid": sid})


@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, files: list[UploadFile] = File(...), sid: str = Form(...)):
    subs = []
    for f in files:
        result = parse(await f.read(), f.filename)
        if isinstance(result, str):  # Error message
            return templates.TemplateResponse("index.html", {"request": request, "sid": sid, "error": result})
        subs.extend(result)
    if not subs:
        return templates.TemplateResponse("index.html", {"request": request, "sid": sid, "error": "No subscriptions found"})
    sessions[sid] = subs
    return templates.TemplateResponse("index.html", {
        "request": request, "sid": sid, "subs": subs,
        "total_monthly": round(sum(s.monthly for s in subs), 2),
        "total_yearly": round(sum(s.yearly for s in subs), 2)
    })



if __name__ == "__main__":
    import uvicorn
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  Set OPENROUTER_API_KEY first!")
    print("🚀 http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
