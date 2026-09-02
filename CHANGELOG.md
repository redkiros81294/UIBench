# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Core engine refactor with registry-based analyzer orchestration
- Granular analyzers: SEO, accessibility, performance, design system, NLP
- `AnalysisContext` and `AnalysisResponse` standardized output contracts
- Browser analyzer stubs (axe-core, Playwright performance)
- `EvaluationService` for concurrent analyzer execution
- `RegistryPageEvaluator` as the new recommended page evaluator
- Backend FastAPI `app/` package with routes, services, models, middleware
- `/metrics` endpoint and structured logging
- Docker Compose multi-stage builds for backend and frontend
- Frontend environment variable support via `VITE_API_URL`
- `.env.example` and `Makefile`

### Changed
- PDF export moved from stub JSON encoder to ReportLab-based layout
- All analyzer outputs normalized to `AnalysisResponse` schema
- Backend `requirements.txt` split into runtime and dev dependencies
- Frontend typography switched to system fonts

### Fixed
- Duplicate `code_quality_score` field in `EnhancedEvaluationReport`
- Missing PDF generation dependencies in backend

## [0.1.0] — 2026-06-13

### Added
- Initial project scaffold with SvelteKit frontend and FastAPI backend
- MongoDB integration with async Motor driver
- JWT authentication with role-based access
- Core analysis engine with Playwright, spaCy, and reportlab
- SEO, accessibility, performance, security analyzers
- PDF report generation
- Docker Compose orchestration
- Installation script with spaCy model setup

### Changed
- CLI website evaluation interface
- Backend can handle concurrent analysis requests

### Fixed
- Python version compatibility in installation script
- spaCy model download fallback handling
