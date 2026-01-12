"""
Subscription Tracker - FastAPI + OpenRouter/Gemini Flash
"""

import os, json, uuid, pdfplumber
from io import BytesIO
from dataclasses import dataclass
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openrouter import OpenRouter

app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
sessions: dict = {}


@dataclass
class Sub:
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


PROMPT = """Extract subscriptions from this bank statement.

Known services (with cancel URLs):
- Netflix (netflix.com/cancelplan), Spotify (spotify.com/account), YouTube Premium, Hulu, Disney+, HBO Max, Amazon Prime, Apple TV+
- ChatGPT Plus (chat.openai.com/settings), Claude Pro (claude.ai/settings), GitHub Copilot (github.com/settings/copilot), Cursor, Midjourney
- Notion (notion.so/my-account), Dropbox, Adobe, Microsoft 365, 1Password, iCloud, Google One
- X Premium, Discord Nitro (discord.com/settings/subscriptions), LinkedIn Premium
- NYTimes, WSJ, Substack, Planet Fitness, Equinox, Peloton, ClassPass

Return ONLY this JSON:
{"subscriptions": [{"name": "Netflix", "amount": 15.99, "frequency": "monthly", "last_charged": "2024-01-15", "count": 3, "cancel_url": "netflix.com/cancelplan"}]}

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
            resp = client.chat.send(
                model="google/gemini-2.0-flash-001",
                messages=[{"role": "user", "content": PROMPT + text[:50000]}],
                temperature=0.1, max_tokens=8000
            )
            result = resp.choices[0].message.content.strip()
            
            # Clean JSON
            if "```" in result:
                result = result.replace("```json", "").replace("```", "").strip()
            start, end = result.find("{"), result.rfind("}") + 1
            if start >= 0 and end > start:
                result = result[start:end]
            
            data = json.loads(result)
            subs = []
            for i, s in enumerate(data.get("subscriptions", [])):
                amt = float(s.get("amount", 0))
                freq = s.get("frequency", "monthly").lower()
                monthly = amt if freq == "monthly" else amt/12 if freq == "yearly" else amt*4.33
                yearly = amt*12 if freq == "monthly" else amt if freq == "yearly" else amt*52
                subs.append(Sub(
                    id=f"s{i}", name=s.get("name", "?"), amount=amt, frequency=freq,
                    last_charged=s.get("last_charged", ""), count=int(s.get("count", 1)),
                    monthly=round(monthly, 2), yearly=round(yearly, 2),
                    cancel_url=s.get("cancel_url", "")
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


@app.post("/categorize/{sub_id}", response_class=HTMLResponse)
async def categorize(request: Request, sub_id: str, category: str = Form(...), sid: str = Form(...)):
    for s in sessions.get(sid, []):
        if s.id == sub_id:
            s.category = category
    subs = sessions.get(sid, [])
    return templates.TemplateResponse("index.html", {
        "request": request, "sid": sid, "subs": subs,
        "total_monthly": round(sum(s.monthly for s in subs), 2),
        "total_yearly": round(sum(s.yearly for s in subs), 2)
    })


@app.get("/report", response_class=HTMLResponse)
async def report(request: Request, sid: str):
    subs = sessions.get(sid, [])
    return templates.TemplateResponse("report.html", {
        "request": request,
        "keep": [s for s in subs if s.category == "keep"],
        "cancel": [s for s in subs if s.category == "cancel"],
        "investigate": [s for s in subs if s.category == "investigate"],
        "pending": [s for s in subs if s.category == "pending"],
        "savings": round(sum(s.yearly for s in subs if s.category == "cancel"), 2),
        "total_yearly": round(sum(s.yearly for s in subs), 2),
        "total": len(subs)
    })


if __name__ == "__main__":
    import uvicorn
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  Set OPENROUTER_API_KEY first!")
    print("🚀 http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
