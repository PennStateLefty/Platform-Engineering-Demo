from __future__ import annotations

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from domain.models import EnvironmentStack, ProvisioningRequest
from domain.store import InMemoryProvisioningStore, LimitExceeded
import importlib.metadata as metadata

SERVICE_NAME = "platform-engineering-demo"


_STORE: InMemoryProvisioningStore | None = None


def get_store() -> InMemoryProvisioningStore:
    global _STORE
    if _STORE is None:
        # Seed catalog
        stacks = [
            EnvironmentStack(
                id="basic-web-app",
                name="Basic Web App",
                description="Simple single-tier web application",
                category="web",
                estimatedProvisionMinutes=5,
            ),
            EnvironmentStack(
                id="basic-api-app",
                name="Basic API Application",
                description="Foundational API service template",
                category="api",
                estimatedProvisionMinutes=7,
            ),
            EnvironmentStack(
                id="microservice-service",
                name="Microservice",
                description="Independent microservice component",
                category="service",
                estimatedProvisionMinutes=9,
            ),
        ]
        _STORE = InMemoryProvisioningStore(stacks)
    return _STORE


def create_app() -> FastAPI:
    app = FastAPI(title="Platform Engineering Demo API")

    version = _get_version_fallback()

    @app.get("/health", tags=["system"], summary="Liveness and basic readiness check.")
    async def health():  # noqa: D401
        return {"status": "ok", "service": SERVICE_NAME, "version": version}

    # ---- Environment Stacks ----
    @app.get("/environment-stacks", tags=["stacks"], summary="List available environment stack blueprints", response_model=List[EnvironmentStack])
    async def list_environment_stacks(store: InMemoryProvisioningStore = Depends(get_store)):
        return store.list_stacks()

    # ---- Submit Provisioning Request ----
    @app.post(
        "/provisioning-requests",
        tags=["provisioning"],
        summary="Submit a new provisioning request (async simulated lifecycle)",
        status_code=202,
        response_model=ProvisioningRequest,
    )
    async def submit_provisioning_request(payload: dict, store: InMemoryProvisioningStore = Depends(get_store)):
        required = ["stackId", "projectName", "environment", "department"]
        missing = [f for f in required if f not in payload]
        if missing:
            raise HTTPException(status_code=400, detail={"error": {"code": "missing_fields", "message": f"Missing fields: {', '.join(missing)}"}})
        environment = payload["environment"]
        if environment not in {"dev", "qa", "production"}:
            raise HTTPException(status_code=400, detail={"error": {"code": "invalid_environment", "message": "environment must be one of dev|qa|production"}})
        mode = payload.get("mode")
        if mode and mode not in {"force_success", "force_failure"}:
            raise HTTPException(status_code=400, detail={"error": {"code": "invalid_mode", "message": "mode must be force_success|force_failure"}})
        try:
            pr = store.create_request(
                stack_id=payload["stackId"],
                project_name=payload["projectName"],
                environment=environment,
                department=payload["department"],
                forced_outcome=mode,
            )
        except LimitExceeded:
            return JSONResponse(status_code=429, content={"error": {"code": "limit_exceeded", "message": "Too many active provisioning requests"}})
        except ValueError as ve:
            if str(ve) == "invalid_stack":
                return JSONResponse(status_code=400, content={"error": {"code": "invalid_stack", "message": "Stack not found"}})
            raise
        return pr

    # ---- Get Provisioning Request Status ----
    @app.get(
        "/provisioning-requests/{request_id}",
        tags=["provisioning"],
        summary="Retrieve the current status of a provisioning request",
        response_model=ProvisioningRequest,
    )
    async def get_provisioning_request_status(request_id: str, store: InMemoryProvisioningStore = Depends(get_store)):
        pr = store.get_request(request_id)
        if not pr:
            return JSONResponse(status_code=404, content={"error": {"code": "not_found", "message": "Provisioning request not found"}})
        return pr

    return app


def _get_version_fallback() -> str:
    try:
        return metadata.version("platform-engineering-demo")
    except metadata.PackageNotFoundError:
        return "0.1.0"


app = create_app()
