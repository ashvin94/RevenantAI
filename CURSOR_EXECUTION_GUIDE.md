# Cursor Execution Guide — Build MirrorHeal AI Fast, Without Losing Correctness

**Companion:** [MIRRORHEAL_MASTER_PLAN.md](./MIRRORHEAL_MASTER_PLAN.md)  
**Objective:** Make Cursor implement a **working** hybrid self-healing MVP during a six-hour sprint.  
**Method:** Small phase-specific prompts → run real tests → review diff → commit.

> **Critical:** Cursor is a coding assistant, not proof that code works. Ask it to run commands, inspect exit codes, and show actual test results. Never let an Agent invent sample metrics, pretend to call Gemini, silently simulate model responses, or implement repair buttons that only animate.

## 1. Prepare Cursor before the clock

1. Create an empty `mirrorheal` folder and copy `MIRRORHEAL_MASTER_PLAN.md`, `CURSOR_EXECUTION_GUIDE.md`, `AGENTS.md`, and `.cursor/rules/mirrorheal.mdc` inside it, preserving the relative paths.
2. Open the folder in Cursor using **File → Open Folder**.
3. Open **Agent** (`Ctrl+I` on Windows/Linux). Cursor's current docs list Agent for multi-file edits and terminal commands; Plan mode is useful for reviewing complex tasks, but don't let lengthy planning consume the clock.
4. Ensure Git and Python and Node are installed. Agree on the main data contracts before team members create files.
5. Put Gemini/Groq keys in `backend/.env` yourself. **Never give actual keys to Cursor chat.**
6. Use `.cursor/rules/mirrorheal.mdc` or root `AGENTS.md` as persistent project rules. Both supplied here; do not put ordinary `.md` inside `.cursor/rules` expecting it to be an auto-applied rule.
7. Make first commit containing only the docs, no secret material.

### One master instruction to paste into a *new* Cursor Agent chat

```text
You are the implementation engineer for MirrorHeal AI + PhantomGuard, a 6-hour hackathon MVP.
Read @MIRRORHEAL_MASTER_PLAN.md and @AGENTS.md carefully before editing code.
We need one truthful end-to-end working pipeline: synthetic order -> duplicate reservation silent failure -> deterministic rule detection + trained Isolation Forest signal -> real Gemini diagnosis (Groq backup) -> three independently executed state-copy simulations -> human approval -> idempotent atomic recovery -> post-commit DB verification -> React dashboard.

Obey priorities P0 > P1 > P2. Never generate arbitrary SQL or code from the LLM. Never fake model calls, database mutations, metrics, test output or recovery success. The model only proposes allowlisted repairs. Simulator and verifier are deterministic.

For THIS turn, first examine repository state and report an implementation checklist and the precise files you'll touch. Then implement only the phase I ask for, run relevant tests/build, and report commands/results. If a dependency/API is unavailable, fail visibly and give a narrower fallback; do not disguise it as working. Do not overwrite teammates' files. Work iteratively, not as one giant rewrite.
```

## 2. Recommended interaction loop (use every phase)

1. Paste the phase prompt below into Cursor Agent.
2. Agent reads the relevant sections and edits only named modules.
3. You approve only expected terminal commands and inspect changes.
4. Agent runs the exact validation gate (`pytest`/`npm run build`/API smoke test).
5. Save a Git commit for the phase after tests pass.
6. Start a fresh Agent chat for the next large stage, referencing relevant files. This helps avoid bloated context.
7. If the first attempt fails, provide actual traceback/output to Cursor and ask for a minimal fix; do not ask for a complete rewrite.

**Never paste the entire project into one enormous prompt and hope it works.**

---

## 3. Phase-by-phase prompts — copy directly into Cursor

### PHASE 0 (first 15 minutes) — Environment + API access

```text
Read @MIRRORHEAL_MASTER_PLAN.md sections 0, 3, 4, and 13 and @AGENTS.md.
Check Python, Node, npm, Git versions. Scaffold a Vite react-ts frontend and FastAPI backend compatible with current official docs; set up Tailwind's current Vite plugin, local CORS, /api/health, requirements.txt, .env.example, .gitignore, README start commands.
Do not install LangGraph, Celery, Temporal, Redis, Docker, vector databases or other non-MVP dependencies.
Create one small backend Gemini smoke-test script that checks presence of API key from environment and calls the configured model; never print the key. Add a clearly visible error on 401/403/429/model not found.
Do not create fake success responses.
Run frontend build and backend /api/health, report actual result and files changed.
```

