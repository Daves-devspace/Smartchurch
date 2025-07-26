# scripture/speech_utils.py

import os
from functools import lru_cache

import librosa
from transformers import pipeline
from .ner.scripture_ner import detect_references

# 1) One Whisper pipeline for multilingual ASR + translation:
#    - We specify `task="automatic-speech-recognition"` once
#    - We switch between transcription vs. translation using generate_kwargs
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small",
    trust_remote_code=True,
)

# 2) Summarizer (optional)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def detect_language(text: str) -> str:
    kisw_words = {"yesu", "mungu", "mwokozi"}
    tokens = {w.lower().strip(".,") for w in text.split()}
    return "sw" if kisw_words.intersection(tokens) else "en"

def process_audio_file(wav_path: str) -> dict:
    """
    1) Resample to 16 kHz
    2) Whisper-transcribe (source language)
    3) If non-English, Whisper-translate → English
    4) Scripture NER
    5) Summarize
    """
    # 1) load + resample
    audio, sr = librosa.load(wav_path, sr=16_000)
    tmp = "/tmp/audio.wav"
    librosa.output.write_wav(tmp, audio, sr)

    # 2) Transcribe in original language
    result = asr_pipeline(tmp)
    transcript = result["text"].strip()
    lang = detect_language(transcript)

    # 3) If not English, re-run Whisper in translate mode
    if lang != "en":
        result = asr_pipeline(
            tmp,
            generate_kwargs={"task": "translate"}
        )
        transcript = result["text"].strip()

    # 4) Scripture NER on the final English text
    refs = detect_references(transcript)

    # 5) Summarize (first 1024 tokens)
    summary = summarizer(transcript[:1024])[0]["summary_text"]

    return {
        "text": transcript,
        "references": refs,
        "summary": summary
    }
