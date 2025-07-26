# scripture/management/commands/index_verses.py
import sqlite3, os, json
import faiss
import numpy as np
from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer

DB = os.path.join(os.getcwd(), "db.sqlite3")
EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_PATH = "verse_index.faiss"
META_PATH  = "verses_meta.json"

class Command(BaseCommand):
    help = "Build FAISS index over all Bible verses."

    def handle(self, *args, **opts):
        # 1) load verses
        conn = sqlite3.connect(DB)
        c    = conn.cursor()
        c.execute("SELECT rowid, book, chapter, verse, text FROM bible_fts")
        rows = c.fetchall()
        conn.close()

        # 2) embed
        model = SentenceTransformer(EMB_MODEL)
        texts = [r[4] for r in rows]
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

        # 3) build index
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(embeddings)
        index.add(embeddings)
        faiss.write_index(index, INDEX_PATH)

        # 4) store metadata
        meta = [
            {"rowid": r[0], "book": r[1], "chapter": r[2], "verse": r[3], "text": r[4]}
            for r in rows
        ]
        with open(META_PATH, "w") as f:
            json.dump(meta, f)

        self.stdout.write(self.style.SUCCESS(f"Indexed {len(rows)} verses."))
