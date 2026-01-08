# VendorAuditAI

AI-Powered Vendor Security Report Analyzer

## Overview

VendorAuditAI transforms manual SOC 2, SIG, HECVAT, and security report reviews from 6-8 hours to under 15 minutes. The platform leverages large language models with Retrieval-Augmented Generation (RAG) to extract controls, identify gaps against compliance frameworks (NIST 800-53, ISO 27001, CIS Controls, SOC 2 TSC), and provide auditor-grade citations with confidence scoring.

## Features

- **Automated Document Parsing** - Extract text, tables, and structure from PDFs and DOCX files
- **Multi-Framework Gap Analysis** - Compare against NIST 800-53, ISO 27001, SOC 2 TSC, CIS Controls
- **Confidence-Scored Findings** - Every finding includes a confidence score and page-specific citations
- **Natural Language Querying** - Ask questions across your entire vendor portfolio
- **Self-Hosted Option** - Full control over your data with on-premise deployment

## Tech Stack

### Backend
- Python 3.12
- FastAPI
- SQLAlchemy 2.0 + SQLite/PostgreSQL
- Celery + Redis (async tasks)
- LangChain + Claude API

### Frontend
- React 18 + TypeScript
- Vite
- Tailwind CSS + shadcn/ui
- TanStack Query + Zustand

### AI/ML
- Anthropic Claude API (analysis)
- OpenAI Embeddings (vector search)
- PyMuPDF (document parsing)

## Project Structure

```
VendorAuditAI/
├── backend/           # FastAPI application
│   ├── app/           # Application code
│   ├── alembic/       # Database migrations
│   └── tests/         # Backend tests
├── frontend/          # React application
│   ├── src/           # Source code
│   └── tests/         # Frontend tests
├── infrastructure/    # Docker & Kubernetes configs
├── data/              # Frameworks and sample data
├── docs/              # Documentation
└── .bmad/             # BMAD planning artifacts
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Git

### Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# Optional (defaults work for development)
DATABASE_URL=sqlite+aiosqlite:///./vendorauditai.db
```

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
ruff check .

# Frontend linting
cd frontend
npm run lint
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome. Please read the contributing guidelines before submitting PRs.
