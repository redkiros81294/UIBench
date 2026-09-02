# UIBench

UIBench is a web interface analysis and design system platform that provides automated reports on aesthetics, accessibility, and performance.

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd uibench

# Copy environment file
cp .env.example .env.local

# Start with Docker Compose
docker compose up --build
```

## Project Structure

```
├── frontend/          # SvelteKit + Vite + Tailwind SPA
├── backend/           # FastAPI + MongoDB REST API
├── core/              # Python analysis engine
├── docker-compose.yml # Full stack orchestration
└── README.md
```

## Documentation

- `ARCHITECTURE.md` - System design and output contract
- `CONTRIBUTING.md` - Branch strategy and commit conventions
- `CHANGELOG.md` - Version history

## License

MIT