**Gate:** `http://localhost:8000/api/health` returns health JSON; frontend builds; AI smoke test actually works or is clearly marked unavailable. If AI access fails, continue business logic while teammate fixes keys.

### PHASE 1 (hour 1) — Real workflow and database

```text
Implement backend normal e-commerce workflow only; see master plan sections 5, 6, 10.
Use FastAPI, SQLModel and SQLite. Add tables: orders, inventory, inventory_reservations, workflow_events, processed_events. A normal order quantity 1 should create exactly one active reservation and stored logical event, returning a working response.
Keep business transitions as pure functions where practical so the same transitions can run in a copied-state simulator. Store order.version for optimistic checks. Define Pydantic DTOs and typed errors.
Create POST /api/orders, GET /api/orders/{id}, and tests for correct reservation, insufficient stock, duplicate logical event deduplication and non-negative inventory.
Do not implement fake payments; label payment confirmation simulated.
Run pytest; show the test output and a real database query for a created order.
```

**Gate:** normal persisted order, zero incidents; unique processed logical event; no duplicate side effects.

### PHASE 2 (hour 2) — Controlled silent fault and deterministic detector

```text
Implement exactly one DEMO-ONLY faulty-event injection endpoint that deliberately bypasses ordinary idempotency for an existing order and creates a second active inventory reservation for the same logical event. Label this as simulated fault injection and gate it by ENABLE_FAULT_INJECTION.
Implement invariant checker checking active reservation quantity matches ordered quantity, no negative stock, duplicate active reservations by logical event, and shippability/fulfillment safety. Store incident record and evidence from actual SQLite rows. Add POST /api/orders/{id}/inject-duplicate, POST /api/orders/{id}/inspect and GET /api/incidents.
Demonstrate silent failure: API request completes but business invariant is violated.
Write tests: normal no incident; injected duplicate -> incident; repeated inspection does not make unlimited duplicate open incidents.
Run pytest and display DB before/after values.
```

**Gate:** actual two active reservations and an incident with correct evidence.

### PHASE 2B (parallel with phase 2) — Generate and train our ML model

```text
Read master plan section 7. Build backend/scripts/generate_dataset.py, train_model.py, eval_model.py and app/ml/features.py, inference.py.
Generate reproducible synthetic NORMAL business workflow telemetry using realistic correlated features. Split into disjoint normal training, validation and held-out testing, plus independent synthetic anomaly test samples. No label, fault_type, outcome, or post-recovery data may enter model features. Use IsolationForest, save trusted local model artifact and metadata including feature names/order, seed, training count, sklearn version and decision threshold. Show confusion matrix, precision/recall/F1 and false positive rate on held-out synthetic data; write actual metrics to a JSON file.
Expose model inference through the incident inspection flow without altering the invariant rules. ML-only anomalies trigger investigation, NEVER automatic repair. Make an explicit test scenario with normal inventory but excessive retries/latency.
Run train, eval, and pytest. Do not hardcode scores or claim real-world accuracy.
```

**Gate:** trained model artifact exists; real inference is called; honest synthetic held-out metrics saved; missing artifact gives clear status.

### PHASE 3 (hour 3) — Real LLM diagnosis and candidate plans

```text
Read master plan sections 4 and 8. Add Gemini provider adapter using google-genai, optional Groq adapter, and common Investigator interface. Model gets sanitized incident evidence and allowlisted actions, and returns Pydantic-validated structured Diagnosis with root_cause, explanation, evidence_ids and 1-3 repair plans (each plan is a list of typed actions).
Allowed action types: RETRY_ORDER, RECORD_EVENT_DEDUP, RELEASE_EXTRA_RESERVATION, ESCALATE. Validate every target refers to real evidence/DB records; strict max actions per plan. The LLM must never execute SQL, Python, shell, arbitrary HTTP calls or database writes. Add POST /api/incidents/{id}/diagnose.
Handle invalid JSON, unavailable provider, rate limit, timeout, unsupported action. Mark provider on every response. Show real provider integration; NO fabricated AI success. Add deterministic mock provider ONLY in tests, labeled there.
Test with a real Gemini API call if credentials configured; also use mocked tests for invalid and dangerous outputs.
```

**Gate:** real LLM returns typed candidates; failure doesn't change orders/reservations.

