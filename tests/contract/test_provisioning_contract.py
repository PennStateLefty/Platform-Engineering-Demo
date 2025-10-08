import yaml
from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from app.main import create_app

SPEC_PATH = Path(__file__).resolve().parents[2] / "specs" / "openapi.yaml"


@pytest.fixture(scope="module")
def spec():
    with SPEC_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_spec_includes_new_paths(spec):
    for path in ["/environment-stacks", "/provisioning-requests", "/provisioning-requests/{requestId}"]:
        assert path in spec["paths"], f"Expected {path} to be defined in OpenAPI contract."


def test_environment_stack_schema_contract(spec):
    stacks_schema = spec["components"]["schemas"].get("EnvironmentStack")
    assert stacks_schema, "EnvironmentStack schema must exist"
    for field in ["id", "name", "description", "category", "estimatedProvisionMinutes"]:
        assert field in stacks_schema["properties"], f"Missing EnvironmentStack property {field}"


def test_provisioning_request_schema_contract(spec):
    pr_schema = spec["components"]["schemas"].get("ProvisioningRequest")
    assert pr_schema, "ProvisioningRequest schema must exist"
    for field in [
        "id",
        "stackId",
        "projectName",
        "environment",
        "department",
        "status",
        "createdTimestamp",
        "updatedTimestamp",
    ]:
        assert field in pr_schema["properties"], f"Missing ProvisioningRequest property {field}"


# Endpoint behavior tests (expected to FAIL until implementation is added)
client = TestClient(create_app())


def test_list_environment_stacks_endpoint_contract():
    response = client.get("/environment-stacks")
    # Expected eventual outcome: 200 with JSON array
    assert response.status_code == 200, "Endpoint not yet implemented or returning incorrect status (contract-first)."
    assert isinstance(response.json(), list), "Response body MUST be a list of stacks."


def test_submit_provisioning_request_endpoint_contract():
    payload = {
        "stackId": "basic-web-app",
        "projectName": "Demo Project",
        "environment": "dev",
        "department": "Engineering",
    }
    response = client.post("/provisioning-requests", json=payload)
    # Expected eventual outcome: 202
    assert response.status_code == 202, "Provisioning submission contract not yet satisfied."
    body = response.json()
    for field in ["id", "stackId", "status", "createdTimestamp", "updatedTimestamp"]:
        assert field in body, f"Missing field {field} in provisioning response"


def test_get_provisioning_request_status_contract():
    # This test assumes at least one request created; without implementation it will 404.
    fake_id = "nonexistent-id"
    response = client.get(f"/provisioning-requests/{fake_id}")
    # Expected eventual contract: 404 for unknown id OR 200 for existing.
    # We assert 200 here to force red test until implemented properly (adjust later if needed).
    assert response.status_code == 200, "Status retrieval endpoint not yet implemented (red test)."


def test_invalid_stack_rejected_contract():
    payload = {
        "stackId": "does-not-exist",
        "projectName": "Demo Project",
        "environment": "dev",
        "department": "Engineering",
    }
    response = client.post("/provisioning-requests", json=payload)
    # Expect 400 once implemented; assert 400 now to keep test red until logic added.
    assert response.status_code == 400, "Invalid stack id should return 400 per contract once implemented."
