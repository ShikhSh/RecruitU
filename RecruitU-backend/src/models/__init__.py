"""
Models Module

Contains Pydantic models and data validation logic for natural language
query parsing and structured data representation.
"""

from .nl_slots import NLSlots, normalize_slots, ALLOWED_SECTOR

__all__ = ['NLSlots', 'normalize_slots', 'ALLOWED_SECTOR']