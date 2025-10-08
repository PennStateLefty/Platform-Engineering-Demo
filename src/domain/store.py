from __future__ import annotations

from typing import Dict, List, Optional, Protocol
from .models import EnvironmentStack, ProvisioningRequest, ProvisioningStatus, new_request
import random


class LimitExceeded(Exception):
    pass


class ProvisioningStore(Protocol):  # pragma: no cover - structural protocol
    def list_stacks(self) -> List[EnvironmentStack]: ...
    def create_request(self, *, stack_id: str, project_name: str, environment: str, department: str, forced_outcome: Optional[str]) -> ProvisioningRequest: ...
    def get_request(self, request_id: str) -> Optional[ProvisioningRequest]: ...
    def list_active(self) -> List[ProvisioningRequest]: ...
    def count_active(self) -> int: ...


class InMemoryProvisioningStore:
    def __init__(self, stacks: List[EnvironmentStack]):
        self._stacks: Dict[str, EnvironmentStack] = {s.id: s for s in stacks}
        self._requests: Dict[str, ProvisioningRequest] = {}
        self._failure_rate = 0.10
        self._concurrency_limit = 5

    # ---- Stacks ----
    def list_stacks(self) -> List[EnvironmentStack]:
        return list(self._stacks.values())

    # ---- Requests ----
    def create_request(
        self,
        *,
        stack_id: str,
        project_name: str,
        environment: str,
        department: str,
        forced_outcome: Optional[str],
    ) -> ProvisioningRequest:
        if stack_id not in self._stacks:
            raise ValueError("invalid_stack")
        if self.count_active() >= self._concurrency_limit:
            raise LimitExceeded("Too many active provisioning requests")
        pr = new_request(stack_id, project_name, environment, department, forced_outcome)
        self._requests[pr.id] = pr
        # Immediately bump to IN_PROGRESS for demo realism; completion deferred
        pr.mark_status(ProvisioningStatus.IN_PROGRESS)
        # Decide terminal state (simulate) if forced outcome absent
        if forced_outcome == "force_success":
            pr.mark_status(ProvisioningStatus.SUCCEEDED)
        elif forced_outcome == "force_failure":
            pr.mark_status(ProvisioningStatus.FAILED, failure_reason="Forced failure (demo mode)")
        else:
            # Random outcome quickly for now; could be scheduled later
            outcome_roll = random.random()
            if outcome_roll < (1 - self._failure_rate):
                pr.mark_status(ProvisioningStatus.SUCCEEDED)
            else:
                pr.mark_status(ProvisioningStatus.FAILED, failure_reason="Simulated failure")
        return pr

    def get_request(self, request_id: str) -> Optional[ProvisioningRequest]:
        return self._requests.get(request_id)

    def list_active(self) -> List[ProvisioningRequest]:
        return [r for r in self._requests.values() if not r.status.terminal]

    def count_active(self) -> int:
        return len(self.list_active())
