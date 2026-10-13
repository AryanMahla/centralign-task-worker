
import json
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent
INVOICE_DIR = ROOT / "invoices"


def main():
    inbox = json.loads((ROOT / "inbox.json").read_text(encoding="utf-8"))
    records = json.loads(
        (ROOT / "ground_truth.json").read_text(encoding="utf-8")
    )

    errors = []
    readable = 0
    page_counts = []

    if len(inbox) != 60:
        errors.append(f"Expected 60 inbox records; found {len(inbox)}.")

    if len(records) != 60:
        errors.append(f"Expected 60 ground-truth records; found {len(records)}.")

    for item in inbox:
        path = ROOT / item["file"]

        if not path.exists():
            errors.append(f"Missing PDF: {item['file']}")
            continue

        try:
            with pdfplumber.open(path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                page_counts.append(len(pdf.pages))

                if not text.strip():
                    errors.append(f"No extractable text: {item['file']}")
                    continue

                readable += 1

        except Exception as exc:
            errors.append(f"Could not read {item['file']}: {exc}")

    by_number = {record["invoice_no"]: record for record in records}

    checks = {
        "missing due date": any(r["due_date"] is None for r in records),
        "credit note": any(r["credit_note"] for r in records),
        "prompt injection": any(r["injection"] for r in records),
        "total on page two": any(r["page_two_total"] for r in records),
        "duplicate database key": any(
            r["company"] == "Bluepeak Logistics"
            and r["invoice_no"] == "BL-2026-001"
            for r in records
        ),
        "similar company names": all(
            name in {r["company"] for r in records}
            for name in [
                "Northwind Traders",
                "Northwind Trading Co.",
                "Northwind Logistics",
            ]
        ),
    }

    print(f"Inbox records: {len(inbox)}")
    print(f"Ground-truth records: {len(records)}")
    print(f"Readable PDFs: {readable}")
    print(f"PDFs with multiple pages: {sum(n > 1 for n in page_counts)}")

    print("\nEdge-case checks:")
    for label, passed in checks.items():
        print(f"  {'PASS' if passed else 'FAIL'} — {label}")
        if not passed:
            errors.append(f"Missing edge case: {label}")

    if errors:
        print("\nVALIDATION FAILED:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("\nVALIDATION PASSED")


if __name__ == "__main__":
    main()
