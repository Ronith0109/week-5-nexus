from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductLine(str, Enum):
    BANKING = "banking"
    INSURANCE = "insurance"
    WEALTH = "wealth"
    CROSS_PRODUCT = "cross_product"


class RequestType(str, Enum):
    BALANCE_INQUIRY = "balance_inquiry"
    TRANSACTION_HISTORY = "transaction_history"
    LINKED_ACCOUNTS = "linked_accounts"

    AUTO_DEBIT_SETUP = "auto_debit_setup"
    PAYMENT_TERMS = "payment_terms"
    COVERAGE_QUESTION = "coverage_question"
    CLAIM_STATUS = "claim_status"

    PORTFOLIO_QUERY = "portfolio_query"
    INVESTMENT_PRODUCT_QUERY = "investment_product_query"
    SUITABILITY_CHECK = "suitability_check"

    COMPLAINT = "complaint"
    OTHER = "other"


class Urgency(str, Enum):
    ROUTINE = "routine"
    HIGH = "high"
    CRITICAL = "critical"


class EscalationCategory(str, Enum):
    NONE = "none"
    FINANCIAL_HARDSHIP = "financial_hardship"
    SAFEGUARDING_CONCERN = "safeguarding_concern"
    COMPLIANCE_OVERRIDE_REQUEST = "compliance_override_request"


class IntakeRequest(BaseModel):
    """
    Structured representation of a customer's inbound request.

    This is the contract produced by the Classifier Agent and validated
    before any retrieval or MCP operation is allowed.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(
        default_factory=lambda: f"REQ-{uuid4().hex[:12].upper()}"
    )

    customer_id: str

    product_line: ProductLine
    request_type: RequestType
    urgency: Urgency

    customer_stated_intent: str = Field(
        min_length=1,
        max_length=2000,
    )

    escalation_category: EscalationCategory = EscalationCategory.NONE

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, value: str) -> str:
        if not value.startswith("CUS-"):
            raise ValueError("customer_id must use CUS-XXXXX format")

        suffix = value[4:]

        if len(suffix) != 5 or not suffix.isdigit():
            raise ValueError("customer_id must use CUS-XXXXX format")

        return value

    @field_validator("customer_stated_intent")
    @classmethod
    def validate_intent(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("customer_stated_intent cannot be empty")

        return value