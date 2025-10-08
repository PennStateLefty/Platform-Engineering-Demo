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


def test_get_provisioning_request_status_contract_404_for_unknown():
    fake_id = "nonexistent-id"
    response = client.get(f"/provisioning-requests/{fake_id}")
    assert response.status_code == 404


def test_get_provisioning_request_status_contract_existing():
    payload = {
        "stackId": "basic-web-app",
        "projectName": "Status Demo",
        "environment": "dev",
        "department": "Engineering",
    }
    submit = client.post("/provisioning-requests", json=payload)
    assert submit.status_code == 202
    pr_id = submit.json()["id"]
    status_resp = client.get(f"/provisioning-requests/{pr_id}")
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body["id"] == pr_id
    assert body["stackId"] == "basic-web-app"


def test_invalid_stack_rejected_contract():
    payload = {
        "stackId": "does-not-exist",
        "projectName": "Demo Project",
        "environment": "dev",
        "department": "Engineering",
    }
    response = client.post("/provisioning-requests", json=payload)
    assert response.status_code == 400
