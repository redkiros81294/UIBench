# UIBench CLI

A terminal-native client for the UIBench web interface analysis
platform — implements the full command surface from the design brief:
`evaluate`, `batch`, `watch`, `config`, `login`/`logout`/`whoami`,
JSON/text/HTML/PDF output, threshold-based exit codes, `NO_COLOR` /
`TERM=dumb` handling, and an ASCII fallback for every symbol.

This repo is the **CLI shell** — argument parsing, config, terminal UX,
output formats, error handling. It ships with a deterministic
`MockEngine` so every command runs end-to-end today. Swapping in your
real evaluation core is one class; see **[CORE_INTEGRATION.md](CORE_INTEGRATION.md)**.

## Install

```bash
pip install -e ".[pdf,watch,dev]"
```

- `pdf` — pulls in `reportlab` for `--output pdf`
- `watch` — pulls in `watchdog` for real filesystem events in `uibench watch` (falls back to polling without it)
- `dev` — `pytest`, for the test suite

## Try it

```bash
uibench evaluate https://example.com                          # JSON, default
uibench evaluate https://example.com --output text             # human-readable
uibench evaluate https://example.com --analyzer seo,performance
uibench evaluate ./my-project --depth 2 --max-pages 20
uibench evaluate https://example.com --fail-below 80            # exit 1 if under
uibench batch sites.txt --analyzer seo --output json | jq .
uibench watch ./my-app --output text
uibench config list
uibench config set thresholds.seo 80
```

Everything runs against the bundled `MockEngine` right now — scores are
fake but deterministic (same target + analyzer always returns the same
number), so demos and screenshots are reproducible.

## Project layout

```
cli/
  cli.py               Typer app: global flags, context assembly, command registration
  context.py           AppContext — the object every command receives via ctx.obj
  config.py            .uibench.toml loading (layered) / writing
  models.py            AnalyzerResult, EvaluationResult — status is computed from score vs. threshold
  output.py            json / text / html / pdf renderers
  theme.py             rich Theme — the palette from the design spec, as actual color tokens

  core/
    engine.py           AnalyzerEngine protocol + EvaluateOptions — the integration seam
    mock_engine.py       deterministic fake engine, used until the real one is wired in
    exceptions.py         UIBenchError subclasses, one per exit code

  commands/
    evaluate.py          `uibench evaluate` — also exports run_evaluation()/render_result()
                          which batch.py and watch.py both reuse
    batch.py              `uibench batch`
    watch.py               `uibench watch` — watchdog if installed, polling fallback otherwise
    config_cmd.py           `uibench config get|set|list`
    auth.py                  `uibench login|logout|whoami`

  ui/
    spinner.py            rich Status wrapper (dots spinner = the exact frame spec)
    table.py                analyzer table: widths/alignment/truncation per the layout spec
    icons.py                  status glyph <-> ASCII fallback mapping
    errors.py                   ERROR:/WARNING:/INFO: formatting
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Score below `--fail-below` |
| 2 | Invalid arguments |
| 3 | Network error |
| 4 | Core engine error (missing dependency, analyzer crash) |
| 5 | Auth failure |
| 6 | Config error |

Every non-zero exit prints `ERROR: <short>` / `<detail>` / `Run: <suggestion>`
— see `cli/ui/errors.py` and `core/exceptions.py`.

## What's real vs. a stand-in

**Real and tested:** argument parsing for every command in the brief,
config layering and read/write, all seven exit-code paths, JSON
(compact when piped / pretty on a TTY), the text report with the
analyzer table, HTML/PDF export, `--save`, `NO_COLOR`/`--no-unicode`
fallbacks, and the watch polling loop.

**Stand-in, documented in CORE_INTEGRATION.md:** the evaluation engine
itself (`MockEngine`), the login network call, and PDF/HTML report
layout — these are where your actual analyzers, auth backend, and
report design plug in.

## Tests

```bash
pytest
```

`tests/test_models.py` covers the score → status logic (the thing most
likely to silently drift if thresholds change); it's a reasonable
starting point to extend once the real engine is in.
