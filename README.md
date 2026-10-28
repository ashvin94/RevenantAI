# Revenant AI

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://dashboard.render.com/blueprint/new?repo=https%3A%2F%2Fgithub.com%2Fashvin94%2FRevenantAI)

The Blueprint deploys both `mirrorheal-api` and `mirrorheal-ui`. Render prompts for `GEMINI_API_KEY`; keep it in Render secrets and never commit it.

Revenant AI is a local-first hackathon MVP for detecting and safely repairing a simulated silent inventory-reservation failure.

## Current status

P0 is complete: real order workflow, controlled duplicate fault, trained IsolationForest suspicion signal, deterministic invariant proof, typed Gemini proposal, isolated digital-twin simulation, approved transactional recovery, idempotency, and post-commit verification.

## Prerequisites

- Python 3.11 or newer
- Node.js compatible with the Vite/Vitest version selected during frontend scaffolding
- npm
- Git
- SQLite through Python's standard `sqlite3` module

Versions verified on this workstation on 28 October 2026:

```text
Python 3.13.14
Node.js 24.14.1
npm 11.11.0
Git 2.52.0.windows.1
SQLite 3.50.4
```

These are observed development versions, not minimum dependency pins.

## Backend environment setup

Run from the repository root in PowerShell:

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install --upgrade pip
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
backend\.venv\Scripts\python.exe -m pip install --no-deps -e backend
Copy-Item backend\.env.example backend\.env
```

Edit `backend/.env` locally if provider access is needed. Never commit this file or paste its values into chat, logs, screenshots, issues, or API responses.

## AI provider smoke check

The smoke check uses the official `google-genai` SDK and makes one small structured-output request only when `GEMINI_API_KEY` is present.

```powershell
backend\.venv\Scripts\python.exe backend\scripts\ai_smoke.py
```

Expected outcomes:

- Exit `0`: the configured Gemini model returned a schema-valid response.
- Exit `2`: no API key is configured; provider is honestly unavailable.
- Exit `3`: a required local SDK is not installed.
- Exit `4`: authentication, quota, model availability, network, timeout, or response validation failed.

The script never prints the API key or raw request headers. Provider failure does not authorize a canned diagnosis.

## Configuration

`backend/.env.example` documents configuration with empty secret placeholders. Provider model IDs are configurable because availability changes over time. Confirm the selected model through the smoke check before claiming live AI.

## Planned validation commands

Backend and frontend commands become active in later phases:

```powershell
# Backend tests, after Phase 1+
cd backend
python -m pytest -q

# Frontend build, after frontend scaffolding
cd frontend
npm run build
```

## Safety rules

- LLM output is a bounded proposal, never executable SQL, Python, shell, or network instructions.
- ML anomaly scores are suspicions, not proof of corruption.
- Simulations use independent copied state and do not write business tables.
- Recovery requires deterministic evidence, a passing simulation, explicit approval, version checks, a transaction, idempotency, and fresh post-commit verification.
- Synthetic metrics are always labeled synthetic.

## Phase 0 limitations

- No provider credentials are bundled.
- A missing key produces an explicit unavailable result.
- No live Gemini result has been claimed unless the smoke command exits successfully.
- `backend/requirements.lock.txt` records the exact Phase 0 environment resolved on this workstation. `pyproject.toml` remains the source declaration and the lock should be deliberately regenerated after dependency updates.
