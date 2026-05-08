# Contributing to VendorAuditAI

Thank you for your interest in contributing to VendorAuditAI! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Branch Naming Convention](#branch-naming-convention)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and professional environment. We expect contributors to:

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the project
- Show empathy towards other community members

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Set up** your development environment
4. **Create** a feature branch
5. **Make** your changes
6. **Test** thoroughly
7. **Submit** a pull request

## Development Setup

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 20+ | Frontend build |
| PostgreSQL | 16+ | Production database |
| Git | 2.40+ | Version control |

### API Keys Required

- **Google Gemini API Key** - For Gemini AI integration (get free key: https://aistudio.google.com/apikey)
- **OpenAI API Key** - For embeddings generation

### Backend Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/VendorAuditAI.git
cd VendorAuditAI

# Create and activate virtual environment
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Required: DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, GEMINI_API_KEY, OPENAI_API_KEY

# Run database migrations (if using PostgreSQL)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# In a new terminal, from repository root
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Start development server
npm run dev
```

### Verify Setup

- Backend: http://localhost:8000/docs (Swagger UI)
- Frontend: http://localhost:5173

## Code Style Guidelines

### Python (Backend)

We follow PEP 8 with the following specifics:

```python
# Use type hints for all function parameters and returns
def process_document(document_id: str, options: ProcessingOptions) -> AnalysisResult:
    """Process a document and return analysis results.

    Args:
        document_id: Unique identifier for the document
        options: Processing configuration options

    Returns:
        AnalysisResult containing findings and metadata
    """
    pass

# Use Pydantic models for data validation
class VendorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    tier: VendorTier
    description: Optional[str] = None

# Async functions for database operations
async def get_vendor(db: AsyncSession, vendor_id: str) -> Vendor | None:
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    return result.scalar_one_or_none()
```

**Tools:**
- `black` - Code formatting
- `ruff` - Linting
- `mypy` - Type checking

### TypeScript (Frontend)

```typescript
// Use TypeScript strict mode
// Prefer interfaces over types for objects
interface VendorCardProps {
  vendor: Vendor;
  onSelect: (id: string) => void;
  isSelected?: boolean;
}

// Use functional components with explicit return types
export function VendorCard({ vendor, onSelect, isSelected = false }: VendorCardProps): JSX.Element {
  // Component implementation
}

// Use descriptive variable names
const isLoadingVendors = vendorsQuery.isLoading;
const hasVendorError = vendorsQuery.isError;
```

**Tools:**
- ESLint configuration in repository
- Prettier for formatting
- TypeScript strict mode

### CSS/Styling

- Use TailwindCSS utility classes
- Follow the Digital Obsidian theme
- Avoid inline styles except for dynamic values
- Use CSS custom properties for theme values

## Branch Naming Convention

```
<type>/<short-description>

Examples:
feature/add-vendor-export
fix/auth-token-expiry
hotfix/critical-db-connection
docs/update-api-reference
refactor/optimize-document-processing
test/add-vendor-service-tests
```

| Type | Use Case |
|------|----------|
| `feature/` | New features or enhancements |
| `fix/` | Bug fixes |
| `hotfix/` | Critical production fixes |
| `docs/` | Documentation updates |
| `refactor/` | Code refactoring |
| `test/` | Test additions or updates |
| `chore/` | Build, CI, or tooling changes |

## Commit Message Format

```
TYPE: Brief description (max 72 chars)

[Optional body with more details]

[Optional footer with references]
```

### Types

| Type | Description |
|------|-------------|
| `FEAT` | New feature |
| `FIX` | Bug fix |
| `DOCS` | Documentation |
| `REFACTOR` | Code refactoring |
| `TEST` | Test updates |
| `CHORE` | Build/tooling |
| `SECURITY` | Security fixes |
| `PERF` | Performance improvements |

### Examples

```
FEAT: Add vendor risk score calculation

Implements weighted risk scoring based on:
- Number of critical findings
- Compliance coverage percentage
- Document recency

Closes #123
```

```
FIX: Resolve JWT token refresh race condition

Token refresh now uses mutex to prevent concurrent
refresh requests from invalidating each other.
```

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**
   ```bash
   # Backend
   cd backend
   python -m pytest tests/ -v

   # Frontend
   cd frontend
   npm run lint
   npm run build
   ```

2. **Update documentation** if you changed APIs or features

3. **Add/update tests** for new functionality

### PR Requirements

- [ ] Descriptive title following commit message format
- [ ] Detailed description of changes
- [ ] Link to related issue (if applicable)
- [ ] Tests pass locally
- [ ] No linting errors
- [ ] Documentation updated (if needed)
- [ ] Screenshots for UI changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested the changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
```

## Testing Requirements

### Backend Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_api/test_vendors.py -v

# Run specific test
python -m pytest tests/test_api/test_vendors.py::test_create_vendor -v
```

### Frontend Tests

```bash
# Lint check
npm run lint

# Type check
npx tsc --noEmit

# Build test
npm run build
```

### Test Guidelines

- Write tests for new features
- Maintain or improve code coverage
- Use descriptive test names
- Test edge cases and error scenarios

## Documentation

### When to Update Docs

- New API endpoints
- Changed request/response schemas
- New features or capabilities
- Configuration changes
- Breaking changes

### Documentation Locations

| Location | Content |
|----------|---------|
| `README.md` | Project overview, quick start |
| `docs/` | Detailed documentation |
| Code docstrings | API documentation |
| Swagger/ReDoc | Auto-generated API docs |

## Questions?

- Open a [GitHub Discussion](https://github.com/MikeDominic92/VendorAuditAI/discussions)
- Check existing [issues](https://github.com/MikeDominic92/VendorAuditAI/issues)
- Review [documentation](https://vendorauditai-production.up.railway.app/docs)

---

Thank you for contributing to VendorAuditAI!
