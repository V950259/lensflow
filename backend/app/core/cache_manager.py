import hashlib
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class AsyncCacheManager:
    def __init__(self, max_size: int = 100, ttl_minutes: int = 60):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._ttl = timedelta(minutes=ttl_minutes)
        self._lock = asyncio.Lock()

    def _generate_key(self, content: str) -> str:
        """Generate a SHA-256 hash key from content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    async def get(self, content: str) -> Optional[Any]:
        """Retrieve value from cache if it exists and hasn't expired"""
        key = self._generate_key(content)
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if datetime.now() < entry['expires_at']:
                    # Move to end (LRU)
                    self._cache.pop(key)
                    self._cache[key] = entry
                    return entry['value']
                else:
                    del self._cache[key]
        return None

    async def set(self, content: str, value: Any):
        """Store value in cache"""
        key = self._generate_key(content)
        async with self._lock:
            # Evict if full
            if len(self._cache) >= self._max_size:
                # Remove first item (LRU policy since we re-insert on access)
                if self._cache:
                    first_key = next(iter(self._cache))
                    del self._cache[first_key]
            
            self._cache[key] = {
                'value': value,
                'expires_at': datetime.now() + self._ttl
            }
