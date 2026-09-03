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

### CLI Commands

```bash
# Evaluate a live URL
uibench evaluate https://example.com

# Evaluate with specific analyzers
uibench evaluate https://example.com --analyzer seo,performance

# Batch evaluation from file
uibench batch urls.txt

# Watch a project directory for changes
uibench watch ./my-project

# Manage config
uibench config show
```

### Output Formats

The CLI supports multiple output formats via `--output`:

- `json` — machine-readable (default)
- `text` — human-readable terminal output
- `html` — standalone HTML report
- `pdf` — branded PDF report (requires `reportlab`)

Example:
```bash
uibench evaluate https://example.com --output pdf --save report.pdf
```

## Project Structure

```
├── frontend/          # SvelteKit + Vite + Tailwind SPA
├── backend/           # FastAPI + MongoDB REST API
├── core/              # Python analysis engine
├── cli/               # Terminal-native CLI (Typer + Rich)
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
