<!--
Sync Impact Report
Version change: 1.0.0 → 1.0.1 (PATCH)
Modified principles: None (documentation refinement only)
Added sections: None
Removed sections: None
Templates updates: (no changes required this patch)
Follow-up TODOs:
	- TODO(SECURITY_BASELINE): Enumerate concrete authN/Z approach (e.g., Azure Entra ID + OAuth2 scopes) and key management (Azure Key Vault) mapping.
	- TODO(CI_PIPELINE): Add GitHub Actions workflow implementing security scan and coverage gate (skeleton present).
Resolved TODOs:
	- TECH_STACK_DECISIONS (Python 3.11 + FastAPI + Uvicorn chosen)
	- OPENAPI_SPEC_PATH (/specs/openapi.yaml committed)
-->

# Platform Engineering Demo Constitution

## Core Principles

### 1. Simplicity First
The codebase MUST prioritize clarity and minimalism over premature optimization or architectural layering. Every
abstraction MUST earn its place: if a feature can be delivered with a direct function, do not introduce a class or
pattern. Remove (not comment out) unused code within the same PR that makes it obsolete. Complexity justifications
MUST be captured in the "Complexity Tracking" table of the implementation plan when a non-trivial pattern (factories,
CQRS, hexagonal layering, event sourcing, etc.) is introduced.
Rationale: Simple, easily modifiable code accelerates demo tailoring and reduces cognitive load under time pressure.

### 2. Contract-First Delivery
All externally reachable capabilities MUST begin as an OpenAPI 3.0 specification (or future MCP contract when adopted)
committed before implementation. Implementation code MUST NOT merge until: (a) new endpoints are defined in the spec,
(b) breaking changes are explicitly versioned (URL, header, or media type), and (c) contract tests exist and fail. Any
change to the spec MUST trigger contract test regeneration/adjustment in the same PR. Specs are the single source of
truth for consumers; inline code doc comments are secondary.
Rationale: Guarantees predictability for headless consumption and supports rapid consumer integration in demos.

### 3. Security by Default
Authentication and authorization MUST be enforced on every endpoint unless explicitly documented as Public in the
OpenAPI spec with justification. Secrets/configuration MUST be injected via environment variables or managed service
bindings—never hard-coded. Keys, tokens, and certificates MUST be rotated automatically or have documented rotation
procedure. Logging MUST exclude sensitive values (tokens, PII) and follow structured JSON format to enable redaction.
Rationale: Demo environments frequently become long-lived; baseline security prevents accidental misuse or leakage.

### 4. Testing Discipline (Non-Negotiable)
Every feature MUST have: (a) unit tests for pure logic, (b) contract tests validating the OpenAPI-defined behavior, and
(c) integration tests only where cross-component behavior cannot be unit or contract tested. Tests MUST be written (and
initially fail) before implementation merges. Code without tests MUST NOT be merged. Coverage gates: 100% of functions
and all declared contract operations executed. Flaky tests MUST be quarantined within 24h or fixed—no ignoring.
Rationale: Guarantees demonstrable reliability and enables fearless refactoring for varied demo scenarios.

### 5. Continuous Integration & Delivery
Every merged change MUST execute a CI pipeline including: lint, unit tests, contract tests, security static analysis,
and (when infrastructure present) ephemeral deployment smoke tests. The default branch MUST be always deployable.
CD workflows SHOULD automate environment updates for tagged versions. Pipeline failures MUST block merges—no manual
overrides without a documented incident note.
Rationale: Ensures consistency and credibility when demonstrating engineering excellence alongside solution features.

## Architecture & Quality Constraints

1. API Style: REST (OpenAPI 3.0). Future MCP integration MUST wrap or align with canonical REST contracts—not fork
	 divergent domain models.
2. Versioning: Use semantic versioning for API groups; breaking changes demand /v{n} path or negotiated media type.
3. Observability: Structured JSON logs, request correlation ID propagation, minimal metrics (req_count, error_count,
	 latency p95) MUST be emitted. Tracing MAY be added when multi-service emerges.
4. Error Model: Consistent problem+json schema with trace id reference.
5. Performance (initial): Latency target (p95 < 250ms) for single operation under nominal demo load (TODO refine).
6. Dependencies: Prefer small, well-supported libraries; avoid meta-framework sprawl.
7. Documentation: Each new API capability MUST include an example request/response snippet in the spec.

Tech Stack (decided): Python 3.11, FastAPI, Uvicorn, pytest. Contract file at `specs/openapi.yaml` authoritative.
TODO(SECURITY_BASELINE): Define concrete auth provider, token scopes, and key management details.

## Development Workflow & Quality Gates

Phases (mirrors templates): Plan → Spec → Research/Data Model → Contract → Tasks → Implementation → Demo Hardening.

Quality Gates (fail-fast):
1. Plan (Constitution Check): Simplicity justification present, contract placeholder added, security impact noted.
2. Spec: User stories independently testable; each story lists contract endpoints; acceptance criteria are executable.
3. Contract: OpenAPI diff validated; breaking changes flagged; version strategy noted.
4. Tasks: Every story includes test tasks (unit + contract) preceding implementation tasks.
5. PR: CI pipeline green; coverage threshold met; complexity table updated for any new abstraction.
6. Post-Merge: Tagging optional unless API change (then tag required) + release notes stub.

Automation Expectations:
- Lint + formatting pre-commit (to be defined in tooling decisions).
- Contract verification job compares OpenAPI in PR vs main.
- Security scanning (SAST + dependency audit) runs on every push.

## Governance

Authority: This Constitution supersedes ad hoc preferences. Conflicts resolved in favor of principles order (1 highest
weight when trade-offs occur, except security (3) can block all others if violated).

Amendments: Submit PR labeled `governance`. Include: (a) proposed change diff, (b) rationale, (c) impact on existing
templates, (d) version bump type (MAJOR/MINOR/PATCH) with justification. Approval requires ≥1 maintainer + explicit
version decision in PR description.

Versioning Policy (of this document):
- MAJOR: Remove or redefine a principle or governance rule incompatibly.
- MINOR: Add a new principle, section, or materially expand mandatory guidance.
- PATCH: Clarifications, wording improvements, non-semantic formatting.

Compliance Review: Each feature plan includes a Constitution Check table. CI MAY introduce automated lint rules (e.g.,
presence of contract file, coverage report). Quarterly (or before major demo events) a light review ensures no drift.

Exceptions: Temporary deviations MUST include an OWNER, EXPIRATION DATE, and REMOVAL TASK ID in the PR description.

## Version & Dates

**Version**: 1.0.1 | **Ratified**: 2025-10-07 | **Last Amended**: 2025-10-07

<!-- End Constitution -->