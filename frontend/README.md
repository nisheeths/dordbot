# CfP Team Matcher — Frontend

Minimal Vite + React UI to submit CfP text and view team recommendations.

## Setup

```bash
# from workspace root, with Node.js installed
npm --prefix frontend install
npm --prefix frontend run dev
```

- Dev server: http://localhost:5173
- Backend base URL defaults to http://127.0.0.1:8000; override with `VITE_API_BASE`.

## Configure API base (optional)
Create `frontend/.env` with:
```
VITE_API_BASE=http://127.0.0.1:8000
```