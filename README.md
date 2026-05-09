# Assessment Content Operations Platform (ACOP)

> Automates creation, validation, and management of assessment dump sheets for SBA, PAT, and NIPUN workflows.

## 🧠 Overview

ACOP is a production-grade, full-stack internal platform that automates the entire assessment content operations pipeline — from question paper parsing to final Excel export. The system is **rule-based**, **deterministic**, **modular**, and **scalable**. No AI is used for validation logic.

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Tailwind CSS v4, React Router, React Hook Form |
| Backend | Python, FastAPI, Pandas, OpenPyXL |
| Parsing | pdfplumber, python-docx, PyMuPDF |
| Auth | JWT (python-jose) |
| Storage | Local filesystem (Google Drive in MVP v2) |

## 📦 Core Modules

1. **Question Paper Parser Engine** — Parses PDF/DOCX question papers, extracts questions, options, images, tables
2. **LO Mapping Parser Engine** — Parses LO mapping PDFs/Excel with auto-detection of column headers
3. **Mapping Resolver Engine** — Merges question data with LO mappings by Item ID
4. **Dump Sheet Generator** — Generates Topic Master, Assessment Master, and Question Master data
5. **Guardrail Validation Engine** — 13 rule types, all deterministic, config-driven
6. **Media Extraction Engine** — Extracts images/tables/audio from documents
7. **Media Mapping Engine** — Maps media files to questions using naming conventions
8. **Google Drive Upload Engine** — Stub for MVP v2
9. **Multi-language Content Engine** — Supports English, Assamese, Hindi
10. **Excel Export Engine** — Produces formatted workbooks with dropdowns, error highlighting

## 🚀 Quick Start

### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Default Login

- **Username:** `admin`
- **Password:** `admin123`

## 📄 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔄 Processing Pipeline

```
Upload Files → Parse Questions → Parse LO Mappings → Resolve Mappings
     → Generate Dump Sheet → Validate → Export Excel
```

## 📂 Project Structure

```
dump_sheet/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── api/routes/          # API endpoints
│   │   ├── engines/             # 10 processing engines
│   │   ├── blueprints/          # Sheet structure blueprints
│   │   ├── models/              # Pydantic schemas
│   │   ├── rules/               # Validation rules JSON
│   │   └── utils/               # File, naming utilities
│   ├── uploads/                 # Uploaded files
│   └── output/                  # Generated outputs
├── frontend/
│   ├── src/
│   │   ├── pages/               # Login, Dashboard, Upload, Validation, Media, Export
│   │   ├── components/          # Sidebar, shared components
│   │   └── services/            # API client
│   └── ...
└── README.md
```

## 🎯 MVP Roadmap

| Phase | Features | Status |
|-------|----------|--------|
| MVP v1 | Parsing, mapping, dump sheet, validation, media, export | ✅ Done |
| MVP v2 | Google Drive upload, multilingual mapping, advanced validations | ⏳ Planned |
| MVP v3 | AI-assisted extraction, auto translations, smart suggestions | ⏳ Planned |
