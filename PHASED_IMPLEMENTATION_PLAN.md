# MirrorHeal AI — Researched Phased Implementation and Test Plan

**Document purpose:** Turn `MIRRORHEAL_MASTER_PLAN.md` into an implementation-ready sequence with file ownership, contracts, tests, exit gates, and failure fallbacks.

**Plan date:** 28 October 2026  
**Target:** A truthful, local-first, six-hour hackathon MVP  
**Priority:** P0 correctness and evidence first; P1 only after every P0 gate passes; P2 excluded  
**Current repository state:** Planning documents only; implementation has not started

---

## 1. Outcome and non-negotiable demo

The MVP is complete only when this real path works:

1. A synthetic order for one laptop is persisted in SQLite.
2. Normal processing creates exactly one active reservation and one processed logical event.
3. A demo-only endpoint deliberately creates a second reservation for the same logical event while returning a successful HTTP response.
4. Deterministic invariants prove that reserved quantity is 2 while ordered quantity is 1.
5. A locally trained Isolation Forest scores current telemetry; its score is shown as suspicion, never as proof or confidence.
6. Gemini, with optional Groq fallback, returns a schema-valid diagnosis and allowlisted candidate plans, or the system visibly reports AI unavailable.
7. Every candidate is executed on its own deep copy of the same immutable starting snapshot.
8. The simulator rejects retry-only and dedup-only plans and passes the uniquely targeted release-plus-dedup plan only because its calculated post-state satisfies all checks.
9. A human approves the exact passing plan and state version.
10. The server rechecks evidence and version, applies one atomic transaction, and records an idempotency key.
11. Fresh post-commit queries prove that one active reservation remains and stock is consistent.
12. Repeating the same recovery request causes no second mutation.
13. The React UI displays the persisted facts and actual API results throughout the journey.

Anything that substitutes animations, static JSON, hardcoded scores, invented metrics, or a model's opinion for these state changes is incomplete.

---

## 2. Researched decisions that affect implementation

These decisions refine the existing master plan using current official documentation.

### 2.1 LLM integration

- Use `google-genai` through a backend-only adapter. Gemini structured output accepts JSON Schema/Pydantic-compatible schemas, but some schema constraints are ignored by constrained decoding. Therefore Pydantic validation and local semantic validation remain mandatory.
- Keep `GEMINI_MODEL` configurable. At plan time, Google's model catalog lists `gemini-3.5-flash-lite` as a stable, cost-efficient choice and recommends exact stable model names for predictable behavior. The Phase 0 smoke test must call the configured model rather than assuming availability.
- Groq strict structured output supports only selected models and requires all fields to be required with `additionalProperties: false`. At plan time, `openai/gpt-oss-20b` is listed as a strict-mode option. The adapter must still perform the same local validation.
- Do not use LLM tools, function execution, arbitrary URLs, SQL, or generated code. The only output is a bounded `Diagnosis` value.
- One explicit user action causes at most one provider call per evidence hash. Use a 15-second timeout, at most one safe retry for transient failure, and a cache keyed by the sanitized evidence hash.

### 2.2 SQLite and transaction safety

- Enable SQLite foreign-key enforcement for every connection; declaring foreign keys alone is not enough.
- Use an explicit SQLAlchemy/SQLModel transaction boundary for recovery. Current Python SQLite drivers retain legacy transaction behavior, so the executor must not depend on an implicit transaction beginning at the desired point.
- Keep transactions short and perform no network call inside a transaction.
- Use database uniqueness for `processed_events.logical_event_id` and `recovery_attempts.operation_key` as the last line of defense against replay.
- Use optimistic order versions. Approval binds `incident_id + plan_id + plan_hash + order_version`; any mismatch blocks recovery with `409` and no mutation.
- Run post-commit verification using a new session so verification cannot accidentally read only an identity-map value.

### 2.3 Isolation Forest and artifact safety

- Train only on synthetic normal samples. Tune the operational threshold on validation data and evaluate once on disjoint held-out data.
- Preserve raw `decision_function` output. In scikit-learn, contamination affects the outlier threshold; it is not a probability of corruption.
- Load only an artifact produced by the repository's trusted training script. Joblib is pickle-based and can execute code while loading.
- Save `sha256`, feature order, generator seeds, estimator settings, Python version, scikit-learn version, row counts, and evaluation results alongside the artifact.
- Refuse inference if the artifact hash, feature order, or library compatibility metadata is invalid. Deterministic inspection must continue with `ML_UNAVAILABLE`.

### 2.4 Testing strategy

- Backend API tests use pytest and FastAPI `TestClient`, backed by a fresh temporary SQLite database per test.
- Provider dependencies are replaceable through FastAPI dependency overrides. Unit/integration tests never spend API quota; a separately marked smoke test exercises a real configured provider.
- Frontend unit/component tests use Vitest plus Testing Library. End-to-end tests use Playwright and assert user-visible behavior.
- The production build remains a mandatory gate even when UI tests pass.
- Tests assert both expected changes and absence of forbidden changes.

### 2.5 Version policy

