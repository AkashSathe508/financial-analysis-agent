from pydantic import BaseModel, Field


class GuardDecision(BaseModel):
    safe: bool = Field(
        description="True if the query is safe."
    )

    reason: str = Field(
        description="Reason for the decision."
    )


class CompanyExtraction(BaseModel):
    company: str
