from fastapi import FastAPI, Depends, Query, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
from backend_app.config import Settings, get_settings
from backend_app.clients import people_api
from backend_app.nl_parser_llm import generate_query_with_llm, call_llm_for_suggestions_async
from backend_app.schemas import NLSearchRequest, SearchResponse, PeopleResponse
import os

app = FastAPI(title="RecruitU LateralGPT")

app.mount("/static", StaticFiles(directory="backend_app/static"), name="static")
templates = Jinja2Templates(directory="backend_app/templates")

@app.get("/health")
def health():
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/suggest_conversation")
async def suggest_conversation(payload: Dict[str, Any] = Body(...)):
    userA = payload.get("currentUser", {})
    userB = payload.get("inquiredUser", {})

    # Check if we have valid user data
    if not userA or not userB:
        return {"suggestions": ["Unable to generate suggestions - missing user data."]}
    
    # Compose a prompt for the LLM
    prompt = (
        f"User A: {userA}\n"
        f"User B: {userB}\n"
        "Find common backgrounds and suggest 2-3 ways User A can start a conversation with User B."
    )
    
    try:
        suggestions = await call_llm_for_suggestions_async(prompt)
        print(f"Raw LLM suggestions: {suggestions}")
        if not suggestions:
            suggestions = ["Consider reaching out to discuss shared professional interests."]
        return {"suggestions": suggestions}                
    except Exception as e:
        print(f"Error in suggest_conversation: {e}")
        return {"suggestions": [
            "You could reach out to discuss shared professional interests.",
            "Consider connecting over industry trends and insights.",
            "You might start with a comment about their recent career achievements."
        ]}

@app.post("/search_nl")
async def search_nl(req: NLSearchRequest, settings: Settings = Depends(get_settings)):
    use_llm = (os.getenv("LLM_PROVIDER") and os.getenv("LLM_PROVIDER").lower() != "none")
    parsed = {}
    if use_llm:
        try:
            parsed = generate_query_with_llm(req.query)
        except Exception as e:
            print(f"LLM parsing failed: {e}")

    # Defaults
    parsed.setdefault("page", 1)
    parsed.setdefault("count", 20)

    results = await people_api.search_with_formatted_results(parsed, settings=settings)
    return results

@app.get("/people", response_model=PeopleResponse)
async def proxy_people(
    ids: List[str] = Query(None, description="comma-separated ids"),
    settings: Settings = Depends(get_settings),
):
    if not ids or not ids[0]:
        return {"error": "User ID is required"}

    user_information = await people_api.get_user_information(ids[0], settings)
    if not user_information:
        return {"error": "User not found"}
    
    return user_information