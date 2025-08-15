from fastapi import FastAPI, Depends, Query, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
from app.config import Settings, get_settings
from app.clients import people_api
# from app.nl_parser import parse_nl_query
from app.nl_parser_llm import generate_query_with_llm, call_llm_for_suggestions
from app.schemas import NLSearchRequest, SearchResponse, PeopleResponse
import os

app = FastAPI(title="RecruitU LateralGPT")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/health")
def health():
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/suggest_conversation")
async def suggest_conversation(payload: Dict[str, Any] = Body(...)):
    userA = payload["userA"]
    userB = payload["userB"]
    # Compose a prompt for the LLM
    prompt = (
        f"User A: {userA}\n"
        f"User B: {userB}\n"
        "Find common backgrounds and suggest 2-3 ways User A can start a conversation with User B."
    )
    suggestions = call_llm_for_suggestions(prompt)
    return {"suggestions": suggestions}

@app.post("/search_nl")
async def search_nl(req: NLSearchRequest, settings: Settings = Depends(get_settings)):
    use_llm = (os.getenv("LLM_PROVIDER") and os.getenv("LLM_PROVIDER").lower() != "none")
    parsed = {}
    if use_llm:
        try:
            parsed = generate_query_with_llm(req.query)
        except Exception as e:
            # fall back to deterministic parser
            print(f"LLM parsing failed: {e}")
    #         parsed = parse_nl_query(req.query)
    # else:
    #     parsed = parse_nl_query(req.query)

    # Allow caller overrides
    # if req.overrides:
    #     parsed.update({k: v for k, v in req.overrides.items() if v is not None})

    # Defaults
    parsed.setdefault("page", 1)
    parsed.setdefault("count", 20)

    results = await people_api.search(parsed, settings=settings)
    return {"filters": parsed, "results": results}

@app.get("/search", response_model=SearchResponse)
async def proxy_search(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (default 1)"),
    count: int = Query(20, ge=1, le=200, description="Items per page (default 20)"),
    settings: Settings = Depends(get_settings),
):
    allowed = {
        "name","current_company","previous_company","title","role",
        "undergraduate_year","city","sector","page","count"
    }
    params = dict(request.query_params.multi_items())
    params.update({"page": str(page), "count": str(count)})
    params = {k: v for k, v in params.items() if k in allowed}
    return await people_api.search(params, settings)

@app.get("/people", response_model=PeopleResponse)
async def proxy_people(
    ids: List[str] = Query(None, description="comma-separated ids"),
    settings: Settings = Depends(get_settings),
):
    current_person = await people_api.people(ids=ids, settings=settings)
    results = current_person.get("results", {})
    if not results or not ids or ids[0] not in results:
        return {"error": "User not found"}
    user_data = results[ids[0]]

    linkedin = user_data.get("linkedin", {})
    user_information = {
        "education": linkedin.get("education"),
        "occupation": linkedin.get("occupation"),
        "city": linkedin.get("city"),
        "volunteer_work": linkedin.get("volunteer_work"),
        "summary": linkedin.get("summary"),
        "headline": linkedin.get("headline"),
        "groups": linkedin.get("groups"),
        "certifications": linkedin.get("certifications"),
        "experiences": linkedin.get("experiences"),
        "full_name": linkedin.get("full_name"),
    }
    return user_information


# @app.post("/search_nl")
# async def search_nl(req: NLSearchRequest, settings: Settings = Depends(get_settings)):
#     """Turn NL into a structured payload, call People API /search, return results."""
#     parsed = parse_nl_query(req.query)
#     # Merge user-provided overrides
#     if req.overrides:
#         parsed.update({k: v for k, v in req.overrides.items() if v is not None})
#     results = await people_api.search(parsed, settings=settings)
#     return {"filters": parsed, "results": results}

# @app.post("/search_nl")
# async def search_nl(req: NLSearchRequest, settings: Settings = Depends(get_settings)):
#     """
#     Turn NL into a structured payload, call People API /search, and return results.
#     Supported params: name, current_company, previous_company, title, role,
#     undergraduate_year, city, sector, page, count
#     """
#     parsed = parse_nl_query(req.query)
#     if req.overrides:
#         parsed.update({k: v for k, v in req.overrides.items() if v is not None})
#     parsed.setdefault("page", 1)
#     parsed.setdefault("count", 20)
#     results = await people_api.search(parsed, settings=settings)
#     return {"filters": parsed, "results": results}

# @app.get("/export/csv")
# async def export_csv(
#     request: Request,
#     settings: Settings = Depends(get_settings),
# ):
#     params = dict(request.query_params.multi_items())
#     data = await people_api.search(params, settings)
#     csv_bytes = rows_to_csv(data.get("results", []))
#     return StreamingResponse(io.BytesIO(csv_bytes), media_type="text/csv", headers={
#         "Content-Disposition": "attachment; filename=results.csv"
#     })


# @app.get("/doppelganger")
# async def doppelganger(
#     source_id: str,
#     top_k: int = 20,
#     settings: Settings = Depends(get_settings)
# ):
#     source = await people_api.people(id=source_id, settings=settings)
#     # Candidate generation: for simplicity we re-use /search with coarse filters (same school/company if present)
#     coarse = {}
#     edu = (source or {}).get("education", [])
#     exp = (source or {}).get("experiences", [])
#     if edu:
#         coarse["school"] = ",".join({e.get("school", "") for e in edu if e.get("school")})
#     if exp:
#         coarse["company"] = ",".join({e.get("company", "") for e in exp if e.get("company")})
#     coarse["limit"] = 500
#     candidates = await people_api.search(coarse, settings=settings)
#     ranked = rank_similar(source, candidates.get("results", []), top_k=top_k)
#     return {"source": source, "matches": ranked}