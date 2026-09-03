# UIBench

![UIBench](logo.png)

**UIBench** is a web interface analysis and design system platform that evaluates websites and digital products across aesthetics, accessibility, performance, SEO, security, and design-system consistency. It delivers actionable reports through a web dashboard, REST API, PDF exports, and a terminal-native CLI.

---

## Features

- **Multi-format analysis** — SEO, accessibility, performance, security, NLP/content, and design-system token checks
- **Flexible targets** — analyze live URLs or local project directories
- **Multiple output formats** — interactive terminal cards, JSON, HTML, PDF, and text reports
- **CI/CD ready** — scriptable CLI with stable exit codes, JSON output, and Docker support
- **Interactive terminal UX** — analyzer cards, color-coded status, and an optional interactive analyzer picker
- **Design-system awareness** — token consistency checks, spacing/typography audits, and drift detection
- **Batch evaluation** — evaluate multiple URLs from a file with progress tracking
- **Watch mode** — re-evaluate local projects automatically on file changes
- **Configurable thresholds** — customize pass/fail criteria per analyzer
- **PDF reports** — branded PDF exports with cover page, executive summary, and detailed analysis

---

## Quick Start

### Full Stack (Web Dashboard + API)

```bash
git clone https://github.com/redkiros81294/UIBench.git
cd UIBench
docker compose up --build
```

### CLI Only

```bash
git clone https://github.com/redkiros81294/UIBench.git
cd UIBench
pip install -e cli/
playwright install chromium
uibench --help
```

### Docker (CLI)

```bash
docker compose run --rm cli --help
```

---

## CLI Usage

### Evaluate a URL or Project

```bash
# Interactive terminal (cards by default)
uibench evaluate https://example.com

# JSON output (ideal for piping/scripts)
uibench evaluate https://example.com --output json

# Specific analyzers
uibench evaluate https://example.com --analyzer seo,performance

# Run all analyzers without prompting
uibench evaluate https://example.com --all

# Accept defaults without prompting
uibench evaluate https://example.com -y

# Local project
uibench evaluate ./my-project
```

### Batch Evaluation

```bash
uibench batch urls.txt --analyzer seo --output json | jq .
```

### Watch Mode

```bash
uibench watch ./my-app --output text
```

### Configuration

```bash
uibench config list
uibench config set thresholds.seo 80
```

### Output Formats

| Format | Description |
|---|---|
| `json` | Machine-readable (default when piped) |
| `text` | Human-readable terminal table |
| `cards` | Colorful per-analyzer cards (default on TTY) |
| `html` | Standalone HTML report |
| `pdf` | Branded PDF report (requires `reportlab`) |

### Interactive Analyzer Picker

When running `uibench evaluate` interactively without `--analyzer` or `--skip`, an interactive picker lets you select analyzers with the spacebar. It only appears in interactive terminals — never in CI, scripts, or batch mode.

Install the optional dependency:
```bash
pip install -e cli/[interactive]
```

---

## Project Structure

```
├── frontend/                 # SvelteKit + Vite + Tailwind SPA
│   └── src/
│       ├── lib/             # Shared components, stores, i18n
│       ├── routes/          # File-based routes
│       └── app.html         # SvelteKit entrypoint
├── backend/                  # FastAPI + MongoDB REST API
│   └── app/
│       ├── main.py          # FastAPI app entrypoint
│       ├── routes/          # API route handlers
│       ├── services/        # Business logic
│       ├── models/          # Pydantic models
│       └── middleware/      # Auth, CORS, logging
├── core/                     # Python analysis engine
│   ├── analyzers/           # Modular analyzer registry
│   ├── evaluators/          # Page/project evaluators
│   ├── models/              # AnalysisContext, AnalysisResponse
│   ├── services/            # EvaluationService orchestration
│   ├── utils/               # PDF export, helpers
│   └── engine.py            # Core engine entrypoint
├── cli/                      # Terminal-native CLI (Typer + Rich)
│   ├── cli.py               # Typer app, global flags, command registration
│   ├── commands/            # evaluate, batch, watch, config, auth
│   ├── ui/                  # Cards, picker, spinner, icons, banner
│   ├── output.py            # JSON, text, cards, HTML, PDF renderers
│   ├── config.py            # .uibench.toml loading and writing
│   ├── models.py            # AnalyzerResult, EvaluationResult
│   ├── core/                # Engine protocol, MockEngine, RealEngine
│   └── pyproject.toml       # CLI package config
├── scripts/                  # Setup and utility scripts
│   └── setup.py             # Interactive mode selection (fullstack/cli/core)
├── docker-compose.yml        # Full stack orchestration
├── requirements.txt          # Root Python dependencies
├── pyproject.toml           # Root project metadata and tool config
├── Makefile                 # Developer convenience targets
├── ARCHITECTURE.md          # System design and data flow
├── CONTRIBUTING.md          # Branch strategy and commit conventions
├── CHANGELOG.md             # Version history
├── LOGO_BRIEF.md            # Logo design brief for designers
└── README.md
```

---

## Documentation

| Document | Description |
|---|---|
| `ARCHITECTURE.md` | System design, layer boundaries, data flow, environment variables |
| `CONTRIBUTING.md` | Branch strategy, commit conventions, PR process |
| `CHANGELOG.md` | Version history and release notes |
| `cli/CORE_INTEGRATION.md` | How to wire the real core engine into the CLI |
| `LOGO_BRIEF.md` | Logo design brief for designers |

---

## Development

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional, for containerized setup)

### Setup

```bash
# Full stack
make dev

# Backend only
make backend-start

# Frontend only
make frontend-start

# CLI only
make cli-install
```

### Testing

```bash
# Backend tests
cd backend && python -m pytest tests/ -v

# CLI tests
cd cli && pytest
```

### Linting

```bash
mypy --strict core/ cli/
ruff format core/ cli/
```

---

## Deployment

UIBench is containerized with multi-stage Docker builds. See `docker-compose.yml` for the full stack, or `cli/Dockerfile` for a standalone CLI container.

```bash
# Build all services
docker compose build

# Run full stack
docker compose up --build
```

---

## License

MIT — see `LICENSE` for details.

---

## Contributing

Contributions are welcome. Please read `CONTRIBUTING.md` for branch naming, commit conventions, and the PR process.
