"""
Prompt Builder Utilities

This module provides utilities for building system and user prompts
for Large Language Model interactions, particularly for query parsing.
"""

from pathlib import Path
import json

# Load prompt configuration from JSON file
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "nl_parser.json"

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    PROMPT_DATA = json.load(f)


def build_system_prompt() -> str:
    """
    Build the system prompt for LLM query parsing.
    
    Uses the instructions from the prompt configuration file as the system message
    for consistent LLM behavior across parsing requests.
    
    Returns:
        str: System prompt text from configuration
    """
    return PROMPT_DATA["instructions"]


def build_user_prompt(query: str) -> str:
    """
    Build the user prompt for LLM query parsing.
    
    Formats the user query for submission to the LLM, following the
    expected input/output pattern. Examples are commented out but could 
    be re-enabled for few-shot learning.
    
    Args:
        query (str): The natural language query to parse
        
    Returns:
        str: Formatted user prompt
    """
    # Note: Examples are commented out but could be re-enabled for few-shot learning
    # examples_text = "\n".join(
    #     f"Input: {ex['input']}\nOutput: {ex['output']}"
    #     for ex in PROMPT_DATA.get("examples", [])
    # )
    # return f"{examples_text}\n\nInput: {query}\nOutput:"
    return f"\nInput: {query}\nOutput:"


# Export list for module imports
__all__ = ['build_system_prompt', 'build_user_prompt']