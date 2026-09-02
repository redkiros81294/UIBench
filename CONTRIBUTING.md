# Contributing to UIBench

## Branching Model

- `main` — production-ready, never commit directly
- `develop` — integration branch
- `feature/A-*` — Member A frontend branches
- `feature/B-*` — Member B frontend branches
- `fix/A-*` — Member A bugfix branches
- `fix/B-*` — Member B bugfix branches

Always branch off `develop`, not `main`.

## Commit Convention

```
type(scope): description
```

Types:
- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation only
- `style` — formatting, no logic change
- `refactor` — code change that neither fixes a bug nor adds a feature
- `test` — adding or updating tests
- `chore` — build, CI, dependencies

Examples:
```
feat(frontend): add QR scanner with jsQR
fix(core): handle missing spaCy model gracefully
docs(backend): update API endpoint descriptions
```

## Code Standards

- Python: `mypy --strict`, `ruff format`, `black`
- Frontend: ESLint, Prettier
- All spacing follows the 8-point grid in frontend components
- Design tokens must be used instead of raw values

## Pull Requests

1. Branch from `develop`
2. Make changes with conventional commits
3. Run `make test` before submitting
4. Open PR against `develop`
5. Request review from at least one team member

## Environment

Copy `.env.example` to `.env.local` and fill in values. Never commit secrets.
