from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool = True
    session_id: str
    document_id: str
    cached: bool
    message: str = "Document processed successfully"
