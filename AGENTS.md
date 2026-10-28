# MirrorHeal AI — Instructions for Cursor Agent

You are implementing a **real**, local-first, six-hour hackathon MVP. Read `MIRRORHEAL_MASTER_PLAN.md` and `CURSOR_EXECUTION_GUIDE.md` before writing major features.

## Priority and scope
- P0 = one complete synthetic order → hidden duplicate reservation → deterministic check + trained anomaly signal → Gemini/Groq root-cause proposal → isolated repair simulations → server-approved transactional recovery → post-commit verification.
- P1 = ML-only anomaly demo, React Flow visualization, metrics.
- P2 = external integrations, distributed infrastructure, additional failure types; **do not build P2 in the hackathon sprint**.
- Never replace missing logic with UI-only animations, canned "successful repair" JSON, or fabricated model output.

## Stack
- Frontend: React + Vite + TypeScript + Tailwind, optional `@xyflow/react`, `lucide-react`.
- Backend: Python 3.11+ + FastAPI + SQLModel + SQLite + Pydantic v2.
- AI: `google-genai` Gemini primary and optional `groq` backup; strictly typed output.
- ML: scikit-learn IsolationForest on synthetic normal telemetry; NumPy/Pandas; metadata + honest holdout metrics.
- Digital twin: pure transition functions and deep-copied in-memory snapshots. No DB writes during simulation.
- Tests: pytest; frontend `npm run build`.

## Safety invariants (never break)
1. LLM proposes allowlisted structured plans; it never executes arbitrary Python/SQL/shell/network requests.
2. ML anomaly is a suspicion, **not proof of business corruption**. Never auto-repair based solely on an ML score.
3. Known violations detected by deterministic invariants; only independently verified plans can be approved.
4. Each candidate is simulated on an independent copy of the same starting state using shared transition functions.
5. Live simulated DB changes require server-side human approval, exact target/evidence checks, version checks, a transaction, and idempotency protection.
6. A repeated recovery request cannot release the same reservation or alter stock again.
7. Original state must be re-queried after commit; incident is recovered only after verification.
8. Never expose environment secrets in code, browser, responses, logs, commits or reports.
9. Model/pipeline artifacts loaded with joblib are only those generated locally by our trusted scripts.
10. Synthetic-data metrics must be marked synthetic; do not invent scores or claim generalization to real production data.

## Engineering behavior
- Make scoped edits; avoid rewriting unrelated or teammate-owned files.
- Before each change explain proposed files; after change run relevant tests/build and report actual output.
- Store shared API contracts in Pydantic schemas; mirror them in frontend TypeScript types.
- Preserve working gates; if blocked by external LLM, show unavailable rather than fake responses.
- Build functionality and tests first, UI polish last.
- Write a small commit-ready change at the end of each successful phase.
- If ambiguity would block development, choose the smallest implementation consistent with P0 and document the assumption.
