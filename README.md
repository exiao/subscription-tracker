# 💸 Subscription Tracker

**Find and cancel those forgotten subscriptions eating your money!**

This app analyzes your bank statements using AI to find recurring charges you might have forgotten about. It's also a great first coding project to learn how modern web apps work.

---

## 🎯 What You'll Learn

By setting up this project, you'll get hands-on experience with:

| Concept | What It Means |
|---------|---------------|
| **Terminal** | The text-based way to talk to your computer (like texting instead of calling) |
| **API** | How apps talk to each other over the internet |
| **API Key** | Your personal password to use someone else's service |
| **Backend** | The "brain" of the app that runs on a server |
| **Frontend** | What users see and interact with in their browser |
| **LLM** | Large Language Model — AI like ChatGPT that understands text |

---

## 🚀 Getting Started (Step-by-Step)

### Step 1: Open Your Terminal

The terminal is a text-based way to control your computer. Don't worry — you'll just be copying and pasting!

**How to open it:**
- **Mac:** Press `Cmd + Space`, type "Terminal", hit Enter
- **Windows:** Press `Win + R`, type "cmd", hit Enter

You'll see a blank window with a blinking cursor. This is where you'll type commands.

---

### Step 2: Navigate to This Project

When you download this project, you need to tell your terminal where it is.

```bash
cd ~/Downloads/subscription-tracker
```

> 💡 **What's happening?** `cd` means "change directory" — you're telling your computer to look inside that folder.

---

### Step 3: Install the Package Manager

We need a tool called **uv** to install the app's dependencies (the code libraries it needs to work).

**Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (in PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

> 💡 **What's happening?** This downloads and installs `uv`, a fast tool for managing Python projects. Think of it like an app store for code libraries.

**Close and reopen your terminal** after installing so it recognizes the new tool.

---

### Step 4: Set Up the Project Environment

Navigate back to the project folder and run:

```bash
cd ~/Downloads/subscription-tracker
uv venv
uv pip install -r requirements.txt
```

> 💡 **What's happening?**
> - `uv venv` creates an isolated space for this project (so it doesn't mess with other things on your computer)
> - `uv pip install` downloads all the code libraries this app needs

---

### Step 5: Get Your AI API Key

This app uses an AI service called **OpenRouter** to analyze your bank statements. You'll need an API key (like a password) to use it.

1. Go to [openrouter.ai](https://openrouter.ai) and sign up (free)
2. Visit [openrouter.ai/keys](https://openrouter.ai/keys)
3. Click **"Create Key"**
4. Copy the key (it starts with `sk-or-v1-...`)

Now create a file to store your key. In your terminal:

```bash
echo "export OPENROUTER_API_KEY='paste-your-key-here'" > .env.local
```

Replace `paste-your-key-here` with your actual key.

> 💡 **Why a separate file?** API keys are like passwords — you don't want to accidentally share them. This file stays private on your computer.

> 💰 **Cost:** About $0.0005 per bank statement analyzed (that's 2,000 statements for $1)

---

### Step 6: Run the App!

```bash
source .env.local
uv run backend.py
```

> 💡 **What's happening?**
> - `source .env.local` loads your API key into memory
> - `uv run backend.py` starts the app

You should see something like:
```
INFO:     Uvicorn running on http://localhost:8000
```

---

### Step 7: Open the App in Your Browser

Go to: **[http://localhost:8000](http://localhost:8000)**

🎉 **You did it!** The app is running on your own computer.

> 💡 **What's localhost?** It means "this computer." Instead of visiting a website on the internet, you're visiting a website running locally on your machine.

---

## 📱 How to Use the App

1. **Upload** — Drag and drop a CSV or PDF bank statement (try `sample_statement.csv` included in the project!)
2. **Review** — The AI identifies recurring subscriptions
3. **Categorize** — Mark each as Keep / Cancel / Investigate
4. **Report** — See your potential savings

---

## 🔧 Troubleshooting

### "command not found: uv"
Close your terminal and reopen it. If still broken, reinstall uv (Step 3).

### "OPENROUTER_API_KEY not set"
Make sure you ran `source .env.local` before starting the app.

### "Address already in use"
Another app is using port 8000. Either close that app, or the app will try port 8001 automatically.

### The page won't load
Make sure the terminal still shows the app running. If you closed it, run Step 6 again.

---

## 📁 Project Files Explained

```
subscription-tracker/
├── backend.py              ← The main app logic (Python)
├── templates/
│   └── index.html          ← What you see in the browser (HTML)
├── sample_statement.csv    ← Test data to try the app
├── requirements.txt        ← List of code libraries needed
├── .env.local              ← Your secret API key (you create this)
└── README.md               ← This file!
```

---

## 🧠 How the Tech Works (Optional Reading)

Curious how the pieces fit together? Here's the flow:

```
[You upload a file]
        ↓
[Backend.py receives it]
        ↓
[Sends to OpenRouter AI]
        ↓
[AI analyzes transactions]
        ↓
[Backend formats results]
        ↓
[Browser displays them]
```

**The tech stack:**
- **Python** — The programming language
- **FastAPI** — A framework for building web backends
- **Jinja2** — Turns data into HTML pages
- **HTMX** — Makes the page update without full reloads
- **OpenRouter** — Connects to AI models like Gemini

---

## 🎓 Next Steps for Learning

Now that you've run your first app, here are some things to try:

1. **Read the code** — Open `backend.py` and try to follow along
2. **Change something** — Edit the text in `templates/index.html` and refresh
3. **Break it** — See what error messages look like (then undo!)
4. **Google errors** — Learning to search for solutions is a key skill

---

## 💬 Questions?

If you get stuck, try:
1. Googling the exact error message
2. Asking ChatGPT or Claude to explain what went wrong
3. Asking a developer friend to pair with you

Remember: Every developer was a beginner once. Getting stuck is part of learning! 🌱

---

## License

MIT — Use this however you like!
