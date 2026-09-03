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

# Run interactive setup
python scripts/setup.py

# Select "cli" mode, then:
# 1. Create virtual environment
# 2. Install CLI dependencies
# 3. Run: uibench --help

# Or install directly with pip
pip install -e ".[cli]"
playwright install chromium
```

### CLI Commands

```bash
# Evaluate a live URL
uibench evaluate https://example.com

# Generate PDF report
uibench pdf https://example.com

# Analyze local project
uibench project ./my-project
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

## License

MIT
