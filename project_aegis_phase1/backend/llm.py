import os
from typing import Any

import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")


def call_llm(messages: list[dict[str, Any]]) -> str:
    if not API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is missing in .env")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 500,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as exc:
        raise HTTPException(status_code=503, detail=f"LLM API unreachable: {exc}")
