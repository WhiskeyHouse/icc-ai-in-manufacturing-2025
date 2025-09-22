# Demo Workspace

Central home for scripted demos, automation utilities, and supporting assets.

- `scripts/` – Shell entry points for presenters (`run-*.sh`, `demo-*.sh`). Each script resolves the repo root automatically so you can run them from anywhere.
- `python/` – Narrative Python demos (`demo-*.py`). Called from shell wrappers and suitable for direct execution with `uv run`.
- `go/` – Go-based CLI experiences (`demo-stack-*.go`) plus compiled binaries in `go/bin/` used by the wrappers.
- `materials/` – Slide copy, prompts, and supporting text pulled into the demos.

> When adding a new demo, drop code in the appropriate subdirectory and link documentation from `docs/demos/`.
