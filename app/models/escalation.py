from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from .intake import EscalationCategory


class EscalationReason(str, Enum):
    NONE = "none"
    LOW_CONFIDENCE = "low_confidence"
    HARD_CATEGORY = "hard_category"
    VALIDATION_FAILURE = "validation_failure"
    MCP_FAILURE = "mcp_failure"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"


class EscalationResult(BaseModel):
    """
    Deterministic escalation decision returned after validation.

    Hard escalation categories must override confidence.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str
    customer_id: str

    should_escalate: bool

    category: EscalationCategory

    reason: EscalationReason

    draft_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    hard_escalation_triggered: bool = False

    decision_source: str = "concierge_ops.run_escalation_check"

    explanation: str

    human_action_required: bool = False