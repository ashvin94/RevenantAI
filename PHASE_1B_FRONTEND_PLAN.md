# Phase 1B — Parallel Frontend Foundation

**Owner:** Frontend track  
**Runs in parallel with:** Phase 1A backend foundation  
**Goal:** Build a tested React shell that consumes the frozen health contract without touching backend or shared planning files.

---

## 1. Exclusive file ownership

The Phase 1B owner may create or edit only:

```text
frontend/**
```

Do not edit:

```text
backend/**
README.md
.gitignore
AGENTS.md
MIRRORHEAL_MASTER_PLAN.md
CURSOR_EXECUTION_GUIDE.md
PHASED_IMPLEMENTATION_PLAN.md
PHASE_1B_FRONTEND_PLAN.md
```

If a backend or shared-file change appears necessary, record it as an integration note instead of changing the file.

---

## 2. Required deliverable

Create a Vite React TypeScript frontend with:

- Tailwind CSS using the current Vite integration.
- Three navigable screens:
  - Mission Control
  - AI Investigation
  - Simulation Lab
- A shared application layout and navigation.
- One typed API client.
- A real health-status panel backed by `GET /api/health`.
- Loading, degraded, unavailable, and connection-error states.
- Vitest and Testing Library tests.
- A passing production build.

Do not implement orders, incidents, diagnosis, simulations, approval, or recovery in this phase.

---

## 3. Frozen backend contract

Endpoint:

```text
GET http://localhost:8000/api/health
```

TypeScript contract:

```ts
export interface HealthResponse {
  status: "ok" | "degraded";
  database: "available" | "unavailable";
  ml: "available" | "unavailable";
  ai_provider: "gemini" | "groq" | "unavailable";
  ai_configured: boolean;
  fault_injection_enabled: boolean;
  version: string;
}
```

Representative development fixture:

```json
{
  "status": "degraded",
  "database": "available",
  "ml": "unavailable",
  "ai_provider": "gemini",
  "ai_configured": false,
  "fault_injection_enabled": true,
  "version": "0.1.0"
}
```

This fixture is for component tests only. Production UI must fetch the API and must never present the fixture as live data.

---

## 4. Environment contract

Use one public frontend variable:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Create `frontend/.env.example` with that non-secret value. Never add Gemini or Groq keys to frontend files or any variable prefixed with `VITE_`.

The API client should fall back to `http://localhost:8000` for local development when the variable is absent.

---

## 5. Suggested file structure

```text
frontend/
├── .env.example
├── package.json
├── vite.config.ts
├── tsconfig.json
├── index.html
└── src/
    ├── App.tsx
    ├── main.tsx
    ├── index.css
    ├── pages/
    │   ├── MissionControl.tsx
    │   ├── Investigation.tsx
    │   └── SimulationLab.tsx
    ├── components/
    │   ├── AppLayout.tsx
    │   ├── Navigation.tsx
    │   └── HealthPanel.tsx
    ├── lib/
    │   └── api.ts
    ├── types/
    │   └── contracts.ts
    └── test/
        ├── setup.ts
        └── HealthPanel.test.tsx
```

Keep the structure small. Do not add state-management libraries, React Flow, charting libraries, component kits, or speculative abstractions.

---

## 6. Implementation steps

### Step 1 — Scaffold

Create a Vite `react-ts` application inside `frontend` and install only the Phase 1B dependencies:

```powershell
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install tailwindcss @tailwindcss/vite lucide-react
npm install -D vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

Do not install React Flow yet.

### Step 2 — Configure Tailwind and tests

- Add the Tailwind Vite plugin.
- Import Tailwind from the main stylesheet.
- Configure Vitest with `jsdom` and the test setup file.
- Add scripts for `test`, `test:run`, and `build`.

### Step 3 — Define the contract

- Add the exact `HealthResponse` interface to `src/types/contracts.ts`.
- Do not add optional fields or alternate spellings.
- Do not copy backend implementation details into the browser.

### Step 4 — Build the API client

The client must:

- Read `VITE_API_BASE_URL`.
- Request `/api/health`.
- Check `response.ok`.
- Parse the JSON into the expected application shape.
- Throw a safe error on HTTP or network failure.
- Never log response headers, environment variables, or secrets.

Do not retry indefinitely. One explicit page load/request is enough for Phase 1B.

### Step 5 — Build the shell

- Create persistent navigation for the three screens.
- Make Mission Control the default screen.
- Render clear placeholders explaining that business workflow functionality arrives in later phases.
- Do not render invented order, incident, ML, AI, or recovery values.

### Step 6 — Build the health panel

The health panel must visibly distinguish:

- Loading.
- API connection failure.
- Overall `ok`.
- Overall `degraded`.
- Database available/unavailable.
- ML available/unavailable.
- AI configured/unconfigured and provider name.
- Fault injection enabled/disabled.
- Backend version.

Use text and icons as well as color so statuses remain understandable without color perception.

### Step 7 — Accessibility and responsiveness

- Use semantic navigation and headings.
- Ensure keyboard-visible focus states.
- Give icon-only controls accessible labels.
- Maintain readable contrast.
- Support narrow and desktop widths.
- Avoid motion-heavy effects.

---

## 7. Required tests

### Component tests

1. Loading state appears before the request resolves.
2. A successful `ok` response displays all real fields.
3. A `degraded` response labels unavailable ML and unconfigured AI accurately.
4. A network failure displays an API connection error.
5. A non-2xx response displays an error and no success status.
6. Navigation reaches all three screens.
7. No screen displays fabricated order, incident, plan, metric, or recovery data.

Mock only the HTTP boundary in tests. Test fixtures must never be imported into production API code.

### Static/security checks

Search frontend source and built output for forbidden secret names:

```text
GEMINI_API_KEY
GROQ_API_KEY
```

Neither string should appear in production frontend code or `dist`.

### Required commands

```powershell
cd frontend
npm run test:run
npm run build
```

Both commands must exit successfully. Report actual output rather than claiming success from inspection.

---

## 8. Visual direction

- Dark navy or charcoal background.
- Cyan or restrained gold accent.
- Green for verified/available.
- Amber for degraded/investigating.
- Red for unavailable/error.
- Readable cards and typography before decorative effects.

This phase needs a professional shell, not final visual polish.

---

## 9. Explicitly forbidden in Phase 1B

- Editing any backend file.
- Direct Gemini or Groq browser calls.
- Frontend provider keys.
- Fake successful API responses in production code.
- Hardcoded incidents, plans, anomaly scores, metrics, or recovery results.
- React Flow, charts, Redux, or large UI kits.
- Approval or recovery behavior.
- Changing the frozen health contract without coordination.

---

## 10. Phase 1B exit gate

Phase 1B is complete only when:

- All work is confined to `frontend/**`.
- The three-screen shell works.
- The health panel consumes the real API contract.
- Loading, degraded, and error states are implemented.
- Component tests pass.
- Production build passes.
- No provider secrets or fabricated business data exist.
- The owner reports files changed and actual command results.

---

## 11. Integration handoff

When Phase 1A and Phase 1B are independently green:

1. Compare `backend/app/schemas.py` with `frontend/src/types/contracts.ts`.
2. Start the backend on port 8000.
3. Start the frontend on port 5173.
4. Confirm the browser displays the live health response.
5. Verify CORS permits only the configured frontend origin.
6. Run backend tests, frontend tests, and frontend build again.
7. Resolve any contract difference in one coordinated integration change.

Do not begin Phase 2 until this integration gate passes.
