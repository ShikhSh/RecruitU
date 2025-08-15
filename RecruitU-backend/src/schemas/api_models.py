"""
Pydantic Schema Models for RecruitU Backend

This module defines all Pydantic models used for request/response validation
and serialization in the RecruitU FastAPI application.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class NLSearchRequest(BaseModel):
    """
    Request model for natural language search endpoint.
    
    Attributes:
        query (str): Natural language search query
    """
    query: str = Field(..., description="Natural language search query", min_length=1)

class PersonLite(BaseModel):
    """
    Lightweight person model for search results.
    
    This model represents a condensed version of person data suitable
    for search result listings.
    
    Attributes:
        id (Optional[str]): Unique identifier for the person
        name (str): Full name of the person
        title (Optional[str]): Job title
        current_company (Optional[str]): Current employer
        previous_company (Optional[str]): Previous employer
        sector (Optional[str]): Industry sector (CONSULTING | FINANCE)
        undergraduate_year (Optional[int]): Year of undergraduate graduation
        city (Optional[str]): Current city/location
    """
    id: Optional[str] = None
    name: str
    title: Optional[str] = None
    current_company: Optional[str] = None
    previous_company: Optional[str] = None
    sector: Optional[str] = None  # CONSULTING | FINANCE
    undergraduate_year: Optional[int] = None
    city: Optional[str] = None


class SearchResponse(BaseModel):
    """
    Response model for search endpoints.
    
    This model represents the complete response from search operations,
    including results, pagination metadata, and error information.
    
    Attributes:
        results (List[Dict]): List of search results (flexible schema)
        total (Optional[int]): Total number of results available
        page (Optional[int]): Current page number
        count (Optional[int]): Number of results in this response
        filters (Optional[Dict]): Applied search filters
        success (Optional[bool]): Whether the search was successful
        error (Optional[str]): Error message if search failed
        nextPageToken (Optional[str]): Token for pagination (if supported)
    """
    results: List[PersonLite] = []
    total: Optional[int]
    nextPageToken: Optional[str]

class PeopleResponse(BaseModel):
    """
    Response model for people endpoint.
    
    This model has flexible typing to accommodate various response formats
    from the external people API.
    """
    __root__: Any = Field(
        ..., 
        description="Flexible response data from people API"
    )