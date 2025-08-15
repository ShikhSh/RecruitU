from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class NLSearchRequest(BaseModel):
    query: str
    overrides: Optional[Dict[str, Any]] = None

class PersonLite(BaseModel):
    id: Optional[str] = None
    name: str
    title: Optional[str] = None
    current_company: Optional[str] = None
    previous_company: Optional[str] = None
    sector: Optional[str] = None  # CONSULTING | FINANCE
    undergraduate_year: Optional[int] = None
    city: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[PersonLite] = []
    total: Optional[int]
    nextPageToken: Optional[str]

class PeopleResponse(BaseModel):
    # loose typing; depends on real API
    __root__: Any