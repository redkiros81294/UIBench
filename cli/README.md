# UIBench CLI

A terminal-native client for the UIBench web interface analysis
platform — implements the full command surface from the design brief:
`evaluate`, `batch`, `watch`, `config`, `login`/`logout`/`whoami`,
JSON/text/HTML/PDF/cards output, threshold-based exit codes, `NO_COLOR` /
`TERM=dumb` handling, and an ASCII fallback for every symbol.

This repo is the **CLI shell** — argument parsing, config, terminal UX,
output formats, error handling. It ships with a deterministic
`MockEngine` so every command runs end-to-end today. Swapping in your
real evaluation core is one class; see **[CORE_INTEGRATION.md](CORE_INTEGRATION.md)**.

## Install

```bash
pip install -e ".[pdf,watch,interactive,dev]"
```

- `pdf` — pulls in `reportlab` for `--output pdf`
- `watch` — pulls in `watchdog` for real filesystem events in `uibench watch` (falls back to polling without it)
- `interactive` — pulls in `questionary` for the interactive analyzer picker
- `dev` — `pytest`, for the test suite

## Try it

```bash
uibench evaluate https://example.com                          # cards on TTY, JSON when piped
uibench evaluate https://example.com --output text             # human-readable table
uibench evaluate https://example.com --analyzer seo,performance
uibench evaluate ./my-project --depth 2 --max-pages 20
uibench evaluate https://example.com --fail-below 80            # exit 1 if under
uibench batch sites.txt --analyzer seo --output json | jq .
uibench watch ./my-app --output text
uibench config list
uibench config set thresholds.seo 80
```

### Output formats

| Format | When to use |
|---|---|
| `json` | Piping, scripts, CI — machine-readable |
| `text` | Human-readable table report |
| `cards` | Interactive terminal — one card per analyzer with color-coded borders |
| `html` | Standalone HTML report |
| `pdf` | Branded PDF report (requires `reportlab`) |

The default format changes based on context:
- **TTY, no `--output` flag:** `cards` (colorful per-analyzer cards)
- **Piped/redirected, no `--output` flag:** `json` (compact)
- **Explicit `--output <fmt>`:** always uses that format

Override the TTY default with config:
```toml
[output]
tty_format = "cards"  # or "json" to restore old behavior
default_format = "json"  # piped default, don't change this for scripts
```

### Analyzer picker

When you run `uibench evaluate` interactively without `--analyzer` or `--skip`, an interactive picker appears (requires `questionary`):

```bash
uibench evaluate https://example.com
```

Select analyzers with space, confirm with enter. The picker only fires in interactive terminals — it never appears in CI, scripts, or batch mode.

Skip the picker:
```bash
uibench evaluate https://example.com --all                # run every analyzer
uibench evaluate https://example.com -y                    # accept default (all) without prompting
uibench evaluate https://example.com --analyzer seo,perf   # explicit list, no picker
```

## Project layout

```
cli/
  cli.py               Typer app: global flags, context assembly, command registration
  context.py           AppContext — the object every command receives via ctx.obj
  config.py            .uibench.toml loading (layered) / writing
  models.py            AnalyzerResult, EvaluationResult — status is computed from score vs. threshold
  output.py            json / text / html / pdf / cards renderers
  theme.py             rich Theme — the palette from the design spec, as actual color tokens

  core/
    engine.py           AnalyzerEngine protocol + EvaluateOptions — the integration seam
    mock_engine.py       deterministic fake engine, used until the real one is wired in
    real_engine.py       real core integration (RegistryPageEvaluator / ProjectAnalyzer)
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
    cards.py                analyzer cards: color-coded panels for interactive TTY
    icons.py                  status glyph <-> ASCII fallback mapping + analyzer category icons
    picker.py                interactive analyzer selection via questionary
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
fallbacks, the watch polling loop, analyzer cards on TTY, and the
interactive analyzer picker.

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