- Verify Python, Node, npm, Git, and SQLite versions before scaffolding.
- Record top-level dependencies with compatible bounds during development and generate a reproducible lock file after the first green install.
- Do not hardcode claims about provider free tiers or quotas. Check the actual account/model endpoint before the event.

---

## 3. Scope and priority rules

### P0 — must ship

- Health/configuration reporting without secrets.
- Normal order and inventory workflow.
- Controlled duplicate-reservation injection.
- Deterministic invariant inspection and incident persistence.
- Real Isolation Forest training, evaluation, persistence, and runtime inference.
- Real structured LLM adapter with an honest unavailable state.
- Three independently calculated repair simulations.
- Exact-plan approval, atomic recovery, idempotency, and fresh verification.
- React dashboard for the complete path.
- Automated backend, frontend, security, and end-to-end tests.

### P1 — only after P0 is green

- Separate ML-only slow/retry anomaly story.
- React Flow dependency view.
- Database-derived metrics and event replay.
- Multi-browser Playwright run.

### P2 — explicitly excluded

- Real commerce/payment integrations.
- Kubernetes, Redis, Celery, Temporal, LangGraph, distributed tracing, or microservices.
- Authentication, multitenancy, vector databases, online learning, or arbitrary agent tools.
- Multiple failure families or production claims.

---

## 4. Target repository layout

Create files only in the phase that needs them.

```text
.
├── AGENTS.md
├── MIRRORHEAL_MASTER_PLAN.md
├── CURSOR_EXECUTION_GUIDE.md
├── PHASED_IMPLEMENTATION_PLAN.md
├── README.md
├── .gitignore
├── backend/
│   ├── .env.example
│   ├── pyproject.toml
│   ├── requirements.lock.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── dependencies.py
│   │   ├── core/
│   │   │   ├── workflow.py
│   │   │   ├── invariants.py
│   │   │   └── evidence.py
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── orders.py
│   │   │   ├── incidents.py
│   │   │   └── ml.py
│   │   ├── ai/
│   │   │   ├── protocol.py
│   │   │   ├── validation.py
│   │   │   ├── gemini.py
│   │   │   └── groq.py
│   │   ├── ml/
│   │   │   ├── features.py
│   │   │   └── inference.py
│   │   └── healing/
│   │       ├── actions.py
│   │       ├── snapshot.py
│   │       ├── simulator.py
│   │       ├── verifier.py
│   │       └── executor.py
│   ├── scripts/
│   │   ├── ai_smoke.py
│   │   ├── generate_dataset.py
│   │   ├── train_model.py
│   │   ├── evaluate_model.py
│   │   └── demo_reset.py
│   ├── artifacts/
│   ├── data/
│   └── tests/
│       ├── conftest.py
│       ├── test_health.py
│       ├── test_workflow.py
│       ├── test_detector.py
│       ├── test_ml.py
│       ├── test_ai.py
│       ├── test_twin.py
│       ├── test_recovery.py
│       ├── test_contracts.py
│       └── test_security.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── playwright.config.ts
    ├── src/
    │   ├── App.tsx
    │   ├── pages/
    │   │   ├── MissionControl.tsx
    │   │   ├── Investigation.tsx
    │   │   └── SimulationLab.tsx
    │   ├── components/
    │   ├── lib/api.ts
    │   └── types/contracts.ts
    ├── tests/
    └── e2e/full-recovery.spec.ts
```

---

## 5. Frozen P0 contracts

Contracts are authored once in `backend/app/schemas.py`, mirrored in `frontend/src/types/contracts.ts`, and protected by contract tests.

### 5.1 Action allowlist

```text
RETRY_ORDER
RECORD_EVENT_DEDUP
RELEASE_EXTRA_RESERVATION
ESCALATE
```

No generic command/action field is allowed. Every action has a typed target and the server resolves it against persisted evidence.

### 5.2 Core statuses

```text
Order: CREATED | PAYMENT_VERIFIED | INVENTORY_RESERVED | SHIPPING_REQUESTED | COMPLETE
Reservation: ACTIVE | RELEASED | COMMITTED
Incident: OPEN | DIAGNOSED | SIMULATED | APPROVAL_PENDING | RECOVERED | ESCALATED
Recovery: APPLIED | VERIFIED | REPLAY_NOOP | BLOCKED | VERIFICATION_FAILED
Provider: GEMINI | GROQ | UNAVAILABLE
ML: AVAILABLE | UNAVAILABLE
```

### 5.3 Stable request shapes

```json
POST /api/orders
{"sku":"LAPTOP-001","quantity":1,"logical_event_id":"EVT-101"}
```

```json
POST /api/incidents/{incident_id}/approve
{"plan_id":"<id>","plan_hash":"<sha256>","state_version":3,"approved_by":"demo-operator"}
```

```json
POST /api/incidents/{incident_id}/recover
{"plan_id":"<id>","operation_key":"RECOVER-<incident>-v3","approved_by":"demo-operator"}
```

### 5.4 Error envelope

```json
{
  "error": {
    "code": "STALE_STATE",
    "message": "The order changed after simulation.",
    "request_id": "<uuid>",
    "incident_id": "<uuid-or-null>",
    "details": {}
  }
}
```

