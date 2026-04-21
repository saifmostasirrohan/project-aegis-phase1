# Project Aegis Phase 1

## Structure

- backend/database.py: SQLAlchemy engine and session logic
- backend/models.py: SQLAlchemy schemas
- backend/schemas.py: Pydantic request/response models
- backend/llm.py: Groq call_llm logic
- backend/prompts.py: PromptTemplate and prompts
- backend/main.py: FastAPI app and routes
- frontend/api_client.py: Backend HTTP client
- frontend/app.py: Streamlit UI

## Run

1. Open terminal in this folder:

```powershell
cd "project_aegis_phase1"
```

2. Start backend:

```powershell
uvicorn backend.main:app --port 8001
```

3. Start frontend (second terminal):

```powershell
cd frontend
streamlit run app.py --browser.gatherUsageStats false
```

4. Open frontend at http://localhost:8501
