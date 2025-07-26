from scripture.transcription.whisper_runner import transcribe, transcribe_live
from scripture.summarization.summarizer import summarize
from scripture.ner.scripture_ner import detect_references
from scripture.retrieval.verse_retriever import get_exact_verses

def run_pipeline(use_summary: bool = False) -> dict:
    """
    Live-stream pipeline: listen on microphone, transcribe, detect scripture,
    and optionally summarize.

    Returns:
        dict: {
            "transcript": Full live transcript string,
            "summary": Summary text if requested, else None,
            "verses": List of verse texts retrieved from DB
        }
    """
    # 1) Continuous transcription from mic
    print("[INFO] Starting live transcription from microphone...")
    text = transcribe_live()  # blocks until buffer is processed
    print(f"[DEBUG] Live Transcript: {text}")

    # 2) Optionally summarize
    summary = None
    if use_summary and len(text.split()) >= 10:
        summary = summarize(text)
        print(f"[DEBUG] Summary: {summary}")

    # 3) Scripture NER
    mentions = detect_references(text)
    print(f"[DEBUG] Scripture Mentions: {mentions}")

    # 4) Verse retrieval
    verses = []
    for m in mentions:
        verses.extend(get_exact_verses(m['book'], m['chapter'], m['verse']))
    print(f"[DEBUG] Retrieved Verses: {verses}")

    return {
        "transcript": text,
        "summary": summary,
        "verses": verses
    }
    
# scripture/pipeline/runner.py
from scripture.pipeline.live_processor import process_transcript_chunk

def run_pipeline(transcript_text: str) -> dict:
    return process_transcript_chunk(transcript_text)
