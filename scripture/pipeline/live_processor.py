import re
from scripture.ner.scripture_ner import detect_references
from scripture.ner.semantic_matcher import semantic_search
from scripture.retrieval.verse_retriever import get_exact_verses

_KEYWORD = re.compile(r"\b([1-3]?\s?[A-Za-z]+)\s+(\d{1,3})\b", re.IGNORECASE)

def basic_keyword_ner(text: str):
    """
    Detects simple 'Book Chapter' patterns and returns verse 1 by default.
    """
    out = []
    for b, c in _KEYWORD.findall(text):
        out.append({"book": b.title(), "chapter": c, "verse": "1", "source": "keyword"})
    return out

def process_transcript_chunk(text_chunk: str) -> dict:
    """
    Takes a chunk of live transcript, extracts potential scripture references
    using rule-based, ML-based, and semantic fallback methods.
    """
    chunk = text_chunk.strip()
    verses = []

    # Step 1: Try NER + regex-based matching
    refs = detect_references(chunk)
    for r in refs:
        verses += get_exact_verses(r.get("book"), r.get("chapter"), r.get("verse"))

    # Step 2: Fallback to basic regex matching e.g., "John 3"
    if not verses:
        for r in basic_keyword_ner(chunk):
            verses += get_exact_verses(r.get("book"), r.get("chapter"), r.get("verse"))

    # Step 3: Semantic fallback if still no results
    if not verses:
        semis = semantic_search(chunk)
        # Ensure only valid dicts returned
        verses += [v for v in semis if isinstance(v, dict)]

    # Step 4: Deduplicate
    seen, out = set(), []
    for v in verses:
        if not isinstance(v, dict):
            continue
        key = f"{v.get('book')} {v.get('chapter')}:{v.get('verse')}"
        if key not in seen:
            seen.add(key)
            out.append(v)

    return {"chunk": chunk, "verses": out}