The client receives safe messages only. Stack traces, environment values, provider response bodies containing sensitive data, and filesystem paths stay out of API responses.

### 5.5 HTTP behavior

| Condition | Status |
|---|---:|
| Valid request | 200/201 |
| Invalid input/action/target | 400 or 422 |
| Missing order/incident | 404 |
| Replay with different payload or stale version | 409 |
| Fault injection disabled/unapproved recovery | 403 |
| AI unavailable | 503 |
| Provider returned unusable output | 502 |

---

## 6. Data model and invariants

### 6.1 Required tables

| Table | Critical fields and database protection |
|---|---|
| `orders` | id, sku, quantity > 0, status, version, timestamps |
| `inventory` | sku PK, initial_stock, available_stock >= 0, version |
| `inventory_reservations` | id, order FK, logical_event_id, attempt_id, qty > 0, status, timestamps |
| `workflow_events` | id, order FK, logical_event_id, attempt_id, step, result, duration_ms >= 0, retry_no >= 0 |
| `processed_events` | logical_event_id unique, order FK, processed_at |
| `telemetry` | scoring-time features, raw model score, model version |
| `incidents` | order FK, fingerprint unique for open incident, source, type, status, evidence JSON |
| `repair_plans` | incident FK, provider, typed actions JSON, immutable plan hash |
| `simulations` | plan FK, state version, before/after/checks JSON, passed |
| `approvals` | incident/plan/hash/version/operator, created_at, consumed_at |
| `recovery_attempts` | operation_key unique, before/after version, status, verification JSON |

### 6.2 Deterministic invariants

Every invariant returns an ID, pass/fail status, expected value, actual value, and evidence IDs.

1. `RESERVATION_QUANTITY_MATCH`: active reservation quantity equals order quantity when inventory is reserved.
2. `NO_DUPLICATE_ACTIVE_EVENT`: one logical event cannot own multiple active reservations.
3. `NON_NEGATIVE_AVAILABLE_STOCK`: inventory is never negative.
4. `STOCK_CONSERVATION`: available stock plus active reserved quantity equals initial stock for the scoped SKU in this simplified demo.
5. `RELEASE_TARGET_SAFE`: target is active, belongs to the order/event, is uncommitted, and has not shipped.
6. `UNIQUE_EXTRA_IDENTIFIED`: exactly one reservation is independently identifiable as the extra attempt.
7. `DEDUP_PROTECTION_PRESENT`: a passing repair also prevents the same logical event from recurring.
8. `NO_ORPHAN_REFERENCES`: all reservation/event/order relationships are valid.
9. `VERSION_MATCH`: live version equals simulated and approved version.
10. `NO_REPEAT_COMPENSATION`: operation key and released state prohibit a second adjustment.

### 6.3 Stock semantics

- Normal reserve decrements `available_stock` once.
- Controlled faulty reserve decrements it a second time, making the silent corruption visible in both reservations and stock projection.
- Releasing the verified extra reservation increments available stock exactly once.
- Dedup recording alone changes no stock.
- Retry uses normal idempotent processing and therefore is a no-op when the event is already processed.

These semantics must be implemented as shared pure transition functions used by both normal logic and simulation. Persistence code translates the verified state delta into database writes.

---

## 7. Six-hour execution schedule

The schedule is sequential for one implementer. With teammates, ML work may run beside Phases 2–3, but shared contracts remain single-owner.

| Time | Phase | Required gate |
|---|---|---|
| 0:00–0:25 | Phase 0 — environment and repository | Versions known, secrets ignored, commands reproducible |
| 0:25–0:50 | Phase 1 — skeleton and frozen contracts | Health/API/build tests green |
| 0:50–1:40 | Phase 2 — normal persisted workflow | Normal order is correct and replay-safe |
| 1:40–2:20 | Phase 3 — fault and deterministic detection | Actual two-reservation incident persisted |
| 2:20–3:00 | Phase 4 — ML training and inference | Artifact and honest held-out metrics produced |
| 3:00–3:35 | Phase 5 — structured AI diagnosis | Typed plans or honest unavailable state |
| 3:35–4:15 | Phase 6 — digital twin | Two calculated rejects, one calculated pass, zero DB writes |
| 4:15–5:00 | Phase 7 — approval and recovery | Atomic verified repair; replay no-op |
| 5:00–5:35 | Phase 8 — connected React UI | Full journey visible from live APIs |
| 5:35–6:00 | Phase 9 — adversarial test and demo freeze | Full gates pass; no new features |

If a gate overruns, cut P1 and visual polish. Never cut transaction, idempotency, simulation isolation, or post-commit verification.

---

## 8. Phase-by-phase implementation plan

## Phase 0 — Environment, repository, and secret boundary

**Goal:** Establish a reproducible workspace without implementing product behavior.

**Files:** `.gitignore`, `README.md`, `backend/.env.example`, dependency manifests.

**Work:**

