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


def _parse_json_response(raw_response: str) -> Dict[str, Any]:
    """
    Parse JSON response with fallback for malformed responses.
    
    Args:
        raw_response (str): Raw response content from Ollama
        
    Returns:
        Dict[str, Any]: Parsed JSON response
        
    Raises:
        RuntimeError: If response cannot be parsed as JSON
    """
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        # Fallback: extract JSON from potentially malformed response
        match = re.search(r"\{.*\}", raw_response, re.S)
        if not match:
            raise RuntimeError(f"Ollama did not return JSON: {raw_response[:200]}")
        return json.loads(match.group(0))


def _get_ollama_config() -> tuple[str, str]:
    """Get Ollama host and model configuration from environment variables."""
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    return host, model


def _build_chat_request(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """Build the chat request payload for Ollama API."""
    return {
        "messages": [
            {"role": "system", "content": system_prompt}, 
            {"role": "user", "content": user_prompt}
        ],
        "options": {"temperature": 0},  # Deterministic output
        "format": "json",
    }


def call_ollama_json(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Synchronously call Ollama API to get JSON response.
    
    Args:
        system_prompt (str): System message for the LLM
        user_prompt (str): User query/prompt
        
    Returns:
        Dict[str, Any]: Parsed JSON response from Ollama
        
    Raises:
        RuntimeError: If Ollama API call fails or returns invalid JSON
    """
    host, model = _get_ollama_config()
    
    try:
        client = Client(host=host)
        chat_request = _build_chat_request(system_prompt, user_prompt)
        resp = client.chat(model=model, **chat_request)
        return _parse_json_response(resp["message"]["content"])
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        raise RuntimeError(f"Ollama API call failed: {e}")


async def call_ollama_json_async(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Asynchronously call Ollama API to get JSON response.
    
    Args:
        system_prompt (str): System message for the LLM
        user_prompt (str): User query/prompt
        
    Returns:
        Dict[str, Any]: Parsed JSON response from Ollama
        
    Raises:
        RuntimeError: If Ollama API call fails or returns invalid JSON
    """
    host, model = _get_ollama_config()
    
    try:
        client = AsyncClient(host=host)
        chat_request = _build_chat_request(system_prompt, user_prompt)
        resp = await client.chat(model=model, **chat_request)
        return _parse_json_response(resp["message"]["content"])
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        raise RuntimeError(f"Ollama API call failed: {e}")


# Export list for module imports
__all__ = ['call_ollama_json', 'call_ollama_json_async']