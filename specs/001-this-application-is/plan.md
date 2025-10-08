# Implementation Plan: Mock Environment Provisioning API (Stacks, Submit, Status)

**Branch**: `001-this-application-is` | **Date**: 2025-10-08 | **Spec**: [/specs/001-this-application-is/spec.md]
**Input**: Feature specification from `/specs/001-this-application-is/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deliver three contract-first demo endpoints: list environment stacks, submit provisioning request (async simulated), and poll provisioning status. Implementation uses Python 3.11 + FastAPI (per constitution tech stack) with an in-memory store abstraction and simulated lifecycle progression (timer-based). Non-goals include persistence, real infra orchestration, and auth (documented assumptions). Decisions: non-idempotent submissions, concurrency soft cap (5), retain completed requests for process life.

## Technical Context

**Language/Version**: Python 3.11 (constitution)  
**Primary Dependencies**: FastAPI, Uvicorn (runtime), Pydantic (model validation), pytest (testing)  
**Storage**: In-memory dictionary via interface abstraction (no persistence)  
**Testing**: pytest unit + contract (OpenAPI conformance tests), potential simple lifecycle simulation test harness  
**Target Platform**: Local dev server (macOS / Linux) containerizable later  
**Project Type**: Single backend service (demo API)  
**Performance Goals**: SC-001/002 (list <2s, submission <1s) & constitution baseline p95 < 250ms for each operation  
**Constraints**: Simplicity (no DB, no message queue), minimal external dependencies, deterministic test mode  
**Scale/Scope**: Single-user / low concurrency demo; max dozens of requests per session  

No outstanding NEEDS CLARIFICATION items.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Evidence (link or note) | Status |
|-----------|------|-------------------------|--------|
| Simplicity | Minimal scope, in-memory only; no extra layers beyond store interface | Spec non-goals + no complexity entries | PASS |
| Contract-First | New paths defined in feature additions file; root spec update pending merge | `contracts/openapi.additions.yaml` present | PASS (pending merge) |
| Security by Default | Explicitly public for demo; future auth stated in assumptions | Spec Assumptions & Constitution TODO(SECURITY_BASELINE) | PASS (temporary) |
| Testing Discipline | Will enumerate tests in upcoming tasks.md (Phase 2) | Placeholder until tasks phase | PENDING |
| CI/CD | Existing pipeline skeleton; no new jobs required this feature | Note in plan; no changes needed | PASS |

Failure of any gate MUST block progression until resolved or an approved temporary exception (with expiration) is recorded.

## Project Structure

### Documentation (this feature)

```
specs/001-this-application-is/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.additions.yaml
└── tasks.md   (future: /speckit.tasks)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```
src/
├── app/
│   └── main.py (existing)
├── domain/ (to be added)
│   ├── models.py (provisioning + stacks dataclasses/pydantic models)
│   ├── store.py (state store interface + in-memory impl)
│   └── lifecycle.py (simulation logic deterministic mode)
└── api/ (optional future extraction; initial endpoints stay in app/main or incremental refactor)

tests/
├── contract/ (add tests for new endpoints)
├── unit/
│   ├── test_lifecycle.py
│   └── test_store.py
└── integration/ (not needed now)
```

**Structure Decision**: Stay within existing single-service Python project. Introduce `domain` package for cohesion (models, store, lifecycle). Defer extracting dedicated `api` package until >5 endpoints. No additional services or layers added.

## Complexity Tracking

No complexity justifications required (no extra architectural layers beyond minimal domain grouping). Table intentionally empty.
