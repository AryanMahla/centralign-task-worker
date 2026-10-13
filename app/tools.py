
import json
import os
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pdfplumber

from app.db import get_connection, create_entry

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INVOICE_DIR = PROJECT_ROOT / "data" / "invoices"


def read_invoice(invoice_file: str) -> dict:
    """Read text from a PDF inside the approved invoice directory."""
    name = Path(invoice_file).name

    if name != invoice_file or not name.lower().endswith(".pdf"):
        return {"ok": False, "error": "Invalid invoice filename."}

    path = (INVOICE_DIR / name).resolve()

    if not path.is_relative_to(INVOICE_DIR.resolve()):
        return {"ok": False, "error": "Invoice path is not allowed."}

    if not path.is_file():
        return {"ok": False, "error": "Invoice PDF not found."}

    try:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]

        text = "\n\n".join(
            f"--- PAGE {index + 1} ---\n{page}"
            for index, page in enumerate(pages)
        )

        return {
            "ok": True,
            "filename": name,
            "page_count": len(pages),
            "text": text[:20000],
        }
    except Exception as exc:
        return {"ok": False, "error": f"Could not read PDF: {exc}"}


def list_inbox() -> dict:
    """Return invoice documents available for processing."""
    manifest = PROJECT_ROOT / "data" / "inbox.json"

    if not manifest.is_file():
        return {"ok": False, "error": "Inbox manifest not found."}

    try:
        items = json.loads(manifest.read_text(encoding="utf-8"))
        return {"ok": True, "documents": items}
    except (json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "error": f"Could not read inbox: {exc}"}


def lookup_entry(company: str, invoice_no: str) -> dict:
    """Check whether this company and invoice number already exist."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, company, invoice_no, amount, currency, due_date
            FROM entries
            WHERE company = ? AND invoice_no = ?
            """,
            (company.strip(), invoice_no.strip()),
        ).fetchone()

    return {
        "ok": True,
        "found": row is not None,
        "entry": dict(row) if row else None,
    }


def submit_entry(
    company: str,
    invoice_no: str,
    amount: str,
    currency: str,
    due_date: str | None,
) -> dict:
    """Create a record after basic validation."""
    company = company.strip()
    invoice_no = invoice_no.strip()
    currency = currency.strip().upper()

    if not company or not invoice_no:
        return {"ok": False, "error": "Company and invoice number are required."}

    if currency not in {"INR", "USD"}:
        return {"ok": False, "error": "Currency must be INR or USD."}

    try:
        value = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        return {"ok": False, "error": "Amount must be numeric."}

    if not value.is_finite() or value <= 0:
        return {"ok": False, "error": "Amount must be positive and finite."}

    if due_date is not None:
        try:
            date.fromisoformat(due_date)
        except ValueError:
            return {"ok": False, "error": "Due date must use YYYY-MM-DD."}

    try:
        entry_id = create_entry(
            company=company,
            invoice_no=invoice_no,
            amount=f"{value:.2f}",
            currency=currency,
            due_date=due_date,
        )
        return {"ok": True, "entry_id": entry_id}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def verify_entry(company: str, invoice_no: str) -> dict:
    """Read back the stored record for post-submission verification."""
    return lookup_entry(company, invoice_no)


TOOLS = {
    "list_inbox": list_inbox,
    "read_invoice": read_invoice,
    "lookup_entry": lookup_entry,
    "submit_entry": submit_entry,
    "verify_entry": verify_entry,
}
