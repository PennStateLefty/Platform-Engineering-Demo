from __future__ import annotations

from fastapi import FastAPI
import importlib.metadata as metadata

SERVICE_NAME = "platform-engineering-demo"


def create_app() -> FastAPI:
    app = FastAPI(title="Platform Engineering Demo API")

    version = _get_version_fallback()

    @app.get("/health", tags=["system"], summary="Liveness and basic readiness check.")
    async def health():  # noqa: D401
        return {"status": "ok", "service": SERVICE_NAME, "version": version}

    return app


def _get_version_fallback() -> str:
    try:
        return metadata.version("platform-engineering-demo")
    except metadata.PackageNotFoundError:
        return "0.1.0"


app = create_app()
