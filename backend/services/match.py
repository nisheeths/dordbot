from typing import List, Dict, Any
import numpy as np
from ..models.schemas import RecommendRequest, RecommendResponse, Assignment, Candidate, WorkElement
from .decompose import decompose_cfp
from .score import team_confidence


def _iterative_refine(elements: List[WorkElement], sims: np.ndarray, idxs: np.ndarray, min_sim: float) -> List[int]:
    gaps = []
    for i in range(len(elements)):
        if sims.shape[0] == 0 or sims[i, 0] < min_sim:
            gaps.append(i)
    return gaps


def recommend_team(req: RecommendRequest, store, embedder) -> RecommendResponse:
    elements: List[WorkElement] = req.cfp_elements or []
    if not elements:
        if not req.text:
            return RecommendResponse(assignments=[], coverage_score=0.0, confidence_score=0.0, gaps=[])
        elements = decompose_cfp(req.text)

    texts = [(" ".join(e.keyphrases) + " " + e.text).strip() for e in elements]
    queries = embedder.encode(texts)

    sims, idxs = store.search(queries, req.top_k)
    assignments: List[Assignment] = []
    id_lookup: Dict[int, Dict[str, Any]] = {i: m for i, m in enumerate(store.metadata)}
    meta_by_empid: Dict[str, Dict[str, Any]] = {}

    for i, el in enumerate(elements):
        candidates: List[Candidate] = []
        if idxs.size > 0 and i < idxs.shape[0]:
            for rank in range(req.top_k):
                j = int(idxs[i, rank]) if idxs[i, rank] >= 0 else -1
                if j < 0 or j not in id_lookup:
                    continue
                meta = id_lookup[j]
                emp_id = meta.get("id") or str(j)
                meta_by_empid[emp_id] = meta
                candidates.append(
                    Candidate(
                        employee_id=emp_id,
                        name=meta.get("name") or "Unknown",
                        similarity=float(sims[i, rank]) if sims.size > 0 else 0.0,
                        rationale=meta.get("role"),
                    )
                )
        assignments.append(Assignment(work_element_id=el.id, candidates=candidates))

    gaps_idx = _iterative_refine(elements, sims, idxs, req.min_similarity)
    gaps = [elements[g].text[:160] for g in gaps_idx]
    covered = sum(1 for a in assignments if a.candidates and a.candidates[0].similarity >= req.min_similarity)
    coverage_score = covered / max(1, len(assignments))
    confidence_score = team_confidence(assignments, meta_by_empid)
    return RecommendResponse(
        assignments=assignments,
        coverage_score=float(coverage_score),
        confidence_score=float(confidence_score),
        gaps=gaps,
    )
