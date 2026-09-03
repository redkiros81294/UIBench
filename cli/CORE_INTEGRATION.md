# Wiring in the real UIBench core

The entire CLI — argument parsing, config, output formatting, colors,
spinners, tables, error handling, exit codes — works against one seam:

```python
uibench_cli/core/engine.py:AnalyzerEngine
```

Right now `cli.py` hands every command a `MockEngine`
(`uibench_cli/core/mock_engine.py`), which fabricates deterministic
scores so the whole CLI is runnable and demoable without your backend.
Replacing it is a two-step job.

## 1. Implement the protocol

```python
# uibench_cli/core/real_engine.py
from uibench_cli.core.engine import AnalyzerEngine, EvaluateOptions
from uibench_cli.core.exceptions import NetworkError, CoreEngineError
from uibench_cli.models import AnalyzerResult, EvaluationResult

class RealEngine:
    def evaluate(self, target: str, options: EvaluateOptions) -> EvaluationResult:
        # target is either a URL ("https://...") or a local path ("./app")
        # exactly as the user typed it — decide dispatch based on that.
        #
        # options carries every evaluate/batch/watch flag:
        #   .resolved_analyzers()  -> ["seo", "performance", ...] (skip already applied)
        #   .browser / .zap / .lighthouse -> opt-in analyzer toggles
        #   .depth / .max_pages / .timeout
        #   .design -> "none" | "figma:<key>" | "sketch:<url>"
        #   .thresholds -> {"seo": 75.0, "accessibility": 90.0, ...} from config
        #
        # Call into your existing evaluation pipeline here, then map its
        # output into AnalyzerResult / EvaluationResult (see models.py —
        # AnalyzerResult.status is computed automatically from score vs.
        # threshold, you don't need to set it).
        #
        # Raise NetworkError for unreachable hosts / timeouts (exit 3).
        # Raise CoreEngineError for missing deps or analyzer crashes (exit 4).
        ...
```

`AnalyzerResult` and `EvaluationResult` (in `uibench_cli/models.py`) are
plain dataclasses — construct them directly from whatever your pipeline
returns. `EvaluationResult.overall_score` and `.status` are computed
properties, so you never set them by hand.

## 2. Point the CLI at it

In `uibench_cli/cli.py`, `main_callback`:

```python
from uibench_cli.core.real_engine import RealEngine

ctx.obj = AppContext(
    ...
    engine=RealEngine(),   # was: MockEngine()
    ...
)
```

That's the whole swap — every command (`evaluate`, `batch`, `watch`)
calls `ctx.obj.engine.evaluate(...)` and never imports `MockEngine`
directly, so nothing else in the codebase needs to change.

## Remote backend / auth

If your core runs as a service rather than in-process, `RealEngine`
can simply be an HTTP client hitting it — `AppContext.core_url` and
`AppContext.token` are already threaded through from `--core-url`,
`--token`, `UIBENCH_TOKEN`, and stored login credentials
(`~/.config/uibench/credentials.json`, written by `uibench login`).

`uibench_cli/commands/auth.py` has a placeholder `_request_token()`
hitting `POST {core_url}/api/auth/login` — point it at your real auth
endpoint, or replace it entirely if auth works differently.

## Things intentionally left as stubs for you

- `render_pdf` / `render_html` in `output.py` are minimal — extend the
  templates/layout once you know what a "real" report should contain.
- `batch` only wires up `json` and `text` output; `html`/`pdf` batch
  export is a TODO comment in `commands/batch.py`.
- `watch`'s polling fallback (when `watchdog` isn't installed) does a
  full directory `os.walk` per tick — fine for small projects, but
  swap in `watchdog` (`pip install uibench-cli[watch]`) for anything
  larger.
- Design system checks (`--design figma:<key>` / `sketch:<url>`) are
  passed through in `EvaluateOptions.design` untouched — your engine
  decides what to do with the source string.
