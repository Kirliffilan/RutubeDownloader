import os
import sqlite3

from config import get_base_path


def get_database_path():
    return os.path.join(get_base_path(), "rutube_downloader.db")


def get_connection():
    return sqlite3.connect(get_database_path())


def add_column(cursor, table, column, data_type):
    cursor.execute(f"PRAGMA table_info({table})")

    columns = [row[1] for row in cursor.fetchall()]

    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {data_type}")


def init_database():
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT,
                file TEXT,
                date TEXT,
                type TEXT,
                season INTEGER,
                episode INTEGER,
                size INTEGER,
                quality TEXT
            )
        """)

        add_column(cursor, "history", "type", "TEXT")
        add_column(cursor, "history", "season", "INTEGER")
        add_column(cursor, "history", "episode", "INTEGER")
        add_column(cursor, "history", "size", "INTEGER")
        add_column(cursor, "history", "quality", "TEXT")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error TEXT,
                date TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        connection.commit()


def save_history(item, file, settings=None):
    with get_connection() as connection:
        cursor = connection.cursor()

        video_type = "serial" if item.get("season") else "video"
        size = 0
        if os.path.exists(file):
            size = os.path.getsize(file)

        quality = None
        if settings:
            quality = settings.get("quality")

        cursor.execute(
            """
            INSERT INTO history (
                title,
                url,
                file,
                date,
                type,
                season,
                episode,
                size,
                quality
            )
            VALUES (?, ?, ?, datetime('now'), ?, ?, ?, ?, ?)
            """,
            (
                item.get("title"),
                item.get("url"),
                file,
                video_type,
                item.get("season"),
                item.get("episode"),
                size,
                quality,
            ),
        )
        connection.commit()


def log_error(error):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO errors (
                error,
                date
            )
            VALUES (?, datetime('now'))
            """,
            (error,),
        )
        connection.commit()


def get_history():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT *
            FROM history
            ORDER BY id DESC
        """)

        return cursor.fetchall()


def delete_history(history_id):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT file
            FROM history
            WHERE id=?
            """,
            (history_id,),
        )
        row = cursor.fetchone()
        if row and row[0]:
            try:
                if os.path.exists(row[0]):
                    os.remove(row[0])
            except Exception:
                pass
        cursor.execute(
            """
            DELETE FROM history
            WHERE id=?
            """,
            (history_id,),
        )
        connection.commit()


def clear_history():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT file
            FROM history
            """)
        files = cursor.fetchall()
        for row in files:
            file = row[0]
            if file:
                try:
                    if os.path.exists(file):
                        os.remove(file)
                except Exception:
                    pass
        cursor.execute("""
            DELETE FROM history
            """)
        connection.commit()
