# Data Model

## Entities

### EnvironmentStack
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | yes | Unique stable identifier (kebab-case) |
| name | string | yes | Human-friendly title |
| description | string | yes | Short descriptive text |
| category | string | yes | e.g., "web", "api", "service" |
| estimatedProvisionMinutes | integer | yes | Approximate simulated duration |

Validation:
- id: regex `^[a-z0-9-]{3,40}$`
- name: 3–60 chars
- estimatedProvisionMinutes: 1–120

### ProvisioningRequest
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | yes | Generated UUID-like token |
| stackId | string | yes | FK to EnvironmentStack.id |
| projectName | string | yes | Human-friendly project identifier |
| environment | enum | yes | dev, qa, production |
| department | string | yes | Owning organizational unit (e.g., Finance, Eng) |
| status | enum | yes | PENDING, IN_PROGRESS, SUCCEEDED, FAILED |
| createdTimestamp | datetime | yes | ISO8601 UTC |
| updatedTimestamp | datetime | yes | ISO8601 UTC, changes on status mutation |
| completedTimestamp | datetime | no | Set only on SUCCEEDED/FAILED |
| failureReason | string | no | Present only if FAILED |
| forcedOutcome | string | no | Optional test override: SUCCESS | FAILURE |

Validation:
- stackId must reference existing stack
- projectName: length 3–80, allowed characters letters, numbers, spaces, dashes (normalize on storage)
- environment: must be one of dev | qa | production (lowercase)
- department: length 2–60, uppercase A-Z + spaces recommended (no enforcement beyond length)
- status transitions validated (see lifecycle)
- failureReason only when status=FAILED

### Lifecycle
States: PENDING → IN_PROGRESS → (SUCCEEDED | FAILED)
- Terminal: SUCCEEDED, FAILED
- Illegal transitions: terminal → non-terminal, FAILED → SUCCEEDED, SUCCEEDED → FAILED

### StateStore Interface (conceptual)
Methods:
- list_stacks() -> list[EnvironmentStack]
- create_request(stackId, forcedOutcome?) -> ProvisioningRequest
- get_request(id) -> ProvisioningRequest | None
- update_status(id, new_status, failureReason?) -> ProvisioningRequest
- list_active_requests() -> list[ProvisioningRequest] (status in PENDING/IN_PROGRESS)
- count_active_requests() -> int

Concurrency Limit:
- Before create_request: if count_active_requests() >= 5 -> raise LimitExceeded

### Error Model
| Field | Type | Notes |
|-------|------|-------|
| error.code | string | MACHINE_READABLE (e.g., `invalid_stack`, `limit_exceeded`, `not_found`) |
| error.message | string | Human readable |

### Deterministic Mode
Optional query/body flag (e.g., `mode=force_success` or `mode=force_failure`) sets forcedOutcome and bypasses randomness.

## Derived/Computed Fields
- updatedTimestamp: set on each status change
- completedTimestamp: set when entering terminal state

## OpenAPI Schema Alignment (to be added in contracts)
- Components: EnvironmentStack, ProvisioningRequest, ProvisioningStatus, ErrorResponse

*End of data model.*
