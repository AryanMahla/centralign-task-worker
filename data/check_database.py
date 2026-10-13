
from app.db import get_connection

conn = get_connection()

try:
    rows = conn.execute(
        """
        SELECT id, company, invoice_no, amount, currency, due_date, created_at
        FROM entries
        ORDER BY id
        """
    ).fetchall()

    print(f"Total entries: {len(rows)}\n")

    for row in rows:
        print(dict(row))

finally:
    conn.close()
