from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, Field
import json
import os
import requests
import uuid
from dotenv import load_dotenv
from prompts import json_classifier_template
from database import engine, Base, get_db
import models

# Ensure environment is loaded
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

# --- PYDANTIC MODELS ---
class SymptomRequest(BaseModel):
    # Field enforces validation rules. The prompt cannot be empty or insanely long.
    symptom_description: str = Field(..., min_length=10, max_length=1000, description="The raw symptom text from the farmer.")

class DiagnosisResponse(BaseModel):
    suspected_disease: str
    confidence_score: float
    requires_quarantine: bool


class ChatRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Leave empty to start a new session")
    message: str = Field(..., min_length=2)


class ChatResponse(BaseModel):
    session_id: str
    response: str


# --- LLM ENGINE ---
def call_llm(messages: list) -> str:
    URL = "https://api.groq.com/openai/v1/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",  # Fast, free tier model (llama3-8b-8192 is decommissioned)
        "messages": messages,
        "temperature": 0.2,  # Lower temperature for classification tasks
        "max_tokens": 500
    }

    try:
        response = requests.post(URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"LLM API unreachable: {e}")


# --- FASTAPI APP ---
app = FastAPI(title="Aegis Crop Intelligence API", version="1.0")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Creates aegis_memory.db if it doesn't exist
        await conn.run_sync(models.Base.metadata.create_all)

@app.get("/health")
async def health_check():
    """Simple endpoint to verify the server is running."""
    return {"status": "operational"}

@app.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose_crop(request: SymptomRequest):
    """
    Takes a symptom description, passes it through the strict JSON prompt,
    and returns a structured Pydantic response.
    """
    # 1. Format the prompt
    formatted_prompt = json_classifier_template.format(symptom_description=request.symptom_description)

    # 2. Call the LLM
    raw_response = call_llm([{"role": "user", "content": formatted_prompt}])

    # 3. Parse and Validate
    try:
        parsed_data = json.loads(raw_response)
        # We pass the parsed dictionary directly into our Pydantic response model
        return DiagnosisResponse(**parsed_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM failed to return valid JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {e}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 1. Fetch existing message history for the session.
    history_query = (
        select(models.Message)
        .where(models.Message.session_id == request.session_id)
        .order_by(models.Message.timestamp)
    )
    history_result = await db.execute(history_query)
    existing_messages = history_result.scalars().all()

    # 2. Bootstrap a new session with a system prompt when this is first contact.
    if not existing_messages:
        db.add(models.ChatSession(session_id=request.session_id))
        db.add(
            models.Message(
                session_id=request.session_id,
                role="system",
                content="You are a precise, highly technical AI assistant. Keep answers concise.",
            )
        )

    # 3. Persist the user's newest message.
    db.add(models.Message(session_id=request.session_id, role="user", content=request.message))
    await db.commit()

    # 4. Re-query full history and map it to the Groq message format.
    full_history_result = await db.execute(history_query)
    full_history = full_history_result.scalars().all()
    llm_messages = [{"role": msg.role, "content": msg.content} for msg in full_history]

    # 5. Generate assistant response from the full conversation context.
    llm_response = call_llm(llm_messages)

    # 6. Persist assistant response.
    db.add(models.Message(session_id=request.session_id, role="assistant", content=llm_response))
    await db.commit()

    # 7. Return payload for client-side session continuation.
    return ChatResponse(session_id=request.session_id, response=llm_response)
