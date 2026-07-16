from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str


class HealthResponse(BaseModel):
    success: bool = True
    status: str
    version: str
