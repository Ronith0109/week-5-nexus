from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from .escalation import EscalationResult
from .validation import ValidationResult


class ResponseStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    ESCALATED = "escalated"
    BLOCKED = "blocked"
    FAILED = "failed"


class DraftResponse(BaseModel):
    """
    Customer-facing response proposed by the Drafting Agent.

    The draft must be grounded in GroundedContext.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str

    message: str = Field(
        min_length=1,
        max_length=5000,
    )

    evidence_ids: list[str] = Field(
        default_factory=list
    )

    proposed_action: str | None = None

    status: ResponseStatus = ResponseStatus.DRAFT


class FinalResponse(BaseModel):
    """
    Final response produced by the Nexus orchestration pipeline.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str
    customer_id: str

    message: str

    status: ResponseStatus

    validation: ValidationResult

    escalation: EscalationResult

    can_be_sent_to_customer: bool

    next_action: str | None = None