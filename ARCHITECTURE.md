# UIBench Architecture

## Overview

UIBench is split into three primary layers:

- **Frontend** — SvelteKit + Vite + Tailwind SPA
- **Backend** — FastAPI REST API
- **Core Engine** — Python analysis engine with modular analyzers

These layers are orchestrated via Docker Compose.

```
┌─────────────────────────────────────────────────────────────┐
│                        docker-compose.yml                    │
├──────────────┬──────────────┬───────────────────────────────┤
│   Frontend   │   Backend    │         Core Engine           │
│  SvelteKit   │  FastAPI     │   Python Analysis Engine      │
│  Vite        │  MongoDB     │   Playwright / spaCy / ZAP    │
│  Tailwind    │  JWT Auth    │   Modular Analyzer Registry   │
└──────────────┴──────────────┴───────────────────────────────┘
```

## Frontend (`/frontend`)

- Framework: SvelteKit
- Styling: Tailwind CSS
- HTTP: Axios
- Routing: SvelteKit file-based routing
- Auth: JWT stored in React-like context state
- Charts: Recharts
- QR: jsQR

Key environment variable:
- `VITE_API_URL` — backend API base URL

## Backend (`/backend`)

- Framework: FastAPI
- Database: MongoDB (Motor async driver)
- Auth: JWT with role-based guards
- Structure: `app/` package with `routes/`, `services/`, `models/`, `middleware/`

Key endpoints:
- `POST /evaluate` — single URL analysis
- `POST /evaluate/pdf` — PDF report generation
- `POST /evaluate/batch` — batch URL analysis
- `GET /health` — health check
- `GET /metrics` — Prometheus metrics

## Core Engine (`/core`)

The analysis engine uses a registry-based architecture with lazy-loaded analyzers.

### Analyzer Registry

`core/analyzers/registry.py` — `AnalyzerRegistry` discovers and composes analyzers.

### Analyzer ABCs

`core/analyzers/base.py` defines role-specific interfaces:

- `Analyzer` — static analysis base
- `BrowserAnalyzer` — browser-backed analysis (Playwright/axe)
- `Persistable` — analyzers that can store results

### Output Contract

All analyzers return `AnalysisResponse` containing `AnalyzerResult` items.

```python
@dataclass
class AnalyzerResult:
    name: str
    score: float
    status: Literal["passed", "warning", "failed", "skipped"]
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
```

### Analysis Context

`core/models/context.py` — `AnalysisContext` decouples analyzers from page-fetching logic.

```python
@dataclass
class AnalysisContext:
    url: str
    html: Optional[str] = None
    soup: Optional[Any] = None
    page: Optional[Any] = None
    body_text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Modular Analyzers

Static analyzers live under `core/analyzers/` by category:

- `seo/` — `MetaTagsAnalyzer`, `HeadingsAnalyzer`, `ImageSEOAnalyzer`
- `accessibility/` — `AltTextAnalyzer`, `AccessibilityHeadingsAnalyzer`
- `performance/` — `PageSizeAnalyzer`
- `design_system/` — `CSSVariablesAnalyzer`
- `nlp/` — `ReadabilityAnalyzer`, `SentimentAnalyzer`

Browser analyzers live under `core/analyzers/browser/` and are opt-in:

- `AxeAccessibilityAnalyzer`
- `BrowserPerformanceAnalyzer`

### Evaluation Service

`core/services/evaluation_service.py` — `EvaluationService` uses the registry to run available analyzers concurrently and aggregate results into a single `AnalysisResponse`.

### Page Evaluators

- `core/evaluators/page_evaluator.py` — `PageEvaluator` (legacy)
- `core/evaluators/page_evaluator.py` — `RegistryPageEvaluator` (new, recommended)

## PDF Report Generation

PDF export is handled by `ReportGenerator.generate_pdf()` and `PDFExporter.export_results()` in `core/utils/pdf_exporter.py`.

Current status:
- `ReportGenerator.generate_pdf()` is a stub that encodes JSON.
- `PDFExporter` provides a richer ReportLab-based layout with intro page, metadata, summary, detailed analyzer breakdown, and optional Figma data.

## Data Flow

```
Frontend → Backend → Core Engine → Registry → Analyzers
                ↓
            AnalysisResponse
                ↓
            PDFExporter → PDF bytes
```

## Environment Variables

| Variable | Description |
|---|---|
| `VITE_API_URL` | Frontend API base URL |
| `MONGODB_URL` | Backend MongoDB connection string |
| `JWT_SECRET` | Backend JWT signing secret |
| `ENABLE_LIGHTHOUSE` | Enable Lighthouse analyzer (default: false) |
| `ENABLE_ZAP` | Enable ZAP security scanner (default: false) |

## Deployment

Docker Compose with multi-stage builds:
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker/nginx/nginx.conf`
