# scripture/management/commands/load_bible.py

from django.core.management.base import BaseCommand
import sqlite3
import os
import json

class Command(BaseCommand):
    help = "Load Bible JSON into SQLite FTS5 table."

    def handle(self, *args, **kwargs):
        db_path = os.path.join(os.getcwd(), "db.sqlite3")
        bible_path = os.path.join(os.getcwd(), "data", "bible_kjv.json")

        with open(bible_path, "r") as f:
            bible = json.load(f)

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS bible_fts
            USING fts5(book, chapter, verse, text);
        """)

        for book in bible["books"]:
            book_name = book["name"]
            for chapter in book["chapters"]:
                chapter_num = chapter["chapter"]
                for verse in chapter["verses"]:
                    verse_num = verse["verse"]
                    text = verse["text"]
                    c.execute("""
                        INSERT INTO bible_fts (book, chapter, verse, text)
                        VALUES (?, ?, ?, ?);
                    """, (book_name, str(chapter_num), str(verse_num), text))

        conn.commit()
        conn.close()
        self.stdout.write(self.style.SUCCESS("Bible successfully loaded into FTS5."))