- Confirm Python 3.11+, Node compatible with the selected Vite/Vitest release, npm, Git, and SQLite.
- Initialize Git if desired by the owner; do not commit `.env`, SQLite DBs, caches, coverage, Playwright artifacts, or joblib files until artifact policy is decided.
- Create `.env.example` with empty keys and safe defaults.
- Configure localhost origins explicitly.
- Add setup, test, and run commands to README.
- Create `ai_smoke.py`: check key presence, list/get the configured model if supported, make one tiny structured request, redact errors, and return a nonzero exit code when unavailable.
- Decide model artifact location and ensure only locally generated artifacts can be loaded.

**Tests/checks:**

- `python --version`, `node --version`, `npm --version`, `git --version`.
- Secret-pattern scan of tracked files for common key prefixes and nonempty key assignments.
- Test `.env.example` contains no credential value.
- Run AI smoke only when a key is configured; absence is a clear `UNAVAILABLE`, not a failed product gate.

**Exit gate:** Fresh setup instructions are executable; secret files are ignored; no provider is claimed working without a real response.

## Phase 1 — Application skeleton and contracts

**Goal:** Produce a bootable API and buildable frontend with stable shared types.

**Files:** `app/main.py`, `config.py`, `db.py`, `schemas.py`, `routes/health.py`, frontend scaffold, API client/types, initial tests.

**Work:**

- Build an app factory so each test can inject a temporary database and fake provider.
- Configure Pydantic settings with unknown environment fields handled deliberately and secrets represented as secret types.
- Initialize SQLModel engine and per-request sessions.
- Enable SQLite foreign keys on connection.
- Add CORS for configured local origins only.
- Implement `/api/health` returning database reachability, ML artifact status, configured provider name, and fault-injection status—never keys.
- Create the frontend shell with three routes/screens and no fake incident data.
- Mirror backend DTO enums and basic response types in TypeScript.

**Tests:**

- Health returns 200 and expected safe fields.
- Health response and application logs do not contain configured fake secrets.
- Invalid configuration fails early with an actionable error.
- CORS accepts the configured origin and rejects an unrelated origin.
- Backend OpenAPI includes the intended health schema.
- TypeScript compile and production build pass.

**Commands:**

```powershell
cd backend
python -m pytest tests/test_health.py tests/test_contracts.py -q
cd ..\frontend
npm run build
```

**Exit gate:** API boots, frontend builds, shared contract baseline is frozen.

## Phase 2 — Normal order workflow

**Goal:** Implement the correct path before introducing failure behavior.

**Files:** `models.py`, `core/workflow.py`, `routes/orders.py`, workflow schemas and tests.

**Work:**

- Create order, inventory, reservation, event, and processed-event models with constraints/indexes.
- Seed `LAPTOP-001` inventory deterministically in test/demo setup.
- Implement pure transitions for reserve, release, and event deduplication.
- Implement `POST /api/orders` and `GET /api/orders/{id}`.
- In one transaction: validate stock, create order/event/reservation, decrement stock, record processed logical event, and increment order version.
- A duplicate normal request with the same logical event must not create a second reservation. Define whether it returns the original result or a conflict; keep behavior stable and test it.
- Mark payment as simulated in event/result fields.

**Tests:**

- T01: quantity 1 creates one active reservation and correct stock delta.
- Invalid quantity 0/negative is rejected without rows.
- Unknown SKU is rejected without rows.
- Insufficient stock rolls back order, event, reservation, and stock changes.
- Same logical event produces no duplicate side effect.
- Foreign-key violation is rejected.
- Available stock cannot become negative.
- Order version increments only on real state mutation.
- Concurrent/repeated logical event requests result in at most one reservation.

**Evidence command:** Query order, reservation, event, processed-event, and inventory rows after a real API request.

**Exit gate:** Correct persisted workflow passes all tests; no incident exists for normal state.

## Phase 3 — Controlled fault, rules, and incident evidence

**Goal:** Reproduce the exact silent failure and detect it from real persisted state.

**Files:** `core/invariants.py`, `core/evidence.py`, incident model/routes, detector tests.

**Work:**

- Add `POST /api/orders/{id}/inject-duplicate`, guarded by `ENABLE_FAULT_INJECTION` and visibly labeled demo-only.
- The endpoint creates a new physical attempt for the existing logical event, deliberately bypassing normal deduplication.
- Persist the second active reservation and stock delta; do not auto-create an incident until inspection.
- Add `POST /api/orders/{id}/inspect` and incident list/detail endpoints.
- Build evidence exclusively from queried rows. Include expected/actual values and stable evidence IDs.
- Fingerprint an open incident so repeated inspection updates/reuses it rather than creating unlimited duplicates.
- Keep rule outcome separate from later ML score.

**Tests:**

- T02: injection succeeds at HTTP level and leaves two active reservations.
- Fault injection is 403 when disabled.
- Injection for missing/completed/shipped order is rejected without mutation.
- T03: inspection creates one rule incident with expected 1, actual 2.
- Normal order inspection creates no rule incident.
- Duplicate-event invariant and stock-conservation invariant both use actual rows.
- Repeated inspection is incident-idempotent.
- Evidence contains only the scoped order and no secrets.
- Failed injection transaction leaves the original order unchanged.

**Exit gate:** Database proof shows two active reservations and one open incident derived from them.

## Phase 4 — Synthetic ML pipeline and runtime scoring

**Goal:** Train, evaluate, save, load, and invoke a real anomaly detector honestly.

