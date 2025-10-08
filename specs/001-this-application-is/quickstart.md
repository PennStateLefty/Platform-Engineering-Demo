# Quickstart: Mock Environment Provisioning API

## Overview
This guide explains how to interact with the three new demo endpoints: list stacks, submit a provisioning request, and poll status. The feature is contract-first; ensure OpenAPI additions are merged before implementation.

## Endpoints
1. GET /environment-stacks
2. POST /provisioning-requests
3. GET /provisioning-requests/{requestId}

## Typical Flow
1. List available stacks.
2. Choose a stack id.
3. Submit provisioning request (optionally force success/failure via `mode`).
4. Poll status until terminal (SUCCEEDED/FAILED).

## Example Requests (Conceptual)
```
GET /environment-stacks
→ 200 [ { "id": "basic-web-app", ... } ]

POST /provisioning-requests
Body: { "stackId": "basic-web-app", "mode": "force_success" }
→ 202 { "id": "req_123", "status": "PENDING", ... }

GET /provisioning-requests/req_123
→ 200 { "id": "req_123", "status": "IN_PROGRESS" }
→ 200 { "id": "req_123", "status": "SUCCEEDED", "completedTimestamp": "..." }
```

## Error Examples
```
POST /provisioning-requests { "stackId": "unknown" }
→ 400 { "error": { "code": "invalid_stack", "message": "Stack not found" }}

POST /provisioning-requests (exceeding 5 active)
→ 429 { "error": { "code": "limit_exceeded", "message": "Too many active provisioning requests" }}

GET /provisioning-requests/bad-id
→ 404 { "error": { "code": "not_found", "message": "Provisioning request not found" }}
```

## Lifecycle Simulation
- Default path: PENDING → IN_PROGRESS → SUCCEEDED (90%) / FAILED (10%)
- Forced outcomes: supply `mode` with `force_success` or `force_failure` to override randomness.

## Testing Notes
- Contract tests validate schemas + status codes.
- Unit tests cover lifecycle transitions and failure injection.
- Rate limit test ensures 429 when >5 concurrent active requests.

## Next Steps
1. Merge contract additions into root OpenAPI.
2. Implement models/store/lifecycle.
3. Add contract + unit tests before endpoint logic.

*End of quickstart.*
