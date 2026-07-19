# DocQuiz

Upload study notes (PDF) → get an AI-powered quiz that adapts to you.

Built in one hands-on session, in two parts:

1. **The engine** (plain Python): PDF text extraction, chunking notes into
   sections, and LLM question generation that spreads across those sections.
2. **The web app**: a FastAPI backend, an SQLite database, an adaptive
   engine that targets your weak topics, a browser frontend — then deployed
   to a public URL on Render.

## Prerequisites

- Python 3.10+
- Git
- A free Groq API key: https://console.groq.com
- A GitHub account (for the deployment step)

## Setup

```bash
git clone <repo-url>
cd docquiz
./setup.sh          # Windows: use Git Bash, run: bash setup.sh
```

This creates a virtual environment and installs dependencies (using `uv` if
you have it installed, otherwise standard `venv` + `pip`). It also checks
your Python is 3.10+ and tells you the exact install command for your OS if
it isn't.

**Windows without Git Bash?** Use the PowerShell backup instead:

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

**Both scripts fail?** Manual fallback — three commands:

```bash
python -m venv .venv                                # or python3
./.venv/bin/pip install -r requirements.txt         # Mac/Linux
.venv\Scripts\pip install -r requirements.txt       # Windows
cp .env.example .env                                # Windows: copy .env.example .env
```

Activate the environment:

```bash
source .venv/bin/activate        # Mac/Linux
source .venv/Scripts/activate    # Windows (Git Bash)
```

Open `.env` (created automatically from `.env.example`) and paste in your
Groq API key:

```
GROQ_API_KEY=your_actual_key
```

## Folder guide

- `starter/` — where you write code. Functions have a docstring and a
  numbered `# TODO` — fill in the body. TODO 1–3 are the engine,
  TODO 4–8 are the web app.
- `solution/` — a working reference. Try the TODO yourself first; only peek
  if you're stuck.
- `sample_notes/` — a sample PDF (`python_oop_basics.pdf`) to test against.

## Part 1 — run the engine (CLI)

Once `pdf_service.py` (TODO 1–2) and `llm_service.py` (TODO 3) are filled in:

```bash
python starter/main.py sample_notes/python_oop_basics.pdf
```

This should print 5 generated multiple-choice questions.

## Part 2 — run the web app

Once `db.py` (TODO 4–5), `app.py` (TODO 6–7) and `adaptive.py` (TODO 8) are
filled in:

```bash
cd starter
uvicorn app:app --reload
```

Open http://127.0.0.1:8000 — upload a PDF, take the quiz. The next question
adapts to how you're doing: weak topics come back, difficulty steps up and
down with your accuracy.

The database is `starter/docquiz.db` — one SQLite file. Delete it any time
for a clean slate; it's recreated on the next run.

## Part 3 — deploy to Render (free)

1. Push your code to your **own** GitHub repository:

   ```bash
   git remote rename origin upstream
   git remote add origin https://github.com/<your-username>/docquiz.git
   git add -A && git commit -m "My DocQuiz"
   git push -u origin main
   ```

2. On https://render.com (sign in with GitHub): **New → Web Service**, pick
   your `docquiz` repo. Render reads `render.yaml` automatically; if you
   configure manually instead, use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT --app-dir starter`
3. Add environment variable `GROQ_API_KEY` = your key (never commit it!).
4. Deploy. First build takes a few minutes; your app appears at
   `https://<name>.onrender.com`.

**Free-tier honesty:** the instance sleeps after inactivity (first request
takes ~1 min to wake), and the SQLite file lives on an ephemeral disk — it
resets on redeploy/restart. Real production would swap SQLite for a managed
Postgres; the code change is small, the lesson is the point.

## Troubleshooting

- **`groq.AuthenticationError` / 401** — check `GROQ_API_KEY` is set correctly in `.env`.
- **`ModuleNotFoundError: No module named 'pdfplumber'`** (or `fastapi`) — make sure
  your venv is activated (`source .venv/bin/activate`) before running Python. If
  `fastapi` alone is missing, re-run `./setup.sh` — requirements grew since your
  first install.
- **`json.decoder.JSONDecodeError` on the LLM response** — the model didn't return
  valid JSON; re-run, or check the prompt still asks for a JSON object.
- **`NotImplementedError`** — expected until you fill in the corresponding TODO.
- **`uvicorn: command not found`** — venv not activated, or dependencies not
  reinstalled after requirements grew: `./setup.sh`, then activate.
- **Web app returns 500 on `/quiz/next`** — usually TODO 8 (`adaptive.py`) not
  filled in yet, or no questions uploaded.
- **Upload says "No text found in PDF"** — scanned/image PDF with no text layer;
  use a text-native PDF (anything exported from Word/Docs).
- **Render build succeeds but app crashes** — check the `GROQ_API_KEY` env var is
  set in the Render dashboard (Environment tab), then "Manual Deploy → Restart".
- **Render app worked, then quiz vanished** — free-tier disk is ephemeral; the
  DB resets on restart. Upload again (or upgrade to Postgres — see above).
