import os
import json
import requests
from dotenv import load_dotenv
from prompts import (
    agronomist_template,
    summarizer_template,
    json_classifier_template,
)

# 1. Load the environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("CRITICAL ERROR: GROQ_API_KEY is missing from .env file.")

# 2. Define the exact API endpoint (Groq uses OpenAI's format)
URL = "https://api.groq.com/openai/v1/chat/completions"

# 3. Setup the HTTP Headers
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def call_llm(messages: list) -> str:
    """Sends a raw HTTP request to the LLM and returns the text response."""
    
    # 4. Construct the JSON payload
    payload = {
        "model": "llama-3.1-8b-instant", # Fast, free tier model
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }

    # 5. Execute the POST request
    try:
        response = requests.post(URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status() # Catches 401 Unauthorized, 404, 500, etc.
        
        # 6. Parse the raw JSON
        response_data = response.json()
        
        # 7. Extract the exact string the model generated
        return response_data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        return f"SYSTEM ERROR: API Call Failed. {e}"


def trim_history(history: list, max_messages: int = 10) -> list:
    """
    Ensures the conversation history does not exceed max_messages.
    ALWAYS preserves the System Prompt at index 0.
    """
    # If we are within the limit (+1 to account for the system prompt), do nothing
    if len(history) <= max_messages + 1:
        return history

    # Keep the system prompt (index 0) and the last 'max_messages' items
    return [history[0]] + history[-max_messages:]


def run_prompt_template_tests() -> None:
    """Executes CP-03 template checks and enforces JSON output validity."""
    print("Running CP-03 PromptTemplate tests...")

    role_based_prompt = agronomist_template.format(
        crop="Cavendish Banana",
        question="Lower leaves are yellowing from margins inward. What is your differential diagnosis?",
    )
    role_based_response = call_llm([{"role": "user", "content": role_based_prompt}])
    print("\n[Role-Based Q&A]\n" + role_based_response)

    summarizer_prompt = summarizer_template.format(
        text=(
            "The field team observed irregular chlorosis on older banana leaves with mild necrotic spotting. "
            "Recent rainfall was heavy for five days, and drainage channels were partially blocked. "
            "Leaf tissue analysis suggests marginal potassium deficiency."
        )
    )
    summarizer_response = call_llm([{"role": "user", "content": summarizer_prompt}])
    print("\n[Few-Shot Summarizer]\n" + summarizer_response)

    json_prompt = json_classifier_template.format(
        symptom_description=(
            "Cavendish banana lower leaves show yellow streaking that progresses to brown necrosis. "
            "Several plants have wilt and vascular discoloration in pseudostem cross-sections."
        )
    )
    json_response = call_llm([{"role": "user", "content": json_prompt}])
    print("\n[JSON Classifier Raw Output]\n" + json_response)

    try:
        parsed_json = json.loads(json_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "CP-03 GATE FAILED: JSON classifier output is not valid JSON. "
            "Tighten json_classifier_template to forbid markdown/fences and retry."
        ) from exc

    print("\n[JSON Classifier Parsed Output]\n" + str(parsed_json))
    print("CP-03 gate check passed: JSON output is valid.")


if __name__ == "__main__":
    run_prompt_template_tests()

    print("\nInitializing Project Aegis Base Terminal...")
    print("Type 'exit' or 'quit' to terminate.\n")

    # The System Prompt dictates the absolute rules the model must follow.
    conversation_history = [
        {"role": "system", "content": "You are a precise, highly technical AI assistant. Keep answers concise."}
    ]

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ['exit', 'quit']:
            print("Terminating session.")
            break

        # 1. Append the user's new message to the history
        conversation_history.append({"role": "user", "content": user_input})

        # 2. Enforce context limits (Keep only the last 6 messages + 1 system prompt)
        conversation_history = trim_history(conversation_history, max_messages=6)

        print("Thinking...")

        print(f"DEBUG: History length is {len(conversation_history)}")

        # 3. Send the optimized history to the model
        model_response = call_llm(conversation_history)

        print(f"\nAegis: {model_response}")

        # 3. Append the model's response to the history so it remembers this exchange
        conversation_history.append({"role": "assistant", "content": model_response})
