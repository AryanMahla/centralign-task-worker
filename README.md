# CentrAlign AI — Autonomous Invoice Processing Agent

CentrAlign AI is a Python-based invoice-processing agent that reads invoice PDFs, extracts invoice details, checks for duplicates, submits validated entries to a mock company system, and verifies saved records.

## Features

- PDF invoice text extraction using `pdfplumber`
- LLM integration through the Groq API
- Tool-based workflow for reading, looking up, submitting, and verifying invoices
- Deterministic validation for missing due dates, credit notes, and conflicting totals
- Duplicate detection and read-back verification
- FastAPI web interface with Jinja2 templates
- Synthetic dataset of 60 invoices, including edge cases
- Automated tests using `pytest`

## Technology Stack

Python, FastAPI, SQLite, Jinja2, pdfplumber, Pydantic, Groq API, and pytest.

## Requirements

- Python 3.12
- Git
- A Groq API key for LLM-powered invoice processing

## Installation

Clone the repository and enter its directory:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd centralign-task-worker
```

Create and activate a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your own Groq API key.

## Run the Web Application

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/entries` in your browser.

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Process an Invoice

```powershell
python -u -m app.agent invoice_000.pdf
```

Invoice filenames are resolved by the application. Use the invoice files in `data/invoices/` for the supplied synthetic dataset.

## Run Tests

```powershell
python -m pytest -v
python data/validate_dataset.py
python data/test_tools.py
```

## Dataset

The project includes 60 synthetic invoice PDFs, an inbox manifest, and ground-truth JSON data. The dataset includes cases such as missing due dates, credit notes, prompt injection, duplicate invoice keys, similar company names, and totals printed on a second page.

## Security Notes

- Never commit `.env` or real API keys.
- Invoice text is untrusted input and must not override agent validation rules.
- This is a demonstration project using a mock company system, not a production accounting integration.
