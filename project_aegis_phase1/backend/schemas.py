from pydantic import BaseModel, Field
import uuid


class SymptomRequest(BaseModel):
    symptom_description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="The raw symptom text from the farmer.",
    )


class DiagnosisResponse(BaseModel):
    suspected_disease: str
    confidence_score: float
    requires_quarantine: bool


class ChatRequest(BaseModel):
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Leave empty to start a new session",
    )
    message: str = Field(..., min_length=2)


class ChatResponse(BaseModel):
    session_id: str
    response: str
