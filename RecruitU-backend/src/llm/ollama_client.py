"""
Ollama Client Module

This module provides synchronous and asynchronous clients for interacting
with the Ollama API to get structured JSON responses from Large Language Models.
"""

from typing import Dict, Any
import os
import json
import re
from ollama import Client, AsyncClient


def call_ollama_json(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Synchronously call Ollama API to get JSON response.
    
    This is the synchronous version for blocking API calls to Ollama.
    It includes error handling and JSON extraction from potentially malformed responses.
    
    Args:
        system_prompt (str): System message for the LLM
        user_prompt (str): User query/prompt
        
    Returns:
        Dict[str, Any]: Parsed JSON response from Ollama
        
    Raises:
        RuntimeError: If Ollama API call fails or returns invalid JSON
    """
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    client = Client(host=host)
    
    try:
        resp = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0},  # Deterministic output
            format="json",
        )
        raw = resp["message"]["content"]
        
        # Try to parse JSON directly
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: extract JSON from potentially malformed response
            m = re.search(r"\{.*\}", raw, re.S)
            if not m:
                raise RuntimeError(f"Ollama did not return JSON: {raw[:200]}")
            return json.loads(m.group(0))
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        raise RuntimeError(f"Ollama API call failed: {e}")


async def call_ollama_json_async(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Asynchronously call Ollama API to get JSON response.
    
    This function makes an async API call to Ollama with the provided prompts
    and returns the parsed JSON response. It includes error handling and
    JSON extraction from potentially malformed responses.
    
    Args:
        system_prompt (str): System message for the LLM
        user_prompt (str): User query/prompt
        
    Returns:
        Dict[str, Any]: Parsed JSON response from Ollama
        
    Raises:
        RuntimeError: If Ollama API call fails or returns invalid JSON
    """
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    client = AsyncClient(host=host)
    
    try:
        resp = await client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0},  # Deterministic output
            format="json",
        )
        raw = resp["message"]["content"]
        
        # Try to parse JSON directly
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError(f"Ollama did not return JSON: {raw[:200]}")
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        raise RuntimeError(f"Ollama API call failed: {e}")


# Export list for module imports
__all__ = ['call_ollama_json', 'call_ollama_json_async']