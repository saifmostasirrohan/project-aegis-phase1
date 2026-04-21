import requests
import uuid

# Adjusting to the port you successfully used
BASE_URL = "http://127.0.0.1:8001"

def send_chat_message(message: str, session_id: str = None) -> dict:
    """Sends a message to the FastAPI backend and returns the response."""
    payload = {
        "message": message,
        "session_id": session_id if session_id else str(uuid.uuid4())
    }

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Backend API Error: {e}"}