### PHASE 4 (hour 4) — Digital twin and independent simulation

```text
Read master plan sections 5.3 and 9. Implement WorkflowSnapshot, pure shared transition functions, simulate_plan() using deepcopy for each candidate and invariant verifier. Each simulation must start from identical original state and have ZERO SQLite business writes. Implement three strategies based on REAL transitions:
P1 RETRY_ORDER (no effective correction, reject),
P2 RECORD_EVENT_DEDUP only (existing excess remains, reject),
P3 RELEASE_EXTRA_RESERVATION of uniquely identified uncommitted duplicate + RECORD_EVENT_DEDUP (correct post-state, passes).
Require final active reservations==ordered quantity, nonnegative stock, no unauthorized/shipped release, dedup protection, no orphan records, and valid evidence references.
Return per-candidate before/after snapshot, individual invariant results, final pass/reject reason. Never pre-fill a candidate outcome.
Implement POST /api/incidents/{id}/simulate and tests: original SQLite rows unchanged; separate copies; unknown/unsafe actions rejected.
Run actual tests and show output.
```

**Gate:** two rejected, one passing **because of code and state**, not because of scripted display.

### PHASE 5 (hour 5) — Approval, atomic recovery and frontend integration

```text
Read master plan sections 6.1, 9.3, 10 and 11. Add server-enforced approval of an exact simulated plan, with incident ID, plan ID, snapshot version, explicit operator identity for demo and operation_key. Implement guarded recovery within one SQLite transaction; apply only previously validated plan after rechecking order.version, reservation status and evidence, then persist recovery and post-commit verification. Repeat recovery with same operation_key must be a no-op; stale version, missing approval, bad target or already-shipped reservation must not mutate state.
Implement POST /api/incidents/{id}/approve, POST /api/incidents/{id}/recover.
Frontend pages: Mission Control, AI Investigation, Simulation Lab. Connect actual APIs and show persisted state; use simple professional dark design first. Implement loading/error states, selected incident, three plan comparison cards, approval dialog and final DB readback. Only add React Flow after end-to-end tests pass.
Run backend tests, frontend build, manual UI fault-to-recovery walkthrough.
```

**Gate:** real DB repaired safely; UI reflects truth; replay no second mutation.

### PHASE 6 (hour 6) — Test, stabilize and pitch

```text
Do NOT add any new framework or major feature. Read master plan sections 15, 16 and 17. Run full backend pytest and frontend npm run build. Test the actual user journey: create order -> inject duplicate -> inspect (rules and trained ML) -> real provider diagnose -> three sandbox simulations -> approve correct plan -> recover -> verify actual DB rows -> repeat recovery no-op. Test AI unavailable and invalid action are non-mutating.
Fix ONLY blockers and critical UI readability. Add real README setup instructions, demo reset instructions and known limitations. Add a compact test report with command output summaries and explicit failed/skipped tests. Collect real (not made-up) evaluation/incident metrics. Commit working build and prepare backup screen recording. Do not misrepresent simulation as production integration.
```

**Gate:** ready for demo before buzzer, and working repo + clear `README.md`.

---

## 4. Windows PowerShell command reference

Run from project root unless specified:

```powershell
# Python backend (in a NEW terminal)
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# React frontend (in another terminal)
cd frontend
npm run dev

# Python tests
cd backend
python -m pytest -q

# Frontend type/build check
cd frontend
npm run build

# Git checkpoint
git status
git add .
git commit -m "MVP gate: implemented and verified phase"
```

Before `git add .`, verify `.env`, local DB, training data with sensitive information, and any secrets are gitignored. Keep demo synthetic dataset as generated scripts; committing tiny `evaluation.json` is fine if it comes from measured output.

## 5. API payload patterns to keep stable

**Normal order request:**
```json
{"sku":"LAPTOP-001","quantity":1,"logical_event_id":"EVT-101"}
```

**Incident diagnosis response (shape, not hardcoded values):**
```json
{
  "incident_id":"INC-101",
  "provider":"gemini",
  "diagnosis":{
    "root_cause":"DUPLICATE_EVENT_PROCESSING",
    "evidence_ids":["A1","A2","R1","R2"],
    "plans":[{"plan_id":"P3","actions":[
      {"type":"RELEASE_EXTRA_RESERVATION","target_id":"R2"},
      {"type":"RECORD_EVENT_DEDUP","target_id":"EVT-101"}
    ]}]
  }
}
```

