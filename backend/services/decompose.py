import re
import uuid
from typing import List
import yake
from ..models.schemas import WorkElement

_key = yake.KeywordExtractor(lan="en", n=3, top=8)


def _split_paragraphs(text: str) -> List[str]:
    parts = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _split_bullets(text: str) -> List[str]:
    lines = [l.rstrip() for l in text.splitlines()]
    items, cur = [], []
    for l in lines:
        if re.match(r"^\s*([-*•]|(\d+[\.)]))\s+", l):
            if cur:
                items.append(" ".join(cur).strip())
                cur = []
            items.append(re.sub(r"^\s*([-*•]|(\d+[\.)]))\s+", "", l).strip())
        else:
            cur.append(l.strip())
    if cur:
        items.append(" ".join(cur).strip())
    return [i for i in items if i]


def decompose_cfp(text: str) -> List[WorkElement]:
    bullets = _split_bullets(text)
    chunks = bullets if len(bullets) >= 3 else _split_paragraphs(text)
    elements: List[WorkElement] = []
    for ch in chunks:
        phrases = [k for k, _ in _key.extract_keywords(ch)]
        elements.append(WorkElement(id=str(uuid.uuid4()), text=ch, keyphrases=phrases))
    return elements
