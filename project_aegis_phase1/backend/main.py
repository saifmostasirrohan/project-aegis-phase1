import json

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.database import engine, get_db
from backend.llm import call_llm
from backend.prompts import json_classifier_template
from backend.schemas import ChatRequest, ChatResponse, DiagnosisResponse, SymptomRequest
import backend.models as models


app = FastAPI(title="Aegis Crop Intelligence API", version="1.0")


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "operational"}


@app.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose_crop(request: SymptomRequest) -> DiagnosisResponse:
    formatted_prompt = json_classifier_template.format(
        symptom_description=request.symptom_description
    )
    raw_response = call_llm([{"role": "user", "content": formatted_prompt}])

    try:
        parsed_data = json.loads(raw_response)
        return DiagnosisResponse(**parsed_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM failed to return valid JSON.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Validation error: {exc}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)) -> ChatResponse:
    history_query = (
        select(models.Message)
        .where(models.Message.session_id == request.session_id)
        .order_by(models.Message.timestamp)
    )
    history_result = await db.execute(history_query)
    existing_messages = history_result.scalars().all()

    if not existing_messages:
        db.add(models.ChatSession(session_id=request.session_id))
        db.add(
            models.Message(
                session_id=request.session_id,
                role="system",
                content="You are a precise, highly technical AI assistant. Keep answers concise.",
            )
        )

    db.add(models.Message(session_id=request.session_id, role="user", content=request.message))
    await db.commit()

    full_history_result = await db.execute(history_query)
    full_history = full_history_result.scalars().all()
    llm_messages = [{"role": msg.role, "content": msg.content} for msg in full_history]

    llm_response = call_llm(llm_messages)

    db.add(models.Message(session_id=request.session_id, role="assistant", content=llm_response))
    await db.commit()

    return ChatResponse(session_id=request.session_id, response=llm_response)
