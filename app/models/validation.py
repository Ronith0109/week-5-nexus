from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    severity: ValidationSeverity

    message: str

    evidence_reference: str | None = None

    blocks_response: bool = False


class ValidationResult(BaseModel):
    """
    Result produced by the Validation Agent.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str

    passed: bool

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    issues: list[ValidationIssue] = Field(
        default_factory=list
    )

    unsupported_claims: list[str] = Field(
        default_factory=list
    )

    pii_detected: bool = False

    conflicts_detected: bool = False

    grounding_valid: bool = True

    compliance_valid: bool = True