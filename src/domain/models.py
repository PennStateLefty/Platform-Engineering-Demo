from __future__ import annotations

from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, constr
import uuid


class ProvisioningStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

    @property
    def terminal(self) -> bool:
        return self in {self.SUCCEEDED, self.FAILED}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EnvironmentStack(BaseModel):
    id: constr(pattern=r"^[a-z0-9-]{3,40}$")  # type: ignore
    name: constr(min_length=3, max_length=60)  # type: ignore
    description: str
    category: str
    estimatedProvisionMinutes: int = Field(ge=1, le=120)


class ProvisioningRequest(BaseModel):
    id: str
    stackId: str
    projectName: constr(min_length=3, max_length=80)  # type: ignore
    environment: str  # validated externally (dev|qa|production)
    department: constr(min_length=2, max_length=60)  # type: ignore
    status: ProvisioningStatus
    createdTimestamp: datetime
    updatedTimestamp: datetime
    completedTimestamp: Optional[datetime] = None
    failureReason: Optional[str] = None
    forcedOutcome: Optional[str] = Field(default=None, description="SUCCESS|FAILURE when deterministic mode engaged")

    def mark_status(self, new_status: ProvisioningStatus, failure_reason: Optional[str] = None) -> None:
        if self.status.terminal:
            # Do not allow transitions out of terminal state
            return
        self.status = new_status
        self.updatedTimestamp = utc_now()
        if new_status.terminal:
            self.completedTimestamp = self.updatedTimestamp
            if new_status == ProvisioningStatus.FAILED and failure_reason:
                self.failureReason = failure_reason


def new_request(
    stack_id: str,
    project_name: str,
    environment: str,
    department: str,
    forced_outcome: Optional[str] = None,
) -> ProvisioningRequest:
    now = utc_now()
    return ProvisioningRequest(
        id=str(uuid.uuid4()),
        stackId=stack_id,
        projectName=project_name,
        environment=environment,
        department=department,
        status=ProvisioningStatus.PENDING,
        createdTimestamp=now,
        updatedTimestamp=now,
        forcedOutcome=forced_outcome,
    )
