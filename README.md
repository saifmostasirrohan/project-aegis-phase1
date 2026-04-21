# Project Aegis: Agronomy Assistant (Phase 1)

Project Aegis is a stateful, microservice-based AI assistant designed to provide accurate crop pathology intelligence. Phase 1 establishes the core architecture, enforcing strict data contracts and persistent memory before scaling to RAG and Agentic workflows.

## 🏗️ Architecture

- **Backend:** FastAPI (Python), handling strict validation via Pydantic.
- **Database:** SQLite with asynchronous SQLAlchemy ORM for conversational state persistence.
- **LLM Engine:** Groq API (Llama 3), controlled via rigid system prompting.
- **Frontend:** Streamlit, fully decoupled from the LLM and database.

## 🚀 Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone [your-repo-url]
   cd project_aegis_phase1
   ```

2. **Create and activate virtual environment (Windows PowerShell):**
   ```powershell
   python -m venv .venv
   (Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Create environment file:**
   - Create `.env` in the project root and add:
   ```env
   GROQ_API_KEY=your_actual_api_key_here
   ```

5. **Run the full stack (recommended, PowerShell):**
   ```powershell
   .\start-all.ps1
   ```
   This launches:
   - Backend API: `http://127.0.0.1:8001`
   - Frontend UI: `http://localhost:8501`

6. **Manual startup (alternative):**
   - Terminal 1 (backend):
   ```powershell
   .\start-backend.ps1
   ```
   - Terminal 2 (frontend):
   ```powershell
   .\start-frontend.ps1
   ```

## 🔎 API Endpoints

- `GET /health` - Service health check.
- `POST /diagnose` - Structured crop pathology classification.
- `POST /chat` - Stateful conversational endpoint with SQLite-backed memory.

## 🧠 Phase 1 Highlights

- Strict request/response contracts via Pydantic.
- JSON-safe LLM prompt constraints for backend reliability.
- Persistent chat memory surviving process restarts.
- Clean service separation between frontend, backend, and storage layers.