**Files:** dataset/train/evaluate scripts, `ml/features.py`, `ml/inference.py`, generated metadata/evaluation, ML tests.

**Work:**

- Define a single ordered feature tuple: `event_count`, `retry_count`, `processing_time_ms`, `order_quantity`, `active_reservation_count`, `distinct_step_count`.
- Generate correlated normal training data with seed 42; use separate seeds for validation and test.
- Generate held-out anomaly families: event storms, retries, latency, and duplicate reservations. Include benign slow-but-correct cases in held-out normals.
- Fit Isolation Forest only on normal training rows.
- Select a threshold using validation data and document the selection rule. Do not tune on held-out test data.
- Evaluate once on held-out samples and save confusion matrix, precision, recall, F1, FPR, FNR, sample counts, and the synthetic-data disclaimer.
- Persist artifact plus metadata and SHA-256.
- At runtime derive features from current stored events/reservations, not request-provided scores.
- Missing/invalid artifact returns `ML_UNAVAILABLE`; deterministic rules continue.
- ML-only alerts must never produce an approvable mutation plan without a deterministic violation.

**Tests:**

- Same seeds reproduce identical datasets and measured output.
- Training rows contain only normal samples and no held-out row IDs.
- Feature order is identical across generation, fitting, and inference.
- Label/fault/outcome/post-recovery columns cannot enter model features.
- T04: locally generated artifact loads and scores real feature vectors.
- Artifact hash mismatch or version mismatch fails closed.
- Missing artifact yields `ML_UNAVAILABLE` without breaking rule inspection.
- Score/threshold are numeric raw values, not percentages.
- T05: slow/retry telemetry with correct reservations may create an ML-only investigation but changes no business state.
- Evaluation JSON equals freshly computed metrics within exact deterministic output or documented numeric tolerance.

**Commands:**

```powershell
cd backend
python scripts/generate_dataset.py
python scripts/train_model.py
python scripts/evaluate_model.py
python -m pytest tests/test_ml.py tests/test_detector.py -q
```

**Exit gate:** Trusted artifact and measured synthetic holdout metrics exist; runtime path actually invokes the loaded model.

## Phase 5 — Bounded AI diagnosis

**Goal:** Obtain grounded, typed proposals without giving the model execution authority.

**Files:** AI protocol/adapters/validation, incident diagnosis route, AI tests.

**Work:**

- Define `InvestigatorProtocol.diagnose(evidence) -> Diagnosis`.
- Use a strict Pydantic response model with forbidden extra fields, action enums, nonempty IDs, 1–3 plans, and bounded action counts.
- Sanitize and size-limit evidence. Treat all stored text as untrusted data.
- Gemini adapter requests structured JSON using the configured stable model.
- Optional Groq adapter uses strict mode only when supported; otherwise use best-effort JSON plus identical local validation.
- Semantic validator confirms every evidence and target ID exists and belongs to the incident.
- Persist accepted plans and a canonical SHA-256 plan hash. Do not persist invalid provider output as executable plans.
- Return `UNAVAILABLE`/502/503 accurately on missing key, timeout, quota, auth, unsupported model, refusal, invalid JSON, or invalid semantics.
- Tests use a deterministic fake provider only through dependency override and label it as a test double.

**Tests:**

- T06: optional live smoke returns a valid typed diagnosis when credentials are present.
- T07: unavailable provider leaves all business rows unchanged.
- Fake provider valid response persists only allowed plans.
- Unknown action, extra field, empty target, too many plans/actions, absent evidence ID, cross-order target, SQL/code text in action type, and duplicate plan IDs are rejected.
- Provider timeout and malformed JSON are non-mutating.
- Evidence payload excludes secrets and is size bounded.
- Repeating diagnosis for unchanged evidence uses the cache or stable evidence hash without duplicate plan rows.

**Exit gate:** A real provider works or the UI/API truthfully shows unavailable; neither outcome can mutate reservations or stock.

## Phase 6 — Independent digital-twin simulation

**Goal:** Prove candidate behavior with shared transitions and no database writes.

**Files:** healing action/snapshot/simulator/verifier modules, simulation route, twin tests.

**Work:**

- Construct an immutable `WorkflowSnapshot` from persisted incident state.
- Serialize a canonical snapshot hash and record the order version.
- Deep-copy the same baseline separately for every plan.
- Apply only shared pure transition functions.
- Run all deterministic invariants plus prevention and target-safety checks after each plan.
- Save before/after/check results; saving simulation records is allowed, but business tables must remain byte-for-byte/state-equivalent.
- Mark a plan approvable only when all checks pass and the incident is deterministically proven. ML-only incidents cannot reach an automatic mutation approval path.

**Tests:**

- T08: `RETRY_ORDER` is an idempotent no-op and mismatch remains.
- T09: `RECORD_EVENT_DEDUP` leaves existing excess and is rejected.
- T10: unique extra release plus dedup produces one active reservation and consistent stock.
- T11: simulations do not alter orders, inventory, reservations, events, or processed events.
- All candidates start with identical snapshot/hash.
- Mutating one candidate cannot affect another.
- Unknown action and bad target are rejected before transition.
- Release of committed/shipped/unrelated reservation is rejected.
- Ambiguous duplicate selection escalates instead of guessing.
- Passing current count without dedup prevention is rejected.
- A prefilled provider `passed=true` field, if supplied, has no influence because it is not part of the schema.

