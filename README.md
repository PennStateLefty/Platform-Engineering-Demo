# Platform Engineering Demo

Contract-first FastAPI service used to demonstrate Azure solution engineering patterns.

## Stack
- Language: Python 3.11
- Framework: FastAPI
- ASGI Server: Uvicorn
- Testing: pytest + httpx TestClient
- Contract: OpenAPI 3.0 (`specs/openapi.yaml` authoritative)
- CI: GitHub Actions (`.github/workflows/ci.yml`)

## Quickstart (uv managed)

Install uv (once):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create & sync virtual env (auto) + run server (explicitly use Python 3.11 to avoid current 3.13 build issues in pydantic-core):
```bash
uv python install 3.11
uv sync --dev   # installs runtime + [tool.uv].dev-dependencies (pytest, ruff)
uv run uvicorn app.main:app --reload
```

Visit: http://localhost:8000/health

### Legacy (pip) Option
`requirements.txt` is retained for tooling compatibility; authoritative dependency list is in `pyproject.toml`.

## Tests

```bash
uv run pytest   # uses dev dependencies from [tool.uv]
```

## Contract-First Workflow
1. Modify `specs/openapi.yaml` (add or change endpoints).
2. Add/adjust contract tests in `tests/contract/`.
3. Implement or update endpoint logic.
4. Ensure all tests pass + CI green.

## Future Roadmap
- Security: integrate Azure Entra ID (JWT validation middleware).
- Observability: add structured logging + metrics emitters.
- MCP Integration: generate MCP contracts wrapping existing REST endpoints.
- Python 3.13 Enablement: remove `<3.13` constraint after upstream pydantic-core build stability confirmed.

## Governance
See `.specify/memory/constitution.md` for principles and quality gates.
