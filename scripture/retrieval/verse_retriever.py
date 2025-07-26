import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "db.sqlite3"
# one global connection
_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_cursor = _conn.cursor()


def get_exact_verses(book, chapter, verse):
    if "-" in verse:
        start, end = verse.split("-")
        _cursor.execute(
            "SELECT text FROM bible_fts WHERE book=? AND chapter=? AND verse BETWEEN ? AND ?",
            (book, chapter, start, end)
        )
    else:
        _cursor.execute(
            "SELECT text FROM bible_fts WHERE book=? AND chapter=? AND verse=?",
            (book, chapter, verse)
        )
    return [row[0] for row in _cursor.fetchall()]