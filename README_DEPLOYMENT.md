# MirrorHeal deployment

## Local verification

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

Frontend:

```powershell
cd frontend
npm ci
npm run test:run
npm run build
```

## Render deployment

The root `render.yaml` defines a backend web service and frontend static site.

1. Create a GitHub repository and push this project.
2. In Render, choose **New → Blueprint** and select the repository.
3. Set `GEMINI_API_KEY` as a secret when prompted. Never commit `.env`.
4. Render supplies `VITE_API_BASE_URL` and `ALLOWED_ORIGIN` from the service URLs.
5. Verify `https://<api-host>/api/health` before opening the frontend.

The SQLite database is suitable for the hackathon demo only. Use a persistent database before production use.
