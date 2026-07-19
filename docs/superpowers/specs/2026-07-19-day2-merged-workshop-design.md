# Day 2 Merged Workshop — Design

Date: 2026-07-19. Approved by instructor (Hemang).

## Context

Day 1 ran as theory-only (Python fundamentals, AI fundamentals,
architecture — no laptops). Day 2 (3:00–6:30 PM, extended 30 min for
deployment) must therefore cover: environment setup, the full engine build,
a web app with student-typed TODOs across the stack, the adaptive engine,
and a live deploy. Everything lives on `main` — no separate branches.

## Deliverables

1. **Web app files** in both `solution/` (complete) and `starter/` (TODOs):
   - `db.py` — stdlib sqlite3. Schema + `init_db` + reads given;
     `save_questions` (TODO 4) and `record_answer` (TODO 5) typed.
   - `app.py` — FastAPI. App setup, static serving, `GET /quiz/next`,
     `GET /progress` given; `POST /upload` (TODO 6) and `POST /answer`
     (TODO 7) typed.
   - `adaptive.py` — `pick_next_question` (TODO 8) typed: per-topic
     accuracy → weakest topic → difficulty stepping.
   - `static/index.html` — full vanilla-JS frontend, given, never typed.
2. **Engine TODOs unchanged** (TODO 1–3: extract, chunk, generate).
3. **`requirements.txt`** — add fastapi, uvicorn, python-multipart (pinned
   ranges, consistent with existing style).
4. **`render.yaml`** — Render Blueprint config; manual-path instructions in
   README and script as primary, Blueprint as shortcut.
5. **`README.md`** — updated: one-day flow, web app run command
   (`uvicorn app:app --reload` from `starter/`), deploy steps,
   web-app troubleshooting.
6. **`instructor/day2-script.md`** — full teleprompter in day1-script
   style: run sheet, Say-blocks, 5 checkpoints, live-debug ladders,
   anticipated questions, troubleshooting appendix. Theory blocks from
   Day 1 compressed into a 10-min recap + inline callbacks ("remember
   context windows — this line is that"). Deploy block covers GitHub
   push (rename origin → upstream, add own repo), Render web service,
   `GROQ_API_KEY` env var, ephemeral-disk caveat.
7. **`instructor/day1-script.md`** — superseded note at top pointing to
   day2 script.

## Timeline (3:00–6:30)

| Block | Content |
|---|---|
| 3:00–3:20 | Setup: clone, setup.sh, venv, key. Checkpoint 1 |
| 3:20–3:30 | Recap: architecture redrawn, theory→file map |
| 3:30–4:00 | extract + chunk (TODO 1–2). Checkpoint 2 |
| 4:00–4:25 | generate_questions (TODO 3), CLI runs. Checkpoint 3 |
| 4:25–5:15 | db.py + upload + answer endpoints (TODO 4–7) |
| 5:15–5:35 | adaptive.py (TODO 8), full app local. Checkpoint 4 |
| 5:35–6:15 | Deploy: GitHub push, Render, env var, live URL. Checkpoint 5 |
| 6:15–6:30 | Close, extensions, buffer |

## Data model

`questions(id, question, options_json, correct_answer, explanation,
difficulty, topic)`; `answers(id, question_id, selected, is_correct,
answered_at)`. Options stored as JSON text (reinforces Day-1 JSON lesson).
Upload wipes both tables — one active quiz at a time.

## Adaptive rule (teachable, ~20 lines)

Unanswered questions only. Per-topic accuracy from answers; unknown topic
counts 0.5. Target = topic of the unanswered question with lowest accuracy.
Desired difficulty: acc < 0.5 → easy, < 0.8 → medium, else hard; fall back
through easy→medium→hard if no exact match.

## Deploy

Render free tier (no card). Students: create own empty GitHub repo,
`git remote rename origin upstream && git remote add origin <theirs> &&
git push -u origin main`. Render manual web service: build
`pip install -r requirements.txt`, start
`uvicorn app:app --host 0.0.0.0 --port $PORT --app-dir starter`,
env vars `GROQ_API_KEY` + `PYTHON_VERSION`. SQLite on free tier is
ephemeral — stated honestly in script as the Postgres-migration teaching
moment. Fallback: student swaps `--app-dir solution` if their starter
is broken.

## Testing (no real Groq key available in this environment)

Engine import + chunk tests on sample PDF. Web app: seed DB directly with
fixture questions, run uvicorn, curl the full quiz loop
(next → answer → progress → adaptivity), verify frontend serves.
LLM call path verified by code review + identical structure to existing
tested solution.