**Exit gate:** Calculated output is exactly two rejected plans and one passing plan for the demo incident, with unchanged live business state.

## Phase 7 — Approval, atomic recovery, and verification

**Goal:** Apply only the independently verified plan exactly once.

**Files:** `healing/executor.py`, approval/recovery schemas and routes, recovery tests.

**Work:**

- Approval endpoint accepts exact plan ID/hash, state version, and nonempty demo operator identity.
- Verify simulation passed, incident has a deterministic violation, and current version still matches.
- Persist approval; bind it to the immutable plan and version. Any later state change invalidates it.
- Recovery begins an explicit transaction, rechecks every precondition, claims the unique operation key, releases the exact reservation, restores stock once, records dedup, increments versions, and writes an audit attempt.
- Do not make LLM/network calls in the transaction.
- Commit, close session, open a fresh session, and rerun invariants.
- Mark incident recovered only after fresh verification passes.
- Same operation key with the same payload returns `REPLAY_NOOP`; same key with a different payload returns `409`.
- Any precondition failure rolls back and keeps the incident unresolved/escalated as appropriate.

**Tests:**

- T12: recovery without approval is forbidden and non-mutating.
- Approval of rejected/unknown/stale/hash-mismatched plan is blocked.
- T13: approved passing plan releases one reservation, restores one stock unit, writes audit, and verifies.
- T14: identical operation replay produces zero additional delta.
- Same key with different incident/plan is a conflict.
- T15: changed order version invalidates approval.
- T16: shipped, committed, unrelated, already released, or ambiguous target is rejected.
- Forced exception after each mutation step rolls back the full transaction.
- Concurrent recovery calls produce at most one applied attempt.
- Post-commit verifier uses a fresh session and actual database values.
- Simulated verifier pass alone cannot mark the incident recovered.
- Verification failure is visible and not mislabeled as rolled back after commit.

**Exit gate:** Real database moves from two active reservations to one exactly once, and a fresh read proves it.

## Phase 8 — Connected React dashboard

**Goal:** Present the real system state without duplicating backend decisions in the browser.

**Files:** three pages, components, API client, TypeScript contracts, component tests, Playwright test.

**Work:**

- Mission Control: create order, inject controlled fault, inspect, current workflow state, reservations/events, API-success-versus-invariant warning.
- Investigation: rule results, observed/expected values, raw ML score/threshold/status, provider, grounded diagnosis, and explicit unavailable/error states.
- Simulation Lab: calculated before/after states, per-check results, rejection reasons, exact-plan approval, recovery, fresh readback, and audit result.
- Use one typed API client. No provider key or direct provider request exists in frontend code.
- Disable actions while requests are pending, but rely on backend idempotency for correctness.
- Use accessible labels, keyboard-operable dialogs, visible focus, and non-color status text.
- Do not show fake confidence percentages, fake live badges, or optimistic success before the API confirms it.

**Tests:**

- Component: loading, empty, error, AI unavailable, ML unavailable, rule violation, rejected/pass plan, and recovered states render from fixture contracts.
- Component: approval is disabled for rejected plans and enabled only for server-marked approvable plan.
- Component: API errors do not mutate cached UI state into success.
- Contract: representative backend responses satisfy TypeScript expectations.
- Security: built frontend contains no test/provider secret or `GEMINI_API_KEY`/`GROQ_API_KEY` reference.
- Playwright: create → inject → inspect → diagnose (fake provider in controlled test server) → simulate → approve → recover → refresh → replay.
- Playwright asserts user-visible one-active-reservation result and replay-safe message.
- `npm run build` succeeds.

**Exit gate:** A judge can complete the entire workflow through live local APIs, and refresh preserves truth.

## Phase 9 — Adversarial audit, demo freeze, and handoff

**Goal:** Stop adding features and prove the MVP under failure conditions.

**Files:** README/test report/known limitations only, plus minimal blocker fixes.

**Work:**

- Run all backend, frontend, build, and E2E gates from a clean demo database.
- Run the real-provider smoke separately and record provider/model/timestamp without recording prompts containing secrets.
- Inspect Git diff/status for `.env`, DB, caches, artifacts, logs, PII, and secret patterns.
- Verify metrics shown in UI come from evaluation JSON or database queries.
- Document synthetic-data limits, local simulation scope, AI availability, and unimplemented P1/P2.
- Rehearse the 90-second demo and one network-outage path.
- Freeze changes except critical correctness/readability fixes.

**Commands:**

```powershell
cd backend
python -m pytest -q
cd ..\frontend
npm run test -- --run
npm run build
npx playwright test
```

**Exit gate:** All mandatory commands have actual recorded exit codes; failures/skips are disclosed; repository is demo-ready.

---

## 9. Master automated test matrix

