from typing import List, Dict, Any
import numpy as np
from ..models.schemas import Assignment


def _norm(val: float, low: float, high: float) -> float:
    if high <= low:
        return 0.0
    v = (val - low) / (high - low)
    return float(max(0.0, min(1.0, v)))


def team_confidence(assignments: List[Assignment], meta_by_id: Dict[str, Dict[str, Any]]) -> float:
    sims = []
    vigor_vals = []
    covered = 0
    for a in assignments:
        if not a.candidates:
            continue
        top = a.candidates[0]
        sims.append(top.similarity)
        covered += 1 if top.similarity > 0 else 0
        emp = meta_by_id.get(top.employee_id)
        if emp:
            tr = emp.get("track_record", {}) or {}
            vigor = tr.get("custom_score")
            if vigor is None:
                vigor = (tr.get("h_index") or 0.0)
            vigor_vals.append(float(vigor))
    fit = float(np.mean(sims)) if sims else 0.0
    coverage = covered / max(1, len(assignments))
    if vigor_vals:
        vmin, vmax = min(vigor_vals), max(vigor_vals)
        span = (vmax - vmin) if (vmax - vmin) > 1e-9 else 1.0
        vigor = float(np.mean([_norm(v, vmin, vmin + span) for v in vigor_vals]))
    else:
        vigor = 0.0
    confidence = 0.5 * fit + 0.35 * vigor + 0.15 * coverage
    return float(confidence)
