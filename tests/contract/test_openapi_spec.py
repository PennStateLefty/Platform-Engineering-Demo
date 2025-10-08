import yaml
from pathlib import Path

import pytest

SPEC_PATH = Path(__file__).resolve().parents[2] / "specs" / "openapi.yaml"


def test_openapi_spec_exists():
    assert SPEC_PATH.exists(), "OpenAPI spec file must exist (contract-first)."


def test_openapi_spec_parses():
    with SPEC_PATH.open("r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    assert spec["openapi"].startswith("3."), "Spec must be OpenAPI 3.x"
    assert "/health" in spec["paths"], "Health endpoint must be defined before implementation."


@pytest.mark.parametrize("method", ["get"])
def test_health_operation_contract(method):
    with SPEC_PATH.open("r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    op = spec["paths"]["/health"][method]
    assert op["operationId"] == "getHealth"
    responses = op["responses"]
    assert "200" in responses
    schema = responses["200"]["content"]["application/json"]["schema"]
    assert "$ref" in schema and schema["$ref"].endswith("HealthResponse")
