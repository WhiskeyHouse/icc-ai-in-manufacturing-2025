# Repository Guidelines

## Project Structure & Module Organization
The stack is driven by `docker-compose.yml`, with service definitions under `llama-index-service/`, `rabbitmq/`, `kong_config/`, and container init data in `postgres/`. Ignition gateway assets live in `gw-build/`, `gw-init/`, and `ignition-projects/`, while supplemental docs and runbooks sit under `docs/` and the top-level `*-GUIDE.md` files. Automation helpers and demo flows reside in `scripts/` (shell), `demo-*.py`, and `rules-engine-service.py`. Demo content, seeded assets, and training materials are kept in `demo-patterns/`, `demo-ai-responses.py`, and `refs/`. Tests and health scripts follow the `test-*.py`/`.sh` naming at the repo root.

## Build, Test, and Development Commands
Run `npm install` once to fetch the lone Node dependency used by dotenv tooling. Before demos, execute `./scripts/demo-preflight.sh` to validate Docker and secrets, then `docker compose up -d` or `./scripts/demo-up.sh` to bring the environment online; `./scripts/demo-down.sh` stops it. Use `run-seeding.sh` after first boot to populate the manufacturing services. During development, `python3 demo-rag-service.py` and `python3 rules-engine-service.py` start the mock AI components outside Docker when needed.

## Coding Style & Naming Conventions
Python modules use 4-space indentation, `snake_case` functions, and `black`-compatible formatting; keep API payload examples in JSON dictionaries. Shell scripts are Bash with `set -euo pipefail` and lowercase, hyphenated filenames (`demo-up.sh`). YAML and JSON under `ignition-*` and `docs/` follow 2-space indentation. Maintain secrets in `secrets/` files referenced by scripts and avoid inlining credentials.

## Testing Guidelines
UI and service smoke checks live in `test-ai-generation.py`, `test-presentation-scenarios.py`, and `test-connectivity.sh`. Run them with `python3 <script>` or `bash test-connectivity.sh` once the stack is up. Mirror the `test-*` naming for new ad hoc validations and ensure they tolerate services being offline by handling connection failures gracefully.

## Commit & Pull Request Guidelines
There is no established history yet, so adopt Conventional Commit-style subjects (`feat: add ai validation hooks`) written in imperative voice with <=72 characters. PRs should link to presentation or demo objectives, outline environment changes (compose services, secrets), and include screenshots or terminal captures when adjusting demo flows. Confirm Docker orchestration and manual tests have been rerun before requesting review.

## Security & Configuration Tips
Secrets are mounted from `secrets/` and `.env`; refresh them via `npx dotenv-vault@latest pull` when onboarding. Restrict local certificates and backups (`gw-build/ssl.pfx`, `ignition-backups/`) to trusted storage and avoid committing regenerated keys.
