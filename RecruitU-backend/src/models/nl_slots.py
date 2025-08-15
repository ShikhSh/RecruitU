"""
Natural Language Query Slot Models

This module defines the Pydantic models used for parsing and validating
natural language query parameters into structured search filters.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator

# Allowed sector values for validation
ALLOWED_SECTOR = {"CONSULTING", "FINANCE"}


class NLSlots(BaseModel):
    """
    Pydantic model for structured natural language query parameters.
    
    This model defines the schema for parsed query results, including
    validation rules and default values for search parameters.
    
    Attributes:
        name (Optional[str]): Person's name to search for
        current_company (Optional[str]): Current employer
        previous_company (Optional[str]): Previous employer
        sector (Optional[str]): Industry sector (CONSULTING or FINANCE)
        title (Optional[str]): Job title
        role (Optional[str]): Job role
        school (Optional[str]): Educational institution
        undergraduate_year (Optional[int]): Year of undergraduate graduation
        city (Optional[str]): Location/city
        page (int): Page number for pagination (default: 1)
        count (int): Number of results per page (default: 20)
    """
    
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
        """
        Validate that sector is one of the allowed values.
        
        Args:
            v: The sector value to validate
            
        Returns:
            str: The validated and normalized sector value
            
        Raises:
            ValueError: If sector is not in ALLOWED_SECTOR
        """
        if v is None: 
            return v
        v2 = v.upper().strip()
        if v2 not in ALLOWED_SECTOR:
            raise ValueError("sector must be CONSULTING or FINANCE")
        return v2


def normalize_slots(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and clean slot values from LLM parsing results.
    
    This function processes the raw dictionary from LLM parsing to:
    - Trim whitespace from string values
    - Remove empty or None values
    - Ensure valid page and count values with appropriate defaults and limits
    
    Args:
        d (Dict[str, Any]): Raw dictionary from LLM parsing
        
    Returns:
        Dict[str, Any]: Cleaned and normalized dictionary
    """
    # Trim strings, drop empties, clamp page/count
    cleaned: Dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, str):
            v = v.strip()
        if v in ("", None):
            continue
        cleaned[k] = v
    
    # Ensure valid pagination parameters
    cleaned["page"] = int(cleaned.get("page", 1) or 1)
    cleaned["count"] = int(cleaned.get("count", 20) or 20)
    cleaned["count"] = max(1, min(cleaned["count"], 200))  # Limit to reasonable range
    return cleaned


# Export list for module imports
__all__ = ['NLSlots', 'normalize_slots', 'ALLOWED_SECTOR']