| ID | Layer | Scenario | Required assertion |
|---|---|---|---|
| T01 | API/DB | Normal order q=1 | One active reservation; correct stock; no incident |
| T02 | API/DB | Controlled duplicate | Successful HTTP response; two persisted active reservations |
| T03 | Rules | Inspect duplicate | Expected 1 vs actual 2 with row evidence |
| T04 | ML | Train/evaluate/infer | Trusted artifact and measured held-out synthetic metrics |
| T05 | ML safety | Slow/retry but consistent | Investigation only; no mutation authority |
| T06 | AI smoke | Configured provider | Pydantic-valid bounded diagnosis |
| T07 | AI failure | Missing/failed provider | Honest unavailable; state unchanged |
| T08 | Twin | Retry plan | Violation remains; rejected |
| T09 | Twin | Dedup-only plan | Excess remains; rejected |
| T10 | Twin | Release + dedup | All post-state and prevention checks pass |
| T11 | Twin isolation | Any simulation | Business tables unchanged |
| T12 | Recovery guard | No approval | Forbidden and non-mutating |
| T13 | Recovery success | Exact approved plan | One release, one stock restore, audit, fresh verification |
| T14 | Idempotency | Same operation key | Replay no-op and zero second delta |
| T15 | Optimistic lock | Version changes | 409; approval invalid; no mutation |
| T16 | Target safety | Shipped/unrelated/ambiguous | Rejected/escalated |
| T17 | AI validation | Unknown action/bad target | Rejected before simulation/execution |
| T18 | Security | API/build/Git scan | No secrets or real PII |
| T19 | Transaction | Inject failure mid-recovery | Every business write rolls back |
| T20 | Concurrency | Two recovery requests | At most one applied attempt |
| T21 | Incident dedup | Repeat inspection | One open incident fingerprint |
| T22 | Artifact security | Hash/version mismatch | ML unavailable; rules still work |
| T23 | Contract | Backend/frontend DTOs | Representative payloads stay compatible |
| T24 | UI truth | API error | No optimistic recovered state |
| T25 | Fresh read | Post-commit verification | New session reads one active reservation |
| T26 | CORS | Unapproved origin | Browser request rejected |
| T27 | DB integrity | Foreign-key violation | Database rejects invalid reference |
| T28 | Evidence isolation | Multiple orders | Incident evidence contains only target order |
| T29 | Prompt injection | Malicious event text | Treated as data; no new action/tool authority |
| T30 | Full E2E | Judge journey plus refresh/replay | Persisted recovery remains correct |

---

## 10. Test design details

### 10.1 Backend fixtures

- Each test receives a unique temporary SQLite file, not the developer database.
- Apply the same connection settings as production, including foreign keys.
- Seed only required inventory.
- Override provider and artifact dependencies explicitly.
- Clear dependency overrides after every test.
- Freeze or inject clocks where deterministic timestamps are required.
- Never share mutable session/model state between tests.

### 10.2 Database assertions

For any mutation test, capture a before snapshot of row counts, statuses, quantities, stock, and versions. Assert the intended delta and explicitly assert forbidden deltas remain zero. Recovery tests must query through a new session after the request.

### 10.3 ML evaluation assertions

- Dataset partitions have disjoint IDs and independent seeds.
- Metrics are recomputed from saved predictions, not copied constants.
- A high score is not a required gate; pipeline integrity and truthful reporting are. Suspiciously perfect results trigger dataset review.
- The UI labels all evaluation numbers as synthetic holdout results.

### 10.4 AI tests

Most tests use provider doubles for deterministic failure shapes, not fabricated production success. The live test is marked `external` and skipped unless the relevant environment variable is present. Its result is never required for offline unit tests but is required for claiming live AI in the demo.

### 10.5 Property and fault-injection tests

Within the sprint, parameterize quantities, stock levels, reservation statuses, and action order. Inject executor failures after operation-key creation, reservation release, stock restoration, dedup creation, and audit write to demonstrate rollback.

### 10.6 Frontend and E2E

- Unit tests verify conditional rendering and user actions against mocked HTTP boundaries.
- Playwright verifies user-visible behavior through a real local backend configured with a test provider.
- Keep one Chromium E2E project for the six-hour P0 gate; add Firefox/WebKit only as P1 if time remains.

---

## 11. CI/local quality gates

### Per-phase gate

1. Targeted tests for touched behavior.
2. Full backend tests if shared models/schemas/database code changed.
3. Frontend unit/build if contracts or UI changed.
4. Review diff for unrelated files and secret material.
5. Create a small commit-ready checkpoint only after green results.

### Final gate

```text
Backend pytest: PASS
Frontend unit tests: PASS
Frontend production build: PASS
Playwright P0 journey: PASS
Real-provider smoke: PASS or explicitly UNAVAILABLE
Secret scan: PASS
Manual DB readback: one active reservation
Recovery replay: no second stock/reservation mutation
```

Do not convert an unavailable external provider into a fake passing test.

---

## 12. Demo runbook

