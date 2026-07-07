from pydantic import BaseModel
from typing import Literal


class SelfRAGDecision(BaseModel):
    decision: Literal["SUFFICIENT", "INSUFFICIENT"]
    reason: str


class QueryRewrite(BaseModel):
    rewritten_query: str
