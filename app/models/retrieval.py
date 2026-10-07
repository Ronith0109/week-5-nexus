from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RetrievalSource(str, Enum):
    VECTOR_KB = "vector_kb"
    MCP = "mcp"


class RetrievedDocument(BaseModel):
    """
    A document/chunk retrieved from the local vector knowledge base.
    """

    model_config = ConfigDict(extra="forbid")

    document_id: str
    product_line: str | None = None
    document_type: str
    topic: str | None = None

    content: str = Field(min_length=1)

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, str] = Field(default_factory=dict)

    source: RetrievalSource = RetrievalSource.VECTOR_KB


class StructuredFact(BaseModel):
    """
    A fact retrieved live through an MCP server.

    MCP structured data is authoritative over conflicting KB data.
    """

    model_config = ConfigDict(extra="forbid")

    server_name: str
    tool_name: str

    fact_id: str

    field: str
    value: str | int | float | bool | None

    source: RetrievalSource = RetrievalSource.MCP

    authoritative: bool = True

    masked: bool = True


class RetrievalConflict(BaseModel):
    """
    Represents a disagreement between unstructured KB content
    and live structured MCP data.
    """

    model_config = ConfigDict(extra="forbid")

    conflict_id: str

    field: str

    kb_value: str
    mcp_value: str

    kb_document_id: str | None = None

    mcp_server: str
    mcp_tool: str

    authoritative_source: RetrievalSource = RetrievalSource.MCP

    resolution: str = "structured_mcp_data_wins"

    surfaced_to_validation: bool = True


class RetrievalResult(BaseModel):
    """
    Raw hybrid retrieval result before reconciliation.
    """

    model_config = ConfigDict(extra="forbid")

    documents: list[RetrievedDocument] = Field(default_factory=list)

    structured_facts: list[StructuredFact] = Field(
        default_factory=list
    )

    retrieval_errors: list[str] = Field(
        default_factory=list
    )


class GroundedEvidence(BaseModel):
    """
    Evidence that the Drafting Agent is allowed to use.
    """

    model_config = ConfigDict(extra="forbid")

    evidence_id: str

    source: RetrievalSource

    content: str

    source_reference: str

    authoritative: bool = False


class GroundedContext(BaseModel):
    """
    Final reconciled evidence package passed to the Drafting Agent.

    Customer-facing claims should be derived only from this context.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str
    customer_id: str

    evidence: list[GroundedEvidence] = Field(
        default_factory=list
    )

    conflicts: list[RetrievalConflict] = Field(
        default_factory=list
    )

    authoritative_facts: list[StructuredFact] = Field(
        default_factory=list
    )

    retrieval_complete: bool = True

    grounding_summary: str = ""