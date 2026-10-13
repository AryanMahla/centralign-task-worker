
from app.db import get_connection

TEST_ENTRIES = [
    ("Test Company", "TEST-001"),
    ("Northwind Traders", "INV-2026-0000"),
]

conn = get_connection()

try:
    # Show the exact records that will be deleted.
    for company, invoice_no in TEST_ENTRIES:
        row = conn.execute(
            """
            SELECT id, company, invoice_no, amount, currency
            FROM entries
            WHERE company = ? AND invoice_no = ?
            """,
            (company, invoice_no),
        ).fetchone()

        print("Found:", dict(row) if row else "No matching record")

    confirmation = input(
        "\nType DELETE to remove only these two test entries: "
    )

    if confirmation != "DELETE":
        print("Cancelled. No records deleted.")
    else:
        deleted = 0

        for company, invoice_no in TEST_ENTRIES:
            cursor = conn.execute(
                """
                DELETE FROM entries
                WHERE company = ? AND invoice_no = ?
                """,
                (company, invoice_no),
            )
            deleted += cursor.rowcount

        conn.commit()
        print(f"Deleted {deleted} matching record(s).")

finally:
    conn.close()
