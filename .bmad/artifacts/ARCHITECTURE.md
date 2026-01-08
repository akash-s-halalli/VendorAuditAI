# Architecture Document: VendorAuditAI

**Date:** January 8, 2026
**Scale Level:** L4
**Related PRD:** [PRD.md](PRD.md)

---

## System Overview

VendorAuditAI is a full-stack application with a Python FastAPI backend, React TypeScript frontend, and AI/ML pipeline for document analysis. The system uses PostgreSQL with pgvector for data storage and vector search.

---

## High-Level Architecture

```
CLIENT LAYER
├── React Web App (TypeScript, Tailwind CSS)
├── Mobile PWA
└── API Clients

API GATEWAY
└── NGINX / Traefik (Rate Limiting, SSL, Load Balancing)

APPLICATION LAYER
└── FastAPI Backend
    ├── Auth Service
    ├── Documents Service
    ├── Analysis Service
    ├── Framework Service
    └── Reports Service

PROCESSING LAYER
├── Celery Workers (async tasks)
├── Redis Queue
├── MinIO Storage
└── AI/ML Pipeline
    ├── OCR/Extraction
    ├── Chunking Engine
    ├── Embedding Service
    ├── LLM Analysis
    └── Citation Mapper

DATA LAYER
└── PostgreSQL + pgvector
    ├── Users/Organizations
    ├── Documents/Vendors
    ├── Chunks/Embeddings
    ├── Controls/Mappings
    └── Findings/Audit

EXTERNAL SERVICES
├── Anthropic Claude API
├── OpenAI Embeddings
├── Azure Document Intelligence
└── NIST OSCAL
```

---

## Component Descriptions

| Component | Purpose | Technology |
|-----------|---------|------------|
| Web App | User interface | React 18 + TypeScript + Tailwind |
| API Gateway | Rate limiting, SSL, load balancing | NGINX / Traefik |
| FastAPI Backend | REST API, business logic, auth | Python 3.12 + FastAPI |
| Celery Workers | Async document processing | Celery + Redis |
| Document Parser | PDF/DOCX extraction | Azure Doc Intel / PyMuPDF |
| AI Pipeline | LLM analysis, RAG, mapping | LangChain + Claude API |
| PostgreSQL | Primary database + vectors | PostgreSQL 16 + pgvector |
| MinIO | S3-compatible object storage | MinIO |
| Redis | Job queue, caching | Redis 7 |

---

## Technology Stack

### Backend
- Python 3.12
- FastAPI 0.109+
- SQLAlchemy 2.0 (async)
- Pydantic 2.5+
- Alembic (migrations)

### Frontend
- React 18
- TypeScript 5.3
- Vite 5
- Tailwind CSS 3.4
- shadcn/ui
- TanStack Query
- Zustand

### AI/ML
- Anthropic Claude API (claude-sonnet-4-20250514)
- OpenAI text-embedding-3-large
- LangChain 0.1+

### Database
- PostgreSQL 16
- pgvector 0.6

### Infrastructure
- Docker + Docker Compose
- Kubernetes (production)
- MinIO (object storage)

---

## Data Flow

1. **Upload**: User uploads SOC 2/SIG/HECVAT document
2. **Parse**: Document Intelligence extracts text, tables, structure
3. **Chunk**: Document split into semantic chunks with metadata
4. **Embed**: OpenAI creates vector embeddings
5. **Store**: Chunks + vectors stored in PostgreSQL/pgvector
6. **Query**: User queries trigger RAG retrieval
7. **LLM+RAG**: Claude analyzes retrieved chunks against frameworks
8. **Cite**: System maps findings to specific pages/paragraphs
9. **Return**: Results displayed with confidence scores and citations

---

## Security Architecture

### Authentication
- JWT tokens with refresh mechanism
- Optional MFA via TOTP
- API key authentication for programmatic access

### Authorization
- Role-based access control (Admin, Analyst, Viewer)
- Organization-level data isolation
- Resource-level permissions

### Data Protection
- TLS 1.3 for all connections
- AES-256 encryption at rest
- Secrets management via environment variables

---

## Scalability

### Target Metrics
- Throughput: 100+ concurrent document analyses
- Latency: < 2s for API responses
- Storage: 10TB+ document storage

### Scaling Strategy
- Horizontal scaling via Kubernetes
- Read replicas for PostgreSQL
- Distributed Celery workers
- CDN for static assets

---

## Development Environment

### Without Docker (Current)
- SQLite for database (development only)
- Local filesystem for storage
- Synchronous task processing

### With Docker (Production)
- PostgreSQL + pgvector
- MinIO for S3-compatible storage
- Redis + Celery for async tasks
