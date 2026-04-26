import json
from pathlib import Path
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential


def _try_import_scholarly():
    try:
        from scholarly import scholarly  # type: ignore
        return scholarly
    except Exception as e:
        raise RuntimeError(
            "scholarly is not installed or failed to import. Install dependencies from backend/requirements.txt"
        ) from e


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def fetch_profile_by_id(scholar_id: str) -> Dict[str, Any]:
    scholarly = _try_import_scholarly()
    author = scholarly.search_author_id(scholar_id)
    author_filled = scholarly.fill(author, sections=["basics", "indices", "publications"])
    pubs = []
    for pub in (author_filled.get("publications") or [])[:50]:
        title = (pub.get("bib") or {}).get("title") or ""
        year = (pub.get("bib") or {}).get("pub_year") or None
        pubs.append({"title": title, "year": year})
    h_index = (author_filled.get("hindex") or 0) or 0
    citations = 0
    cites = author_filled.get("citedby")
    if isinstance(cites, int):
        citations = cites
    indices = author_filled.get("indices") or {}
    if not citations:
        citations = (indices.get("citedby") or 0) if isinstance(indices, dict) else 0
    return {"h_index": h_index, "citations": citations, "publications": pubs}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def search_author_id_by_name(name: str) -> str:
    scholarly = _try_import_scholarly()
    # search_author yields a generator of basic author dicts
    gen = scholarly.search_author(name)
    best = None
    try:
        for a in gen:
            affil = (a.get("affiliation") or "").lower()
            if "iit kanpur" in affil or "indian institute of technology kanpur" in affil:
                best = a
                break
            if best is None:
                best = a
    except Exception:
        pass
    if not best:
        raise RuntimeError(f"No author found for name: {name}")
    # scholarly stores 'scholar_id' in 'scholar_id' key in search results
    sid = best.get("scholar_id") or best.get("id")
    if not sid:
        # try to fill to obtain id
        filled = scholarly.fill(best, sections=["basics"]) or {}
        sid = filled.get("scholar_id") or filled.get("id")
    if not sid:
        raise RuntimeError(f"No scholar id for name: {name}")
    return sid


def build_skills_text(publications: List[Dict[str, Any]]) -> str:
    titles = [p.get("title") or "" for p in publications]
    titles = [t for t in titles if t]
    return "; ".join(titles[:100])


def update_employees_with_scholar(src_json: str, out_json: str):
    with open(src_json, "r", encoding="utf-8") as f:
        emps = json.load(f)
    updated = []
    for e in emps:
        sid = e.get("scholar_id")
        if not sid:
            # attempt to find by name
            try:
                sid = search_author_id_by_name(e.get("name") or "")
                e["scholar_id"] = sid
            except Exception:
                sid = None
        if not sid:
            updated.append(e)
            continue
        try:
            prof = fetch_profile_by_id(sid)
            tr = e.get("track_record") or {}
            tr.update({
                "h_index": prof.get("h_index") or tr.get("h_index") or 0,
                "citations": prof.get("citations") or tr.get("citations") or 0,
            })
            texts = [e.get("skills_text") or "", build_skills_text(prof.get("publications") or [])]
            e["skills_text"] = "; ".join([t for t in texts if t]).strip()
            e["track_record"] = tr
        except Exception as ex:
            # keep original if fetch fails
            pass
        updated.append(e)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
    print(f"Wrote updated employees to {out_json}")


def main():
    import argparse
    p = argparse.ArgumentParser(description="Fetch Google Scholar data and update employees JSON")
    p.add_argument("--src", required=True, help="Path to employees.json")
    p.add_argument("--out", required=True, help="Output JSON path for updated employees")
    args = p.parse_args()
    update_employees_with_scholar(args.src, args.out)


if __name__ == "__main__":
    main()
