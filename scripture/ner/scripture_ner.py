# scripture/ner/scripture_ner.py

import os
import re
import hashlib
import logging
from functools import lru_cache
from typing import List

from transformers import pipeline
from django.core.cache import cache
from dotenv import load_dotenv

# ─── Environment & Logging ─────────────────────────────────────────────────────
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = os.getenv("HF_MODEL_ID", "Liorixdigital/distilbert-scripture-ner")
if HF_TOKEN:
    from huggingface_hub import login
    login(token=HF_TOKEN)

logger = logging.getLogger(__name__)

# ─── Regex for fallback ─────────────────────────────────────────────────────────
CITATION_REGEX = re.compile(
    r"\b(?:book\s+)?([1-3]?\s?[A-Za-z]+)\s+(\d{1,3})[:.\-–]+(?:verse\s*)?(\d{1,3})\b",
    re.IGNORECASE
)

# ─── Caching settings ───────────────────────────────────────────────────────────
CACHE_TIMEOUT = 600
ML_CACHE_PREFIX = "ml_refs:"

# ─── ML pipeline loader ─────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _ml_pipeline():
    return pipeline(
        "token-classification",
        model=MODEL_ID,
        tokenizer=MODEL_ID,
        aggregation_strategy="simple"
    )

# ─── ML extraction with caching ────────────────────────────────────────────────
@lru_cache(maxsize=100)
def _extract_ml(text: str) -> List[dict]:
    key = ML_CACHE_PREFIX + hashlib.md5(text.encode()).hexdigest()
    cached = cache.get(key)
    if cached:
        return cached

    entities = _ml_pipeline()(text)
    refs = []
    buf = {}
    for ent in entities:
        grp = ent["entity_group"]
        word = ent["word"]
        score = ent["score"]

        if grp == "BOOK":
            buf.update(book=word, confidence=score)
        elif grp == "CHAPTER":
            buf["chapter"] = word
        elif grp == "VERSE":
            buf["verse"] = word

        if all(k in buf for k in ("book", "chapter", "verse")):
            # <— FIXED: quote "source"
            refs.append({**buf, "source": "ml"})
            buf = {}

    cache.set(key, refs, CACHE_TIMEOUT)
    return refs

# ─── Regex fallback ─────────────────────────────────────────────────────────────
def _extract_regex(text: str) -> List[dict]:
    out = []
    for book, chap, verse in CITATION_REGEX.findall(text):
        out.append({
            "book": book.title(),
            "chapter": chap,
            "verse": verse,
            "source": "regex"
        })
    return out

# ─── Public API ────────────────────────────────────────────────────────────────
def detect_references(text: str) -> List[dict]:
    logger.debug(f"Detecting refs in: {text!r}")
    ml_refs = _extract_ml(text)
    regex_refs = _extract_regex(text)
    # combine and dedupe by "Book Chapter:Verse"
    combined = { f"{r['book']} {r['chapter']}:{r['verse']}": r
                 for r in (ml_refs + regex_refs) }
    result = list(combined.values())
    logger.debug(f"Detected references: {result}")
    return result
