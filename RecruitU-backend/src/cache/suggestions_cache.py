"""
Conversation Suggestions Cache Implementation

This module provides a cache for conversation suggestions between users
to improve performance by avoiding redundant LLM API calls for the same user pairs.
"""

from typing import Dict, List, Any
import time


class SuggestionsCache:
    """
    Cache for conversation suggestions between users.

    This cache stores LLM-generated conversation suggestions to avoid redundant
    API calls for the same user pairs.
    
    Attributes:
        cache (Dict): Internal storage for cached suggestion entries
        ttl (int): Time-to-live in seconds for cache entries
    """
    
    def __init__(self, ttl_seconds: int = 3600):  # 1 hour TTL
        """
        Initialize the suggestions cache.
        
        Args:
            ttl_seconds (int): Time-to-live for cache entries in seconds (default: 1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def _generate_key(self, user_a: Dict, user_b: Dict) -> str:
        """
        Generate a cache key based on user IDs.
        
        Creates a consistent key for caching suggestions between two users,
        regardless of the order they're provided in.
        
        Args:
            user_a (Dict): First user's profile data
            user_b (Dict): Second user's profile data
            
        Returns:
            str: Cache key for the user pair
        """
        user_a_id = user_a.get('id', str(user_a))
        user_b_id = user_b.get('id', str(user_b))
        # Sort IDs to ensure consistent keys regardless of order
        ids = sorted([user_a_id, user_b_id])
        return f"{ids[0]}-{ids[1]}"
    
    def get(self, user_a: Dict, user_b: Dict) -> List[str] | None:
        """
        Retrieve cached suggestions if they exist and haven't expired.
        
        Args:
            user_a (Dict): First user's profile data
            user_b (Dict): Second user's profile data
            
        Returns:
            List[str] | None: Cached suggestions if found and valid, None otherwise
        """
        key = self._generate_key(user_a, user_b)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['suggestions']
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, user_a: Dict, user_b: Dict, suggestions: List[str]) -> None:
        """
        Cache suggestions with current timestamp.
        
        Args:
            user_a (Dict): First user's profile data
            user_b (Dict): Second user's profile data
            suggestions (List[str]): List of conversation suggestions to cache
        """
        key = self._generate_key(user_a, user_b)
        self.cache[key] = {
            'suggestions': suggestions.copy(),  # Store a copy to avoid mutation
            'timestamp': time.time(),
            'user_a_id': user_a.get('id', 'unknown'),
            'user_b_id': user_b.get('id', 'unknown')
        }
    
    def clear_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            int: Number of expired entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)
    
    def clear(self) -> int:
        """
        Clear all cached entries.
        
        Returns:
            int: Number of entries that were cleared
        """
        count = len(self.cache)
        self.cache.clear()
        return count


# Global cache instance with 1-hour TTL
suggestions_cache = SuggestionsCache(ttl_seconds=3600)

# Export list for module imports
__all__ = ['SuggestionsCache', 'suggestions_cache']
