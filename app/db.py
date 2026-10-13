
import os
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "inventory.db")))


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                invoice_no TEXT NOT NULL,
                amount TEXT NOT NULL,
                currency TEXT NOT NULL
                    CHECK (currency IN ('INR', 'USD')),
                due_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (company, invoice_no)
            )
            """
        )


def seed() -> None:
    starter_entries = [
        ("Bluepeak Logistics", "BL-2026-001", "12500.00", "INR", "2026-10-20"),
        ("Northwind Traders", "NT-2026-0001", "45200.00", "INR", "2026-10-25"),
        ("Contoso Supplies", "CS-2026-0042", "890.00", "USD", "2026-11-01"),
        ("Fabrikam Services", "FS-2026-0015", "27500.00", "INR", "2026-11-05"),
        ("Adventure Works", "AW-2026-0008", "1640.00", "USD", "2026-11-10"),
    ]

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO entries
                (company, invoice_no, amount, currency, due_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            starter_entries,
        )


def create_entry(
    company: str,
    invoice_no: str,
    amount: str,
    currency: str,
    due_date: str,
) -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO entries
                (company, invoice_no, amount, currency, due_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (company, invoice_no, amount, currency, due_date),
        )
        row = conn.execute(
            "SELECT * FROM entries WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)


def list_entries(company: str | None = None) -> list[dict[str, Any]]:
    with get_connection() as conn:
        if company:
            rows = conn.execute(
                """
                SELECT * FROM entries
                WHERE company = ? COLLATE NOCASE
                ORDER BY id DESC
                """,
                (company,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM entries ORDER BY id DESC"
            ).fetchall()

        return [dict(row) for row in rows]
