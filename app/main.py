
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sqlite3

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.db import create_entry, init_db, list_entries, seed
from app.failures import before_submit, submit_button_text

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="CentrAlign Mock Company System")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed()


@app.get("/", response_class=HTMLResponse)
def home():
    return RedirectResponse(url="/entries", status_code=303)


@app.get("/entries", response_class=HTMLResponse)
def entries_page(request: Request, message: str = "", error: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="entries_list.html",
        context={
            "entries": list_entries(),
            "message": message,
            "error": error,
        },
    )


@app.get("/entries/new", response_class=HTMLResponse)
def new_entry_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="entry_form.html",
        context={
            "error": "",
            "values": {},
            "submit_label": submit_button_text(),
        },
    )


@app.post("/entries/new", response_class=HTMLResponse)
def create_entry_page(
    request: Request,
    company: str = Form(...),
    invoice_no: str = Form(...),
    amount: str = Form(...),
    currency: str = Form(...),
    due_date: str = Form(...),
):
    values = {
        "company": company.strip(),
        "invoice_no": invoice_no.strip(),
        "amount": amount.strip(),
        "currency": currency.strip(),
        "due_date": due_date.strip(),
    }

    error = ""

    if not values["company"] or not values["invoice_no"]:
        error = "Company and invoice number are required."

    elif values["currency"] not in {"INR", "USD"}:
        error = "Currency must be INR or USD."

    else:
        try:
            amount_value = Decimal(values["amount"])
            if not amount_value.is_finite() or amount_value <= 0:
                error = "Amount must be a positive number."
            else:
                values["amount"] = format(amount_value, ".2f")
        except InvalidOperation:
            error = "Enter a valid monetary amount."

    if not error:
        try:
            date.fromisoformat(values["due_date"])
        except ValueError:
            error = "Enter a valid due date in YYYY-MM-DD format."

    if error:
        return templates.TemplateResponse(
            request=request,
            name="entry_form.html",
            context={
                "error": error,
                "values": values,
                "submit_label": submit_button_text(),
            },
            status_code=400,
        )

    try:
        before_submit()
        create_entry(**values)
    except RuntimeError as exc:
        if str(exc) == "SIMULATED_SERVER_ERROR_ONCE":
            return templates.TemplateResponse(
                request=request,
                name="entry_form.html",
                context={
                    "error": "Simulated server error. No entry was inserted.",
                    "values": values,
                    "submit_label": submit_button_text(),
                },
                status_code=500,
            )
        raise
    except sqlite3.IntegrityError:
        return templates.TemplateResponse(
            request=request,
            name="entry_form.html",
            context={
                "error": "Duplicate invoice: this company and invoice number already exist.",
                "values": values,
                "submit_label": submit_button_text(),
            },
            status_code=409,
        )

    return RedirectResponse(
        url="/entries?message=Invoice+saved+successfully",
        status_code=303,
    )


@app.get("/api/entries")
def api_entries(company: str | None = None):
    return list_entries(company)

