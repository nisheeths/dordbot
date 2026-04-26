from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from joblib import load

from backend.models.schemas import CfpRequest, AnalyzeResponse, RecommendRequest, RecommendResponse
from backend.services.decompose import decompose_cfp
from backend.services.vector_store import FaissStore
from backend.services.embed import TfidfEmbedder


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
