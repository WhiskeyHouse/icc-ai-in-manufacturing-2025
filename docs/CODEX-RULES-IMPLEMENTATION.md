# Codex-Oriented Ignition Rule Engine Roadmap

## Mission Alignment
Our priority is to deliver a rule engine that Codex can call during autonomous Ignition development. Every milestone below should expose machine-friendly inputs/outputs, deterministic fixes, and lightweight embeddings so Codex can reason, apply, and verify corrections without human intervention.

## Phase 0 — Foundations (Week 0-1)
- Define rule schema in `rules/schema.yml` with fields for `id`, `applies_to`, `context`, `severity`, `logic`, and `suggested_fix`.
- Stand up `services/rules-api` (FastAPI + Pydantic) with `/health` and `/rulesets` endpoints; enable hot reload of YAML.
- Seed repo with canonical Ignition samples (`samples/perspective`, `samples/jython`, `samples/tags`) that Codex will use for few-shot prompting and regression tests.

## Phase 1 — Perspective Validation (Week 2-3)
- Implement JSON schema validators for views/components and embed baseline WHK standards (security, color, binding hygiene).
- Return structured diagnostics (`code`, `message`, `path`, `fix_patch`) so Codex can programmatically apply changes.
- Ship `codex-demo/perspective-lint.ipynb` to document end-to-end agent flow (generate → validate → patch).

## Phase 2 — Script Analysis (Week 4-5)
- Build Jython AST walker enforcing logging, error handling, and tag write safety.
- Surface remediation snippets using fenced patches suitable for Codex `apply_patch` execution.
- Add integration tests using `pytest-httpx` that mimic Codex calling the validator during code generation.

## Phase 3 — Tag & UDT Governance (Week 6-7)
- Parse Ignition tag JSON to ensure naming, historian settings, and alarm metadata compliance.
- Provide rule context routing (`production`, `lab`, `demo`) so Codex can request targeted bundles.
- Extend CLI `whk-rules lint` to accept paths or zipped gateway exports for local agent validation.

## Phase 4 — Agent Loop Instrumentation (Week 8+)
- Publish `/suggest` endpoint returning ranked remediation plans Codex can evaluate before editing files.
- Emit evaluation telemetry (rule coverage, fix success) to `telemetry/` for fine-tuning prompts.
- Create Codex playbooks under `docs/codex/` detailing prompt scaffolds, expected validator payloads, and fallback strategies.

## Ongoing Guardrails
- Keep fixtures and samples in sync with live Ignition projects; auto-refresh via nightly export.
- Document every new rule with purpose, edge cases, and Codex-specific patch examples.
- Treat telemetry as first-class: capture false positives/negatives so the rule engine and Codex prompts improve together.
