# UIBench

UIBench is a web interface analysis and design system platform that provides automated reports on aesthetics, accessibility, and performance.

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd uibench

# Full stack with Docker Compose
docker compose up --build
```

## Lightweight CLI Setup

For users who only need the command-line interface:

### Option A: Quick test without full install

```bash
# From repo root, using the existing venv we created:
.venv/bin/uibench --help
.venv/bin/uibench evaluate --help
.venv/bin/uibench batch --help
.venv/bin/uibench watch --help
```

### Option B: Install CLI package

```bash
# Clone repo
git clone <repository-url>
cd uibench

# Install CLI package
pip install -e cli/

# Install Playwright browser (required for URL evaluation)
playwright install chromium

# Run CLI
uibench --help
```

### Option C: Run CLI in Docker

```bash
# Build and run CLI container
docker compose run --rm cli --help

# Evaluate a URL
docker compose run --rm cli evaluate https://example.com

# Batch evaluation
docker compose run --rm cli batch urls.txt
```

### CLI Commands

```bash
# Evaluate a live URL (cards on TTY, JSON when piped)
uibench evaluate https://example.com

# Evaluate with specific analyzers
uibench evaluate https://example.com --analyzer seo,performance

# Run all analyzers without interactive picker
uibench evaluate https://example.com --all

# Accept default analyzer selection without prompting
uibench evaluate https://example.com -y

# Batch evaluation from file
uibench batch urls.txt

# Watch a project directory for changes
uibench watch ./my-project

# Manage config
uibench config show
```

The CLI shows a startup banner when run in an interactive terminal. Use `--no-banner` to suppress it.

### Output Formats

The CLI supports multiple output formats via `--output`:

- `json` — machine-readable (default when piped)
- `text` — human-readable terminal output
- `cards` — colorful per-analyzer cards (default on TTY)
- `html` — standalone HTML report
- `pdf` — branded PDF report (requires `reportlab`)

Example:
```bash
uibench evaluate https://example.com --output pdf --save report.pdf
```

### Interactive Analyzer Picker

When running `uibench evaluate` interactively without `--analyzer` or `--skip`, an interactive picker appears (requires `questionary`):

```bash
uibench evaluate https://example.com
```

Select analyzers with space, confirm with enter. The picker only fires in interactive terminals — it never appears in CI, scripts, or batch mode.

## Project Structure

```
├── frontend/          # SvelteKit + Vite + Tailwind SPA
├── backend/           # FastAPI + MongoDB REST API
├── core/              # Python analysis engine
├── cli/               # Terminal-native CLI (Typer + Rich)
│   ├── Dockerfile     # CLI container image
│   ├── pyproject.toml # CLI package config
│   ├── README.md      # CLI-specific docs
│   └── CORE_INTEGRATION.md # How to wire real core
├── scripts/           # Setup and utility scripts
├── docker-compose.yml # Full stack orchestration
└── README.md
```

## Documentation

- `ARCHITECTURE.md` - System design and output contract
- `CONTRIBUTING.md` - Branch strategy and commit conventions
- `CHANGELOG.md` - Version history
- `cli/CORE_INTEGRATION.md` - How to wire the real core into the CLI

## License

MIT
