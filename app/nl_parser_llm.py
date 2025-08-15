from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from pathlib import Path
import os, json, re
from ollama import Client

# from .nl_parser_llm import NLSlots, normalize_slots

PROMPT_FILE = Path(__file__).parent / "prompts" / "nl_parser.json"

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    PROMPT_DATA = json.load(f)

ALLOWED_SECTOR = {"CONSULTING", "FINANCE"}

class NLSlots(BaseModel):
    name: Optional[str] = None
    current_company: Optional[str] = None
    previous_company: Optional[str] = None
    sector: Optional[str] = Field(default=None, description="CONSULTING or FINANCE")
    title: Optional[str] = None
    role: Optional[str] = None
    school: Optional[str] = None
    undergraduate_year: Optional[int] = None
    city: Optional[str] = None
    page: int = 1
    count: int = 20

    @validator("sector")
    def _sector_enum(cls, v):
        if v is None: 
            return v
        v2 = v.upper().strip()
        if v2 not in ALLOWED_SECTOR:
            raise ValueError("sector must be CONSULTING or FINANCE")
        return v2

def normalize_slots(d: Dict[str, Any]) -> Dict[str, Any]:
    # Trim strings, drop empties, clamp page/count
    cleaned: Dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, str):
            v = v.strip()
        if v in ("", None):
            continue
        cleaned[k] = v
    cleaned["page"] = int(cleaned.get("page", 1) or 1)
    cleaned["count"] = int(cleaned.get("count", 20) or 20)
    cleaned["count"] = max(1, min(cleaned["count"], 200))
    return cleaned

def build_system_prompt() -> str:
    """
    Use the instructions from the prompt file directly as the system message.
    """
    return PROMPT_DATA["instructions"]

def build_user_prompt(query: str) -> str:
    """
    Add the examples and the current query to the user message.
    """
    examples_text = "\n".join(
        f"Input: {ex['input']}\nOutput: {ex['output']}"
        for ex in PROMPT_DATA.get("examples", [])
    )
    return f"{examples_text}\n\nInput: {query}\nOutput:"

def generate_query_with_llm(query: str) -> Dict[str, Any]:
    provider = (os.getenv("LLM_PROVIDER") or "none").lower()
    if provider == "ollama":
        return _ollama_parse(query)
    # keep other branches if you want (openai, etc.)
    raise RuntimeError(f"Unsupported LLM_PROVIDER={provider}")

def call_ollama_json(system_prompt: str, user_prompt: str) -> dict:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    client = Client(host=host)
    try:
        resp = client.chat(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            options={"temperature": 0},
            format="json",
        )
        raw = resp["message"]["content"]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", raw, re.S)
            if not m:
                raise RuntimeError(f"Ollama did not return JSON: {raw[:200]}")
            return json.loads(m.group(0))
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        raise RuntimeError(f"Ollama API call failed: {e}")

def _ollama_parse(query: str) -> dict:
    sys = build_system_prompt()
    user = build_user_prompt(query)
    obj = call_ollama_json(sys, user)
    obj = normalize_slots(obj)
    slots = NLSlots(**obj)
    return slots.dict(exclude_none=True)

def call_llm_for_suggestions(prompt: str):
    """
    Calls the LLM with the given prompt and returns a list of suggestions.
    """
    sys = "You are an expert networking assistant. Given two user profiles and their backgrounds, suggest 2-3 ways they could start a conversation based on their commonalities. Respond with a JSON object: {\"suggestions\": [ ... ]}"
    user = prompt
    try:
        response = call_ollama_json(sys, user)
        if isinstance(response, dict) and "suggestions" in response:
            return response["suggestions"]
        elif isinstance(response, str):
            try:
                suggestions = json.loads(response)
                if isinstance(suggestions, list):
                    return suggestions
            except Exception:
                return [line.strip() for line in response.split("\n") if line.strip()]
        else:
            return []
    except Exception as e:
        print(f"LLM suggestion error: {e}")
        return ["Sorry, could not generate suggestions at this time."]


# def _ollama_parse(query: str) -> Dict[str, Any]:
#     host  = os.getenv("OLLAMA_HOST", "http://localhost:11434")
#     model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

#     client = Client(host=host)
#     sys = build_system_prompt()
#     user = build_user_prompt(query)

#     # Ask for JSON output. Most recent Llama models in Ollama honor `format="json"`.
#     try:
#         resp = client.chat(
#             model=model,
#             messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}],
#             options={"temperature": 0},
#             format="json",
#         )
#         raw = resp["message"]["content"]
#         obj = json.loads(raw)
#     except json.JSONDecodeError:
#         m = re.search(r"\{.*\}", raw, re.S)
#         if not m:
#             raise RuntimeError(f"Ollama did not return JSON: {raw[:200]}")
#         obj = json.loads(m.group(0))
#     except Exception as e:
#         print(f"Error calling Ollama API: {e}")
#         raise RuntimeError(f"Ollama API call failed: {e}")

#     obj = normalize_slots(obj)
#     slots = NLSlots(**obj)
#     return slots.dict(exclude_none=True)

# def call_llm_for_suggestions(prompt: str):
#     """
#     Calls the LLM with the given prompt and returns a list of suggestions.
#     You can adapt this to use your preferred LLM client.
#     """
#     # Example using Ollama via _ollama_parse (adapt as needed)
#     try:
#         # You may want to use your own LLM client here.
#         # For demonstration, let's assume _ollama_parse returns a dict with 'suggestions'
#         response = _ollama_parse(prompt)
#         # If your LLM returns a string, parse it into a list:
#         if isinstance(response, dict) and "suggestions" in response:
#             return response["suggestions"]
#         elif isinstance(response, str):
#             # Try to parse as JSON list or split by lines
#             try:
#                 suggestions = json.loads(response)
#                 if isinstance(suggestions, list):
#                     return suggestions
#             except Exception:
#                 return [line.strip() for line in response.split("\n") if line.strip()]
#         else:
#             return []
#     except Exception as e:
#         print(f"LLM suggestion error: {e}")
#         return ["Sorry, could not generate suggestions at this time."]