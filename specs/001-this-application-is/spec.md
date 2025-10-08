# Feature Specification: Mock Environment Provisioning API (List Stacks, Submit Provisioning Request, Check Status)

> Constitution Alignment: Each user story MUST map to one or more OpenAPI operations (Contract-First). List new or
> changed endpoint identifiers (method + path) under each story. Security impacts (auth scopes/roles) MUST be noted.

**Feature Branch**: `[001-this-application-is]`  
**Created**: 2025-10-08  
**Status**: Draft  
**Input**: User description: "This application is intended to support demos in my Azure environment. The first iteration will expose simple RESTful APIs using the OpenAPI 3.0 specification that will allow for interactions with a simulated platform engineer environment. At a minimum there should be an endpoint to: 1. Retrieve a list of environment stacks (examples: Basic web app, basic api application, microservice, etc..) 2. Initiate provisioning of an environment 3. Check the status of a provisioning request. For the first iteration we won't be building any logic to actually deploy something. Instead we should focus on mocking endpoints that would normally result in state changes. The state should be stored. Use an interface style abstraction to represent the state store but for the initial implementation maintaining the state in memory is fine. Engage me in a conversation on what other details we need to get started."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Discover Available Environment Stacks (Priority: P1)

Platform demo consumer retrieves a curated list of environment stack blueprints (e.g., Basic Web App, Basic API, Microservice) with descriptive metadata to decide which to provision.

**Why this priority**: List discovery is prerequisite to any provisioning; without it no further value can be delivered.

**Independent Test**: Perform a GET on `/environment-stacks` and verify a non-empty, structured list with required fields; no other stories needed.

**OpenAPI Operations**: `GET /environment-stacks`

**Acceptance Scenarios**:

1. **Given** system has predefined stack catalog, **When** user requests list, **Then** system returns all stacks with id, name, description, category, estimatedProvisionMinutes.
2. **Given** catalog present, **When** user filters (future enhancement – not in scope), **Then** (out of scope for this iteration).
3. **Given** no stacks configured (edge simulation), **When** user requests list, **Then** empty array is returned with 200.

---

### User Story 2 - Submit Provisioning Request (Priority: P2)

User selects a stack and submits a provisioning request, receiving a tracking identifier immediately while the system simulates progression of state in the background.

**Why this priority**: Enables primary value demonstration (initiating an environment) after discovery baseline (Story 1).

**Independent Test**: POST to `/provisioning-requests` with valid payload and verify a 202 (or 201) response containing requestId and initial status without dependency on status polling implementation.

**OpenAPI Operations**: `POST /provisioning-requests`

**Acceptance Scenarios**:

1. **Given** valid stack id, **When** user submits request, **Then** system returns unique requestId, stackId, status = `PENDING` (or `IN_PROGRESS`), and createdTimestamp.
2. **Given** invalid stack id, **When** submission attempted, **Then** 400 returned with validation error message.
3. **Given** duplicate identical submission quickly after original, **When** user submits again, **Then** system returns a distinct new request (explicitly non-idempotent behavior for demo simplicity).

---

### User Story 3 - Check Provisioning Status (Priority: P3)

User polls the status of a previously created provisioning request to understand progress and final outcome.

**Why this priority**: Completes basic lifecycle visibility; can be added after ability to submit exists.

**Independent Test**: After creating a request via Story 2 (or seeding), perform GET `/provisioning-requests/{requestId}` and verify status transitions follow defined lifecycle.

**OpenAPI Operations**: `GET /provisioning-requests/{requestId}`

**Acceptance Scenarios**:

1. **Given** existing request in progress, **When** user retrieves status, **Then** status is one of `PENDING | IN_PROGRESS | SUCCEEDED | FAILED`.
2. **Given** non-existent request id, **When** user retrieves status, **Then** 404 returned.
3. **Given** request reaches terminal state, **When** user retrieves status, **Then** terminal state is stable and includes completedTimestamp.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- Request submitted with whitespace or malformed stack id -> 400 validation.
- Rapid successive submissions exceeding soft concurrency limit per user -> 429 (soft cap = 5 active IN_PROGRESS requests). 
- Status requested before system has recorded request (race) -> 404.
- Simulated failure path (random or forced) -> status transitions to FAILED with failureReason.
- Empty stack catalog -> GET returns 200 with empty array (no error).
- Large number of provisioning requests -> pagination for list (future; not in scope this iteration).

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST provide an endpoint to list all predefined environment stacks with fields: id, name, description, category, estimatedProvisionMinutes.
- **FR-002**: System MUST validate that a provisioning request references an existing stack id; invalid ids MUST produce 400 with error details.
- **FR-003**: System MUST accept a provisioning request and return a tracking identifier plus initial status in a single response within 1 second (simulated, non-blocking processing).
- **FR-004**: System MUST maintain in-memory state of provisioning requests for the lifetime of the process so subsequent status checks reflect lifecycle progression.
- **FR-005**: System MUST simulate asynchronous lifecycle transitions (e.g., PENDING -> IN_PROGRESS -> SUCCEEDED/FAILED) using time-based or event simulation.
- **FR-006**: System MUST expose an endpoint to retrieve the current status (and relevant timestamps) for a provisioning request by id.
- **FR-007**: System MUST ensure statuses for terminal states (SUCCEEDED, FAILED) do not revert afterward (immutability of terminal state).
- **FR-008**: System SHOULD include optional failureReason when status=FAILED.
- **FR-009**: System MUST ensure unique request identifiers (collision-resistant within session).
- **FR-010**: System MUST respond deterministically for missing request ids with 404.
- **FR-011**: System MUST (for demo) not require authentication (assumption) and note that future security will layer roles/scopes.
- **FR-012**: System MUST document (OpenAPI) all new endpoints and schemas prior to implementation (contract-first alignment).
- **FR-013**: System SHOULD allow deterministic test mode (e.g., force success/failure via a reserved flag) to support demos.
- **FR-014**: System MUST treat identical rapid duplicate submissions as independent (non-idempotent) requests; each submission yields a new requestId.
- **FR-015**: System MUST enforce a soft limit of 5 concurrently IN_PROGRESS requests per user/session; additional submissions SHOULD receive 429 with explanatory error.

Non-Goals (Explicitly Out of Scope This Iteration):
- Actual infrastructure provisioning or external platform integration.
- Persistence beyond process memory (no database / file storage).
- Authentication & authorization enforcement (future iteration).
- Pagination & filtering for stacks or requests.
- Bulk submission endpoints.

### Key Entities *(include if feature involves data)*

- **EnvironmentStack**: Blueprint descriptor with attributes (id, name, description, category, estimatedProvisionMinutes). Immutable during process lifetime.
- **ProvisioningRequest**: Represents a single requested environment instantiation with attributes (id, stackId, status, createdTimestamp, updatedTimestamp, completedTimestamp?, failureReason?).
- **ProvisioningLifecycleStatus**: Enumeration of states: PENDING, IN_PROGRESS, SUCCEEDED, FAILED (future: CANCELED). Terminal states: SUCCEEDED, FAILED.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 100% of stack list requests return within 2 seconds under demo conditions (single-user typical usage).
- **SC-002**: 95% of provisioning submissions return tracking identifier within 1 second.
- **SC-003**: 90% of provisioning simulations reach a terminal state (success or failure) within 30 seconds (demo target) unless deliberately forced longer.
- **SC-004**: 100% of status retrievals for existing request ids return correct current lifecycle state consistent with allowed transitions.
- **SC-005**: 0% of terminal-state requests regress to non-terminal status during session (immutability guarantee).
- **SC-006**: Documentation (OpenAPI) for all 3 endpoints is accepted (lint/contract tests pass) before implementation merge.
- **SC-007**: Demo operator can deterministically trigger success or failure outcomes in >90% of attempts using test mode flag.

### Assumptions
- Single-user or low-concurrency demo context; per-user concurrency cap fixed at 5 active IN_PROGRESS requests.
- In-memory store lifespan equals process uptime; completed requests retained for full process lifetime (no expiration this iteration).
- No authentication required this iteration; future iteration will introduce bearer auth or similar.
- Random failure injection rate default 10% unless forced via test flag.

### Risks / Considerations
- Without persistence, long-running demos may lose context if process restarts.
- Overuse of clarification markers could stall; limited to essential 3.
- Simulated timing may create flaky test expectations if not bounded; propose deterministic mode.

### Dependencies
- OpenAPI contract update before code (contract tests already in repo pattern).

### Clarification Resolutions
All initial clarification points have been resolved:
1. Idempotency: Non-idempotent; every submission creates a new request (decision favors simplicity for demo).
2. Concurrency: Soft cap of 5 active IN_PROGRESS requests per user/session; excess submissions return 429.
3. Retention: Completed requests retained for entire process lifetime; no expiration or purge endpoint this iteration.
