import hashlib
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class PdfTextResult:
    text: str
    pages: int
    chars: int
    sha256: str


def _normalize_text(s: str) -> str:
    s = s.replace('\ufb01', 'fi').replace('\ufb02', 'fl')
    # de-hyphenate common line breaks: e.g., algo-\n rithm -> algorithm
    s = re.sub(r"(\w+)-\n(\w+)", r"\1\2", s)
    # collapse line breaks within paragraphs but keep double newlines
    s = re.sub(r"([^\n])\n(?!\n)", r"\1 ", s)
    # collapse whitespace
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _extract_with_pymupdf(data: bytes) -> Optional[Dict]:
    try:
        import fitz  # PyMuPDF
    except Exception:
        return None
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception:
        return None
    texts = []
    for page in doc:
        # Use page.get_text("text") for simple text flow; "blocks" could be used for layout-aware extraction
        t = page.get_text("text") or ""
        texts.append(t)
    full = "\n\n".join(texts)
    return {"text": full, "pages": len(doc)}


def _extract_with_pdfminer(data: bytes) -> Optional[Dict]:
    try:
        from pdfminer.high_level import extract_text
    except Exception:
        return None
    try:
        text = extract_text(io.BytesIO(data)) or ""
        # pages count fallback unknown; leave as 0
        return {"text": text, "pages": 0}
    except Exception:
        return None


def extract_pdf_text(data: bytes) -> PdfTextResult:
    sha = hashlib.sha256(data).hexdigest()
    # try PyMuPDF first
    out = _extract_with_pymupdf(data)
    if out is None or not (out.get("text") or "").strip():
        # fallback to pdfminer
        out = _extract_with_pdfminer(data) or {"text": "", "pages": 0}
    text = _normalize_text(out.get("text") or "")
    return PdfTextResult(text=text, pages=int(out.get("pages") or 0), chars=len(text), sha256=sha)


def persist_cfp_text(cache_dir: Path, res: PdfTextResult, meta: Optional[Dict] = None) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    base = cache_dir / f"{res.sha256}"
    txt_path = base.with_suffix(".txt")
    json_path = base.with_suffix(".json")
    txt_path.write_text(res.text, encoding="utf-8")
    payload = {"pages": res.pages, "chars": res.chars, "sha256": res.sha256}
    if meta:
        payload.update(meta)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return txt_path
