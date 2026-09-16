import os
import sqlite3

from config import get_base_path


def get_database_path():
    return os.path.join(get_base_path(), "rutube_downloader.db")


def get_connection():
    return sqlite3.connect(get_database_path())


def init_database():
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT,
                file TEXT,
                date TEXT
            )
            """)

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


def save_history(item, file):
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO history (
                title,
                url,
                file,
                date
            )
            VALUES (?, ?, ?, datetime('now'))
            """,
            (item["title"], item["url"], file),
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


def clear_history():
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM history
            """)

        connection.commit()
