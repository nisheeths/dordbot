import json
from pathlib import Path
from typing import List, Dict, Any
from backend.services.embed import TfidfEmbedder
from backend.services.vector_store import FaissStore


def load_employees(json_path: str) -> List[Dict[str, Any]]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(src_json: str, out_dir: str):
    emps = load_employees(src_json)
    corpus = [(e.get("skills_text") or "") for e in emps]
    embedder = TfidfEmbedder()
    embedder.fit(corpus)
    emb = embedder.encode(corpus)
    store = FaissStore()
    store.add(emb, emps)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    store.persist(out_dir)
    from joblib import dump
    dump(embedder.vectorizer, str(Path(out_dir) / "tfidf_vectorizer.joblib"))
    print(f"Ingested {len(emps)} employees to {out_dir}")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True, help="Path to employees.json")
    p.add_argument("--out", default="backend/data", help="Output dir for index/metadata")
    args = p.parse_args()
    main(args.src, args.out)