1. Reset only the configured demo database with explicit confirmation.
2. Start backend and frontend in separate terminals.
3. Open health and state the real ML/provider status.
4. Create `LAPTOP-001`, quantity 1, event `EVT-101`.
5. Show one active reservation and stock.
6. Inject the controlled duplicate and emphasize that HTTP success is not business correctness.
7. Inspect and show deterministic mismatch plus raw ML signal.
8. Diagnose; show real provider or clearly disclosed unavailable fallback.
9. Simulate all candidates; compare calculated checks.
10. Approve only the passing exact plan.
11. Recover and show fresh database readback.
12. Repeat recovery and show replay no-op.
13. Close with the safety chain: evidence → bounded proposal → isolated proof → approval → guarded transaction → verification.

---

## 13. Failure policy and fallbacks

| Failure | Required behavior | Forbidden behavior |
|---|---|---|
| Gemini unavailable | Try configured Groq once or report unavailable | Canned response labeled Gemini |
| Both providers unavailable | Continue rule/ML/twin demo with predeclared deterministic fallback clearly labeled | Claim live AI |
| ML artifact missing/bad | `ML_UNAVAILABLE`; rules continue | Hardcoded score |
| Invalid model action | Reject and preserve state | Coerce into a known action |
| Ambiguous extra reservation | Escalate | Guess a reservation |
| Stale version | 409 and require re-simulation | Apply old approval |
| Transaction precondition fails | Roll back; incident stays unresolved | Partial success response |
| Post-commit verification fails | Mark verification failed/escalated | Claim automatic rollback after commit |
| Frontend request fails | Display error and refetch truth | Optimistic recovered badge |

---

## 14. Risks and mitigations

| Risk | Early signal | Mitigation |
|---|---|---|
| Provider/model drift | Smoke test returns model/auth/quota error | Configurable exact model; verify before event; honest fallback |
| SQLite transaction misconception | Partial rows after forced failure | Explicit transaction and mutation-step rollback tests |
| Duplicate compensation | Stock increases twice | Unique operation key, status predicate, transaction, replay test |
| Twin/live divergence | Sim passes, commit fails | Shared transitions plus live preconditions and fresh verification |
| ML leakage | Unrealistically perfect holdout | Partition/feature audit and benign edge cases |
| Unsafe artifact | Unknown joblib file appears | Hash metadata; locally generated path only; fail closed |
| Contract drift | UI runtime errors after backend change | Frozen schemas, fixtures, build, contract tests |
| UI consumes sprint | Backend gate incomplete at hour 4 | Plain cards first; cut P1 visualization |
| Secret exposure | Key appears in diff/build/log | Backend-only env, scans, redaction tests |
| Overclaiming | Demo language says production/self-autonomous | Explicitly call it a simulated workflow-state twin |

---

## 15. Definition of done

P0 is done only if all statements below are true:

- The implementation contains no static successful incident, diagnosis, simulation, metric, or recovery response in production paths.
- Tests T01–T30 pass, except the external AI smoke may be reported unavailable when no credentials/network exist.
- The Isolation Forest artifact was created locally by the committed training code and its actual synthetic metrics are stored with metadata.
- A real configured LLM call has been demonstrated before claiming live AI.
- Simulation produces no SQLite business-state writes.
- Only a deterministically proven incident can approve a mutating plan.
- Recovery requires exact approval, matching version/hash/evidence, and a unique operation key.
- A fresh database session verifies one active reservation after commit.
- Replay changes neither reservation state nor stock.
- The frontend production build and P0 Playwright journey pass.
- No secrets, real customer data, or unsupported production claims are present.
- Remaining limitations are documented plainly.

---

## 16. Research sources

Official primary documentation used to refine this plan:

- [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output) — JSON Schema/Pydantic support, locally unenforced constraints, and semantic-validation guidance.
- [Gemini model catalog](https://ai.google.dev/gemini-api/docs/models) and [Models API](https://ai.google.dev/api/models) — stable model naming and runtime availability checks.
- [Groq structured outputs](https://console.groq.com/docs/structured-outputs) and [Groq supported models](https://console.groq.com/docs/models) — strict-mode requirements and model-dependent support.
- [SQLAlchemy SQLite transactions](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html) — Python SQLite legacy transaction behavior and explicit transaction control.
- [SQLAlchemy session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) — short session/transaction scope and commit/rollback context management.
- [SQLite foreign-key support](https://sqlite.org/foreignkeys.html) — immediate/deferred constraint behavior and referential integrity.
- [scikit-learn IsolationForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) — anomaly score and contamination semantics.
- [scikit-learn model persistence](https://scikit-learn.org/stable/model_persistence.html) — joblib/pickle execution risk and version metadata requirements.
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/) and [dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/) — TestClient and external dependency replacement.
- [Vitest guide](https://vitest.dev/guide/) — Vite-aligned frontend unit test runner requirements.
- [Playwright test guidance](https://playwright.dev/docs/running-tests) and [best practices](https://playwright.dev/docs/best-practices) — isolated, user-visible end-to-end behavior.

Provider models, pricing, free tiers, quotas, frontend runtime requirements, and library compatibility are time-sensitive. Recheck them during Phase 0; this plan intentionally makes those settings configurable.

---

## 17. First implementation action

Begin Phase 0 only. Report exact tool versions and proposed files, establish secret-safe configuration and reproducible commands, then run the Phase 0 checks. Do not scaffold later phases until the Phase 0 gate is recorded.
