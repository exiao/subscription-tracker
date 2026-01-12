# Subscription Tracker

Find and cancel forgotten subscriptions by analyzing bank statements.

![Demo](https://img.shields.io/badge/status-active-brightgreen)

## Prerequisites

### Required Accounts

| Service | Purpose | Signup |
|---------|---------|--------|
| **OpenRouter** | LLM API access (Gemini Flash) | [openrouter.ai/keys](https://openrouter.ai/keys) |

### Get Your API Key

1. Sign up at [openrouter.ai](https://openrouter.ai)
2. Go to [openrouter.ai/keys](https://openrouter.ai/keys)
3. Click "Create Key"
4. Copy the key and add to `.env.local`:

```bash
export OPENROUTER_API_KEY='sk-or-v1-...'
```

> **Cost:** ~$0.0005 per bank statement using Gemini Flash

## Quick Start

```bash
# Install uv (if needed): https://docs.astral.sh/uv/getting-started/installation/
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
- **Pydantic** — Structured LLM outputs
- **pdfplumber** — PDF extraction

## Files

```
subscription-tracker/
├── backend.py              # FastAPI + LLM parsing
├── templates/
│   ├── index.html          # Main page (Jinja2 + HTMX + Alpine)
│   └── report.html         # Audit report
├── sample_statement.csv    # Test data
├── requirements.txt
└── README.md
```

## Customization

### Change LLM

In `backend.py`:
```python
model="google/gemini-2.0-flash-001"  # change this
```

See [openrouter.ai/models](https://openrouter.ai/models) for available models.

### Add Services

Edit the `PROMPT` and `SubscriptionItem` model in `backend.py` to add more known services.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main page |
| POST | `/upload` | Parse bank statements |
| POST | `/categorize/{id}` | Set category |
| GET | `/report` | Audit report |

## License

MIT

