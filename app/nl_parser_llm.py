from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError, validator
from openai import OpenAI
import os
import json
from pathlib import Path

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

# def build_system_prompt() -> str:
#     return (
#         "You convert natural-language queries about US finance/consulting professionals "
#         "into a strict JSON payload for the RecruitU /search API. "
#         "Only fill fields that are clearly implied. Never invent data. "
#         "Respond with JSON only, no commentary."
#     )

# def build_user_prompt(query: str) -> str:
#     examples = [
#         # few-shot pairs help the model learn your schema precisely
#         ("CMU '19 M&A at Evercore or Gugg in NYC",
#          {"current_company":"Evercore,Guggenheim","role":"M&A",
#           "undergraduate_year":2019,"city":"New York","sector":"FINANCE","count":20,"page":1}),
#         ("strategy consultants in SF, any year",
#          {"sector":"CONSULTING","city":"San Francisco","page":1,"count":20}),
#     ]
#     eg_txt = "\n".join(
#         [f"Q: {q}\nA: {a}" for q, a in examples]
#     )
#     return f"{eg_txt}\n\nQ: {query}\nA:"

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

# Provider-agnostic entrypoint. Swap in your LLM of choice.
def parse_with_llm(query: str) -> Dict[str, Any]:
    provider = (os.getenv("LLM_PROVIDER") or "none").lower()
    if provider == "none":
        raise RuntimeError("LLM disabled")
    if provider == "openai":
        return _openai_parse(query)
    # elif provider == "anthropic": ...
    # elif provider == "azure_openai": ...
    raise RuntimeError(f"Unsupported LLM_PROVIDER={provider}")

def _openai_parse(query: str) -> Dict[str, Any]:
    # Example using OpenAI responses with JSON mode (pseudo; adapt to your client)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    sys = build_system_prompt()
    user = build_user_prompt(query)
    try:
        # Use the OpenAI client to send a chat completion request
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}],
            response_format={"type": "json_object"},
            temperature=0
        )
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {e}")
    # resp = client.chat.completions.create(
    #     model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    #     messages=[{"role":"system","content":sys},{"role":"user","content":user}],
    #     response_format={"type":"json_object"},
    #     temperature=0
    # )
    raw = resp.choices[0].message.content
    import json
    try:
        obj = json.loads(raw)
        obj = normalize_slots(obj)
        # Validate schema strictly
        slots = NLSlots(**obj)
        return slots.dict(exclude_none=True)
    except (json.JSONDecodeError, ValidationError) as e:
        raise RuntimeError(f"LLM parse/validate failed: {e}")
