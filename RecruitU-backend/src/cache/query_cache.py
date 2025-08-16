"""
Query Parsing Cache Implementation

This module provides a cache for query parsing results to improve
performance by avoiding redundant LLM API calls.
"""

from typing import Dict, Any
import time
import hashlib


class QueryParsingCache:
    """
    In-memory cache for query parsing results.
    
    This cache stores LLM parsing results to avoid redundant API calls for identical
    queries. It includes automatic expiration and cleanup functionality.
    
    Attributes:
        cache (Dict): Internal storage for cached entries
        ttl (int): Time-to-live in seconds for cache entries
    """
    
    def __init__(self, ttl_seconds: int = 7200):  # 2 hours TTL
        """
        Initialize the cache with specified TTL.
        
        Args:
            ttl_seconds (int): Time-to-live for cache entries in seconds (default: 2 hours)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def _generate_key(self, query: str) -> str:
        """
        Generate a consistent cache key from the query string.
        
        The query is normalized (lowercased, whitespace trimmed) and hashed
        to create a consistent key for caching.
        
        Args:
            query (str): The original query string
            
        Returns:
            str: MD5 hash of the normalized query
        """
        # Normalize the query: lowercase, strip whitespace, remove extra spaces
        normalized_query = " ".join(query.lower().strip().split())
        # Create a hash for consistent key generation
        return hashlib.md5(normalized_query.encode()).hexdigest()
    
    def get(self, query: str) -> Dict[str, Any] | None:
        """
        Retrieve cached parsing result if it exists and hasn't expired.
        
        Args:
            query (str): The query to look up
            
        Returns:
            Dict[str, Any] | None: Cached result if found and valid, None otherwise
        """
        key = self._generate_key(query)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['result']
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, query: str, result: Dict[str, Any]) -> None:
        """
        Store parsing result in cache with current timestamp.
        
        Args:
            query (str): The original query string
            result (Dict[str, Any]): The parsing result to cache
        """
        key = self._generate_key(query)
        self.cache[key] = {
            'result': result.copy(),  # Store a copy to avoid mutation
            'timestamp': time.time(),
            'original_query': query  # Store original for debugging
        }
    
    def clear(self) -> int:
        """
        Clear all cached entries.
        
        Returns:
            int: Number of entries that were cleared
        """
        count = len(self.cache)
        self.cache.clear()
        return count
    
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
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dict[str, Any]: Statistics including total, expired, and active entries
        """
        current_time = time.time()
        total_entries = len(self.cache)
        expired_entries = sum(
            1 for entry in self.cache.values()
            if current_time - entry['timestamp'] >= self.ttl
        )
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'ttl_seconds': self.ttl
        }


# Global cache instance with 2-hour TTL
query_parsing_cache = QueryParsingCache(ttl_seconds=7200)

# Export list for module imports
__all__ = ['QueryParsingCache', 'query_parsing_cache']