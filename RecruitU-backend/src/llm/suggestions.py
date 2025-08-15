"""
Conversation Suggestions Module

This module provides functionality for generating conversation starter suggestions
using Large Language Models based on user profile commonalities.
"""

from typing import List
import json
import os
from .ollama_client import call_ollama_json_async


async def call_llm_for_suggestions_async(prompt: str) -> List[str]:
    """
    Asynchronously generate conversation suggestions using LLM.
    
    This function takes user profile information and generates conversation
    starter suggestions based on commonalities between two users. It handles
    various response formats and provides fallback suggestions.
    
    Args:
        prompt (str): Formatted prompt containing user profile information
        
    Returns:
        List[str]: List of conversation suggestions, or fallback message if LLM fails
    """
    sys = ("You are an expert networking assistant. Given two user profiles and their "
           "backgrounds, suggest 2-3 ways they could start a conversation based on their "
           "commonalities. Respond with a JSON object with just Arrays of Strings and no "
           "additional information: {\"suggestions\": [ ... ]}")
    user = prompt
    
    try:
        response = await call_ollama_json_async(sys, user)
        
        # Handle different response formats
        if isinstance(response, dict) and "suggestions" in response:
            return response["suggestions"]
        else:
            return []
    except Exception as e:
        print(f"LLM suggestion error: {e}")
        return ["Sorry, could not generate suggestions at this time."]


# Export list for module imports
__all__ = ['call_llm_for_suggestions_async']