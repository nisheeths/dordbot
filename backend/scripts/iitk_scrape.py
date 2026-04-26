import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

import requests
from bs4 import BeautifulSoup
import yake


def load_employees(src: str) -> List[Dict[str, Any]]:
    with open(src, "r", encoding="utf-8") as f:
        return json.load(f)


def save_employees(out: str, emps: List[Dict[str, Any]]):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(emps, f, ensure_ascii=False, indent=2)


def fetch_html(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def clean_anchor_text(txt: str) -> str:
    # Remove username in parentheses and room/phone icons remnants
    t = re.sub(r"\([^\)]*\)", " ", txt)  # remove (username)
    t = re.sub(r"\uE083|\uE0A7|\uE0BE|\uE0C8|\uE0B0|\uE0B1|\uE0B2", " ", t)  # stray icons if any
    t = re.sub(r"\+?\d[\d\-()/\s]+", " ", t)  # phone-like
    t = re.sub(r"\b(RM|KD|C3i)[\-\w]*\b", " ", t, flags=re.IGNORECASE)  # room labels
    t = re.sub(r"\b(Professor|Associate Professor|Assistant Professor|Chair|Fellow|New Faculty Fellow|Young Faculty Fellow)\b", " ", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def extract_keyphrases(text: str, topk: int = 12) -> List[str]:
    kw = yake.KeywordExtractor(lan="en", n=3, top=topk)
    phrases = [k for k, _ in kw.extract_keywords(text)]
    # de-duplicate and keep order
    seen = set()
    out = []
    for p in phrases:
        p2 = p.strip().strip(',.;:').lower()
        if p2 and p2 not in seen:
            seen.add(p2)
            out.append(p2)
    return out


def build_lookup(anchors: List[Dict[str, str]]):
    # map of normalized name substring -> list of anchors
    return anchors


def scrape_faculty(url: str) -> List[Dict[str, str]]:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    anchors = []
    for a in soup.find_all('a'):
        text = a.get_text(strip=True)
        href = a.get('href') or ''
        if not text:
            continue
        anchors.append({"text": text, "href": href})
    return anchors


def enrich_from_page(emps: List[Dict[str, Any]], anchors: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    # try to find an anchor whose text contains the full name (case-insensitive)
    # then extract keyphrases from the cleaned text, set as skills_text, and set homepage if looks like a personal page
    for e in emps:
        name_norm = normalize_name(e.get("name") or "")
        found: Optional[Dict[str, str]] = None
        for a in anchors:
            if name_norm and name_norm in normalize_name(a["text"]):
                found = a
                break
        if not found:
            # fallback: try last name and first name tokens separately
            parts = [p for p in name_norm.split() if p]
            if len(parts) >= 2:
                first, last = parts[0], parts[-1]
                for a in anchors:
                    t = normalize_name(a["text"])
                    if first in t and last in t:
                        found = a
                        break
        if found:
            raw = clean_anchor_text(found["text"])
            phrases = extract_keyphrases(raw, topk=15)
            if phrases:
                e["skills_text"] = "; ".join(phrases)
            href = found.get("href") or ""
            if href and not href.startswith('#'):
                e["homepage"] = href
    return emps


def main():
    import argparse
    p = argparse.ArgumentParser(description="Scrape IITK CSE Faculty page and fill skills_text via keyphrases")
    p.add_argument("--src", required=True, help="Input employees JSON with names")
    p.add_argument("--out", required=True, help="Output employees JSON path")
    p.add_argument("--url", default="https://cse.iitk.ac.in/pages/Faculty.html", help="Faculty page URL")
    args = p.parse_args()

    emps = load_employees(args.src)
    anchors = scrape_faculty(args.url)
    enriched = enrich_from_page(emps, anchors)
    save_employees(args.out, enriched)
    print(f"Wrote enriched employees with skills_text to {args.out}")


if __name__ == "__main__":
    main()
