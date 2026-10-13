
from app.tools import (
    list_inbox,
    read_invoice,
    lookup_entry,
    verify_entry,
)


def main():
    inbox = list_inbox()
    assert inbox["ok"], inbox
    assert len(inbox["documents"]) == 60
    print("PASS: inbox contains 60 documents")

    first_file = inbox["documents"][0]["file"].split("/")[-1]
    invoice = read_invoice(first_file)
    assert invoice["ok"], invoice
    assert invoice["text"].strip()
    print(f"PASS: read {first_file} ({invoice['page_count']} page(s))")

    unsafe = read_invoice("..\\inventory.db")
    assert not unsafe["ok"]
    print("PASS: rejects unsafe filenames")

    existing = lookup_entry("Bluepeak Logistics", "BL-2026-001")
    assert existing["ok"] and existing["found"], existing
    print("PASS: finds existing database entry")

    verified = verify_entry("Bluepeak Logistics", "BL-2026-001")
    assert verified["found"]
    print("PASS: verification reads back stored entry")

    print("\nTOOL TESTS PASSED")


if __name__ == "__main__":
    main()
