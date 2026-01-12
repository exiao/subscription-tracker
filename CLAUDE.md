# Subscription Tracker

Find and cancel forgotten subscriptions by analyzing bank statements.

**Inspired by:** [just-fucking-cancel](https://github.com/rohunvora/just-fucking-cancel)

## Files

```
subscription-tracker/
├── backend.py              # FastAPI + LLM parsing
├── templates/
│   ├── index.html          # Main page (Jinja2 + HTMX + Alpine)
│   └── report.html         # Audit report
├── sample_statement.csv    # Test data
├── requirements.txt
└── CLAUDE.md
```

## Run

```bash
# install uv - https://docs.astral.sh/uv/getting-started/installation/
uv venv
uv pip install -r requirements.txt
source .env.local
uv run backend.py
```

Open **http://localhost:8000**

## How It Works

1. **Upload** — Drop CSV/PDF bank statements
2. **Parse** — Gemini Flash extracts transactions + identifies subscriptions  
3. **Categorize** — Mark as Keep / Cancel / Investigate
4. **Report** — Generate audit with potential savings

## Tech Stack

- **FastAPI** — Backend
- **Jinja2** — Templates
- **HTMX** — Server-driven UI updates
- **Alpine.js** — Local state (privacy toggle)
- **OpenRouter** — LLM API (Gemini Flash)
- **pdfplumber** — PDF extraction

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main page |
| POST | `/upload` | Parse bank statements |
| POST | `/categorize/{id}` | Set category |
| GET | `/report` | Audit report |

## Customization

### Change LLM

In `backend.py`:
```python
model="google/gemini-2.0-flash-001"  # change this
```

### Add services

Edit `PROMPT` in `backend.py` to add more known services.

## Cost

~$0.0005 per bank statement (Gemini Flash).
