# Dynamic Scripture Finder

## Overview
Detect Bible verse references in live sermons and display full passages with context automatically.

---

## Tech Stack
- **Backend:** Django REST Framework
- **NER Model:** Hugging Face `distilbert-base-uncased` fine-tuned for BOOK/CHAPTER/VERSE detection
- **Retrieval Engine:** SQLite FTS5 (embedded) or Elasticsearch for scale
- **Semantic Search:** Sentence-Transformers `all-mpnet-base-v2` + FAISS
- **Frontend:** React, TailwindCSS
- **Deployment:** Vercel (frontend), Railway.app (backend)

---

## Architecture
1. **Transcript Monitoring**
   - Ingest transcript segments via WebSocket.
   - Run hybrid detection: Regex → NER pipeline.

2. **Reference Parsing**
   - Regex for `Book Chapter:Verse` patterns.
   - ML: TokenClassification model outputs entity spans.
   - Confidence threshold: 0.7; fallback to regex.

3. **Passage Retrieval**
   - **Exact Match:** Query FTS5 index by book/chapter/verse range.
   - **Paraphrase Support:** Compute embedding of transcript snippet; FAISS kNN search.
   - Merge results, filter by score ≥ 0.75.

4. **UI Presentation**
   - Overlay component: slides in verse card with reference & text.
   - Collapsible `VerseHistory` panel for past citations.

5. **Logging & Analytics**
   - Log detected references with timestamps to PostgreSQL.
   - Generate usage reports (verses per service, popular books).

---

## Implementation Steps (2 Weeks)
| Day | Task                                            |
|-----|-------------------------------------------------|
| 1   | Prepare annotated transcripts; setup datasets.  |
| 2-3 | Fine-tune DistilBERT NER model (500 examples).  |
| 4   | Build regex fallback library for citations.     |
| 5   | Index Bible texts in SQLite FTS5; test queries. |
| 6   | Implement FAISS-based semantic search fallback. |
| 7   | Create Django endpoints: detect, retrieve.      |
| 8-9 | Develop React Overlay & VerseHistory components.|
| 10  | Integrate WebSocket transcript monitoring.      |
| 11  | Add logging; analytics dashboard prototype.    |
| 12-13 | Pilot test in live setting; refine thresholds.|
| 14  | Deployment to production; monitoring setup.     |

---

## Challenges & Mitigations
- **Missed References:** Increase regex patterns; retrain NER with more data.
- **False Positives:** Tune confidence; allow user confirmation.
- **Latency:** Load FTS index in memory; batch vector searches.
- **UI Clutter:** Throttle overlays; queue in history panel.

## APPROACH
# Dynamic Scripture Finder

## Overview
The Dynamic Scripture Finder feature automatically detects Bible verse references in live sermon transcripts and displays the full passages with context. It leverages a fine‑tuned NER model, regex fallback, and efficient retrieval to enrich the worship experience.

---

## Components & Responsibilities

| Component                    | Responsibility                                                                         |
|------------------------------|----------------------------------------------------------------------------------------|
| **`ner.py`**                 | ML-based NER (DistilBERT) + regex fallback; span alignment; disambiguation; caching; logging |
| **`train_ner.py`**           | Fine‑tunes `distilbert-base-uncased` on annotated scripture data, producing the NER model checkpoint |
| **Retrieval Service**        | Retrieves verse text from SQLite FTS5 (or Elasticsearch) and optionally via semantic search |
| **Django API (CBV/Serializer)** | Exposes `/api/scripture/detect-references/`, calls `detect_references()`, logs analytics, assembles response |
| **React Frontend**           | Streams transcript segments, consumes API, displays `<VerseOverlay>` & `<VerseHistory>`                        |

---

## Purpose of `train_ner.py`
- **Dataset Preparation:** Converts labeled CoNLL transcript data into token‑aligned training samples.
- **Model Fine‑Tuning:** Trains `distilbert-base-uncased` to recognize `BOOK`, `CHAPTER`, and `VERSE` entities with high precision/recall.
- **Evaluation:** Reports F1 and accuracy metrics on a validation set to ensure model quality.
- **Deployment Artifact:** Outputs a Hugging Face Hub repository (e.g., `your-username/distilbert-scripture-ner`) for production inference in `ner.py`.

Without running `train_ner.py`, `ner.py` would rely on the base pre‑trained model, which is not specialized for scripture citation patterns and would perform poorly.

---

## End‑to‑End Workflow

1. **Audio → Transcript**
   - Sermon audio is captured (WebRTC) and sent to an ASR service (Whisper).
   - Transcript segments (e.g., sentences) arrive at frontend or Django via WebSocket/HTTP.

2. **Reference Detection**
   - Django view (`DetectReferencesAPIView`) receives text segment.
   - Calls `detect_references(text)` in `ner.py`:
     - **ML Pass:** `get_ner_pipeline()` loads fine‑tuned NER; `reconstruct_spans()` groups spans; `disambiguate_book_name()` standardizes book.
     - **Regex Fallback:** `CITATION_REGEX` catches classic citations.
     - **Caching:** Results cached in Redis for repeat segments.
     - **Logging:** Each detection logged for analytics.
   - Returns a list of `{book, chapter, verse, confidence, source}` dicts.

3. **Passage Retrieval**
   - For each detected reference, Django calls `get_exact_verses(book, chapter, verse)`:
     - Queries SQLite FTS5 to fetch verse text and ±1 verse for context.
     - If no exact match and semantic search enabled, uses FAISS + Sentence-Transformers to find paraphrased passages.

4. **Response Assembly**
   - APIView combines reference metadata with retrieved text:
     ```json
     {"book":"John","chapter":"3","verse":"16","text":"For God so loved...","confidence":0.92,"source":"ml"}
     ```
   - Returns JSON: `{ "references": [ ... ] }`.

5. **Frontend Display**
   - React `<VerseOverlay>` slides in each passage in real time.
   - `<VerseHistory>` maintains a scrollable list of all citations during the service.

---

## Sample JSON Flow

**Request:**
```http
POST /api/scripture/detect-references/
Content-Type: application/json

{ "text": "Read John 3:16 and Genesis 1:1 today." }

**RESPONSE**

{
  "references": [
    {
      "book": "John",
      "chapter": "3",
      "verse": "16",
      "text": "For God so loved the world...",
      "confidence": 0.92,
      "source": "ml"
    },
    {
      "book": "Genesis",
      "chapter": "1",
      "verse": "1",
      "text": "In the beginning God created...",
      "confidence": 0.6,
      "source": "regex"
    }
  ]
}
