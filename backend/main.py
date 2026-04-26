from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from joblib import load

from backend.models.schemas import CfpRequest, AnalyzeResponse, RecommendRequest, RecommendResponse
from backend.services.decompose import decompose_cfp
from backend.services.vector_store import FaissStore
from backend.services.embed import TfidfEmbedder
from backend.services.pdf_text import extract_pdf_text, persist_cfp_text


app = FastAPI(title="CfP Team Matcher")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("backend/data")
INDEX_DIR = DATA_DIR
VECTORIZER_PATH = DATA_DIR / "tfidf_vectorizer.joblib"
CACHE_DIR = DATA_DIR / "cfp_cache"

store = FaissStore()
embedder = TfidfEmbedder()


@app.on_event("startup")
def startup_event():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store.load(str(INDEX_DIR))
    if VECTORIZER_PATH.exists():
        vec = load(str(VECTORIZER_PATH))
        embedder.vectorizer = vec


@app.get("/healthz")
def healthz():
    return {"ok": True, "indexed": len(store.metadata)}


@app.post("/cfp/analyze", response_model=AnalyzeResponse)
def analyze_cfp(req: CfpRequest):
    elements = decompose_cfp(req.text)
    return AnalyzeResponse(work_elements=elements)


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    from backend.services.match import recommend_team

    return recommend_team(req, store, embedder)


@app.post("/cfp/upload")
async def upload_cfp(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    res = extract_pdf_text(data)
    if res.chars < 20:
        raise HTTPException(status_code=400, detail="No extractable text detected; please OCR or trim to textual sections")
    persist_cfp_text(CACHE_DIR, res, meta={"filename": file.filename, "content_type": file.content_type})
    preview = res.text[:800]
    return {"cfp_id": res.sha256, "pages": res.pages, "chars": res.chars, "preview": preview}


@app.post("/recommend/pdf", response_model=RecommendResponse)
async def recommend_from_pdf(file: UploadFile = File(...), top_k: int = 3, min_similarity: float = 0.25):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    res = extract_pdf_text(data)
    if res.chars < 20:
        raise HTTPException(status_code=400, detail="No extractable text detected; please OCR or trim to textual sections")
    # Go through the regular recommend flow using extracted text
    from backend.models.schemas import RecommendRequest as RR
    req = RR(text=res.text, top_k=top_k, min_similarity=min_similarity)
    from backend.services.match import recommend_team
    return recommend_team(req, store, embedder)