**Simulation response (shape):**
```json
{
  "incident_id":"INC-101",
  "state_version":3,
  "simulations":[
    {"plan_id":"P1","passed":false,"reason":"Reservation mismatch remains"},
    {"plan_id":"P2","passed":false,"reason":"Existing extra reservation remains"},
    {"plan_id":"P3","passed":true,"reason":"All defined invariants pass"}
  ]
}
```

**Recovery request:**
```json
{"plan_id":"P3","operation_key":"RECOVER-INC-101-v3","approved_by":"demo-operator"}
```

The final implementation may use UUIDs rather than these illustrative IDs, but a **single stable DTO schema** must be shared between backend and frontend.

## 6. Common Cursor traps and best prompts to fix them

| Agent problem | What to tell Cursor |
|---|---|
| It claims success without running app | `Run pytest and npm run build; show actual exit codes; cite exact test failures.` |
| It hardcodes incident/repair results | `Remove hardcoded UI values; load results from API and persist state. Prove with DB readback.` |
| It puts Gemini key in frontend | `Remove the key and use only backend environment variables; inspect git diff for leaks.` |
| It creates 3 disconnected AI agents | `Use one provider call with typed diagnosis and pure deterministic verifier. Integrate first.` |
| It incorrectly treats ML score as probability | `Expose raw decision_function score and threshold; remove fake percent confidence.` |
| It edits everything at once | `Revert unrelated edits, touch only specified files, add targeted tests.` |
| It declares compensation safe from AI text | `Make verification independent of LLM. Require unique target evidence, plan simulation and server approval.` |
| It mishandles repeated recovery | `Add unique operation_key and a test asserting second recover causes zero inventory delta.` |
| It fabricates model training | `Generate data, fit IsolationForest, evaluate holdout, and persist actual metrics. Run script now.` |
| It builds nice UI but no backend | `Stop CSS changes, implement P0 fault->repair->DB proof; UI styling is secondary.` |

## 7. Recommended backup and takeover playbook

If Gemini is unavailable: try Groq if key/quota works. If neither works: **do not claim AI diagnosis**. Keep rule detection, actual ML scoring, digital twin and safe recovery working; show `AI provider unavailable` and allow a predeclared deterministic plan for demonstration, clearly labeled as a fallback. Record a genuine AI run ahead of time if possible; show timestamp and say it is recorded, not live.

If ML training integration fails: leave rule engine and repairs alive; retain training/evaluation scripts for judges, but explicitly state model isn't in live API path. Fix it only if the core workflow is stable.

If time is almost over: one safe recovery with evidence > six half-built scenarios. Stop adding dependencies, finish tests, and commit.

---

## 8. How to split Cursor across teammates

**Avoid two agents editing the same files concurrently.** Assign bounded ownership:
- UI owner: `frontend/src/**` only.
- Backend owner: `backend/app/models.py`, `db.py`, `routes/orders.py`, `core/*`.
- AI/ML owner: `backend/app/ai/*`, `backend/app/ml/*`, `backend/scripts/*`, `backend/data/*`.
- Recovery owner: `backend/app/healing/*`, `backend/app/routes/incidents.py`, `backend/tests/test_recovery.py`.

Shared contracts (`schemas.py`, frontend `types/contracts.ts`) are authored by one integrator and frozen early. If model schema changes, inform all teammates and run contract tests immediately.

## 9. Final Cursor audit prompt

```text
Perform an adversarial audit of this repository against @MIRRORHEAL_MASTER_PLAN.md acceptance tests T01–T18. Do not make up results. Run targeted tests, full pytest, and frontend production build. Identify any fake data, UI-only recovery, LLM direct mutation, unsafe sandbox writes, test-set leakage, missing idempotency protection, secrets in Git, or invalid model confidence displays. Fix only critical blockers, document any remaining limitations accurately, and provide exact command outputs and the end-to-end manual demo commands.
```

---

## 10. Current Cursor documentation

- Agent mode can edit files/run terminal: <https://cursor.com/docs/agent/overview>
- Using project rules and `AGENTS.md`: <https://cursor.com/docs/rules>
- Beginner first-project workflow: <https://prod.cursor.com/help/getting-started/first-project>

**Next action:** Start with Phase 0. Get a real `/api/health` and model smoke test; then complete one phase at a time.
