# CfP Team Matcher — Backend (TF‑IDF + FAISS)

## Quick start

1) Create/activate venv (optional if already active)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
.venv/bin/python -m pip install -U pip setuptools wheel
.venv/bin/python -m pip install -r backend/requirements.txt
```

3) Ingest sample employees (build TF‑IDF + FAISS index)

```bash
.venv/bin/python -m backend.scripts.ingest_employees --src backend/data/employees.sample.json --out backend/data
```

4) Run the API

```bash
.venv/bin/uvicorn backend.main:app --reload
```

5) Test endpoints (using Python requests)

```bash
.venv/bin/python - <<'PY'
import requests, json
print('HEALTH:', requests.get('http://127.0.0.1:8000/healthz').json())
cfp = {"title":"Demo","text":"- Build an NLP pipeline for keyphrase extraction\n- Create a dataset and evaluation\n- Deploy an API for inference"}
print('ANALYZE:', requests.post('http://127.0.0.1:8000/cfp/analyze', json=cfp).json())
rec = {"text":"We need deep learning for vision, information extraction, and deployment.", "top_k": 2}
print('RECOMMEND:', requests.post('http://127.0.0.1:8000/recommend', json=rec).json())
PY
```

## Notes
- Uses TF‑IDF for lightweight embeddings and FAISS (inner product on L2‑normalized vectors) for similarity.
- Place your real employees dataset as JSON at `backend/data/employees.json` with fields: `id`, `name`, `role`, `skills_text`, optional `track_record`.
- Re‑run the ingest script whenever employees change.
- If `faiss-cpu` install fails, try pinning `faiss-cpu==1.8.0.post1` (already pinned via range) or ensure compatible Python/GLIBC.