# Research & Decision Log

## Overview
All clarifications resolved in specification. This document captures design decisions, rationale, and alternatives considered for the mock environment provisioning feature.

## Decisions

### D1: Submission Idempotency
- **Decision**: Non-idempotent; each submission creates a new provisioning request.
- **Rationale**: Simplifies demo flow and visually shows multiple parallel lifecycles; avoids client-side hashing or signature cache.
- **Alternatives Considered**:
  - Idempotent (return same request): Less illustrative for demo, adds request fingerprinting.
  - Conflict on duplicate: Adds additional error handling without strong demo value.

### D2: Concurrency Limit
- **Decision**: Soft cap of 5 active IN_PROGRESS requests per user/session; excess returns HTTP 429.
- **Rationale**: Demonstrates governance control without complexity; easy to test and show boundary behavior.
- **Alternatives**:
  - No limit: Risk of unbounded growth and unrealistic scenario.
  - Adaptive limits: Adds classification logic not needed in first iteration.

### D3: Retention Policy
- **Decision**: Retain completed requests for the entire process lifetime (no expiration or purge this iteration).
- **Rationale**: Simplest; ensures stable history for demo conversation. Memory footprint trivial at demo scale.
- **Alternatives**:
  - Time-based TTL: Adds scheduling/cleanup complexity.
  - Manual purge endpoint: Adds another endpoint outside minimal scope.

### D4: Lifecycle Simulation Approach
- **Decision**: Time-based progression (e.g., small async/background task or scheduler) moving PENDING → IN_PROGRESS → terminal (SUCCEEDED/FAILED).
- **Rationale**: Predictable and easy to reason about; supports deterministic override for tests (force success/failure).
- **Alternatives**:
  - Event-driven queue: Overkill; adds infrastructure complexity.
  - Immediate success: Removes realism and status polling purpose.

### D5: Failure Injection Strategy
- **Decision**: Default 10% random failure probability unless a test/deterministic flag indicates forced success/failure.
- **Rationale**: Keeps demo interesting; provides variation for status polling and error path demonstration.
- **Alternatives**:
  - Always succeed: Less educational.
  - Higher randomness: Could frustrate demonstration reliability.

### D6: Data Validation Strategy
- **Decision**: Use Pydantic models for request/response schema enforcement aligned with OpenAPI spec generation.
- **Rationale**: Native integration with FastAPI; reduces custom validation boilerplate.
- **Alternatives**:
  - Manual validation: More code, higher risk of drift.
  - Custom schema library: Unnecessary complexity.

### D7: Store Abstraction
- **Decision**: Define simple interface (protocol/class) with InMemory implementation. Methods: add_request, update_status, get_request, list_stacks, list_active_requests.
- **Rationale**: Provides future extensibility to persistent store without rewriting lifecycle logic.
- **Alternatives**:
  - Direct dict operations everywhere: Harder to swap later; scatters logic.
  - Full repository pattern w/ unit-of-work: Over-engineered for current scope.

### D8: Error Model
- **Decision**: Minimal structured error body: { "error": { "code": <string>, "message": <string> } } for 4xx/429/404 cases.
- **Rationale**: Simple and understandable; leaves room for future Problem+JSON alignment.
- **Alternatives**:
  - Full RFC 7807 immediately: Acceptable but not necessary for first iteration.

### D9: OpenAPI Extension Strategy
- **Decision**: Stage new paths in feature `contracts/openapi.additions.yaml` then merge into root `specs/openapi.yaml` once validated.
- **Rationale**: Keeps diff focused; clear contract-first evidence.
- **Alternatives**:
  - Direct edit of root spec first: Harder to isolate PR reasoning.

### D10: Status Codes
- **Decision**: List stacks → 200; submit provisioning → 202 (accepted, async) (fallback 201 if simpler, but prefer 202); get status → 200; invalid stack → 400; over limit → 429; missing request → 404.
- **Rationale**: Aligns with HTTP semantics; communicates async nature.
- **Alternatives**:
  - 201 for submission: Suggests resource created synchronously.

## Open Questions (Remaining)
None for this iteration.

## Risk Mitigations
- Flaky time-based tests → Provide deterministic mode param to force outcome and accelerate transitions.
- Memory growth (unbounded requests) → Demo scale negligible; future TTL if needed.
- Concurrency race (submission vs status poll) → Clear 404 for unknown id; doc behavior.

## References
- Constitution 1.0.1 (Simplicity, Contract-First, Testing Discipline) – all decisions adhere.
- Feature spec `specs/001-this-application-is/spec.md`.

*End of research.*
