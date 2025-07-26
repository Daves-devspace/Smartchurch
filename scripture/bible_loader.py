# scripture/utils/bible_loader.py
import json
import os
import sqlite3

import re

def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text

def load_bible(filepath="data/bible_kjv.json"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} not found.")
    with open(filepath, "r") as f:
        return json.load(f)

def match_verses(transcript_text):
    db_path = os.path.join(os.getcwd(), "db.sqlite3")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    normalized = normalize_text(transcript_text)
    query = "SELECT book, chapter, verse, text FROM bible_fts WHERE text MATCH ? LIMIT 5"
    c.execute(query, (normalized,))
    results = c.fetchall()

    conn.close()
    return results
